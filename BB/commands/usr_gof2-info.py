import discord
import os
import asyncio

from . import commandsDB as bbCommands
from ..bbConfig import bbData, bbConfig
from .. import lib, bbGlobals
from ..bbObjects.items import bbShip
from ..reactionMenus import ReactionSkinRegionPicker
from ..logging import bbLogger
from ..shipRenderer import shipRenderer


bbCommands.addHelpSection(0, "gof2 info")
CWD = os.getcwd()


async def cmd_map(message : discord.Message, args : str, isDM : bool):
    """send the image of the GOF2 starmap. If -g is passed, send the grid image

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain -g
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # If -g is specified, send the image with grid overlay
    if args == "-g":
        await message.channel.send(bbData.mapImageWithGraphLink)
    # otherwise, send the image with no grid overlay
    else:
        await message.channel.send(bbData.mapImageNoGraphLink)

bbCommands.register("map", cmd_map, 0, aliases=["starmap"], allowDM=True, helpSection="gof2 info", signatureStr="**map**", shortHelp="Send the complete GOF2 starmap.", longHelp="Send the complete GOF2 starmap with jumpgate routes, including all secret and DLC systems.")


async def cmd_make_route(message : discord.Message, args : str, isDM : bool):
    """display the shortest route between two systems

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the start and end systems, separated by a comma and a space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify two systems are given separated by a comma and a space
    if args == "" or "," not in args or len(args[:args.index(",")]) < 1 or len(args[args.index(","):]) < 2:
        await message.channel.send(":x: Please provide source and destination systems, separated with a comma and space.\nFor example: `" + bbConfig.commandPrefix + "make-route Pescal Inartu, Loma`")
        return
    if args.count(",") > 1:
        await message.channel.send(":x: Please only provide **two** systems!")
        return

    requestedStart = args.split(",")[0].title()
    requestedEnd = args.split(",")[1][1:].title()
    startSyst = ""
    endSyst = ""

    # attempt to look up the requested systems in the built in systems database
    systemsFound = {requestedStart: False, requestedEnd: False}
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(requestedStart):
            systemsFound[requestedStart] = True
            startSyst = syst
        if bbData.builtInSystemObjs[syst].isCalled(requestedEnd):
            systemsFound[requestedEnd] = True
            endSyst = syst

    # report any unrecognised systems
    for syst in [requestedStart, requestedEnd]:
        if not systemsFound[syst]:
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system is not on my star map! :map:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system is not on my star map! :map:")
            return

    # report any systems that were recognised, but do not have any neighbours
    for syst in [startSyst, endSyst]:
        if not bbData.builtInSystemObjs[syst].hasJumpGate():
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system does not have a jump gate! :rocket:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system does not have a jump gate! :rocket:")
            return

    # build and print the route, reporting any errors in the route generation process
    routeStr = ""
    for currentSyst in lib.pathfinding.makeRoute(startSyst, endSyst):
        routeStr += currentSyst + ", "
    if routeStr.startswith("#"):
        await message.channel.send(":x: ERR: Processing took too long! :stopwatch:")
    elif routeStr.startswith("!"):
        await message.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
    elif startSyst == endSyst:
        await message.channel.send(":thinking: You're already there, pilot!")
    else:
        await message.channel.send("Here's the shortest route from **" + startSyst + "** to **" + endSyst + "**:\n> " + routeStr[:-2] + " :rocket:")

bbCommands.register("make-route", cmd_make_route, 0, allowDM=True, helpSection="gof2 info", signatureStr="**make-route <startSystem>, <endSystem>**", shortHelp="Find the shortest route from `startSystem` to `endSystem`.", longHelp="Find the shortest route from `startSystem` to `endSystem`. Both systems must have jump gates. To find out if a system has a jump gate, use `$COMMANDPREFIX$info`.")


async def cmd_info_system(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified system

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a system in the GOF2 starmap
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a systemw as specified
    if args == "":
        await message.channel.send(":x: Please provide a system! Example: `" + bbConfig.commandPrefix + "system Augmenta`")
        return

    # attempt to look up the specified system
    systArg = args.title()
    systObj = None
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(systArg):
            systObj = bbData.builtInSystemObjs[syst]

    # report unrecognised systems
    if systObj is None:
        if len(systArg) < 20:
            await message.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
        else:
            await message.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
    else:
        # build the neighbours statistic into a string
        neighboursStr = ""
        for x in systObj.neighbours:
            neighboursStr += x + ", "
        if neighboursStr == "":
            neighboursStr = "No Jumpgate"
        else:
            neighboursStr = neighboursStr[:-2]

        # build the statistics embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[systObj.faction], desc="__System Information__",
                               titleTxt=systObj.name, footerTxt=systObj.faction.title(), thumb=bbData.factionIcons[systObj.faction])
        statsEmbed.add_field(
            name="Security Level:", value=bbData.securityLevels[systObj.security].title())
        statsEmbed.add_field(name="Neighbour Systems:", value=neighboursStr)

        # list the system's aliases as a string
        if len(systObj.aliases) > 1:
            aliasStr = ""
            for alias in systObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        # list the system's wiki if one exists
        if systObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + systObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-system", 0, cmd_system)


async def cmd_info_criminal(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt criminal

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a criminal name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a criminal was given
    if args == "":
        await message.channel.send(":x: Please provide a criminal! Example: `" + bbConfig.commandPrefix + "criminal Toma Prakupy`")
        return

    # look up the criminal object
    criminalName = args.title()
    criminalObj = None
    for crim in bbData.builtInCriminalObjs.keys():
        if bbData.builtInCriminalObjs[crim].isCalled(criminalName):
            criminalObj = bbData.builtInCriminalObjs[crim]

    # report unrecognised criminal names
    if criminalObj is None:
        if len(criminalName) < 20:
            await message.channel.send(":x: **" + criminalName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + criminalName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[criminalObj.faction],
                               desc="__Criminal File__", titleTxt=criminalObj.name, thumb=criminalObj.icon)
        statsEmbed.add_field(
            name="Wanted By:", value=criminalObj.faction.title() + "s")
        # include the criminal's aliases and wiki if they exist
        if len(criminalObj.aliases) > 1:
            aliasStr = ""
            for alias in criminalObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if criminalObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + criminalObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-criminal", 0, cmd_criminal)


async def cmd_info_ship(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt ship

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")
        return

    # look up the ship object
    itemName = args.title()
    itemObj = None
    for ship in bbData.builtInShipData.values():
        shipObj = bbShip.bbShip.fromDict(ship)
        if shipObj.isCalled(itemName):
            itemObj = shipObj

    # report unrecognised ship names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Ship File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        statsEmbed.add_field(name="Value:", value=lib.stringTyping.commaSplitNum(
            str(itemObj.getValue(shipUpgradesOnly=True))) + " Credits")
        statsEmbed.add_field(name="Armour:", value=str(itemObj.getArmour()))
        statsEmbed.add_field(name="Cargo:", value=str(itemObj.getCargo()))
        statsEmbed.add_field(
            name="Handling:", value=str(itemObj.getHandling()))
        statsEmbed.add_field(name="Max Primaries:",
                             value=str(itemObj.getMaxPrimaries()))
        if len(itemObj.weapons) > 0:
            weaponStr = "*["
            for weapon in itemObj.weapons:
                weaponStr += weapon.name + ", "
            statsEmbed.add_field(name="Equipped Primaries:",
                                 value=weaponStr[:-2] + "]*")
        statsEmbed.add_field(name="Max Secondaries:",
                             value=str(itemObj.getNumSecondaries()))
        # if len(itemObj.secondaries) > 0:
        #     secondariesStr = "*["
        #     for secondary in itemObj.secondaries:
        #         secondariesStr += secondary.name + ", "
        #     statsEmbed.add_field(name="Equipped Secondaries",value=secondariesStr[:-2] + "]*")
        statsEmbed.add_field(name="Turret Slots:",
                             value=str(itemObj.getMaxTurrets()))
        if len(itemObj.turrets) > 0:
            turretsStr = "*["
            for turret in itemObj.turrets:
                turretsStr += turret.name + ", "
            statsEmbed.add_field(name="Equipped Turrets:",
                                 value=turretsStr[:-2] + "]*")
        statsEmbed.add_field(name="Modules Slots:",
                             value=str(itemObj.getMaxModules()))
        if len(itemObj.modules) > 0:
            modulesStr = "*["
            for module in itemObj.modules:
                modulesStr += module.name + ", "
            statsEmbed.add_field(name="Equipped Modules:",
                                 value=modulesStr[:-2] + "]*")
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-ship", 0, cmd_ship)


async def cmd_info_weapon(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt weapon

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a weapon name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a weapon! Example: `" + bbConfig.commandPrefix + "weapon Nirai Impulse EX 1`")
        return

    # look up the weapon object
    itemName = args.title()
    itemObj = None
    for weap in bbData.builtInWeaponObjs.keys():
        if bbData.builtInWeaponObjs[weap].isCalled(itemName):
            itemObj = bbData.builtInWeaponObjs[weap]

    # report unrecognised weapon names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Weapon File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:", value=str(itemObj.dps))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-weapon", 0, cmd_weapon)


async def cmd_info_module(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt module

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a module name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a module! Example: `" + bbConfig.commandPrefix + "module Groza Mk II`")
        return

    # look up the module object
    itemName = args.title()
    itemObj = None
    for module in bbData.builtInModuleObjs.keys():
        if bbData.builtInModuleObjs[module].isCalled(itemName):
            itemObj = bbData.builtInModuleObjs[module]

    # report unrecognised module names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Module File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="Stats:", value=str(
            itemObj.statsStringShort()))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-module", 0, cmd_module)


async def cmd_info_turret(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt turret

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a turret name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a turret! Example: `" + bbConfig.commandPrefix + "turret Groza Mk II`")
        return

    # look up the turret object
    itemName = args.title()
    itemObj = None
    for turr in bbData.builtInTurretObjs.keys():
        if bbData.builtInTurretObjs[turr].isCalled(itemName):
            itemObj = bbData.builtInTurretObjs[turr]

    # report unrecognised turret names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Turret File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:", value=str(itemObj.dps))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-turret", 0, cmd_turret)


async def cmd_info_commodity(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt commodity

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a commodity name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("Commodity items have not been implemented yet!")
    return

    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a commodity! Example: `" + bbConfig.commandPrefix + "commodity Groza Mk II`")
        return

    # look up the commodity object
    itemName = args.title()
    itemObj = None
    for crim in bbData.builtInCommodityObjs.keys():
        if bbData.builtInCommodityObjs[crim].isCalled(itemName):
            itemObj = bbData.builtInCommodityObjs[crim]

    # report unrecognised commodity names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(
            col=bbData.factionColours[itemObj.faction], desc="__Item File__", titleTxt=itemObj.name, thumb=itemObj.icon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(
            name="Wanted By:", value=itemObj.faction.title() + "s")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-commodity", 0, cmd_commodity)


async def cmd_info_skin(message : discord.Message, args : str, isDM : bool):	
    """return statistics about a specified inbuilt skin	
    
    :param discord.Message message: the discord message calling the command	
    :param str args: string containing a skin name	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """	
    # verify a item was given	
    if args == "":	
        await message.channel.send(":x: Please provide a Skin! Example: `" + bbConfig.commandPrefix + "skin tex`")	
        return	
    skin = args.lower()	
    if skin not in bbData.builtInShipSkins:	
        if len(skin) < 20:	
            await message.channel.send(":x: The **" + skin + "** skin is not in my database! :detective:")	
        else:	
            await message.channel.send(":x: The **" + skin[0:15] + "**... skin is not in my database! :detective:")	
    else:	
        shipSkin = bbData.builtInShipSkins[skin]	
        # build the stats embed	
        statsEmbed = lib.discordUtil.makeEmbed(	
            col=lib.discordUtil.randomColour(), desc="__Ship Skin File__", titleTxt=shipSkin.name.title(), thumb=bbConfig.defaultShipSkinToolIcon, footerTxt = ("Preview this skin with the " + "`" + bbConfig.commandPrefix + "showme` command.") if len(shipSkin.compatibleShips) > 0 else "")	
        statsEmbed.add_field(	
            name="Designed by:", value=lib.discordUtil.userTagOrDiscrim(str(shipSkin.designer), guild=message.guild))	
        compatibleShipsStr = ""	
        for ship in shipSkin.compatibleShips:	
            compatibleShipsStr += " - " + ship + "\n"	
        statsEmbed.add_field(	
            name="Compatible ships:", value=compatibleShipsStr[:-1] if compatibleShipsStr != "" else "None")	
        if shipSkin.averageTL != -1:	
            statsEmbed.add_field(name="Average tech level of compatible ships:", value=shipSkin.averageTL)	
        if shipSkin.hasWiki:	
            statsEmbed.add_field(	
                name="‎", value="[Wiki](" + shipSkin.wiki + ")", inline=False)	
        # send the embed	
        await message.channel.send(embed=statsEmbed)	
# bbCommands.register("commodity", cmd_commodity)


async def cmd_info(message : discord.Message, args : str, isDM : bool):
    """Return statistics about a named game object, of a specified type.
    The named used to reference the object may be an alias.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an object type, followed by a space, followed by the object name. For example, 'criminal toma prakupy'
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send(":x: Please give an object type to look up! (system/criminal/ship/weapon/module/turret/commodity)")
        return

    argsSplit = args.split(" ")
    if argsSplit[0] not in ["system", "criminal", "ship", "weapon", "module", "turret", "commodity"]:
        await message.channel.send(":x: Invalid object type! (system/criminal/ship/weapon/module/turret/commodity)")
        return

    if argsSplit[0] == "system":
        await cmd_info_system(message, args[7:], isDM)
    elif argsSplit[0] == "criminal":
        await cmd_info_criminal(message, args[9:], isDM)
    elif argsSplit[0] == "ship":
        await cmd_info_ship(message, args[5:], isDM)
    elif argsSplit[0] == "weapon":
        await cmd_info_weapon(message, args[7:], isDM)
    elif argsSplit[0] == "module":
        await cmd_info_module(message, args[7:], isDM)
    elif argsSplit[0] == "turret":
        await cmd_info_turret(message, args[7:], isDM)
    elif argsSplit[0] == "commodity":
        await cmd_info_commodity(message, args[10:], isDM)
    else:
        await message.channel.send(":x: Unknown object type! (system/criminal/ship/weapon/module/turret/commodity)")

bbCommands.register("info", cmd_info, 0, allowDM=True, helpSection="gof2 info", signatureStr="**info <object-type> <name>**", shortHelp="Display information about something from GOF2. Also gives useful aliases for things.", longHelp="Display information about something from GOF2. object-type must be criminal, system, ship, weapon, module, or turret. Also gives the a list of aliases that can be used to refer to your object in commands.")


async def cmd_showme_criminal(message : discord.Message, args : str, isDM : bool):	
    """Return the URL of the image bountybot uses to represent the specified inbuilt criminal	
    
    :param discord.Message message: the discord message calling the command	
    :param str args: string containing a criminal name	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """	
    # verify a criminal was given	
    if args == "":	
        await message.channel.send(":x: Please provide a criminal! Example: `" + bbConfig.commandPrefix + "criminal Toma Prakupy`")	
        return	
    # look up the criminal object	
    criminalName = args.title()	
    criminalObj = None	
    for crim in bbData.builtInCriminalObjs.keys():	
        if bbData.builtInCriminalObjs[crim].isCalled(criminalName):	
            criminalObj = bbData.builtInCriminalObjs[crim]	
    # report unrecognised criminal names	
    if criminalObj is None:	
        if len(criminalName) < 20:	
            await message.channel.send(":x: **" + criminalName + "** is not in my database! :detective:")	
        else:	
            await message.channel.send(":x: **" + criminalName[0:15] + "**... is not in my database! :detective:")	
    else:	
        itemEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=criminalObj.icon, titleTxt=criminalObj.name, footerTxt="Wanted criminal")	
        await message.channel.send(embed=itemEmbed)	

# bbCommands.register("showme-criminal", cmd_showme_criminal)	


async def cmd_showme_ship(message : discord.Message, args : str, isDM : bool):	
    """Return the URL of the image bountybot uses to represent the specified inbuilt ship	
    
    :param discord.Message message: the discord message calling the command	
    :param str args: string containing a ship name and optionally a skin, prefaced with a + character.	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """	
    # verify a item was given	
    if args == "":	
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")	
        return	
    if "+" in args:	
        if len(args.split("+")) > 2:	
            await message.channel.send(":x: Please only provide one skin, with one `+`!")	
            return	
        elif args.split("+")[1] == "":	
            if len(message.attachments) < 1:	
                await message.channel.send(":x: Please either give a skin name after your `+`, or attach a 2048x2048 jpg to render.")	
                return	
            args, skin = args.split("+")[0], "$ATTACHEDFILE$"	
            if args.lower().endswith("full"):	
                args = args.split("full")[0]	
                skin = "$ATTACHEDFILEFULL$"	
        else:	
            args, skin = args.split("+")	
    else:	
        skin = ""	
    	
    # look up the ship object	
    itemName = args.rstrip(" ").title()	
    itemObj = None	
    for ship in bbData.builtInShipData.values():	
        shipObj = bbShip.bbShip.fromDict(ship)	
        if shipObj.isCalled(itemName):	
            itemObj = shipObj	
    # report unrecognised ship names	
    if itemObj is None:	
        if len(itemName) < 20:	
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")	
        else:	
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")	
        return	
    if skin != "":	
        shipData = bbData.builtInShipData[itemObj.name]	
        if not shipData["skinnable"]:	
            await message.channel.send(":x: That ship is not skinnable!")	
            return	
        if skin in ["$ATTACHEDFILE$", "$ATTACHEDFILEFULL$"]:	
            if len(bbGlobals.currentRenders) >= bbConfig.maxConcurrentRenders:	
                await message.channel.send(":x: My rendering queue is full currently. Please try this command again once someone else's render has completed.")	
                return	
            if itemObj.name in bbGlobals.currentRenders:	
                await message.channel.send(":x: Someone else is currently rendering this ship! Please use this command again once my other " + itemObj.name + " render has completed.")	
                return	
                	
            bbGlobals.currentRenders.append(itemObj.name)	
            if len(message.attachments) < 1:	
                await message.channel.send(":x: Please either give a skin name after your `+`, or attach a 2048x2048 jpg to render.")	
                bbGlobals.currentRenders.remove(itemObj.name)	
                return	
            skinFile = message.attachments[0]	
            if (not skinFile.filename.lower().endswith(".jpg")) or not (skinFile.width == 2048 and skinFile.height == 2048):	
                await message.channel.send(":x: Please either give a skin name after your `+`, or attach a 2048x2048 jpg to render.")	
                bbGlobals.currentRenders.remove(itemObj.name)	
                return	
            try:	
                await skinFile.save(CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_0.jpg")	
            except (discord.HTTPException, discord.NotFound):	
                await message.channel.send(":x: I couldn't download your skin file. Did you delete it?")	
                bbGlobals.currentRenders.remove(itemObj.name)	
                return	
            skinPaths = {0:CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_0.jpg"}	
            disabledLayers = []	
            if skin == "$ATTACHEDFILE$" and shipData["textureRegions"]:	
                layerIndices = [i for i in range(1, shipData["textureRegions"] + 1)]	
                layersPickerMsg = await message.channel.send("** **")	
                layersPickerMenu = ReactionSkinRegionPicker.ReactionSkinRegionPicker(layersPickerMsg, message.author, bbConfig.toolUseConfirmTimeoutSeconds, numRegions=shipData["textureRegions"])	
                pickedLayers = []	
                menuOutput = await layersPickerMenu.doMenu()	
                if bbConfig.spiralEmoji in menuOutput:	
                    pickedLayers = layerIndices	
                elif bbConfig.defaultCancelEmoji in menuOutput:	
                    await message.channel.send("🛑 Skin render cancelled.")	
                    for skinPath in skinPaths.values():	
                        os.remove(skinPath)	
                    bbGlobals.currentRenders.remove(itemObj.name)	
                    return	
                else:	
                    for react in menuOutput:	
                        try:	
                            pickedLayers.append(bbConfig.numberEmojis.index(react))	
                        except ValueError:	
                            pass	
                	
                remainingIndices = [i for i in layerIndices if i not in pickedLayers]	
                if remainingIndices:	
                    disabledLayersPickerMenu = ReactionSkinRegionPicker.ReactionSkinRegionPicker(layersPickerMsg, message.author, bbConfig.toolUseConfirmTimeoutSeconds, possibleRegions=remainingIndices, desc="Would you like to disable any regions?")	
                    menuOutput = await disabledLayersPickerMenu.doMenu()	
                    if bbConfig.spiralEmoji in menuOutput:	
                        disabledLayers = remainingIndices	
                    elif bbConfig.defaultCancelEmoji in menuOutput:	
                        await message.channel.send("🛑 Skin render cancelled.")	
                        for skinPath in skinPaths.values():	
                            os.remove(skinPath)	
                        bbGlobals.currentRenders.remove(itemObj.name)	
                        return	
                    else:	
                        for react in menuOutput:	
                            try:	
                                disabledLayers.append(bbConfig.numberEmojis.index(react))	
                            except ValueError:	
                                pass	
                	
                def showmeAdditionalMessageCheck(newMessage):	
                    return newMessage.author == message.author and (newMessage.content.lower().startswith(bbConfig.commandPrefix + "cancel") or len(newMessage.attachments) > 0)	
                for regionNum in pickedLayers:	
                    nextLayerMsg = await message.channel.send("Please send your image for texture region #" + str(regionNum) + ", or `" + bbConfig.commandPrefix + "cancel` to cancel the render, within " + str(bbConfig.toolUseConfirmTimeoutSeconds) + " seconds.")	
                    try:	
                        imgMsg = await bbGlobals.client.wait_for("message", check=showmeAdditionalMessageCheck, timeout=bbConfig.toolUseConfirmTimeoutSeconds)	
                    except asyncio.TimeoutError:	
                        await nextLayerMsg.edit(content="This menu has now expired. Please try the command again.\n🛑 Skin render cancelled.")	
                        for skinPath in skinPaths.values():	
                            os.remove(skinPath)	
                        bbGlobals.currentRenders.remove(itemObj.name)	
                        return	
                    else:	
                        if imgMsg.content.lower().startswith(bbConfig.commandPrefix + "cancel"):	
                            await message.channel.send("🛑 Skin render cancelled.")	
                            for skinPath in skinPaths.values():	
                                os.remove(skinPath)	
                            bbGlobals.currentRenders.remove(itemObj.name)	
                            return	
                        nextLayer = imgMsg.attachments[0]	
                        if (not nextLayer.filename.lower().endswith(".jpg")) or not (nextLayer.width == 2048 and nextLayer.height == 2048):	
                            await message.channel.send(":x: Please only give 2048x2048 jpgs!\n🛑 Skin render cancelled.")	
                            for skinPath in skinPaths.values():	
                                os.remove(skinPath)	
                            bbGlobals.currentRenders.remove(itemObj.name)	
                            return	
                        try:	
                            await nextLayer.save(CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_" + str(regionNum) + ".jpg")	
                        except (discord.HTTPException, discord.NotFound):	
                            await message.channel.send(":x: I couldn't download your skin file. Did you delete it?\n🛑 Skin render cancelled.")	
                            for skinPath in skinPaths.values():	
                                os.remove(skinPath)	
                            bbGlobals.currentRenders.remove(itemObj.name)	
                            return	
                        skinPaths[regionNum] = CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_" + str(regionNum) + ".jpg"	
            waitMsg = await message.channel.send("🤖 Render started! I'll ping you when I'm done.")	
            	
            renderPath = shipData["path"] + os.sep + "skins" + os.sep + str(message.id) + "-RENDER.png"	
            outSkinPath = shipData["path"] + os.sep + "skins" + os.sep + str(message.id) + ".jpg"	
            await lib.discordUtil.startLongProcess(waitMsg)	
            try:	
                await shipRenderer.renderShip(str(message.id), shipData["path"], shipData["model"], skinPaths, disabledLayers, bbConfig.skinRenderShowmeResolution[0], bbConfig.skinRenderShowmeResolution[1], full=skin == "$ATTACHEDFILEFULL$")	
            except shipRenderer.RenderFailed:	
                await message.channel.send(message.author.mention + "\n🥺 Render failed! The error has been logged, please try a different ship.")	
                bbLogger.log("Main", "cmd_showme_ship", "Ship render failed with args: '" + args + "'")	
            else:	
                with open(renderPath, "rb") as f:	
                    imageEmbedMsg = await bbGlobals.client.get_channel(bbConfig.showmeSkinRendersChannel).send("u" + str(message.author.id) + "g" + ("DM" if message.channel.type in [discord.ChannelType.private, discord.ChannelType.group] else str(message.guild.id)) + "c" + str(message.channel.id) + "m" + str(message.id), file=discord.File(f))	
                    renderEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=imageEmbedMsg.attachments[0].url, authorName="Skin Render Complete!", icon="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/robot_1f916.png", footerTxt="Custom skinned " + itemObj.name.capitalize())	
                    await message.channel.send(message.author.mention, embed=renderEmbed)	
            	
            bbGlobals.currentRenders.remove(itemObj.name)	
            try:	
                os.remove(renderPath)	
            except FileNotFoundError:	
                pass	
            	
            for skinPath in skinPaths.values():	
                os.remove(skinPath)	
            	
            try:	
                os.remove(outSkinPath)	
            except FileNotFoundError:	
                pass	
            await lib.discordUtil.endLongProcess(waitMsg)	
            return	
        else:	
            skin = skin.lstrip(" ").lower()	
            if skin not in bbData.builtInShipSkins:	
                if len(itemName) < 20:	
                    await message.channel.send(":x: The **" + skin + "** skin is not in my database! :detective:")	
                else:	
                    await message.channel.send(":x: The **" + skin[0:15] + "**... skin is not in my database! :detective:")	
            elif skin not in bbData.builtInShipData[itemObj.name]["compatibleSkins"]:	
                await message.channel.send(":x: That skin is not compatible with the **" + itemObj.name + "**!")	
            	
            else:	
                itemEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=bbData.builtInShipSkins[skin].shipRenders[itemObj.name][0], titleTxt=itemObj.name, footerTxt="Custom skin: " + skin.capitalize())	
                await message.channel.send(embed=itemEmbed)	
    else:	
        if not itemObj.hasIcon:	
            await message.channel.send(":x: I don't have an icon for **" + itemObj.name.title() + "**!")	
        else:	
            itemEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=itemObj.icon, titleTxt=itemObj.name, footerTxt=itemObj.manufacturer.capitalize() + " ship")	
            await message.channel.send(embed=itemEmbed)	

# bbCommands.register("showme-ship", cmd_showme_ship)	


async def cmd_showme_weapon(message : discord.Message, args : str, isDM : bool):	
    """Return the URL of the image bountybot uses to represent the specified inbuilt weapon	
    
    :param discord.Message message: the discord message calling the command	
    :param str args: string containing a weapon name	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """	
    # verify a item was given	
    if args == "":	
        await message.channel.send(":x: Please provide a weapon! Example: `" + bbConfig.commandPrefix + "weapon Nirai Impulse EX 1`")	
        return	
    # look up the weapon object	
    itemName = args.title()	
    itemObj = None	
    for weap in bbData.builtInWeaponObjs.keys():	
        if bbData.builtInWeaponObjs[weap].isCalled(itemName):	
            itemObj = bbData.builtInWeaponObjs[weap]	
    # report unrecognised weapon names	
    if itemObj is None:	
        if len(itemName) < 20:	
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")	
        else:	
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")	
    else:	
        if not itemObj.hasIcon:	
            await message.channel.send(":x: I don't have an icon for **" + itemObj.name.title() + "**!")	
        else:	
            itemEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=itemObj.icon, titleTxt=itemObj.name, footerTxt="Level " + str(itemObj.techLevel) + " weapon")	
            await message.channel.send(embed=itemEmbed)	

# bbCommands.register("showme-weapon", cmd_showme_weapon)	


async def cmd_showme_module(message : discord.Message, args : str, isDM : bool):	
    """Return the URL of the image bountybot uses to represent the specified inbuilt module	
    
    :param discord.Message message: the discord message calling the command	
    :param str args: string containing a module name	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a module! Example: `" + bbConfig.commandPrefix + "module Groza Mk II`")	
        return
    # look up the module object
    itemName = args.title()
    itemObj = None
    for module in bbData.builtInModuleObjs.keys():
        if bbData.builtInModuleObjs[module].isCalled(itemName):
            itemObj = bbData.builtInModuleObjs[module]
    # report unrecognised module names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")	
        else:	
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")	
    else:	
        if not itemObj.hasIcon:	
            await message.channel.send(":x: I don't have an icon for **" + itemObj.name.title() + "**!")	
        else:	
            itemEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=itemObj.icon, titleTxt=itemObj.name, footerTxt="Level " + str(itemObj.techLevel) + " module")	
            await message.channel.send(embed=itemEmbed)	

# bbCommands.register("showme-module", cmd_showme_module)	


async def cmd_showme_turret(message : discord.Message, args : str, isDM : bool):	
    """Return the URL of the image bountybot uses to represent the specified inbuilt turret	
    :param discord.Message message: the discord message calling the command	
    :param str args: string containing a turret name	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """
    # verify a item was given	
    if args == "":	
        await message.channel.send(":x: Please provide a turret! Example: `" + bbConfig.commandPrefix + "turret Groza Mk II`")	
        return	
    # look up the turret object	
    itemName = args.title()	
    itemObj = None	
    for turr in bbData.builtInTurretObjs.keys():	
        if bbData.builtInTurretObjs[turr].isCalled(itemName):	
            itemObj = bbData.builtInTurretObjs[turr]	
    # report unrecognised turret names	
    if itemObj is None:	
        if len(itemName) < 20:	
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")	
        else:	
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")	
    else:	
        if not itemObj.hasIcon:	
            await message.channel.send(":x: I don't have an icon for **" + itemObj.name.title() + "**!")	
        else:	
            itemEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=itemObj.icon, titleTxt=itemObj.name, footerTxt="Level " + str(itemObj.techLevel) + " turret")	
            await message.channel.send(embed=itemEmbed)	

# bbCommands.register("showme-turret", cmd_showme_turret)	


async def cmd_showme_commodity(message : discord.Message, args : str, isDM : bool):	
    """Return the URL of the image bountybot uses to represent the specified inbuilt commodity	
    :param discord.Message message: the discord message calling the command	
    :param str args: string containing a commodity name	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """
    await message.channel.send("Commodity items have not been implemented yet!")	
    return	
    # verify a item was given	
    if args == "":	
        await message.channel.send(":x: Please provide a commodity! Example: `" + bbConfig.commandPrefix + "commodity Groza Mk II`")	
        return	
    # look up the commodity object	
    itemName = args.title()	
    itemObj = None	
    for crim in bbData.builtInCommodityObjs.keys():	
        if bbData.builtInCommodityObjs[crim].isCalled(itemName):	
            itemObj = bbData.builtInCommodityObjs[crim]	
    # report unrecognised commodity names	
    if itemObj is None:	
        if len(itemName) < 20:	
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")	
        else:	
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")	
    else:	
        if not itemObj.hasIcon:	
            await message.channel.send(":x: I don't have an icon for **" + itemObj.name.title() + "**!")	
        else:	
            itemEmbed = makeEmbed(col=randomColour(), img=itemObj.icon, titleTxt=itemObj.name)	
            await message.channel.send(embed=itemEmbed)	

# bbCommands.register("showme-commodity", cmd_showme_commodity)	


async def cmd_showme(message : discord.Message, args : str, isDM : bool):	
    """Return the URL of the image bountybot uses to represent the named game object, of a specified type.	
    The named used to reference the object may be an alias.	

    :param discord.Message message: the discord message calling the command	
    :param str args: string containing an object type, followed by a space, followed by the object name. For example, 'criminal toma prakupy'	
    :param bool isDM: Whether or not the command is being called from a DM channel	
    """
    if args == "":	
        await message.channel.send(":x: Please give an object type to look up! (system/criminal/ship/weapon/module/turret/commodity)")	
        return	
    argsSplit = args.split(" ")	
    if argsSplit[0] not in ["system", "criminal", "ship", "weapon", "module", "turret", "commodity"]:	
        await message.channel.send(":x: Invalid object type! (system/criminal/ship/weapon/module/turret/commodity)")	
        return	
    if argsSplit[0] == "criminal":	
        await cmd_showme_criminal(message, args[9:], isDM)	
    elif argsSplit[0] == "ship":	
        await cmd_showme_ship(message, args[5:], isDM)	
    elif argsSplit[0] == "weapon":	
        await cmd_showme_weapon(message, args[7:], isDM)	
    elif argsSplit[0] == "module":	
        await cmd_showme_module(message, args[7:], isDM)	
    elif argsSplit[0] == "turret":	
        await cmd_showme_turret(message, args[7:], isDM)	
    elif argsSplit[0] == "commodity":	
        await cmd_showme_commodity(message, args[10:], isDM)	
    else:	
        await message.channel.send(":x: Unknown object type! (criminal/ship/weapon/module/turret/commodity)")	

bbCommands.register("showme", cmd_showme, 0, allowDM=True, aliases=["show", "render"], helpSection="gof2 info", signatureStr="**showme <object-type> <name>** *[[full]+ [skinName]]*", shortHelp="Get an image of the named item. This command can also render ships with a given skin.", longHelp="Get a larger image of the requested item. If your item is a ship, you may also specify a skin name, prefaced by a `+` symbol.\nAlternatively, give a `+` and no ship name, and attach your own 2048x2048 jpg image, and I will render it onto your ship! Give `full+` instead of `+` to disable autoskin and render exactly your provided image, with no additional texturing.")