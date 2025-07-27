import discord
import os
import asyncio

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig, bbData
from ..userAlerts import UserAlerts
from ..scheduling import TimedTask
from ..reactionMenus import ReactionRolePicker, ReactionSkinRegionPicker
from ..bbObjects.items import bbShip
from ..logging import bbLogger
from ..shipRenderer import shipRenderer
from . import util_autoskin

from . import util_help

CWD = os.getcwd()


async def admin_cmd_admin_help(message : discord.Message, args : str, isDM : bool):
    """admin command printing help strings for admin commands as defined in bbData

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await util_help.util_autohelp(message, args, isDM, 1)

bbCommands.register("admin-help", admin_cmd_admin_help, 1, signatureStr="**admin-help** *[page number, section or command]*", shortHelp="Display information about admin-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info.", longHelp="Display information about admin-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info about a set of commands. These are the currently valid section names:\n- Channels\n- Miscellaneous")


async def admin_cmd_config(message : discord.Message, args : str, isDM : bool):
    """Apply various bountybot configuration settings for the calling guild.
    TODO: Refactor!

    :param discord.Message message: the discord message calling the command
    :param str args: A string containing a config setting id followed by a value
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")

    if len(argsSplit) < 2 or not (argsSplit[0] and argsSplit[1]):
        await message.channel.send(":x: Please provide both a setting and a value! e.g: `" + bbConfig.commandPrefix + "config bounties enable`")
        return

    setting, value = argsSplit[0], " ".join(argsSplit[1:])

    trueStrings = ["yes","true","on","enable","enabled"]
    falseStrings = ["no","false","off","disable","disabled"]
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)

    if setting in ["bounty","bounties"]:
        if value in trueStrings:
            if not callingBBGuild.bountiesDisabled:
                await message.channel.send(":x: Bounties are already enabled in this server!")
            else:
                callingBBGuild.enableBounties()
                await message.channel.send(":white_check_mark: Bounties are now enabled on this server!")
        elif value in falseStrings:
            if callingBBGuild.bountiesDisabled:
                await message.channel.send(":x: Bounties are already disabled in this server!")
            else:
                callingBBGuild.disableBounties()
                await message.channel.send(":white_check_mark: Bounties are now disabled on this server!")
        else:
            await message.channel.send(":x: Unknown value!")
    elif setting in ["shop", "shops"]:
        if value in trueStrings:
            if not callingBBGuild.shopDisabled:
                await message.channel.send(":x: The shop is already enabled in this server!")
            else:
                callingBBGuild.enableShop()
                await message.channel.send(":white_check_mark: The shop is now enabled on this server!")
        elif value in falseStrings:
            if callingBBGuild.shopDisabled:
                await message.channel.send(":x: The shop is already disabled in this server!")
            else:
                callingBBGuild.disableShop()
                await message.channel.send(":white_check_mark: The shop is now disabled on this server!")
        else:
            await message.channel.send(":x: Unknown value!")
    else:
        await message.channel.send(":x: Unknown setting!")

bbCommands.register("config", admin_cmd_config, 1, signatureStr="**config <setting> <value>**", shortHelp="Set various settings for how bountybot will function in this server.", longHelp="Set various settings for how bountybot will function in this server. Currently, `setting` can be either 'bounties' or 'shop', and `value` can either 'enable' or 'disable', all with a few handy aliases. This command is lets you enable or disable large amounts of functionality all together.")


async def admin_cmd_del_reaction_menu(message : discord.Message, args : str, isDM : bool):
    """Force the expiry of the specified reaction menu message, regardless of reaction menu type.

    :param discord.Message message: the discord message calling the command
    :param str args: A string containing the message ID of an active reaction menu.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    msgID = int(args)
    if msgID in bbGlobals.reactionMenusDB:
        await bbGlobals.reactionMenusDB[msgID].delete()
    else:
        await message.channel.send(":x: Unrecognised reaction menu!")

bbCommands.register("del-reaction-menu", admin_cmd_del_reaction_menu, 1, signatureStr="**del-reaction-menu <id>**", longHelp="Remove the specified reaction menu. You can also just delete the message, if you have permissions.\nTo get the ID of a reaction menu, enable discord's developer mode, right click on the menu, and click Copy ID.")


async def admin_cmd_set_notify_role(message : discord.Message, args : str, isDM : bool):
    """For the current guild, set a role to mention when certain events occur.

    can take either a role mention or ID.

    :param discord.Message message: the discord message calling the command
    :param str args: the notfy role type, and either a role mention or a role ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please provide both a notification type, and either a role mention or ID!")
        return
    if not (lib.stringTyping.isInt(argsSplit[-1]) or lib.stringTyping.isRoleMention(argsSplit[-1])):
        await message.channel.send(":x: Invalid role! Please give either a role mention or ID!")
        return

    alertsToSet = UserAlerts.getAlertIDFromHeirarchicalAliases(argsSplit)
    if alertsToSet[0] == "ERR":
        await message.channel.send(alertsToSet[1])
        return

    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if lib.stringTyping.isRoleMention(argsSplit[-1]):
        requestedRole = message.guild.get_role(int(argsSplit[-1][3:-1]))
    else:
        requestedRole = message.guild.get_role(int(argsSplit[-1]))

    if requestedRole is None:
        await message.channel.send(":x: Role not found!")
        return

    for alertID in alertsToSet:
        alertType = UserAlerts.userAlertsIDsTypes[alertID]
        requestedBBGuild.setUserAlertRoleID(alertID, requestedRole.id)
        await message.channel.send(":white_check_mark: Role set for " + UserAlerts.userAlertsTypesNames[alertType] + " notifications!")

bbCommands.register("set-notify-role", admin_cmd_set_notify_role, 1, signatureStr="**set-notify-role <type>** *[alert]* **<role>**", shortHelp="Set a role to ping when various events occur. For valid notification types, see `$COMMANDPREFIX$help notify`.", longHelp="Set a role to ping when various events occur. **<type>** and/or *[alert]* must specify a type of notification. **<role>** can be either a role mention, or a role ID. For valid notification types, see `$COMMANDPREFIX$help notify`.")


async def admin_cmd_remove_notify_role(message : discord.Message, args : str, isDM : bool):
    """For the current guild, remove role mentioning when certain events occur.
    Takes only a UserAlert ID.

    :param discord.Message message: the discord message calling the command
    :param str args: the notfy role type, and either a role mention or a role ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send(":x: Please provide both a notification type!")
        return

    alertsToSet = UserAlerts.getAlertIDFromHeirarchicalAliases(args)
    if alertsToSet[0] == "ERR":
        await message.channel.send(alertsToSet[1])
        return

    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)

    for alertID in alertsToSet:
        alertType = UserAlerts.userAlertsIDsTypes[alertID]
        requestedBBGuild.removeUserAlertRoleID(alertID)
        await message.channel.send(":white_check_mark: Role pings disabled for " + UserAlerts.userAlertsTypesNames[alertType] + " notifications.")

bbCommands.register("remove-notify-role", admin_cmd_remove_notify_role, 1, signatureStr="**remove-notify-role <type>** *[alert]*", shortHelp="Disable role pings for various events. For valid notification types, see `$COMMANDPREFIX$help notify`.", longHelp="Disable role pings for various events. **<type>** and/or *[alert]* must specify a type of notification. For valid notification types, see `$COMMANDPREFIX$help notify`.")


async def admin_cmd_make_role_menu(message : discord.Message, args : str, isDM : bool):
    """Create a reaction role menu, allowing users to self-assign or remove roles by adding and removing reactions.
    Each guild may have a maximum of bbConfig.maxRoleMenusPerGuild role menus active at any one time.
    Option reactions must be either unicode, or custom to the server where the menu is being created.

    args must contain a menu subject and new line, followed by a newline-separated list of emoji-option pairs, where each pair is separated with a space.
    For example: 'Number Roles\n0️⃣ @Role-1\n1️⃣ @Role-2\n2️⃣ @Role-3' will produce three options:
    - Toggling the 0️⃣ reaction will toggle user ownership of @Role-1
    - Toggling the 1️⃣ reaction will toggle user ownership of @Role-2
    - Toggling the 2️⃣ reaction will toggle user ownership of @Role-3
    Where the subject of the menu is 'Number Roles'.
    The menu subject is optional. To not provide a subject, simply start args with a new line.

    args may also optionally contain the following keyword arguments, given as argname=value
    - target         : A role or user to restrict participants by. Must be a user or role mention, not ID.
    - days           : The number of days that the menu should run for. Must be at least one, or unspecified.
    - hours          : The number of hours that the menu should run for. Must be at least one, or unspecified.
    - minutes        : The number of minutes that the menu should run for. Must be at least one, or unspecified.
    - seconds        : The number of seconds that the menu should run for. Must be at least one, or unspecified.

    Reaction menus can be forced to run forever. To do this, specify ALL run time kwargs as 'off'.

    TODO: Change options list formatting from comma separated to new line separated
    TODO: Support target IDs
    TODO: Implement single choice/grouped roles
    TODO: Change non-expiring menu specification from all kwargs 'off' to a special kwarg 'on'

    :param discord.Message message: the discord message calling the command
    :param str args: A comma-separated list of space-separated emoji-option pairs, and optionally any kwargs as specified in this function's docstring
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.ownedRoleMenus >= bbConfig.maxRoleMenusPerGuild:
        await message.channel.send(":x: Guilds can have at most " + str(bbConfig.maxRoleMenusPerGuild) + " role menus!")
        return
    requestedBBGuild.ownedRoleMenus += 1

    botRole = None
    potentialRoles = []
    for currRole in message.guild.me.roles:
        if currRole.name == message.guild.me.name and currRole.managed:
            potentialRoles.append(currRole)
    
    if potentialRoles == []:
        await message.channel.send(":x: I can't find my '" + message.guild.me.name + "' role! Have you renamed it?")
        return
    botRole = potentialRoles[-1]

    reactionRoles = {}
    kwArgs = {}

    argsSplit = args.split("\n")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Invalid arguments! Please provide your menu title, followed by a new line, then a new line-separated series of options.\nFor more info, see `" + bbConfig.commandPrefix + "admin-help`")
        return
    menuSubject = argsSplit[0]
    argPos = 0

    for arg in argsSplit[1:]:
        if arg == "":
            continue
        argPos += 1
        try:
            roleStr, dumbReact = arg.strip(" ").split(" ")[1], lib.emojis.dumbEmojiFromStr(arg.strip(" ").split(" ")[0])
        except (ValueError, IndexError):
            for kwArg in ["target=", "days=", "hours=", "seconds=", "minutes=", "multiplechoice="]:
                if arg.lower().startswith(kwArg):
                    kwArgs[kwArg[:-1]] = arg[len(kwArg):]
                    break
        # except lib.emojis.UnrecognisedCustomEmoji:
            # await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
            # return
        else:
            if dumbReact.sendable == "None":
                await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
                return
            if dumbReact is None:
                await message.channel.send(":x: Invalid emoji: " + arg.strip(" ").split(" ")[1])
                return
            elif dumbReact.isID:
                localEmoji = False
                for localEmoji in message.guild.emojis:
                    if localEmoji.id == dumbReact.id:
                        localEmoji = True
                        break
                if not localEmoji:
                    await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
                    return

            if dumbReact in reactionRoles:
                await message.channel.send(":x: Cannot use the same emoji for two options!")
                return


            role = message.guild.get_role(int(roleStr.lstrip("<@&").rstrip(">")))
            if role is None:
                await message.channel.send(":x: Unrecognised role: " + roleStr)
                return
            elif role.position > botRole.position:
                await message.channel.send(":x: I can't grant the **" + role.name + "** role!\nMake sure it's below my '" + botRole.name + "' role in the server roles list.")
            reactionRoles[dumbReact] = role

    if len(reactionRoles) == 0:
        await message.channel.send(":x: No roles given!")
        return

    targetRole = None
    targetMember = None
    if "target" in kwArgs:
        if lib.stringTyping.isRoleMention(kwArgs["target"]):
            targetRole = message.guild.get_role(int(kwArgs["target"].lstrip("<@&").rstrip(">")))
            if targetRole is None:
                await message.channel.send(":x: Unknown target role!")
                return
        
        elif lib.stringTyping.isMention(kwArgs["target"]):
            targetMember = message.guild.get_member(int(kwArgs["target"].lstrip("<@!").rstrip(">")))
            if targetMember is None:
                await message.channel.send(":x: Unknown target user!")
                return

        else:
            await message.channel.send(":x: Invalid target role/user!")
            return
    
    timeoutDict = {}

    for timeName in ["days", "hours", "minutes", "seconds"]:
        if timeName in kwArgs:
            if kwArgs[timeName].lower() == "off":
                timeoutDict[timeName] = -1
            else:
                if not lib.stringTyping.isInt(kwArgs[timeName]) or int(kwArgs[timeName]) < 1:
                    await message.channel.send(":x: Invalid number of " + timeName + " before timeout!")
                    return

                timeoutDict[timeName] = int(kwArgs[timeName])


    multipleChoice = True

    if "multiplechoice" in kwArgs:
        if kwArgs["multiplechoice"].lower() in ["off", "no", "false", "single", "one"]:
            multipleChoice = False
        elif kwArgs["multiplechoice"].lower() not in ["on", "yes", "true", "multiple", "many"]:
            await message.channel.send("Invalid `multiplechoice` argument '" + kwArgs["multiplechoice"] + "'! Please use either `multiplechoice=yes` or `multiplechoice=no`")
            return

    timeoutExists = False
    for timeName in timeoutDict:
        if timeoutDict[timeName] != -1:
            timeoutExists = True
    timeoutExists = timeoutExists or timeoutDict == {}
    
    menuMsg = await message.channel.send("‎")

    if timeoutExists:
        timeoutDelta = lib.timeUtil.timeDeltaFromDict(bbConfig.roleMenuDefaultTimeout if timeoutDict == {} else timeoutDict)
        timeoutTT = TimedTask.TimedTask(expiryDelta=timeoutDelta, expiryFunction=ReactionRolePicker.markExpiredRoleMenu, expiryFunctionArgs=menuMsg.id)
        bbGlobals.reactionMenusTTDB.scheduleTask(timeoutTT)
    
    else:
        timeoutTT = None

    menu = ReactionRolePicker.ReactionRolePicker(menuMsg, reactionRoles, message.guild, targetRole=targetRole, targetMember=targetMember, timeout=timeoutTT, titleTxt=menuSubject)
    await menu.updateMessage()
    bbGlobals.reactionMenusDB[menuMsg.id] = menu

bbCommands.register("make-role-menu", admin_cmd_make_role_menu, 1, forceKeepArgsCasing=True, signatureStr="**make-role-menu** *<title>*\n**<option1 emoji> <@option1 role>**\n...    ...\n*[kwargs]*", shortHelp="Create a reaction role menu. Each option must be on its own new line, as an emoji, followed by a space, followed by a mention of the role to grant.", longHelp="Create a reaction role menu. Each option must be on its own new line, as an emoji, followed by a space, followed by a mention of the role to grant. The `title` is displayed at the top of the meny and is optional, to exclude your title simply give a new line. \n__kwargs__\n- Give target=@role mention to limit use of the menu only to users with the specified role.\n- You may set expiry time for your menu, with each time division on a new line. Acceptable time divisions are: seconds, minutes, hours, days. To force the menu to never expire, give **all** time divisions as `off`.(default: minutes=5)")


async def admin_cmd_showmeHD(message : discord.Message, args : str, isDM : bool):
    """Render the attached image file onto the specified ship, in high definition.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    prefix = bbConfig.commandPrefix

    # verify a item was given
    if args == "":
        await message.reply(mention_author=False,
                            content=f":x: Please provide a ship! Example: `{prefix}showme ship Groza Mk II`")
        return

    full = args.endswith("-full")
    if full:
        args = args.split("-full")[0].rstrip()

    result = await util_autoskin.collectAutoskinArgs(message, args, bbConfig.skinRenderShowmeHDResolution[0],
                                                                        bbConfig.skinRenderShowmeHDResolution[1],
                                                                        bbConfig.skinRenderShowmeHDSamples, full)
    if result is None:
        return
        
    shipName, rendererArgs = result
    await util_autoskin.doAutoSkin(message, rendererArgs, shipName, "HD")
    

bbCommands.register("showmehd", admin_cmd_showmeHD, 1, allowDM=True, signatureStr="**showmeHD <ship-name>** *[-full]*",
                        shortHelp="Render your specified ship with the given skin, in full HD 1080p! " \
                                    + "⚠ WARNING: THIS WILL TAKE A LONG TIME.",
                        longHelp="You must attach a 2048x2048 jpg to your message. Render your specified ship with the " \
                                    + "given skin, in full HD 1080p! ⚠ WARNING: THIS WILL TAKE A LONG TIME. Give `-full` " \
                                    + "to disable autoskin and render exactly your provided image, " \
                                    + "with no additional texturing.")

bbCommands.register("showmehd", admin_cmd_showmeHD, 2, allowDM=True, signatureStr="**showmeHD <ship-name>** *[-full]*",
                        shortHelp="Render your specified ship with the given skin, in full HD 1080p! " \
                                    + "⚠ WARNING: THIS WILL TAKE A LONG TIME.",
                        longHelp="You must attach a 2048x2048 jpg to your message. Render your specified ship with the " \
                                    + "given skin, in full HD 1080p! ⚠ WARNING: THIS WILL TAKE A LONG TIME. Give `-full` " \
                                    + "to disable autoskin and render exactly your provided image, " \
                                    + "with no additional texturing.")