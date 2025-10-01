import discord
from datetime import datetime, timedelta, timezone

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig, bbData
from ..bbObjects.battles import DuelRequest
from ..scheduling import TimedTask
from ..reactionMenus import ReactionMenu, ReactionDuelChallengeMenu


bbCommands.addHelpSection(0, "bounties")


async def cmd_check(message : discord.Message, args : str, isDM : bool):
    """⚠ WARNING: MARKED FOR CHANGE ⚠
    The following function is provisional and marked as planned for overhaul.
    Details: Criminal fights are to switch algorithm, using bbObjects.items.battles as a base. Criminals are to be assigned
    Procedurally generated ships based on a difficulty rating (by direct extension of the items' rarity rankings from bbConfig.__init__)

    Check a system for bounties and handle rewards

    :param discord.Message message: the discord message calling the command
    :param str args: string containing one system to check
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # Verify that this guild has bounties enabled
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if callingBBGuild.bountiesDisabled:
        await message.channel.send(":x: This server does not have bounties enabled.")
        return

    # verify this is the calling user's home guild. If no home guild is set, transfer here.
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if not requestedBBUser.hasHomeGuild():
        await requestedBBUser.transferGuild(message.guild)
        await message.channel.send(":airplane_arriving: Your home guild has been set.")
    elif requestedBBUser.homeGuildID != message.guild.id:
        await message.channel.send(":x: This command can only be used from your home guild!")
        return

    # verify a system was given
    if args == "":
        await message.channel.send(":x: Please provide a system to check! E.g: `" + bbConfig.commandPrefix + "check Pescal Inartu`")
        return

    requestedSystem = args.title()
    systObj = None

    # attempt to find the requested system in the database
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(requestedSystem):
            systObj = bbData.builtInSystemObjs[syst]

    # reject if the requested system is not in the database
    if systObj is None:
        if len(requestedSystem) < 20:
            await message.channel.send(":x: The **" + requestedSystem + "** system is not on my star map! :map:")
        else:
            await message.channel.send(":x: The **" + requestedSystem[0:15] + "**... system is not on my star map! :map:")
        return

    requestedSystem = systObj.name

    if not requestedBBUser.activeShip.hasWeaponsEquipped() and not requestedBBUser.activeShip.hasTurretsEquipped():
        await message.channel.send(":x: Your ship has no weapons equipped!")
        return

    now = datetime.now(timezone.utc)

    # Restrict the number of bounties a player may win in a single day
    if requestedBBUser.dailyBountyWinsReset < now:
        requestedBBUser.bountyWinsToday = 0
        requestedBBUser.dailyBountyWinsReset = now.replace(
                            hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})

    if requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
        await message.channel.send(":x: You have reached the maximum number of bounty wins allowed for today! Check back tomorrow.")
        return

    # ensure the calling user is not on checking cooldown
    if datetime.fromtimestamp(requestedBBUser.bountyCooldownEnd, timezone.utc) < now:
        bountyWon = False
        bountyWonDoDailyWinsLimit = True
        systemInBountyRoute = False
        dailyBountiesMaxReached = False

        # Loop over all bounties in the database
        for fac in callingBBGuild.bountiesDB.getFactions():
            # list of completed bounties to remove from the bounties database
            toPop = []
            for bounty in callingBBGuild.bountiesDB.getFactionBounties(fac):
                if datetime.fromtimestamp(bounty.issueTime, timezone.utc) > now:
                    continue

                # Check the passed system in current bounty
                # If current bounty resides in the requested system
                checkResult = bounty.check(requestedSystem, message.author.id)
                if checkResult == 3:
                    requestedBBUser.bountyWinsToday += 1
                    if not dailyBountiesMaxReached and requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
                        requestedBBUser.dailyBountyWinsReset = now.replace(
                            hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})
                        dailyBountiesMaxReached = True

                    bountyWon = True
                    bountyWonDoDailyWinsLimit = bountyWonDoDailyWinsLimit and bounty.doDailyWinsLimit
                    # reward all contributing users
                    rewards = bounty.calcRewards()
                    for userID in rewards:
                        u = bbGlobals.usersDB.getUser(userID)
                        u.credits += rewards[userID]["reward"]
                        u.lifetimeCredits += rewards[userID]["reward"]
                    # add this bounty to the list of bounties to be removed
                    toPop += [bounty]
                    # Announce the bounty has ben completed
                    await callingBBGuild.announceBountyWon(bounty, rewards, message.author)

                if checkResult != 0:
                    systemInBountyRoute = True
                    await callingBBGuild.updateBountyBoardChannel(bounty, bountyComplete=checkResult == 3)

            # remove all completed bounties
            for bounty in toPop:
                callingBBGuild.bountiesDB.removeBountyObj(bounty)
                bbGlobals.bountiesEventHub.onBountyDefeated(bounty)

        sightedCriminalsStr = ""
        # Check if any bounties are close to the requested system in their route, defined by bbConfig.closeBountyThreshold
        for fac in callingBBGuild.bountiesDB.getFactions():
            for bounty in callingBBGuild.bountiesDB.getFactionBounties(fac):
                if datetime.fromtimestamp(bounty.issueTime, timezone.utc) > now:
                    continue
                if requestedSystem in bounty.route:
                    if 0 < bounty.route.index(bounty.answer) - bounty.route.index(requestedSystem) < bbConfig.closeBountyThreshold:
                        # Print any close bounty names
                        sightedCriminalsStr += "**       **• Local security forces spotted **" + \
                            lib.discordUtil.criminalNameOrDiscrim(
                                bounty.criminal) + "** here recently.\n"
        sightedCriminalsStr = sightedCriminalsStr[:-1]

        # If a bounty was won, print a congratulatory message
        if bountyWon:
            if bountyWonDoDailyWinsLimit:
                requestedBBUser.bountyWins += 1
                dailyWinsStr = "You have now reached the maximum number of bounty wins allowed for today! Please check back tomorrow." if dailyBountiesMaxReached else ("You have **" + str(bbConfig.maxDailyBountyWins - requestedBBUser.bountyWinsToday) + "** remaining bounty wins today!")
            else:
                dailyWinsStr = "-# Your daily bounty wins has **not** changed."
            await message.channel.send(sightedCriminalsStr + "\n" + ":moneybag: **" + message.author.display_name + "**, you now have **" + str(requestedBBUser.credits) + " Credits!**\n" + dailyWinsStr)
                                       
        # If no bounty was won, print an error message
        else:
            noCooldownIncurStr = "" if systemInBountyRoute else f"\n-# No cooldown incurred: {requestedSystem} is not in any bounty routes."
            await message.channel.send(f":telescope: **" + message.author.display_name + "**, you did not find any criminals in **" + requestedSystem.title() + "**!\n" + sightedCriminalsStr + noCooldownIncurStr)

        # Only put the calling user on checking cooldown and increment systemsChecked stat if the system checked is on an active bounty's route.
        if systemInBountyRoute:
            requestedBBUser.systemsChecked += 1
            # Put the calling user on checking cooldown
            requestedBBUser.bountyCooldownEnd = (now +
                                                 timedelta(minutes=bbConfig.checkCooldown["minutes"])).timestamp()

    # If the calling user is on checking cooldown
    else:
        # Print an error message with the remaining time on the calling user's cooldown
        diff = datetime.fromtimestamp(bbGlobals.usersDB.getUser(
            message.author.id).bountyCooldownEnd, timezone.utc) - now
        minutes = int(diff.total_seconds() / 60)
        seconds = int(diff.total_seconds() % 60)
        await message.channel.send(":stopwatch: **" + message.author.display_name + "**, your *Khador Drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")

bbCommands.register("check", cmd_check, 0, aliases=["search"], allowDM=False, helpSection="bounties", signatureStr="**check <system>**", shortHelp="Check if any criminals are in the given system, arrest them, and get paid! 💰\n🌎 This command must be used in your **home server**.")


async def cmd_bounties(message : discord.Message, args : str, isDM : bool):
    """List a summary of all currently active bounties.
    If a faction is specified, print a more detailed summary of that faction's active bounties

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a faction
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # Verify that this guild has bounties enabled
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if callingBBGuild.bountiesDisabled:
        await message.channel.send(":x: This server does not have bounties enabled.")
        return

    # If no faction is specified
    if args == "":
        outmessage = "__**Active Bounties**__\nTimes given in UTC. See more detailed information with `" + \
            bbConfig.commandPrefix + "bounties <faction>`\n```css"
        preLen = len(outmessage)
        # Collect and print summaries of all active bounties
        for fac in callingBBGuild.bountiesDB.getFactions():
            if callingBBGuild.bountiesDB.hasBounties(faction=fac):
                outmessage += "\n • [" + fac.title() + "]: "
                for bounty in callingBBGuild.bountiesDB.getFactionBounties(fac):
                    outmessage += lib.discordUtil.criminalNameOrDiscrim(bounty.criminal) + ", "
                outmessage = outmessage[:-2]
        # If no active bounties were found, print an error
        if len(outmessage) == preLen:
            outmessage += "\n[  No currently active bounties! Please check back later.  ]"
        # Restrict the number of bounties a player may win in a single day
        requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
        if requestedBBUser.dailyBountyWinsReset < datetime.now(timezone.utc):
            requestedBBUser.bountyWinsToday = 0
            requestedBBUser.dailyBountyWinsReset = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})
        if requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
            maxBountiesMsg = "\nYou have reached the maximum number of bounty wins allowed for today! Check back tomorrow."
        else:
            maxBountiesMsg = "\nYou have **" + str(bbConfig.maxDailyBountyWins - requestedBBUser.bountyWinsToday) + "** remaining bounty wins today!"
        outmessage += "```" + maxBountiesMsg
        await message.channel.send(outmessage)

    # if a faction is specified
    else:
        requestedFaction = args.lower()
        # verify the passed faction
        if requestedFaction not in bbData.bountyFactions:
            if len(requestedFaction) < 20:
                await message.channel.send(":x: Unrecognised faction: **" + requestedFaction + "**")
            else:
                await message.channel.send(":x: Unrecognised faction **" + requestedFaction[0:15] + "**...")
            return

        # Ensure the requested faction has active bounties
        if not callingBBGuild.bountiesDB.hasBounties(faction=requestedFaction):
            await message.channel.send(":stopwatch: There are no **" + requestedFaction.title() + "** bounties active currently!\nYou have **" + str(bbConfig.maxDailyBountyWins - bbGlobals.usersDB.getOrAddID(message.author.id).bountyWinsToday) + "** remaining bounty wins today!")
        else:
            # Collect and print summaries of the requested faction's active bounties
            outmessage = "__**Active " + requestedFaction.title() + \
                " Bounties**__\nTimes given in UTC.```css"
            for bounty in callingBBGuild.bountiesDB.getFactionBounties(requestedFaction):
                endTimeStr = datetime.fromtimestamp(
                    bounty.endTime, timezone.utc).strftime("%B %d %H %M %S").split(" ")
                outmessage += "\n • [" + lib.discordUtil.criminalNameOrDiscrim(bounty.criminal) + "]" + " " * (bbData.longestBountyNameLength + 1 - len(lib.discordUtil.criminalNameOrDiscrim(bounty.criminal))) + ": " + str(
                    int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + lib.stringTyping.getNumExtension(int(endTimeStr[1])) + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                if endTimeStr[4] != "00":
                    outmessage += ":" + endTimeStr[4]
                else:
                    outmessage += "   "
                outmessage += " - " + \
                    str(len(bounty.route)) + " possible system"
                if len(bounty.route) != 1:
                    outmessage += "s"
            maxBountiesMsg = ""
            if bbGlobals.usersDB.userIDExists(message.author.id):
                requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
                # Restrict the number of bounties a player may win in a single day
                if requestedBBUser.dailyBountyWinsReset < datetime.now(timezone.utc):
                    requestedBBUser.bountyWinsToday = 0
                    requestedBBUser.dailyBountyWinsReset = datetime.now(timezone.utc).replace(
                            hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})
                if requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
                    maxBountiesMsg = "\nYou have reached the maximum number of bounty wins allowed for today! Check back tomorrow."
                else:
                    maxBountiesMsg = "\nYou have **" + str(bbConfig.maxDailyBountyWins - requestedBBUser.bountyWinsToday) + "** remaining bounty wins today!"
            await message.channel.send(outmessage + "```\nTrack down criminals and **win credits** using `" + bbConfig.commandPrefix + "route` and `" + bbConfig.commandPrefix + "check`!" + maxBountiesMsg)

bbCommands.register("bounties", cmd_bounties, 0, allowDM=False, helpSection="bounties", signatureStr="**bounties** *[faction]*", shortHelp="List all active bounties, in detail if a faction is specified.", longHelp="If no faction is given, name all currently active bounties.\nIf a faction is given, show detailed info about its active bounties.")


async def cmd_route(message : discord.Message, args : str, isDM : bool):
    """Display the current route of the requested criminal

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a criminal name or alias
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # Verify that this guild has bounties enabled
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if callingBBGuild.bountiesDisabled:
        await message.channel.send(":x: This server does not have bounties enabled.")
        return

    # verify a criminal was specified
    if args == "":
        await message.channel.send(":x: Please provide the criminal name! E.g: `" + bbConfig.commandPrefix + "route Kehnor`")
        return

    requestedBountyName = args
    # if the named criminal is wanted
    if callingBBGuild.bountiesDB.bountyNameExists(requestedBountyName.lower()):
        # display their route
        bounty = callingBBGuild.bountiesDB.getBounty(requestedBountyName.lower())
        outmessage = "**" + \
            lib.discordUtil.criminalNameOrDiscrim(bounty.criminal) + "**'s current route:\n> "
        if datetime.fromtimestamp(bounty.issueTime, timezone.utc) > datetime.now(timezone.utc):
            outmessage += f"*Releases <t:{int(bounty.issueTime)}:R>!*"
        else:
            for system in bounty.route:
                outmessage += " " + ("~~" if bounty.checked[system] != -1 else "") + system + (
                    "~~" if bounty.checked[system] != -1 else "") + ","
            outmessage = outmessage[:-1] + ". :rocket:"
        await message.channel.send(outmessage)
    # if the named criminal is not wanted
    else:
        # display an error
        outmsg = ":x: That pilot isn't on any bounty boards! :clipboard:"
        # accept user name + discrim instead of tags to avoid mention spam
        if lib.stringTyping.isMention(requestedBountyName):
            outmsg += "\n:warning: **Don't tag users**, use their name and ID number like so: `" + \
                bbConfig.commandPrefix + "route Trimatix#2244`"
        await message.channel.send(outmsg)

bbCommands.register("route", cmd_route, 0, allowDM=False, helpSection="bounties", signatureStr="**route <criminal name>**", shortHelp="Get the named criminal's current route.", longHelp="Get the named criminal's current route.\nFor a list of aliases for a given criminal, see `$COMMANDPREFIX$info criminal`.")


async def cmd_duel(message : discord.Message, args : str, isDM : bool):
    """⚠ WARNING: MARKED FOR CHANGE ⚠
    The following function is provisional and marked as planned for overhaul.
    Details: Overhaul is part-way complete, with a few fighting algorithm provided in bbObjects.items.battles. However, printing the fight details is yet to be implemented.
    This is planned to be done using simple message editing-based animation of player ships and progress bars for health etc.
    This command is functional for now, but the output is subject to change.

    Challenge another player to a duel, with an amount of credits as the stakes.
    The winning user is given stakes credits, the loser has stakes credits taken away.
    give 'challenge' to create a new duel request.
    give 'cancel' to cancel an existing duel request.
    give 'accept' to accept another user's duel request targetted at you.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the action (challenge/cancel/accept), a target user (mention or ID), and the stakes (int amount of credits). stakes are only required when "challenge" is specified.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) == 0:
        await message.channel.send(":x: Please provide an action (`challenge`/`cancel`/`accept`/`reject or decline`), a user, and the stakes (an amount of credits)!")
        return
    action = argsSplit[0]
    if action not in ["challenge", "cancel", "accept", "reject", "decline"]:
        await message.channel.send(":x: Invalid action! please choose from `challenge`, `cancel`, `reject/decline` or `accept`.")
        return
    if action == "challenge":
        if len(argsSplit) < 3:
            await message.channel.send(":x: Please provide a user and the stakes (an amount of credits)!")
            return
    else:
        if len(argsSplit) < 2:
            await message.channel.send(":x: Please provide a user!")
            return
    requestedUser = lib.discordUtil.getMemberByRefOverDB(argsSplit[1], dcGuild=message.guild)
    if requestedUser is None:
        await message.channel.send(":x: User not found!")
        return
    if requestedUser.id == message.author.id:
        await message.channel.send(":x: You can't challenge yourself!")
        return
    if action == "challenge" and (not lib.stringTyping.isInt(argsSplit[2]) or int(argsSplit[2]) < 0):
        await message.channel.send(":x: Invalid stakes (amount of credits)!")
        return

    sourceBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    targetBBUser = bbGlobals.usersDB.getOrAddID(requestedUser.id)

    if action == "challenge":
        stakes = int(argsSplit[2])
        if sourceBBUser.hasDuelChallengeFor(targetBBUser):
            await message.channel.send(":x: You already have a duel challenge pending for " + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "! To make a new one, cancel it first. (see `" + bbConfig.commandPrefix + "help duel`)")
            return

        try:
            newDuelReq = DuelRequest.DuelRequest(
                sourceBBUser, targetBBUser, stakes, None, bbGlobals.guildsDB.getGuild(message.guild.id))
            duelTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(
                bbConfig.duelReqExpiryTime), expiryFunction=DuelRequest.expireAndAnnounceDuelReq, expiryFunctionArgs={"duelReq": newDuelReq})
            newDuelReq.duelTimeoutTask = duelTT
            bbGlobals.duelRequestTTDB.scheduleTask(duelTT)
            sourceBBUser.addDuelChallenge(newDuelReq)
        except KeyError:
            await message.channel.send(":x: User not found! Did they leave the server?")
            return
        except Exception:
            await message.channel.send(":woozy_face: An unexpected error occurred! Tri, what did you do...")
            return

        duelExpiryTimeString = f"This duel request will expire <t:{int(duelTT.expiryTime.timestamp())}:f>."

        sentMsgs = []

        if message.guild.get_member(requestedUser.id) is None:
            targetUserDCGuild = lib.discordUtil.findBBUserDCGuild(targetBBUser)
            if targetUserDCGuild is None:
                await message.channel.send(":x: User not found! Did they leave the server?")
                return
            else:
                targetUserBBGuild = bbGlobals.guildsDB.getGuild(targetUserDCGuild.id)
                if targetUserBBGuild.hasPlayChannel():
                    targetUserNameOrTag = lib.discordUtil.IDAlertedUserMentionOrName(
                        "duels_challenge_incoming_new", dcGuild=targetUserDCGuild, bbGuild=targetUserBBGuild, dcUser=requestedUser, bbUser=targetBBUser)
                    sentMsgs.append(await targetUserBBGuild.getPlayChannel().send(":crossed_swords: **" + str(message.author) + "** challenged " + targetUserNameOrTag + " to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString))
            sentMsgs.append(await message.channel.send(":crossed_swords: " + message.author.mention + " challenged **" + str(requestedUser) + "** to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString))
        else:
            targetUserNameOrTag = lib.discordUtil.IDAlertedUserMentionOrName(
                "duels_challenge_incoming_new", dcGuild=message.guild, dcUser=requestedUser, bbUser=targetBBUser)
            sentMsgs.append(await message.channel.send(":crossed_swords: " + message.author.mention + " challenged " + targetUserNameOrTag + " to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString))

        for msg in sentMsgs:
            menuTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.duelChallengeMenuDefaultTimeout), expiryFunction=ReactionMenu.removeEmbedAndOptions, expiryFunctionArgs=msg.id)
            bbGlobals.reactionMenusTTDB.scheduleTask(menuTT)
            newMenu = ReactionDuelChallengeMenu.ReactionDuelChallengeMenu(msg, newDuelReq, timeout=menuTT)
            newDuelReq.menus.append(newMenu)
            await newMenu.updateMessage()
            bbGlobals.reactionMenusDB[msg.id] = newMenu


    elif action == "cancel":
        if not sourceBBUser.hasDuelChallengeFor(targetBBUser):
            await message.channel.send(":x: You do not have an active duel challenge for this user! Did it already expire?")
            return

        if message.guild.get_member(requestedUser.id) is None:
            await message.channel.send(":white_check_mark: You have cancelled your duel challenge for **" + str(requestedUser) + "**.")
            targetUserGuild = lib.discordUtil.findBBUserDCGuild(targetBBUser)
            if targetUserGuild is not None:
                targetUserBBGuild = bbGlobals.guildsDB.getGuild(targetUserGuild.id)
                if targetUserBBGuild.hasPlayChannel() and \
                        targetBBUser.isAlertedForID("duels_challenge_incoming_cancel", targetUserGuild, targetUserBBGuild, targetUserGuild.get_member(targetBBUser.id)):
                    await targetUserBBGuild.getPlayChannel().send(":shield: " + requestedUser.mention + ", " + str(message.author) + " has cancelled their duel challenge.")
        else:
            if targetBBUser.isAlertedForID("duels_challenge_incoming_cancel", message.guild, bbGlobals.guildsDB.getGuild(message.guild.id), message.guild.get_member(targetBBUser.id)):
                await message.channel.send(":white_check_mark: You have cancelled your duel challenge for " + requestedUser.mention + ".")
            else:
                await message.channel.send(":white_check_mark: You have cancelled your duel challenge for **" + str(requestedUser) + "**.")

        # IDAlertedUserMentionOrName(alertType, dcUser=None, bbUser=None, bbGuild=None, dcGuild=None)
        for menu in sourceBBUser.duelRequests[targetBBUser].menus:
            await menu.delete()
        await sourceBBUser.duelRequests[targetBBUser].duelTimeoutTask.forceExpire(callExpiryFunc=False)
        sourceBBUser.removeDuelChallengeTarget(targetBBUser)

    elif action in ["reject", "decline"]:
        if not targetBBUser.hasDuelChallengeFor(sourceBBUser):
            await message.channel.send(":x: This user does not have an active duel challenge for you! Did it expire?")
            return

        duelReq = targetBBUser.duelRequests[sourceBBUser]
        await DuelRequest.rejectDuel(duelReq, message, requestedUser, message.author)

    elif action == "accept":
        if not targetBBUser.hasDuelChallengeFor(sourceBBUser):
            await message.channel.send(":x: This user does not have an active duel challenge for you! Did it expire?")
            return

        requestedDuel = targetBBUser.duelRequests[sourceBBUser]

        if sourceBBUser.credits < requestedDuel.stakes:
            await message.channel.send(":x: You do not have enough credits to accept this duel request! (" + str(requestedDuel.stakes) + ")")
            return
        if targetBBUser.credits < requestedDuel.stakes:
            await message.channel.send(":x:" + str(requestedUser) + " does not have enough credits to fight this duel! (" + str(requestedDuel.stakes) + ")")
            return

        await DuelRequest.fightDuel(message.author, requestedUser, requestedDuel, message)

bbCommands.register("duel", cmd_duel, 0, forceKeepArgsCasing=True, allowDM=False, helpSection="bounties", signatureStr="**duel [action] [user]** *<stakes>*", shortHelp="Fight other players! Action can be `challenge`, `cancel`, `accept` or `reject`.", longHelp="Fight other players! Action can be `challenge`, `cancel`, `accept` or `reject`. When challenging another user to a duel, you must give the amount of credits you will win - the 'stakes'.")


async def cmd_use(message : discord.Message, args : str, isDM : bool):
    """Use the specified tool from the user's inventory.

    :param discord.Message message: the discord message calling the command
    :param str args: a single integer indicating the index of the tool to use
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    callingBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)

    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: Please give the number of the tool you would like to use! e.g: `" + bbConfig.commandPrefix + "use 1`")
    else:
        toolNum = int(args)
        if toolNum < 1:
            await message.channel.send(":x: Tool number must be at least 1!")
        elif callingBBUser.inactiveTools.isEmpty():
            await message.channel.send(":x: You don't have any tools to use!")
        elif toolNum > callingBBUser.inactiveTools.numKeys:
            await message.channel.send(":x: Tool number too big - you only have " + str(callingBBUser.inactiveTools.numKeys) + " tool" + ("" if callingBBUser.inactiveTools.numKeys == 1 else "s") + "!")
        else:
            result = await callingBBUser.inactiveTools[toolNum - 1].item.userFriendlyUse(message, ship=callingBBUser.activeShip, callingBBUser=callingBBUser)
            await message.channel.send(result)


bbCommands.register("use", cmd_use, 0, allowDM=False, helpSection="bounties", signatureStr="**use [tool number]**", shortHelp="Use the tool in your hangar with the given number. See `$COMMANDPREFIX$hangar` for tool numbers.", longHelp="Use the tool in your hangar with the given number. Tool numbers can be seen next your items in `$COMMANDPREFIX$hangar tool`.")
