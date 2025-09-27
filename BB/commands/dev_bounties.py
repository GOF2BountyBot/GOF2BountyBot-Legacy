import discord
from datetime import datetime, timezone, timedelta

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig, bbData
from ..bbObjects.bounties import bbBounty, bbBountyConfig
from ..bbObjects.bounties.bountyRoutes.bountyRouteConfig import ExplicitRouteConfig
from ..bbObjects.bounties.bountyRoutes.bountyAnswerConfig import ExplicitBountyAnswerConfig


bbCommands.addHelpSection(2, "bounties")

async def dev_cmd_clear_bounties(message : discord.Message, args : str, isDM : bool):
    """developer command clearing all active bounties. If a guild ID is given, clear bounties in that guild.
    If 'all' is given, clear bounties in all guilds. If nothing is given, clear bounties in the calling guild.

    :param discord.Message message: the discord message calling the command
    :param str args: empty or a guild id
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "all":
        for guild in bbGlobals.guildsDB.getGuilds():
            if not guild.bountiesDisabled:
                if guild.hasBountyBoardChannel:
                    await guild.bountyBoardChannel.clear()
                guild.bountiesDB.clearBounties()
        await message.channel.send(":ballot_box_with_check: All active bounties cleared.")
        return
    elif args == "":
        if isDM:
            await message.channel.send("Give either an id or 'all', or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(args):
        if not bbGlobals.guildsDB.guildIdExists(int(args)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(args))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + args)
        return
    
    if callingBBGuild.hasBountyBoardChannel:
        await callingBBGuild.bountyBoardChannel.clear()
    callingBBGuild.bountiesDB.clearBounties()
    await message.channel.send(":ballot_box_with_check: Active bounties cleared" + ((" for '" + callingBBGuild.dcGuild.name + "'.") if callingBBGuild.dcGuild is not None else "."))

bbCommands.register("clear-bounties", dev_cmd_clear_bounties, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_get_cooldown(message : discord.Message, args : str, isDM : bool):
    """developer command printing the calling user's checking cooldown

    :param discord.Message message: the discord message calling the command
    :param str args: ignore
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    diff = datetime.fromtimestamp(bbGlobals.usersDB.getUser(
        message.author.id).bountyCooldownEnd, timezone.utc) - datetime.now(timezone.utc)
    minutes = int(diff.total_seconds() / 60)
    seconds = int(diff.total_seconds() % 60)
    await message.channel.send(str(bbGlobals.usersDB.getUser(message.author.id).bountyCooldownEnd) + " = " + str(minutes) + "m, " + str(seconds) + "s.")
    await message.channel.send(datetime.fromtimestamp(bbGlobals.usersDB.getUser(message.author.id).bountyCooldownEnd, timezone.utc).strftime("%Hh%Mm%Ss"))
    await message.channel.send(datetime.now(timezone.utc).strftime("%Hh%Mm%Ss"))

bbCommands.register("get-cool", dev_cmd_get_cooldown, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_reset_cooldown(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the checking cooldown of the calling user, or the specified user if one is given

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).bountyCooldownEnd = datetime.now(timezone.utc).timestamp()
    # otherwise get the specified user's discord object and reset their cooldown.
    # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))
                        ).bountyCooldownEnd = datetime.now(timezone.utc).timestamp()
    await message.channel.send("Done!")

bbCommands.register("reset-cool", dev_cmd_reset_cooldown, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_reset_daily_wins(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the max daily bounty wins of the calling user, or the specified user if one is given

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        # [!] no validation is done.
        requestedBBUser = bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">")))
    requestedBBUser.dailyBountyWinsReset = datetime.now(timezone.utc)
    requestedBBUser.bountyWinsToday = 0
    # otherwise get the specified user's discord object and reset their cooldown.

    await message.channel.send("Done!")

bbCommands.register("reset-daily-wins", dev_cmd_reset_daily_wins, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_setcheckcooldown(message : discord.Message, args : str, isDM : bool):
    """developer command setting the checking cooldown applied to users
    this does not update bbConfig and will be reverted on bot restart

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an integer number of minutes
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a time was requested
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    # verify the requested time is an integer
    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the checking cooldown amount
    bbConfig.checkCooldown["minutes"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)

bbCommands.register("setcheckcooldown", dev_cmd_setcheckcooldown, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_setbountyperiodm(message : discord.Message, args : str, isDM : bool):
    """developer command setting the number of minutes in the new bounty generation period
    this does not update bbConfig and will be reverted on bot restart
    this does not affect the numebr of hours in the new bounty generation period

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an integer number of minutes
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a time was given
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    # verify the given time is an integer
    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the new bounty generation cooldown
    bbConfig.newBountyFixedDelta["minutes"] = int(args)
    bbGlobals.newBountyFixedDeltaChanged = True
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)

bbCommands.register("setbountyperiodm", dev_cmd_setbountyperiodm, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_setbountyperiodh(message : discord.Message, args : str, isDM : bool):
    """developer command setting the number of hours in the new bounty generation period
    this does not update bbConfig and will be reverted on bot restart
    this does not affect the numebr of minutes in the new bounty generation period

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an integer number of hours
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a time was specified
    if args == "":
        await message.channel.send(":x: please give the number of hours!")
        return
    # verify the given time is an integer
    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the bounty generation period
    bbGlobals.newBountyFixedDeltaChanged = True
    bbConfig.newBountyFixedDelta["hours"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)

bbCommands.register("setbountyperiodh", dev_cmd_setbountyperiodh, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_resetnewbountycool(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the current bounty generation period,
    instantly generating a new bounty

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guildStr = args

    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    await callingBBGuild.newBountyTT.forceExpire()
    await message.channel.send(":ballot_box_with_check: New bounty cooldown reset for '" + callingBBGuild.dcGuild.name + "'")

bbCommands.register("resetnewbountycool", dev_cmd_resetnewbountycool, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_getnewbountycool(message : discord.Message, args : str, isDM : bool):
    """developer command getting the current bounty generation period

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guildStr = args

    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    await message.channel.send("Next bounty: '" + callingBBGuild.newBountyTT.nextExpiry.strftime("%d/%m/%Y, %H:%M:%S") + "'")

bbCommands.register("getnewbountycool", dev_cmd_getnewbountycool, 2, allowDM=True, helpSection="bounties", useDoc=True)


async def dev_cmd_canmakebounty(message : discord.Message, args : str, isDM : bool):
    """developer command printing whether or not the given faction can accept new bounties
    If no guild ID is given, bounty spawning ability is checked for the calling guild

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a faction followed by optionally a guild ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    newFaction = args.split(" ")[0].lower()
    guildStr = args.split(" ")[1] if len(args.split(" ")) > 1 else ""

    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    # ensure the given faction exists
    if not callingBBGuild.bountiesDB.factionExists(newFaction):
        await message.channel.send("not a faction: '" + newFaction + "'")
    else:
        await message.channel.send(callingBBGuild.bountiesDB.factionCanMakeBounty(newFaction.lower()))

bbCommands.register("canmakebounty", dev_cmd_canmakebounty, 2, allowDM=False, helpSection="bounties", useDoc=True)


async def dev_cmd_make_bounty(message : discord.Message, args : str, isDM : bool):
    """developer command making a new bounty
    args should be separated by a space and then a plus symbol
    if no args are given, generate a new bounty at complete random
    if only one argument is given it is assumed to be a faction, and a bounty is generated for that faction
    otherwise, all 10 arguments required to generate a bounty must be given
    the route should be separated by only commas and no spaces. the endTime should be a UTC timestamp. Any argument can be given as 'auto' to be either inferred or randomly generated
    as such, '!bb make-bounty' is an alias for '!bb make-bounty +true +auto +auto +auto +auto +auto +auto +auto +auto +auto'

    :param discord.Message message: the discord message calling the command
    :param str args: can be empty, can be '[guild id] +<notify> +<faction>', or can be '[guild id] +<notify> +<faction> +<name> +<route> +<start> +<end> +<answer> +<reward> +<endtime> +<icon> +<doDailyWinsLimit>'
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guildStr = args.split("+")[0].strip()
    args = args[len(guildStr):].lstrip()
    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    # if no args were given, generate a completely random bounty
    if args == "":
        doNotify = True
        newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB)
    # if only two arguments were given, use it as notify flag and faction
    elif len(args.split("+")) == 3:
        rawDoNotify = args.split("+")[1].strip().lower()
        if rawDoNotify in ("true", "1", "auto"):
            doNotify = True
        elif rawDoNotify in ("false", "0"):
            doNotify = False
        else:
            await message.channel.send("Unknown value for first + arg (notify flag). Must be boolean")
            return
        
        newFaction = args.split("+")[2]
        if newFaction.lower() == "auto":
            newFaction = ""
        newBounty = bbBounty.Bounty(
            bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction))

    # if all args were given, generate a completely custom bounty
    # 10 args plus account for empty string at the start of the split = split of 12 elements
    elif len(args.split("+")) == 12:
        # track whether a builtIn criminal was requested
        builtIn = False
        builtInCrimObj = None
        # [1:] remove empty string before + splits
        bData = args.split("+")[1:]

        # parse the given notify flag
        rawDoNotify = bData[0].strip().lower()
        if rawDoNotify in ("true", "1", "auto"):
            doNotify = True
        elif rawDoNotify in ("false", "0"):
            doNotify = False
        else:
            await message.channel.send("Unknown value for first + arg (notify flag). Must be boolean")
            return

        # parse the given faction
        newFaction = bData[1].rstrip(" ")
        if newFaction == "auto":
            newFaction = ""

        # parse the given criminal name
        newName = bData[2].rstrip(" ").title()
        if newName == "Auto":
            newName = ""
        else:
            # if a criminal name was given, see if it corresponds to a builtIn criminal
            for crim in bbData.builtInCriminalObjs.values():
                if crim.isCalled(newName):
                    builtIn = True
                    builtInCrimObj = crim
                    newName = crim.name
                    break

            # if a criminal name was given, ensure it does not already exist as a bounty
            if newName != "" and callingBBGuild.bountiesDB.bountyNameExists(newName):
                await message.channel.send(":x: That pilot is already wanted!")
                return

        # parse the given route
        rawRoute = bData[3].rstrip(" ")
        if rawRoute in ("auto", ""):
            newRoute = None
        else:
            systemNames = bData[3].split(",")
            systemNames[-1] = systemNames[-1].rstrip(" ")
            newRoute = ExplicitRouteConfig(None, systemNames)

        # parse the given start system
        newStart = bData[4].rstrip(" ")
        if newStart == "auto":
            newStart = ""

        # parse the given end system
        newEnd = bData[5].rstrip(" ")
        if newEnd == "auto":
            newEnd = ""

        # parse the given answer system
        newAnswer = bData[6].rstrip(" ")
        if newAnswer in ("auto", ""):
            newAnswer = ""
        elif newRoute is not None:
            newRoute.answerConfig = ExplicitBountyAnswerConfig(newAnswer)

        # parse the given reward amount
        newReward = bData[7].rstrip(" ")
        if newReward == "auto":
            newReward = -1
        newReward = int(newReward)

        # parse the given end time
        newEndTime = bData[8].rstrip(" ")
        if newEndTime == "auto":
            newEndTime = -1.0
        newEndTime = float(newEndTime)

        # parse the given icon
        newIcon = bData[9].rstrip(" ")
        if newIcon == "auto":
            newIcon = "" if not builtIn else builtInCrimObj.icon

        # parse doDailyWinsLimit
        newDoDailyWinsLimit = bData[10].rstrip(" ")
        if newDoDailyWinsLimit.lower() in ("auto", "yes", "true", "1"):
            newDoDailyWinsLimit = True
        elif newDoDailyWinsLimit.lower() in ("no", "false", "0"):
            newDoDailyWinsLimit = False
        else:
            await message.channel.send(f"Unknown value for doDailyWinsLimit: {newDoDailyWinsLimit}")
            return

        # special bounty generation for builtIn criminals
        if builtIn:
            newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, criminalObj=builtInCrimObj, config=bbBountyConfig.BountyConfig(
                faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon),
                doDailyWinsLimit=newDoDailyWinsLimit)
        # normal bounty generation for custom criminals
        else:
            newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute,
                                                                                                start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon),
                                        doDailyWinsLimit=newDoDailyWinsLimit)

    # Report an error for invalid command syntax
    else:
        await message.channel.send("incorrect syntax. give +notify +faction +name +route +start +end +answer +reward +endtime +icon +doDailyWinsLimit")
        return

    newBounty.issueTime = (datetime.now(timezone.utc) + timedelta(seconds=bbConfig.newBountyWarningTimeSeconds)).timestamp()

    # activate and announce the new bounty
    callingBBGuild.bountiesDB.addBounty(newBounty)
    await callingBBGuild.announceNewBounty(newBounty, doNotify)

bbCommands.register("make-bounty", dev_cmd_make_bounty, 2, forceKeepArgsCasing=True, allowDM=True, helpSection="bounties", longHelp=
"""
args should be separated by a space and then a plus symbol
if no args are given, generate a new bounty at complete random
if only one argument is given it is assumed to be a faction, and a bounty is generated for that faction
otherwise, all 10 arguments required to generate a bounty must be given
the route should be separated by only commas and no spaces. the endTime should be a UTC timestamp. Any argument can be given as 'auto' to be either inferred or randomly generated
as such, '!bb make-bounty' is an alias for '!bb make-bounty +true +auto +auto +auto +auto +auto +auto +auto +auto +auto'
""")


async def dev_cmd_make_player_bounty(message : discord.Message, args : str, isDM : bool):
    """developer command making a new PLAYER bounty
    args should be separated by a space and then a plus symbol
    the first argument should be a user MENTION
    if one arg is given, generate a new bounty at complete random, for the specified user
    if two arguments are given the second is assumed to be a faction, and a bounty is generated for that faction for the specified user
    otherwise, all 9 arguments required to generate a bounty must be given
    the route should be separated by only commas and no spaces. the endTime should be a UTC timestamp. Any argument can be given as 'auto' to be either inferred or randomly generated
    as such, '!bb make-player-bounty <user>' is an alias for '!bb make-bounty +auto +<user> +auto +auto +auto +auto +auto +auto +auto'

    :param discord.Message message: the discord message calling the command
    :param str args: can be empty, can be '[guild id] +<user_mention> +<faction>', or can be '[guild id] +<faction> +<user_mention> +<route> +<start> +<end> +<answer> +<reward> +<endtime> +<icon>'
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guildStr = args.split("+")[0].strip()
    args = args[len(guildStr):].lstrip()
    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    # if only one argument is given
    if len(args.split(" ")) == 1:
        # verify the requested user
        requestedID = int(args.lstrip("<@!").rstrip(">"))
        if not lib.stringTyping.isInt(requestedID) or (bbGlobals.client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # create a new bounty at random for the specified user
        newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(
            name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(bbGlobals.client.get_user(requestedID).avatar_url_as(size=64)), aliases=[lib.discordUtil.userTagOrDiscrim(args)]))

    # if the faction is also given
    elif len(args.split("+")) == 2:
        # verify the user
        requestedID = int(args.split(" ")[0].lstrip("<@!").rstrip(">"))
        if not lib.stringTyping.isInt(requestedID) or (bbGlobals.client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # create a bounty at random for the specified user and faction
        newFaction = args.split("+")[1]
        newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(
            bbGlobals.client.get_user(requestedID).avatar_url_as(size=64)), faction=newFaction, aliases=[lib.discordUtil.userTagOrDiscrim(args.split(" ")[0])]))

    # if all arguments are given
    elif len(args.split("+")) == 10:
        # [1:] remove starting empty string before + split
        bData = args.split("+")[1:]

        # parse the requested faction
        newFaction = bData[0].rstrip(" ")
        if newFaction == "auto":
            newFaction = ""

        # parse the requested user ID
        # no auto option!
        newName = bData[1].rstrip(" ").title()
        # verify the requested user
        requestedID = int(newName.lstrip("<@!").rstrip(">"))
        if not lib.stringTyping.isInt(requestedID) or (bbGlobals.client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # ensure no bounty already exists for this user
        if callingBBGuild.bountiesDB.bountyNameExists(newName):
            await message.channel.send(":x: That pilot is already wanted!")
            return

        # parse the requested route
        rawRoute = bData[2].rstrip(" ")
        if rawRoute in ("auto", ""):
            newRoute = None
        else:
            systemNames = bData[2].split(",")
            systemNames[-1] = systemNames[-1].rstrip(" ")
            newRoute = ExplicitRouteConfig(None, systemNames)

        # parse the requested start system
        newStart = bData[3].rstrip(" ")
        if newStart == "auto":
            newStart = ""

        # parse the requested end system
        newEnd = bData[4].rstrip(" ")
        if newEnd == "auto":
            newEnd = ""

        # parse the requested answer system
        newAnswer = bData[5].rstrip(" ")
        if newAnswer in ("auto", ""):
            newAnswer = ""
        elif newRoute is not None:
            newRoute.answerConfig = ExplicitBountyAnswerConfig(newAnswer)

        # parse the requested reward pool
        newReward = bData[6].rstrip(" ")
        if newReward == "auto":
            newReward = -1
        newReward = int(newReward)

        # parse the requested end time
        newEndTime = bData[7].rstrip(" ")
        if newEndTime == "auto":
            newEndTime = -1.0
        newEndTime = float(newEndTime)

        # parse the requested icon URL
        newIcon = bData[8].rstrip(" ")
        if newIcon == "auto":
            newIcon = str(bbGlobals.client.get_user(
                int(newName.lstrip("<@!").rstrip(">"))).avatar_url_as(size=64))

        # create the bounty object
        newBounty = bbBounty.Bounty(
            bountyDB=callingBBGuild.bountiesDB,
            config=bbBountyConfig.BountyConfig(
                faction=newFaction, 
                name=newName, 
                route=newRoute,
                start=newStart,
                end=newEnd, 
                answer=newAnswer, 
                reward=newReward, 
                endTime=newEndTime, 
                isPlayer=True, 
                icon=newIcon, 
                aliases=[lib.discordUtil.userTagOrDiscrim(newName)]))

    # print an error for incorrect syntax
    else:
        await message.channel.send("incorrect syntax. give +faction +userTag +route +start +end +answer +reward +endtime +icon")
        return

    # activate and announce the bounty
    callingBBGuild.bountiesDB.addBounty(newBounty)
    await callingBBGuild.announceNewBounty(newBounty)

bbCommands.register("make-player-bounty", dev_cmd_make_player_bounty, 2, forceKeepArgsCasing=True, allowDM=True, helpSection="bounties", useDoc=True)