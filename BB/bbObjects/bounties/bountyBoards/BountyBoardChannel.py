from __future__ import annotations
import discord
from discord import Embed, HTTPException, Forbidden, NotFound, Client, Message
from datetime import datetime, timedelta, timezone
from ....bbConfig import bbData, bbConfig
from .... import lib
from .. import bbCriminal
from ....logging import bbLogger
import asyncio
from .. import bbBounty
from typing import Dict, Union, List
from ....baseClasses import bbSerializable


def makeBountyEmbed(bounty : bbBounty.Bounty) -> Embed:
    """Construct a discord.Embed for listing in a BountyBoardChannel

    :param Bounty bounty: The bounty to describe in this embed
    :return: A discord.Embed describing statistics about the passed bounty
    :rtype: discord.Embed
    """
    embed = Embed(title=bounty.criminal.name, colour=bbData.factionColours[bounty.faction] if bounty.faction in bbData.factionColours else bbData.factionColours["neutral"])
    embed.set_footer(text=bounty.faction.title())
    embed.set_thumbnail(url=bounty.criminal.icon)
    embed.add_field(name="**Reward:**", value=lib.stringTyping.commaSplitNum(str(bounty.reward)) + " Credits")
    if bounty.issueTime > datetime.now(timezone.utc):
        embed.add_field(name="**Route:**", value=f"*Releases <t:{int(bounty.issueTime.timestamp())}:R>!*")
    else:
        routeStr = ""
        for system in bounty.route:
            if bounty.systemChecked(system):
                routeStr += "~~"
                if 0 < bounty.route.index(bounty.answer) - bounty.route.index(system) < bbConfig.closeBountyThreshold:
                    routeStr += "**" + system + "**"
                else:
                    routeStr += system
                routeStr += "~~"
            else:
                routeStr += system
            routeStr += ", "
        embed.add_field(name="**Route:**", value=routeStr[:-2], inline=False)
    embed.add_field(name="-", value="> ~~Already checked systems~~\n> **Criminal spotted here recently**") #"‎"
    # embed.add_field(value="`Stars indicate systems where the criminal has recently been spotted.`", name="`Crossed-through systems have already been checked.`")
    # embed.add_field(name="**Difficulty:**", value=str(bounty.criminal.techLevel))
    # embed.add_field(name="**See the culprit's loadout with:**", value="`" + bbConfig.commandPrefix + "loadout criminal " + bounty.criminal.name + "`")
    return embed

noBountiesEmbed = Embed(description='> Please check back later, or use the `$notify bounties` command to be notified when they spawn!', colour=discord.Colour.dark_orange())
noBountiesEmbed.set_author(name='No Bounties Available', icon_url='https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/stopwatch_23f1.png')


class BountyBoardChannel(bbSerializable.bbSerializable):
    """A channel which stores a continuously updating listing message for every active bounty.

    Initialisation atts: These attributes are used only when loading in the BBC from dictionary-serialised format. They must be used to initialise the BBC before the BBC can be used.
    :var messagesToBeLoaded: A dictionary of bounty listings to be loaded into the BBC, where keys are message IDs, and values are bbCriminal dicts
    :vartype messagesToBeLoaded: dict[int, dict]
    :var channelIDToBeLoaded: The discord channel ID of the channel where this BBC is active, to be loaded into the BBC
    :vartype channelIDToBeLoaded: int
    :var noBountiesMsgToBeLoaded: The id of the message to be loaded indicating that the BBC is empty, if one exists
    :vartype noBountiesMsgToBeLoaded: int

    Runtime atts: These are the attributes that contribute to the BBC's runtime functionality, unlike initialisation atts.
    :var bountyMessages: A dictionary associating faction names with the bounty listings associated with that faction. Listings are stored as a dictionary of the listing's bbCriminal to the message ID of the listing message.
    :vartype bountyMessages: dict[str, dict[bbCriminal, int]]
    :var noBountiesMessage: Either a reference to a discord.message indicating that the BBC is empty, or None if no empty board message exists 
    :vartype noBountiesMessage: discord.message or None
    :var channel: The channel where this BBC's listings are to be posted
    :vartype channel: discord.TextChannel
    """

    def __init__(self, channelIDToBeLoaded : int, messagesToBeLoaded : Dict[int, dict], noBountiesMsgToBeLoaded : Union[int, None]):
        """
        :param int channelIDToBeLoaded: The discord channel ID of the channel where this BBC is active, to be loaded into the BBC
        :param messagesToBeLoaded: A dictionary of bounty listings to be loaded into the BBC, where keys are message IDs, and values are bbCriminal dicts
        :type messagesToBeLoaded: dict[int, dict]
        :param int noBountiesMsgToBeLoaded: The id of the message to be loaded indicating that the BBC is empty, if one exists
        """
        self.messagesToBeLoaded = messagesToBeLoaded
        self.channelIDToBeLoaded = channelIDToBeLoaded
        self.noBountiesMsgToBeLoaded = noBountiesMsgToBeLoaded

        # dict of "faction": {criminal: int message ID}
        self.bountyMessages = {}
        # discord message object to be filled when no bounties exist
        self.noBountiesMessage = None
        # discord channel object
        self.channel = None


    async def init(self, client : Client, factions : List[str]):
        """Initialise the BBC's attributes to allow it to function.
        Initialisation is done here rather than in the constructor as initialisation can only be done asynchronously.

        :param discord.Client client: A logged in client instance used to fetch the BBC's message and channel instances
        :param list[str] factions: A list of faction names with which bounties can be associated
        """
        for fac in factions:
            self.bountyMessages[fac] = {}

        self.channel = client.get_channel(self.channelIDToBeLoaded)

        for id in self.messagesToBeLoaded:
            criminal = bbCriminal.Criminal.fromDict(self.messagesToBeLoaded[id])

            try:
                msg = await self.channel.fetch_message(id)
                self.bountyMessages[criminal.faction][criminal] = msg
            except HTTPException:
                succeeded = False
                for tryNum in range(bbConfig.bbcHTTPErrRetries):
                    try:
                        msg = await self.channel.fetch_message(id)
                        self.bountyMessages[criminal.faction][criminal] = msg
                        succeeded = True
                    except HTTPException:
                        await asyncio.sleep(bbConfig.bbcHTTPErrRetryDelaySeconds)
                        continue
                    break
                if not succeeded:
                    bbLogger.log("BBC", "init", "HTTPException thrown when fetching listing for criminal: " + criminal.name, category='bountyBoards', eventType="LISTING_LOAD-HTTPERR")
            except Forbidden:
                bbLogger.log("BBC", "init", "Forbidden exception thrown when fetching listing for criminal: " + criminal.name, category='bountyBoards', eventType="LISTING_LOAD-FORBIDDENERR")
            except NotFound:
                bbLogger.log("BBC", "init", "Listing message for criminal no longer exists: " + criminal.name, category='bountyBoards', eventType="LISTING_LOAD-NOT_FOUND")

        if self.noBountiesMsgToBeLoaded == -1:
            self.noBountiesMessage = None
            if self.isEmpty():
                try:
                    # self.noBountiesMessage = await self.channel.send(bbConfig.bbcNoBountiesMsg)
                    self.noBountiesMessage = await self.channel.send(embed=noBountiesEmbed)

                except HTTPException:
                    succeeded = False
                    for tryNum in range(bbConfig.bbcHTTPErrRetries):
                        try:
                            self.noBountiesMessage = await self.channel.send(embed=noBountiesEmbed)
                            succeeded = True
                        except HTTPException:
                            await asyncio.sleep(bbConfig.bbcHTTPErrRetryDelaySeconds)
                            continue
                        break
                    if not succeeded:
                        bbLogger.log("BBC", "init", "HTTPException thrown when sending no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-HTTPERR")
                    self.noBountiesMessage = None
                except Forbidden:
                    bbLogger.log("BBC", "init", "Forbidden exception thrown when sending no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-FORBIDDENERR")
                    self.noBountiesMessage = None
            
        else:
            try:
                self.noBountiesMessage = await self.channel.fetch_message(self.noBountiesMsgToBeLoaded)
            except HTTPException:
                succeeded = False
                for tryNum in range(bbConfig.bbcHTTPErrRetries):
                    try:
                        self.noBountiesMessage = await self.channel.fetch_message(self.noBountiesMsgToBeLoaded)
                        succeeded = True
                    except HTTPException:
                        await asyncio.sleep(bbConfig.bbcHTTPErrRetryDelaySeconds)
                        continue
                    break
                if not succeeded:
                    bbLogger.log("BBC", "init", "HTTPException thrown when fetching no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-HTTPERR")
            except Forbidden:
                bbLogger.log("BBC", "init", "Forbidden exception thrown when fetching no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-FORBIDDENERR")
            except NotFound:
                bbLogger.log("BBC", "init", "No bounties message no longer exists", category='bountyBoards', eventType="NOBTYMSG_LOAD-NOT_FOUND")
                self.noBountiesMessage = None
        # del self.messagesToBeLoaded
        # del self.channelIDToBeLoaded
        # del self.noBountiesMsgToBeLoaded


    def hasMessageForBounty(self, bounty : bbBounty.Bounty) -> bool:
        """Decide whether this BBC stores a listing for the given bounty 

        :param Bounty bounty: The bounty to check for listing existence
        :return: True if this BBC stores a listing for bounty, False otherwise
        :rtype: bool
        """
        return bounty.criminal in self.bountyMessages[bounty.criminal.faction]


    def getMessageForBounty(self, bounty : bbBounty.Bounty) -> Message:
        """Return the message acting as a listing for the given bounty

        :param Bounty bounty: The bounty to fetch a listing for
        :return: This BBC's message listing the given bounty
        :rtype: discord.Message
        """
        return self.bountyMessages[bounty.criminal.faction][bounty.criminal]


    def isEmpty(self) -> bool:
        """Decide whether this BBC stores any bounty listings

        :return: False if this BBC stores any bounty listings, True otherwise
        :rtype: bool
        """
        for faction in self.bountyMessages:
            if bool(self.bountyMessages[faction]):
                return False
        return True

    
    async def addBounty(self, bounty : bbBounty.Bounty, message : Message):
        """Treat the given message as a listing for the given bounty, and store it in the database.
        If the BBC was previously empty, remove the empty bounty board message if one exists.
        If a HTTP error is thrown when attempting to remove the empty board message, wait and retry the removal for the number of times defined in bbConfig

        :param Bounty bounty: The bounty to associate with the given message
        :param discord.Message message: The message acting as a listing for the given bounty
        """
        removeMsg = False
        if self.isEmpty():
            removeMsg = True

        if self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-ADD-BNTY_EXSTS: Attempted to add a bounty to a bountyboardchannel, but the bounty is already listed")
            bbLogger.log("BBC", "addBty", "Attempted to add a bounty to a bountyboardchannel, but the bounty is already listed: " + bounty.criminal.name, category='bountyBoards', eventType="LISTING_ADD-EXSTS")
        self.bountyMessages[bounty.criminal.faction][bounty.criminal] = message

        if removeMsg:
            try:
                await self.noBountiesMessage.delete()
            except HTTPException:
                succeeded = False
                for tryNum in range(bbConfig.bbcHTTPErrRetries):
                    try:
                        await self.noBountiesMessage.delete()
                        succeeded = True
                    except HTTPException:
                        await asyncio.sleep(bbConfig.bbcHTTPErrRetryDelaySeconds)
                        continue
                    break
                if not succeeded:
                    print("addBounty HTTPException")
            except Forbidden:
                print("addBounty Forbidden")
            except AttributeError:
                print("addBounty no message")
    

    async def removeBounty(self, bounty : bbBounty.Bounty):
        """Remove the listing message stored for the given bounty from the database. This does not attempt to delete the message from discord.
        If the BBC is now empty, send an empty bounty board message.
        If a HTTP error is thrown when sending the empty BBC message, wait and retry the removal for the number of times defined in bbConfig

        :param Bounty bounty: The bounty whose listing should be removed from the database
        :raise KeyError: If the database does not store a listing for the given bounty
        """
        if not self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-REM-BNTY_NOT_EXST: Attempted to remove a bounty from a bountyboardchannel, but the bounty is not listed")
            bbLogger.log("BBC", "remBty", "Attempted to remove a bounty from a bountyboardchannel, but the bounty is not listed: " + bounty.criminal.name, category='bountyBoards', eventType="LISTING_REM-NO_EXST")
        del self.bountyMessages[bounty.criminal.faction][bounty.criminal]

        if self.isEmpty():
            try:
                # self.noBountiesMessage = await self.channel.send(bbConfig.bbcNoBountiesMsg)
                self.noBountiesMessage = await self.channel.send(embed=noBountiesEmbed)

            except HTTPException:
                succeeded = False
                for tryNum in range(bbConfig.bbcHTTPErrRetries):
                    try:
                        self.noBountiesMessage = await self.channel.send(embed=noBountiesEmbed)
                        succeeded = True
                    except HTTPException:
                        await asyncio.sleep(bbConfig.bbcHTTPErrRetryDelaySeconds)
                        continue
                    break
                if not succeeded:
                    bbLogger.log("BBC", "remBty", "HTTPException thrown when sending no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-HTTPERR")
                self.noBountiesMessage = None
            except Forbidden:
                bbLogger.log("BBC", "remBty", "Forbidden exception thrown when sending no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-FORBIDDENERR")
                self.noBountiesMessage = None


    async def updateBountyMessage(self, bounty : bbBounty.Bounty):
        """Update the embed for the listing associated with the given bounty. This includes newly checked and near-correct systems along the route.
        If a HTTP error is thrown when updating the listing, wait and retry the edit for the number of times defined in bbConfig
        
        :param Bounty bounty: The bounty whose listing should be updated
        :raise KeyError: If the database does not store a listing for the given bounty
        """
        if not self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-UPD-BNTY_NOT_EXST: Attempted to update a BBC message for a criminal that is not listed")
            bbLogger.log("BBC", "remBty", "Attempted to update a BBC message for a criminal that is not listed: " + bounty.criminal.name, category='bountyBoards', eventType="LISTING_UPD-NO_EXST")

        content = self.bountyMessages[bounty.criminal.faction][bounty.criminal].content
        try:
            await self.bountyMessages[bounty.criminal.faction][bounty.criminal].edit(content=content, embed=makeBountyEmbed(bounty))
        except HTTPException:
            succeeded = False
            for tryNum in range(bbConfig.bbcHTTPErrRetries):
                try:
                    await self.bountyMessages[bounty.criminal.faction][bounty.criminal].edit(content=content, embed=makeBountyEmbed(bounty))
                    succeeded = True
                except HTTPException:
                    await asyncio.sleep(bbConfig.bbcHTTPErrRetryDelaySeconds)
                    continue
                break
            if not succeeded:
                bbLogger.log("BBC", "updBtyMsg", "HTTPException thrown when updating bounty listing for criminal: " + bounty.criminal.name, category='bountyBoards', eventType="UPD_LSTING-HTTPERR")
        except Forbidden:
            bbLogger.log("BBC", "updBtyMsg", "Forbidden exception thrown when updating bounty listing for criminal: " + bounty.criminal.name, category='bountyBoards', eventType="UPD_LSTING-FORBIDDENERR")
        except NotFound:
            bbLogger.log("BBC", "updBtyMsg", "Bounty listing message no longer exists, BBC entry removed: " + bounty.criminal.name, category='bountyBoards', eventType="UPD_LSTING-NOT_FOUND")
            await self.removeBounty(bounty)


    async def clear(self):
        """Clear all bounty listings on the board.
        """
        for fac in self.bountyMessages:
            for bounty in self.bountyMessages[fac]:
                await self.removeBounty(bounty)


    def toDict(self, **kwargs) -> dict:
        """Serialise this BBC to dictionary format

        :return: A dictionary containing all data needed to recreate this BBC
        :rtype: dict
        """
        # dict of message id: criminal dict
        listings = {}
        for fac in self.bountyMessages:
            for crim in self.bountyMessages[fac]:
                listings[self.bountyMessages[fac][crim].id] = crim.toDict(**kwargs)
        return {"channel":self.channel.id, "listings":listings, "noBountiesMsg": self.noBountiesMessage.id if self.noBountiesMessage is not None else -1}


    @classmethod
    def fromDict(cls, BBCDict : dict, **kwargs) -> BountyBoardChannel:
        """Factory function constructing a new BBC from the information in the provided dictionary - the opposite of BountyBoardChannel.toDict

        :param dict BBCDict: a dictionary representation of the BBC, to convert to an object
        :return: The new BountyBoardChannel object
        :rtype: BountyBoardChannel
        """
        if BBCDict is None:
            return None
        return BountyBoardChannel(BBCDict["channel"], BBCDict["listings"], BBCDict["noBountiesMsg"] if "noBountiesMsg" in BBCDict else -1)
