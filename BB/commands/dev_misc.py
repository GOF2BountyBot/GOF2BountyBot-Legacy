import discord
import traceback
from datetime import datetime, timezone, timedelta, time
import re
import json
from typing import Dict, List

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..reactionMenus.ConfirmationReactionMenu import InlineConfirmationMenu
from ..bbConfig import bbConfig
from ..bbObjects.items import bbItem
from ..bbObjects.statRace import StatRace, StatRaceReward
from ..bbObjects import bbGuild

from . import util_help

# used in nested f-strings
NL = "\n"

bbCommands.addHelpSection(2, "stat races")

async def dev_cmd_dev_help(message : discord.Message, args : str, isDM : bool):
    """dev command printing help strings for dev commands as defined in bbData

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await util_help.util_autohelp(message, args, isDM, 2)

bbCommands.register("dev-help", dev_cmd_dev_help, 2, signatureStr="**dev-help** *[page number, section or command]*", shortHelp="Display information about developer-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info.", longHelp="Display information about developer-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info about a set of commands. These are the currently valid section names:\n- Bounties\n- Miscellaneous\n- Items\n- Channels\n- Skins")


async def trySave(message : discord.Message) -> bool:
    """Try to save dbs, and send an error to the caller's DMs if it fails.
    Returns `True` on success, `False` on failure."""
    try:
        bbGlobals.client.bb_saveAllDBs()
        print(datetime.now(timezone.utc).strftime("%H:%M:%S: Data saved manually!"))
        return True
    except Exception as e:
        print("SAVING ERROR", e.__class__.__name__)
        print(traceback.format_exc())
        if message.author.dm_channel is None:
            await message.author.create_dm()
        if message.author.dm_channel is None:
            sendChannel = message.channel
        else:
            sendChannel = message.author.dm_channel

        try:
            await sendChannel.send(f"failed to save with {type(e).__name__}: {e}\n{traceback.format_exc()}")
        except discord.Forbidden:
            await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
    return False


async def getShutdownWarnings(message : discord.Message) -> str:
    warnings = []

    saved = await trySave(message)
    if not saved:
        warnings.append(f"failed to save (last successful save <t:{int(bbGlobals.lastSuccessfulSave.timestamp())}:f>)")

    if len(bbGlobals.currentRenders) > 0:
        warnings.append("a render is currently in progress")
    
    return "" if len(warnings) == 0 else warnings[0] if len(warnings) == 1 else (" - " + "\n - ".join(warnings))


async def dev_cmd_sleep(message : discord.Message, args : str, isDM : bool):
    """developer command saving all data to JSON and then shutting down the bot

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    warn = await getShutdownWarnings(message)
    if warn and "-f" not in args:
        await message.channel.send(f":x: {f'{NL}{warn}' if NL in warn else warn}. Give `-f` to force.")	
    else:
        bbGlobals.shutdown = bbGlobals.ShutDownState.shutdown
        await message.channel.send((f"{warn}. `-f` given, shutting down anyway.\n" if warn else "") + "zzzz....")
        await bbGlobals.client.bb_shutdown()

bbCommands.register("bot-sleep", dev_cmd_sleep, 2, allowDM=True, useDoc=True)


async def dev_cmd_save(message : discord.Message, args : str, isDM : bool):
    """developer command saving all databases to JSON

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if await trySave(message):
        await message.channel.send("saved!")

bbCommands.register("save", dev_cmd_save, 2, allowDM=True, useDoc=True)


async def dev_cmd_restart(message: discord.Message, args: str, isDM: bool):
    """developer command saving all data to JSON and then restarting the bot

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    warn = await getShutdownWarnings(message)
    if warn and "-f" not in args:
        await message.channel.send(f":x: {f'{NL}{warn}' if NL in warn else warn}. Give `-f` to force.")	
    else:
        bbGlobals.shutdown = bbGlobals.ShutDownState.restart
        await message.channel.send((f"{warn}. `-f` given, restarting anyway.\n" if warn else "") + "zzzz....")
        await bbGlobals.client.bb_shutdown()

bbCommands.register("bot-restart", dev_cmd_restart, 2, allowDM=True, useDoc=True)


async def dev_cmd_bot_update(message : discord.Message, args : str, isDM : bool):
    """developer command that gracefully shuts down the bot, performs git pull, and then reboots the bot.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    warn = await getShutdownWarnings(message)
    if warn and "-f" not in args:
        await message.channel.send(f":x: {f'{NL}{warn}' if NL in warn else warn}. Give `-f` to force.")	
    else:
        bbGlobals.shutdown = bbGlobals.ShutDownState.update
        await message.channel.send((f"{warn}. `-f` given, updating and restarting anyway.\n" if warn else "") + "zzzz....")
        await bbGlobals.client.bb_shutdown()

bbCommands.register("bot-update", dev_cmd_bot_update, 2, allowDM=True, useDoc=True)


async def dev_cmd_reset_has_poll(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the poll ownership of the calling user, or the specified user if one is given.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).pollOwned = False
        # otherwise get the specified user's discord object and reset their cooldown.
        # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))).pollOwned = False
    await message.channel.send("Done!")

bbCommands.register("reset-has-poll", dev_cmd_reset_has_poll, 2, allowDM=True, useDoc=True)


async def dev_cmd_broadcast(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the playChannel of all guilds that have one

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]

                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        if useAnnounceChannel:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasAnnounceChannel():
                    await guild.getAnnounceChannel().send(msgText, embed=broadcastEmbed)
        else:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasPlayChannel():
                    await guild.getPlayChannel().send(msgText, embed=broadcastEmbed)

bbCommands.register("broadcast", dev_cmd_broadcast, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_say(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the same channel as the command is called in

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex].replace("{NL}", "\n")
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]
                
                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        await message.channel.send(msgText, embed=broadcastEmbed)

bbCommands.register("say", dev_cmd_say, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_setbalance(message : discord.Message, args : str, isDM : bool):
    """developer command setting the requested user's balance.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a user mention and an integer number of credits
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    # verify both a user and a balance were given
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a user mention followed by the new balance!")
        return
    # verify the requested balance is an integer
    if not lib.stringTyping.isInt(argsSplit[1]):
        await message.channel.send(":x: that's not a number!")
        return
    # verify the requested user
    requestedUser = bbGlobals.client.get_user(
        int(argsSplit[0].lstrip("<@!").rstrip(">")))
    if requestedUser is None:
        await message.channel.send(":x: invalid user!!")
        return
    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        requestedBBUser = bbGlobals.usersDB.addUser(requestedUser.id)
    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
    # update the balance
    requestedBBUser.credits = int(argsSplit[1])
    await message.channel.send("Done!")

bbCommands.register("setbalance", dev_cmd_setbalance, 2, allowDM=True, useDoc=True)


async def dev_cmd_reset_transfer_cool(message : discord.Message, args : str, isDM : bool):
    """developer command resetting a user's home guild transfer cooldown.

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string or string containing a user mention or ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).guildTransferCooldownEnd = datetime.now(timezone.utc)
    # otherwise get the specified user's discord object and reset their cooldown.
    # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))
                        ).guildTransferCooldownEnd = datetime.now(timezone.utc)
    await message.channel.send("Done!")
    

bbCommands.register("reset-transfer-cool", dev_cmd_reset_transfer_cool, 2, allowDM=True, useDoc=True)


async def dev_cmd_startStatRace(message : discord.Message, args : str, isDM : bool):
    """developer command starting a new stat race

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split("\n")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Provide kwargs all on the first line, and after a new line, the rewards json")
        return

    args = argsSplit[0]
    jsonString = "\n".join(argsSplit[1:])

    guildIdMatch = re.match(".*guildid=(\\d+)", args, re.IGNORECASE)
    if not guildIdMatch:
        await message.channel.send(":x: Failed to parse guildid kwarg")
        return
    
    guildId = int(guildIdMatch.group(1))
    
    statNameMatch = re.match(".*statname=((?:\\d|[a-z]|-|_)+)", args, re.IGNORECASE)
    if not statNameMatch:
        await message.channel.send(":x: Failed to parse statname kwarg")
        return
    
    statName = statNameMatch.group(1)

    startInDaysMatch = re.match(".*startInDays=(\\d+)", args, re.IGNORECASE)
    startInDays = int(startInDaysMatch.group(1)) if startInDaysMatch else 1

    if startInDays < 1:
        await message.channel.send(":x: startInDays must be at least 1")
        return

    deltaModeMatch = re.match(".*delta=(false)|(true)", args, re.IGNORECASE)
    deltaMode = (not deltaModeMatch) or deltaModeMatch.group(1).lower() == "true"

    orderAscMatch = re.match(".*orderAsc=(false)|(true)", args, re.IGNORECASE)
    orderAsc = True if orderAscMatch and orderAscMatch.group(1).lower() == "true" else False
    
    timeoutDict: Dict[str, int] = {}

    for timeName in ["months", "weeks", "days", "hours", "minutes"]:
        timeNameMatch = re.match(f".*{timeName}=(\\d+)", args, re.IGNORECASE)
        
        if timeNameMatch:
            timeoutDict[timeName] = int(timeNameMatch.group(1))

    if not timeoutDict:
        await message.channel.send(":x: Failed to parse race length")
        return

    if all(v == 0 for v in timeoutDict.values()):
        await message.channel.send(":x: Race length cannot be zero")
        return
    
    months = timeoutDict.get("months", 0)
    weeks = timeoutDict.get("weeks", 0)
    days = timeoutDict.get("days", 0)
    hours = timeoutDict.get("hours", 0)
    minutes = timeoutDict.get("minutes", 0)

    today = datetime.combine(datetime.now(timezone.utc).date(), time())
    raceEnd = today + timedelta(days=days, hours=hours, minutes=minutes, weeks=weeks)
    if raceEnd.month + months > 12:
        raceEnd.replace(year=raceEnd.year + 1)
    
    newMonth = (raceEnd.month + months) % 12
    raceEnd.replace(month=newMonth or 1)

    raceStart = today + timedelta(days=startInDays)

    confirmMsg = await message.channel.send(f"Confirm the race timing: <t:{int(raceStart.timestamp())}:F> - <t:{int(raceEnd.timestamp())}:F>")
    confirmation = await InlineConfirmationMenu(confirmMsg, message.author, bbConfig.toolUseConfirmTimeoutSeconds).doMenu()

    if bbConfig.defaultRejectEmoji in confirmation:
        await message.channel.send("🛑 Stat race creation cancelled.")
        return
    
    if bbConfig.defaultAcceptEmoji not in confirmation:
        raise ValueError(",".join(str(i) for i in confirmation))
    
    try:
        itemDict = json.loads(jsonString)
    except json.JSONDecodeError as ex:
        await message.channel.send(f":x: Rewards is not valid json: {ex}")
        return
    
    if not isinstance(itemDict, dict):
        await message.channel.send(":x: Rewards json is not a dictionary")
        return
    
    rewards: List[StatRaceReward] = []
    for k, v in itemDict.items():
        if not lib.stringTyping.isInt(k):
            await message.channel.send(f":x: Reward number {k} is not an integer")
            return
        
        placeNumber = int(k)
        if placeNumber < 1:
            await message.channel.send(f":x: Reward number {k} is less than 1")
            return
        
        if placeNumber > 10:
            await message.channel.send(f":x: Reward number {k} is greater than than 10")
            return
        
        if not isinstance(v, dict):
            await message.channel.send(f":x: Reward value {k} is not a dictionary")
            return

        if "type" not in v:
            await message.channel.send(":x: Please give a type in your item dictionary.")
            return

        if v["type"] not in bbItem.subClassNames:
            await message.channel.send(":x: Unknown bbItem subclass type: " + v["type"])
            return
        
        try:
            bbItem.spawnItem(v)
        except Exception as ex:
            await message.channel.send(f":x: Failed to spawn reward value {k}: {ex}")
            return
        
        rewards.append(StatRaceReward(v, placeNumber))

    if not bbGlobals.guildsDB.guildIdExists(guildId):
        await message.channel.send(":x: Unrecognised guild")
        return
    
    r = StatRace(rewards, raceStart, raceEnd, deltaMode, orderAsc, statName)
    hostGuild: bbGuild.bbGuild = bbGlobals.guildsDB.getGuild(guildId)
    hostGuild.statRaces.append(r)

    doAnnounce = raceStart < datetime.now(timezone.utc)
    if doAnnounce:
        announcingStr = " Now announcing..."
    else:
        announcingStr = ""
    await message.channel.send(f"{bbConfig.defaultSubmitEmoji.sendable} stat race created.{announcingStr}")

    if doAnnounce:
        await bbGlobals.client.announceOneNewStatRace(hostGuild, r)
    

bbCommands.register("make-stat-race", dev_cmd_startStatRace, 2, allowDM=True, helpSection="stat races", forceKeepArgsCasing=True,
                    longHelp="Make a leaderboard over the given period for the given stat, and award the given prizes" \
                        + " to the top scorers. Give the kwargs all on the first line, and then after a new line, the rewards as json."
                        + "kwargs:\n"
                        + "- `guildId` (int)\n"
                        + "- `statname` (str, currently credits, lifetimeCredits, systemsChecked, bountyWins, value)\n"
                        + "- `delta` (bool, default false)\n"
                        + "- `orderAsc` (bool, default false)\n"
                        + "- `startInDays` (int, default 1)\n"
                        + "- `months` (int)\n"
                        + "- `weeks` (int)\n"
                        + "- `days` (int)\n"
                        + "- `hours` (int)\n"
                        + "- `minutes` (int)")


async def dev_cmd_getGuildStatRaces(message : discord.Message, args : str, isDM : bool):
    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: Give the guild id as the only argument")
        return
    
    guildId = int(args)
    if not bbGlobals.guildsDB.guildIdExists(guildId):
        await message.channel.send(":x: Unrecognised guild")
        return
    
    g: bbGuild.bbGuild = bbGlobals.guildsDB.getGuild(guildId)
    racesEmbed = lib.discordUtil.makeEmbed(titleTxt=f"{args} Stat Races")
    for i, r in enumerate(g.statRaces):
        racesEmbed.add_field(
            name=f"{i}", 
            value=f"{r.startDate.timestamp()} - {r.endDate.timestamp()} {r.statName} {'delta' if r.deltaMode else 'non-delta'} {'asc' if r.orderAsc else 'desc'}\n"
                + f"rewards for places: {', '.join(str(place.fixedPlace) + ' ' for place in r.rewards)}")
    
    await message.channel.send(racesEmbed=racesEmbed)

bbCommands.register("get-stat-races", dev_cmd_getGuildStatRaces, 2, allowDM=True, helpSection="stat races")


async def dev_cmd_cancelGuildStatRace(message : discord.Message, args : str, isDM : bool):
    argsSplit = args.split(" ")
    if len(argsSplit) != 2 or not any(lib.stringTyping.isInt(i) for i in argsSplit):
        await message.channel.send(":x: Give the guild id followed by the stat race id from `$get-stat-races`")
        return
    
    guildId = int(args[0])
    raceId = int(args[1])

    if not bbGlobals.guildsDB.guildIdExists(guildId):
        await message.channel.send(":x: Unrecognised guild")
        return
    
    g: bbGuild.bbGuild = bbGlobals.guildsDB.getGuild(guildId)

    if not g.statRaces or raceId < 0 or raceId > len(g.statRaces) - 1:
        await message.channel.send(":x: Invalid stat race id. Give the id shown in `$get-stat-races`")
        return

    r = g.statRaces.pop(raceId)
    
    await message.channel.send(f"{bbConfig.defaultSubmitEmoji.sendable} This race has been cancelled. No announcement has been made:\n"
                               + f"{r.startDate.timestamp()} - {r.endDate.timestamp()} {r.statName} {'delta' if r.deltaMode else 'non-delta'} {'asc' if r.orderAsc else 'desc'}")

bbCommands.register("cancel-stat-race", dev_cmd_cancelGuildStatRace, 2, allowDM=True, helpSection="stat races")