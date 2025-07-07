from __future__ import annotations

from discord import Embed
from datetime import datetime, timezone
from . import bbShop
from ..bbDatabases import bbBountyDB
from .bounties.bountyBoards import BountyBoardChannel
from ..userAlerts import UserAlerts
from discord import channel, Client, Forbidden, Guild, Member, Message, HTTPException, NotFound
from typing import List, Dict, Union, Optional
from ..bbConfig import bbConfig, bbData
from .. import bbGlobals, lib
from ..scheduling import TimedTask
from .bounties import bbBounty
from ..logging import bbLogger
from datetime import timedelta
from ..baseClasses import bbSerializable
from .statRace import StatRace


class NoneDCGuildObj(Exception):
    pass


class bbGuild(bbSerializable.bbSerializable):
    """A class representing a guild in discord, and storing extra BountyBot-related information about it. 
    
    :var id: The ID of the guild, directly corresponding to a discord guild's ID.
    :vartype id: int
    :var announceChannel: The discord.channel object for this guild's announcements chanel. None when no announce channel is set for this guild.
    :vartype announceChannel: discord.channel.TextChannel
    :var playChannel: The discord.channel object for this guild's bounty playing chanel. None when no bounty playing channel is set for this guild.
    :vartype playChannel: discord.channel.TextChannel
    :var shop: This guild's bbShop object
    :vartype shop: bbShop
    :var alertRoles: A dictionary of user alert IDs to guild role IDs.
    :vartype alertRoles: dict[str, int]
    :var bountyBoardChannel: A BountyBoardChannel object implementing this guild's bounty board channel if it has one, None otherwise.
    :vartype bountyBoardChannel: BountyBoardChannel
    :var hasBountyBoardChannel: Whether this guild has a bounty board channel or not
    :vartype hasBountyBoardChannel: bool
    :var ownedRoleMenus: The number of ReactionRolePickers present in this guild
    :vartype ownedRoleMenus: int
    :var bountiesDB: This guild's active bounties
    :vartype bountiesDB: bbBountyDB.bbBountyDB
    :var bountiesDisabled: Whether or not to disable this guild's bbBountyDB and bounty spawning
    :vartype bountiesDisabled: bool
    :var shopDisabled: Whether or not to disable this guild's bbShop and shop refreshing
    :vartype shopDisabled: bool
    :var dcGuild: This guild's corresponding discord.Guild object
    :vartype dcGuild: discord.Guild
    """

    def __init__(self, id : int, bountiesDB: bbBountyDB.bbBountyDB, dcGuild: Guild, announceChannel : channel.TextChannel = None,
            playChannel : channel.TextChannel = None, shop : bbShop.bbShop = None,
            bountyBoardChannel : BountyBoardChannel.BountyBoardChannel = None, alertRoles : Dict[str, int] = {},
            ownedRoleMenus : int = 0, bountiesDisabled : bool = False, shopDisabled : bool = False,
            statRaces: Optional[List[StatRace]] = None):
        """
        :param int id: The ID of the guild, directly corresponding to a discord guild's ID.
        :param bbBountyDB.bbBountyDB bountiesDB: This guild's active bounties
        :param discord.Guild guild: This guild's corresponding discord.Guild object
        :param discord.channel announceChannel: The discord.channel object for this guild's announcements chanel. None when no announce channel is set for this guild.
        :param discord.channel playChannel: The discord.channel object for this guild's bounty playing chanel. None when no bounty playing channel is set for this guild.
        :param bbShop shop: This guild's bbShop object
        :param dict[str, int] alertRoles: A dictionary of user alert IDs to guild role IDs.
        :param BoardBoardChannel bountyBoardChannel: A BountyBoardChannel object implementing this guild's bounty board channel if it has one, None otherwise.
        :param int ownedRoleMenus: The number of ReactionRolePickers present in this guild
        :param bool bountiesDisabled: Whether or not to disable this guild's bbBountyDB and bounty spawning
        :param bool shopDisabled: Whether or not to disable this guild's bbShop and shop refreshing
        :raise TypeError: When given an incompatible argument type
        """
        if type(id) == float:
            id = int(id)
        elif type(id) != int:
            raise TypeError("id must be int, given " + str(type(id)))

        if not isinstance(dcGuild, Guild):
            raise NoneDCGuildObj("Given dcGuild of type '" + dcGuild.__class__.__name__ + "', expecting discord.Guild")

        self.id = id
        self.announceChannel = announceChannel
        self.playChannel = playChannel

        self.shopDisabled = shopDisabled
        if shopDisabled:
            self.shop = None
        else:
            self.shop = bbShop.bbShop() if shop is None else shop
        
        self.alertRoles = {}
        for alertID in UserAlerts.userAlertsIDsTypes.keys():
            if issubclass(UserAlerts.userAlertsIDsTypes[alertID], UserAlerts.GuildRoleUserAlert):
                self.alertRoles[alertID] = alertRoles[alertID] if alertID in alertRoles else -1
        
        self.ownedRoleMenus = ownedRoleMenus
        self.dcGuild = dcGuild
        self.bountiesDB = bountiesDB
        self.bountiesDisabled = bountiesDisabled

        bountyDelayGenerators = {"random": lib.timeUtil.getRandomDelaySeconds,
                                "fixed-routeScale": self.getRouteScaledBountyDelayFixed,
                                "random-routeScale": self.getRouteScaledBountyDelayRandom}

        bountyDelayGeneratorArgs = {"random": bbConfig.newBountyDelayRandomRange,
                                    "fixed-routeScale": bbConfig.newBountyFixedDelta,
                                    "random-routeScale": bbConfig.newBountyDelayRandomRange}

        if bountiesDisabled:
            self.newBountyTT = None
            self.bountyBoardChannel = None
            self.hasBountyBoardChannel = False
        else:
            self.bountyBoardChannel = bountyBoardChannel
            self.hasBountyBoardChannel = bountyBoardChannel is not None

            if bbConfig.newBountyDelayType == "fixed":
                self.newBountyTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.newBountyFixedDelta), autoReschedule=True, expiryFunction=self.spawnAndAnnounceRandomBounty)
            else:
                try:
                    self.newBountyTT = TimedTask.DynamicRescheduleTask(
                        bountyDelayGenerators[bbConfig.newBountyDelayType], delayTimeGeneratorArgs=bountyDelayGeneratorArgs[bbConfig.newBountyDelayType], autoReschedule=True, expiryFunction=self.spawnAndAnnounceRandomBounty)
                except KeyError:
                    raise ValueError(
                        "bbConfig: Unrecognised newBountyDelayType '" + bbConfig.newBountyDelayType + "'")

            bbGlobals.newBountiesTTDB.scheduleTask(self.newBountyTT)
        
        self.statRaces = statRaces or []



    def getAnnounceChannel(self) -> channel.TextChannel:
        """Get the discord channel object of the guild's announcements channel.

        :return: the discord.channel of the guild's announcements channel
        :rtype: discord.channel.TextChannel
        :raise ValueError: If this guild does not have an announcements channel
        """
        if not self.hasAnnounceChannel():
            raise ValueError("This guild has no announce channel set")
        return self.announceChannel


    def getPlayChannel(self) -> channel.TextChannel:
        """Get the discord channel object of the guild's bounty playing channel.

        :return: the discord channel object of the guild's bounty playing channel
        :raise ValueError: If this guild does not have a play channel
        :rtype: discord.channel.TextChannel
        """
        if not self.hasPlayChannel():
            raise ValueError("This guild has no play channel set")
        return self.playChannel


    def setAnnounceChannel(self, announceChannel : channel.TextChannel):
        """Set the discord channel object of the guild's announcements channel.

        :param int announceChannel: The discord channel object of the guild's new announcements channel
        """
        self.announceChannel = announceChannel


    def setPlayChannel(self, playChannel : channel.TextChannel):
        """Set the discord channel of the guild's bounty playing channel.

        :param int playChannel: The discord channel object of the guild's new bounty playing channel
        """
        self.playChannel = playChannel
    

    def hasAnnounceChannel(self) -> bool:
        """Whether or not this guild has an announcements channel

        :return: True if this guild has a announcements channel, False otherwise
        :rtype bool:
        """
        return self.announceChannel is not None


    def hasPlayChannel(self) -> bool:
        """Whether or not this guild has a play channel

        :return: True if this guild has a play channel, False otherwise
        :rtype bool:
        """
        return self.playChannel is not None


    def removePlayChannel(self):
        """Remove and deactivate this guild's announcements channel.

        :raise ValueError: If this guild does not have a play channel
        """
        if not self.hasPlayChannel():
            raise ValueError("Attempted to remove play channel on a bbGuild that has no playChannel")
        self.playChannel = None

    
    def removeAnnounceChannel(self):
        """Remove and deactivate this guild's play channel.

        :raise ValueError: If this guild does not have an announcements channel
        """
        if not self.hasAnnounceChannel():
            raise ValueError("Attempted to remove announce channel on a bbGuild that has no announceChannel")
        self.announceChannel = None



    def getUserAlertRoleID(self, alertID : str) -> int:
        """Get the ID of this guild's alerts role for the given alert ID.

        :param str alertID: The alert ID for which the role ID should be fetched
        :return: The ID of the discord role that this guild mentions for the given alert ID.
        :rtype: int
        """
        return self.alertRoles[alertID]


    def setUserAlertRoleID(self, alertID : str, roleID : int):
        """Set the ID of this guild's alerts role for the given alert ID.

        :param str alertID: The alert ID for which the role ID should be set
        :param int roleID: The ID of the role which this guild should mention when alerting alertID
        """
        self.alertRoles[alertID] = roleID


    def removeUserAlertRoleID(self, alertID : str):
        """Remove the stored role and deactivate alerts for the given alertID

        :param str alertID: The alert ID for which the role ID should be removed
        """
        self.alertRoles[alertID] = -1

    
    def hasUserAlertRoleID(self, alertID : str) -> bool:
        """Decide whether or not this guild has a role set for the given alert ID.

        :param str alertID: The alert ID for which the role existence should be tested
        :return: True if this guild has a role set to mention for alertID
        :rtype: bool
        :raise KeyError: If given an unrecognised alertID
        """
        if alertID in self.alertRoles:
            return self.alertRoles[alertID] != -1
        raise KeyError("Unknown GuildRoleUserAlert ID: " + alertID)


    
    async def addBountyBoardChannel(self, channel : channel.TextChannel, client : Client, factions : List[str]):
        """Set this guild's bounty board channel.

        :param discord.Channel channel: The channel where bounty listings should be posted
        :param discord.Client client: A logged in client used to fetch the channel and any existing listings.
        :param list[str] factions: A list of faction names with which bounty listings can be associated
        :raise RuntimeError: If the guild already has an active BountyBoardChannel
        """
        if self.hasBountyBoardChannel:
            raise RuntimeError("Attempted to assign a bountyboard channel for guild " + str(self.id) + " but one is already assigned")
        self.bountyBoardChannel = BountyBoardChannel.BountyBoardChannel(channel.id, {}, -1)
        await self.bountyBoardChannel.init(client, factions)
        self.hasBountyBoardChannel = True

    
    def removeBountyBoardChannel(self):
        """Deactivate this guild's BountyBoardChannel. This does not remove any active bounty listing messages.

        :raise RuntimeError: If this guild does not have an active BountyBoardChannel.
        """
        if not self.hasBountyBoardChannel:
            raise RuntimeError("Attempted to remove a bountyboard channel for guild " + str(self.id) + " but none is assigned")
        self.bountyBoardChannel = None
        self.hasBountyBoardChannel = False


    async def makeBountyBoardChannelMessage(self, bounty : bbBounty.Bounty, msg : str = "", embed : Embed = None) -> Message:
        """Create a new BountyBoardChannel listing for the given bounty, in the given guild.
        guild must own a BountyBoardChannel.

        :param bbBounty.Bounty bounty: The bounty for which to create a listing
        :param str msg: The text to display in the listing message content (Default "")
        :param discord.Embed embed: The embed to display in the listing message - this will be removed immediately in place of the embed generated during BountyBoardChannel.updateBountyMessage, so is only really useful in case updateBountyMessage fails. (Default None)
        :return: The new discord message containing the BBC listing
        :rtype: discord.Message
        :raise ValueError: If guild does not own a BountyBoardChannel
        """
        if not self.hasBountyBoardChannel:
            raise ValueError("The requested bbGuild has no bountyBoardChannel")
        bountyListing = await self.bountyBoardChannel.channel.send(msg, embed=embed)
        await self.bountyBoardChannel.addBounty(bounty, bountyListing)
        await self.bountyBoardChannel.updateBountyMessage(bounty)
        return bountyListing


    async def removeBountyBoardChannelMessage(self, bounty : bbBounty.Bounty):
        """Remove guild's BountyBoardChannel listing for bounty.

        :param bbBounty bounty: The bounty whose BBC listing should be removed
        :raise ValueError: If guild does not own a BBC
        :raise KeyError: If the guild's BBC does not have a listing for bounty
        """
        if not self.hasBountyBoardChannel:
            raise ValueError("The requested bbGuild has no bountyBoardChannel")
        if self.bountyBoardChannel.hasMessageForBounty(bounty):
            try:
                await self.bountyBoardChannel.getMessageForBounty(bounty).delete()
            except HTTPException:
                bbLogger.log("Main", "rmBBCMsg", "HTTPException thrown when removing bounty listing message for criminal: " +
                            bounty.criminal.name, category='bountyBoards', eventType="RM_LISTING-HTTPERR")
            except Forbidden:
                bbLogger.log("Main", "rmBBCMsg", "Forbidden exception thrown when removing bounty listing message for criminal: " +
                            bounty.criminal.name, category='bountyBoards', eventType="RM_LISTING-FORBIDDENERR")
            except NotFound:
                bbLogger.log("Main", "rmBBCMsg", "Bounty listing message no longer exists, BBC entry removed: " +
                            bounty.criminal.name, category='bountyBoards', eventType="RM_LISTING-NOT_FOUND")
            await self.bountyBoardChannel.removeBounty(bounty)
        else:
            raise KeyError("The requested bbGuild (" + str(self.id) + ") does not have a BountyBoardChannel listing for the given bounty: " + bounty.criminal.name)


    async def updateBountyBoardChannel(self, bounty : bbBounty.Bounty, bountyComplete : bool = False):
        """Update the BBC listing for the given bounty in the given server.

        :param bbBounty bounty: The bounty whose listings should be updated
        :param bool bountyComplete: Whether or not the bounty has now been completed. When True, bounty listings will be removed rather than updated. (Default False)
        """
        if self.hasBountyBoardChannel:
            if bountyComplete and self.bountyBoardChannel.hasMessageForBounty(bounty):
                await self.removeBountyBoardChannelMessage(bounty)
            else:
                if not self.bountyBoardChannel.hasMessageForBounty(bounty):
                    await self.makeBountyBoardChannelMessage(bounty, "A new bounty is now available from **" + \
                                                                        bounty.faction.title() + "** central command:")
                else:
                    await self.bountyBoardChannel.updateBountyMessage(bounty)


    def getRouteScaledBountyDelayFixed(self, baseDelayDict : Dict[str, int]) -> timedelta:
        """New bounty delay generator, scaling a fixed delay by the length of the presently spawned bounty.

        :param dict baseDelayDict: A lib.timeUtil.timeDeltaFromDict-compliant dictionary describing the amount of time to wait after a bounty is spawned with route length 1
        :return: A datetime.timedelta indicating the time to wait before spawning a new bounty
        :rtype: datetime.timedelta
        """
        timeScale = bbConfig.fallbackRouteScale if self.bountiesDB.latestBounty is None else len(self.bountiesDB.latestBounty.route)
        delay = lib.timeUtil.timeDeltaFromDict(baseDelayDict) * timeScale * bbConfig.newBountyDelayRouteScaleCoefficient
        bbLogger.log("Main", "routeScaleBntyDelayFixed", "New bounty delay generated, " + \
                                                        ("no latest criminal." if self.bountiesDB.latestBounty is None else \
                                                            ("latest criminal: '" + self.bountiesDB.latestBounty.criminal.name + "'. Route Length " + str(len(self.bountiesDB.latestBounty.route)))) + \
                                                        "\nDelay picked: " + str(delay), category="newBounties", eventType="NONE_BTY" if self.bountiesDB.latestBounty is None else "DELAY_GEN", noPrint=True)
        return delay
        

    def getRouteScaledBountyDelayRandom(self, baseDelayDict : Dict[str, int]) -> timedelta:
        """New bounty delay generator, generating a random delay time between two points, scaled by the length of the presently spawned bounty.

        :param dict baseDelayDict: A dictionary describing the minimum and maximum time in seconds to wait after a bounty is spawned with route length 1
        :return: A datetime.timedelta indicating the time to wait before spawning a new bounty
        :rtype: datetime.timedelta
        """
        timeScale = bbConfig.fallbackRouteScale if self.bountiesDB.latestBounty is None else len(self.bountiesDB.latestBounty.route)
        delay = lib.timeUtil.getRandomDelaySeconds({"min": baseDelayDict["min"] * timeScale * bbConfig.newBountyDelayRouteScaleCoefficient,
                                        "max": baseDelayDict["max"] * timeScale * bbConfig.newBountyDelayRouteScaleCoefficient})
        bbLogger.log("Main", "routeScaleBntyDelayRand", "New bounty delay generated, " + \
                                                        ("no latest criminal." if self.bountiesDB.latestBounty is None else \
                                                            ("latest criminal: '" + self.bountiesDB.latestBounty.criminal.name + "'. Route Length " + str(len(self.bountiesDB.latestBounty.route)))) + \
                                                        "\nRange: " + str((baseDelayDict["min"] * timeScale * bbConfig.newBountyDelayRouteScaleCoefficient)/60) + "m - " + \
                                                                        str((baseDelayDict["max"] * timeScale * bbConfig.newBountyDelayRouteScaleCoefficient)/60) + \
                                                        "m\nDelay picked: " + str(delay), category="newBounties", eventType="NONE_BTY" if self.bountiesDB.latestBounty is None else "DELAY_GEN", noPrint=True)
        return delay

    
    async def announceNewBounty(self, newBounty : bbBounty.Bounty, doNotify: bool = True):
        """Announce the creation of a new bounty to this guild's announceChannel, if it has one

        :param bbBounty newBounty: the bounty to announce
        :param bool doNotify: Give true to ping, false to not ping
        """
        if datetime.fromtimestamp(newBounty.issueTime, timezone.utc) > datetime.now(timezone.utc):
            bbGlobals.newBountiesTTDB.scheduleTask(TimedTask.TimedTask(expiryTime=datetime.fromtimestamp(newBounty.issueTime, timezone.utc), expiryFunction=self.announceNewBountyRoute, expiryFunctionArgs=newBounty))

        msg = f"A {newBounty.reward} credit bounty is now available from **{newBounty.faction.title()}** central command:"
        if self.hasBountyBoardChannel:
            try:
                if doNotify and self.hasUserAlertRoleID("bounties_new"):
                    roleId = self.getUserAlertRoleID("bounties_new")
                    msg = f"<@&{roleId}> {msg}"
                # announce to the given channel
                bountyEmbed = BountyBoardChannel.makeBountyEmbed(newBounty)
                bountyListing = await self.bountyBoardChannel.channel.send(msg, embed=bountyEmbed)
                await self.bountyBoardChannel.addBounty(newBounty, bountyListing)
                await self.bountyBoardChannel.updateBountyMessage(newBounty)
                return bountyListing

            except Forbidden:
                bbLogger.log("bbGuild", "anncBnty", "Failed to post BBCh listing to guild " + bbGlobals.client.get_guild(
                    self.id).name + "#" + str(self.id) + " in channel " + self.bountyBoardChannel.channel.name + "#" + str(self.bountyBoardChannel.channel.id), category="bountyBoards", eventType="BBC_NW_FRBDN")

        # If the guild has an announceChannel
        elif self.hasAnnounceChannel():
            # ensure the announceChannel is valid
            currentChannel = self.getAnnounceChannel()
            if currentChannel is not None:
                # Create the announcement embed
                bountyEmbed = lib.discordUtil.makeEmbed(titleTxt=lib.discordUtil.criminalNameOrDiscrim(newBounty.criminal), desc="⛓ __New Bounty Available__",
                                        col=bbData.factionColours[newBounty.faction], thumb=newBounty.criminal.icon, footerTxt=newBounty.faction.title())
                bountyEmbed.add_field(name="Reward:", value=str(
                    newBounty.reward) + " Credits")
                bountyEmbed.add_field(name="Possible Systems:", value=len(newBounty.route))
                if datetime.fromtimestamp(newBounty.issueTime, timezone.utc) > datetime.now(timezone.utc):
                    bountyEmbed.add_field(
                        name="**Route:**",
                        value=f"*Releases <t:{int(newBounty.issueTime)}:R>!*\nOnce released,"
                            + f"See the culprit's route with: `{bbConfig.commandPrefix}route {lib.discordUtil.criminalNameOrDiscrim(newBounty.criminal)}`",
                        inline=False)
                else:
                    bountyEmbed.add_field(
                        name="**Route:**",
                        value=f"See the culprit's route with: `{bbConfig.commandPrefix}route {lib.discordUtil.criminalNameOrDiscrim(newBounty.criminal)}`",
                        inline=False)
                
                # Create the announcement text
                msg = f"A new bounty is now available from **{newBounty.faction.title()}** central command:"
                try:
                    if doNotify and self.hasUserAlertRoleID("bounties_new"):
                        # announce to the given channel
                        await currentChannel.send("<@&" + str(self.getUserAlertRoleID("bounties_new")) + "> " + msg, embed=bountyEmbed)
                    else:
                        await currentChannel.send(msg, embed=bountyEmbed)
                except Forbidden:
                    bbLogger.log("bbGuild", "anncBnty", "Failed to post announce-channel bounty listing to guild " + bbGlobals.client.get_guild(
                        self.id).name + "#" + str(self.id) + " in channel " + currentChannel.name + "#" + str(currentChannel.id), eventType="ANNCCH_SND_FRBDN")

            # TODO: may wish to add handling for invalid announceChannels - e.g remove them from the bbGuild object


    async def announceNewBountyRoute(self, newBounty : bbBounty.Bounty):
        if self.hasBountyBoardChannel:
            await self.bountyBoardChannel.updateBountyMessage(newBounty)
        # Nothing to do if there's no bountyboardchannel

    async def spawnAndAnnounceRandomBounty(self):
        """Generate a completely random bounty, spawn it, and announce it if this guild has
        an appropriate channel selected.
        """
        if self.bountiesDisabled:
            raise ValueError("Attempted to spawn a bounty into a guild where bounties are disabled")
        # ensure a new bounty can be created
        if self.bountiesDB.canMakeBounty():
            newBounty = bbBounty.Bounty(bountyDB=self.bountiesDB)
            newBounty.issueTime = (datetime.now(timezone.utc) + timedelta(seconds=bbConfig.newBountyWarningTimeSeconds)).timestamp()
            # activate and announce the bounty
            self.bountiesDB.addBounty(newBounty)
            await self.announceNewBounty(newBounty)


    async def announceBountyWon(self, bounty : bbBounty.Bounty, rewards : Dict[int, Dict[str, Union[int, bool]]], winningUser : Member):
        """Announce the completion of a bounty
        Messages will be sent to the playChannel if one is set

        :param bbBounty bounty: the bounty to announce
        :param dict rewards: the rewards dictionary as defined by bbBounty.calculateRewards
        :param discord.Member winningUser: the guild member that won the bounty
        """
        if self.dcGuild is not None:
            if self.hasPlayChannel():
                winningUserId = winningUser.id
                # Create the announcement embed
                rewardsEmbed = lib.discordUtil.makeEmbed(titleTxt="Bounty Complete!", authorName=lib.discordUtil.criminalNameOrDiscrim(bounty.criminal) + " Arrested",
                                        icon=bounty.criminal.icon, col=bbData.factionColours[bounty.faction], desc="`Suspect located in '" + bounty.answer + "'`")

                # Add the winning user to the embed
                rewardsEmbed.add_field(name="1. 🏆 " + str(rewards[winningUserId]["reward"]) + " credits:", value=winningUser.mention + " checked " + str(
                    int(rewards[winningUserId]["checked"])) + " system" + ("s" if int(rewards[winningUserId]["checked"]) != 1 else ""), inline=False)

                # The index of the current user in the embed
                place = 2
                # Loop over all non-winning users in the rewards dictionary
                for userID in rewards:
                    if not rewards[userID]["won"]:
                        rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value="<@" + str(userID) + "> checked " + str(
                            int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[userID]["checked"]) != 1 else ""), inline=False)
                        place += 1

                # Send the announcement to the guild's playChannel
                await self.getPlayChannel().send(":trophy: **You win!**\n**" + winningUser.display_name + "** located and EMP'd **" + bounty.criminal.name + "**, who has been arrested by local security forces. :chains:", embed=rewardsEmbed)

        else:
            bbLogger.log("Main", "AnncBtyWn", "None dcGuild received when posting bounty won to guild " + bbGlobals.client.get_guild(
                self.id).name + "#" + str(self.id) + " in channel ?#" + str(self.getPlayChannel().id), eventType="DCGUILD_NONE")


    def enableBounties(self):
        """Enable bounties for this guild.
        Sets up a new bounties DB and bounty spawning TimedTask.

        :raise ValueError: If bounties are already enabled in this guild
        """
        if not self.bountiesDisabled:
            raise ValueError("Bounties are already enabled in this guild")

        self.bountiesDB = bbBountyDB.bbBountyDB(bbData.bountyFactions)

        bountyDelayGenerators = {"random": lib.timeUtil.getRandomDelaySeconds,
                                "fixed-routeScale": self.getRouteScaledBountyDelayFixed,
                                "random-routeScale": self.getRouteScaledBountyDelayRandom}

        bountyDelayGeneratorArgs = {"random": bbConfig.newBountyDelayRandomRange,
                                    "fixed-routeScale": bbConfig.newBountyFixedDelta,
                                    "random-routeScale": bbConfig.newBountyDelayRandomRange}

        if bbConfig.newBountyDelayType == "fixed":
            self.newBountyTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.newBountyFixedDelta), autoReschedule=True, expiryFunction=self.spawnAndAnnounceRandomBounty)
        else:
            try:
                self.newBountyTT = TimedTask.DynamicRescheduleTask(
                    bountyDelayGenerators[bbConfig.newBountyDelayType], delayTimeGeneratorArgs=bountyDelayGeneratorArgs[bbConfig.newBountyDelayType], autoReschedule=True, expiryFunction=self.spawnAndAnnounceRandomBounty)
            except KeyError:
                raise ValueError(
                    "bbConfig: Unrecognised newBountyDelayType '" + bbConfig.newBountyDelayType + "'")
                    
        bbGlobals.newBountiesTTDB.scheduleTask(self.newBountyTT)
        self.bountiesDisabled = False


    def disableBounties(self):
        """Disable bounties for this guild.
        Removes any bountyboard if one is present, and removes the guild's bounties DB and bounty spawning TimedTask.
        
        :raise ValueError: If bounties are already disabled in this guild
        """
        if self.bountiesDisabled:
            raise ValueError("Bounties are already disabled in this guild")

        if self.hasBountyBoardChannel:
            self.removeBountyBoardChannel()
        bbGlobals.newBountiesTTDB.unscheduleTask(self.newBountyTT)
        self.newBountyTT = None
        self.bountiesDisabled = True
        self.bountiesDB = None


    def enableShop(self):
        """Enable the shop for this guild.
        Creates a new bbShop object for this guild.
        
        :raise ValueError: If the shop is already enabled in this guild
        """
        if not self.shopDisabled:
            raise ValueError("The shop is already enabled in this guild")

        self.shop = bbShop.bbShop(noRefresh=True)
        self.shopDisabled = False


    def disableShop(self):
        """Disable the shop for this guild.
        Removes the guild's bbShop object.
        
        :raise ValueError: If the shop is already disabled in this guild
        """
        if self.shopDisabled:
            raise ValueError("The shop is already disabled in this guild")

        self.shop = None
        self.shopDisabled = True


    async def announceNewShopStock(self):
        """Announce to the guild's play channel that this guild's shop stock has been refreshed.
        If no playChannel has been set, does nothing.

        :raise ValueError: If this guild's shop is disabled
        """
        if self.shopDisabled:
            raise ValueError("Attempted to announceNewShopStock on a guild where shop is disabled")
        if self.hasPlayChannel():
            playCh = self.getPlayChannel()
            msg = "The shop stock has been refreshed!\n**        **Now at tech level: **" + \
                str(self.shop.currentTechLevel) + "**"
            try:
                if self.hasUserAlertRoleID("shop_refresh"):
                    # announce to the given channel
                    await playCh.send(":arrows_counterclockwise: <@&" + str(self.getUserAlertRoleID("shop_refresh")) + "> " + msg)
                else:
                    await playCh.send(":arrows_counterclockwise: " + msg)
            except Forbidden:
                bbLogger.log("Main", "anncNwShp", "Failed to post shop stock announcement to " + self.dcGuild.name + "#" + str(self.id) + " in channel " + playCh.name + "#" + str(playCh.id), category="shop", eventType="PLCH_NONE")


    def toDict(self, **kwargs) -> dict:
        """Serialize this bbGuild into dictionary format to be saved to file.

        :return: A dictionary containing all information needed to reconstruct this bbGuild
        :rtype: dict
        """
        data = {"announceChannel":self.announceChannel.id if self.hasAnnounceChannel() else -1,
                    "playChannel":self.playChannel.id if self.hasPlayChannel() else -1, 
                    "alertRoles": self.alertRoles,
                    "ownedRoleMenus": self.ownedRoleMenus,
                    "bountiesDisabled": self.bountiesDisabled,
                    "shopDisabled": self.shopDisabled
                    }
        if not self.bountiesDisabled:
            data["bountyBoardChannel"] = self.bountyBoardChannel.toDict(**kwargs) if self.hasBountyBoardChannel else None
            data["bountiesDB"] = self.bountiesDB.toDict(**kwargs)

        if not self.shopDisabled:
            data["shop"] = self.shop.toDict(**kwargs)

        if self.statRaces:
            data["statRaces"] = [r.toDict() for r in self.statRaces]
        
        return data


    @classmethod
    def fromDict(cls, guildDict : dict, **kwargs) -> bbGuild:
        """Factory function constructing a new bbGuild object from the information in the provided guildDict - the opposite of bbGuild.toDict

        :param int id: The discord ID of the guild
        :param dict guildDict: A dictionary containing all information required to build the bbGuild object
        :param bool dbReload: Whether or not this guild is being created during the initial database loading phase of bountybot. This is used to toggle name checking in bbBounty contruction.
        :return: A bbGuild according to the information in guildDict
        :rtype: bbGuild
        """
        dbReload = kwargs["dbReload"] if "dbReload" in kwargs else False
        if "id" not in kwargs:
            raise NameError("Required kwarg missing: id")
        id = kwargs["id"]

        dcGuild = bbGlobals.client.get_guild(id)
        if not isinstance(dcGuild, Guild):
            raise NoneDCGuildObj("Could not get guild object for id " + str(id))

        announceChannel = None
        playChannel = None

        if "announceChannel" in guildDict and guildDict["announceChannel"] != -1:
            announceChannel = dcGuild.get_channel(guildDict["announceChannel"])
        if "playChannel" in guildDict and guildDict["playChannel"] != -1:
            playChannel = dcGuild.get_channel(guildDict["playChannel"])


        bountiesDisabled = id in [965011734173712426, 723708988830515231, 723708655031156742, 723706906517962814, 723705817764986900, 723704665560055848, 723704087962583131, 723703454635393056, 723702782640783361, 723704350131748935] or guildDict.get("bountiesDisabled", False)
        if bountiesDisabled:
            bountiesDB = None
        else:
            if "bountiesDB" in guildDict:
                bountiesDB = bbBountyDB.bbBountyDB.fromDict(guildDict["bountiesDB"], dbReload=dbReload)
            else:
                bountiesDB = bbBountyDB.bbBountyDB(bbData.bountyFactions)
        
        statRaces = [StatRace.fromDict(s) for s in guildDict.get("statRaces", [])]

        return bbGuild(id, bountiesDB, dcGuild, announceChannel=announceChannel, playChannel=playChannel,
                        shop=bbShop.bbShop.fromDict(guildDict["shop"]) if "shop" in guildDict else bbShop.bbShop(),
                        bountyBoardChannel=BountyBoardChannel.BountyBoardChannel.fromDict(guildDict["bountyBoardChannel"]) if "bountyBoardChannel" in guildDict and guildDict["bountyBoardChannel"] != -1 else None,
                        alertRoles=guildDict["alertRoles"] if "alertRoles" in guildDict else {}, ownedRoleMenus=guildDict["ownedRoleMenus"] if "ownedRoleMenus" in guildDict else 0,
                        bountiesDisabled=bountiesDisabled,
                        shopDisabled=id in [965011734173712426, 723708988830515231, 723708655031156742, 723706906517962814, 723705817764986900, 723704665560055848, 723704087962583131, 723703454635393056, 723702782640783361, 723704350131748935],
                        statRaces=statRaces)
