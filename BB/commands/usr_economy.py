import discord

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig
from ..logging import bbLogger


bbCommands.addHelpSection(0, "economy")


async def cmd_balance(message : discord.Message, args : str, isDM : bool):
    """print the balance of the specified user, use the calling user if no user is specified.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # If no user is specified, send the balance of the calling user
    if args == "":
        if not bbGlobals.usersDB.userIDExists(message.author.id):
            bbGlobals.usersDB.addUser(message.author.id)
        await message.channel.send(":moneybag: **" + message.author.display_name + "**, you have **" + str(bbGlobals.usersDB.getUser(message.author.id).credits) + " Credits**.")

    # If a user is specified
    else:
        # Verify the passed user tag
        requestedUser = lib.discordUtil.getMemberByRefOverDB(args, dcGuild=message.guild)
        if requestedUser is None:
            await message.channel.send(":x: Unknown user!")
            return
        # ensure that the user is in the users database
        if not bbGlobals.usersDB.userIDExists(requestedUser.id):
            bbGlobals.usersDB.addUser(requestedUser.id)
        # send the user's balance
        await message.channel.send(":moneybag: **" + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "** has **" + str(bbGlobals.usersDB.getUser(requestedUser.id).credits) + " Credits**.")

bbCommands.register("balance", cmd_balance, 0, aliases=["bal", "credits"], forceKeepArgsCasing=True, allowDM=True, helpSection="economy", signatureStr="**balance** *[user]*", shortHelp="Get the credits balance of yourself, or another user if one is given.", longHelp="Get the credits balance of yourself, or another user if one is given. If used from inside of a server, `user` can be a mention, ID, username, or username with discriminator (#number). If used from DMs, `user` must be an ID or mention.")


async def cmd_shop(message : discord.Message, args : str, isDM : bool):
    """list the current stock of the bbShop owned by the guild containing the sent message.
    Can specify an item type to list. TODO: Make specified item listings more detailed as in !bb bounties

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string, or one of bbConfig.validItemNames
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.shopDisabled:
        await message.channel.send(":x: This server does not have a shop.")
        return

    item = "all"
    if args.rstrip("s") in bbConfig.validItemNames:
        item = args.rstrip("s")
    elif args != "":
        await message.channel.send(":x: Invalid item type! (ship/weapon/module/turret/all)")
        return

    sendChannel = None
    sendDM = False

    if item == "all":
        if message.author.dm_channel is None:
            await message.author.create_dm()
        if message.author.dm_channel is None:
            sendChannel = message.channel
        else:
            sendChannel = message.author.dm_channel
            sendDM = True
    else:
        sendChannel = message.channel

    requestedShop = bbGlobals.guildsDB.getGuild(message.guild.id).shop
    shopEmbed = lib.discordUtil.makeEmbed(titleTxt="Shop", desc="__" + message.guild.name + "__\n`Current Tech Level: " + str(requestedShop.currentTechLevel) + "`",
                          footerTxt="All items" if item == "all" else (
                              item + "s").title(),
                          thumb=("https://cdn.discordapp.com/icons/" + str(message.guild.id) + "/" + message.guild.icon + ".png?size=64") if message.guild.icon is not None else "")

    if item in ["all", "ship"]:
        for shipNum in range(1, requestedShop.shipsStock.numKeys + 1):
            if shipNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Ships**__", inline=False)

            try:
                currentItem = requestedShop.shipsStock[shipNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested ship '" + requestedShop.shipsStock.keys[shipNum-1].name + "' (index " + str(shipNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.shipsStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in shipsstock KEYS, index " + str(shipNum-1) + ". Expected bbShip, got " + type(requestedShop.shipsStock.keys[shipNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(shipNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.shipsStock.keys[shipNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(shipNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.shipsStock.keys[shipNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.shipsStock.items[currentItem].count
            shopEmbed.add_field(name=str(shipNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.getNameAndNick() + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.getValue())) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    if item in ["all", "weapon"]:
        for weaponNum in range(1, requestedShop.weaponsStock.numKeys + 1):
            if weaponNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Weapons**__", inline=False)

            try:
                currentItem = requestedShop.weaponsStock[weaponNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested weapon '" + requestedShop.weaponsStock.keys[weaponNum-1].name + "' (index " + str(weaponNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.weaponsStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in weaponsstock KEYS, index " + str(weaponNum-1) + ". Expected bbWeapon, got " + type(requestedShop.weaponsStock.keys[weaponNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(weaponNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.weaponsStock.keys[weaponNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(weaponNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.weaponsStock.keys[weaponNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.weaponsStock.items[currentItem].count
            shopEmbed.add_field(name=str(weaponNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.name + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.value)) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    if item in ["all", "module"]:
        for moduleNum in range(1, requestedShop.modulesStock.numKeys + 1):
            if moduleNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Modules**__", inline=False)

            try:
                currentItem = requestedShop.modulesStock[moduleNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested module '" + requestedShop.modulesStock.keys[moduleNum-1].name + "' (index " + str(moduleNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.modulesStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in modulesstock KEYS, index " + str(moduleNum-1) + ". Expected bbModule, got " + type(requestedShop.modulesStock.keys[moduleNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(moduleNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.modulesStock.keys[moduleNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(moduleNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.modulesStock.keys[moduleNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.modulesStock.items[currentItem].count
            shopEmbed.add_field(name=str(moduleNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.name + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.value)) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    if item in ["all", "turret"]:
        for turretNum in range(1, requestedShop.turretsStock.numKeys + 1):
            if turretNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Turrets**__", inline=False)

            try:
                currentItem = requestedShop.turretsStock[turretNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested turret '" + requestedShop.turretsStock.keys[turretNum-1].name + "' (index " + str(turretNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.turretsStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in turretsstock KEYS, index " + str(turretNum-1) + ". Expected bbTurret, got " + type(requestedShop.turretsStock.keys[turretNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(turretNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.turretsStock.keys[turretNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(turretNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.turretsStock.keys[turretNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.turretsStock.items[currentItem].count
            shopEmbed.add_field(name=str(turretNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.name + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.value)) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    try:
        await sendChannel.send(embed=shopEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return
    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji.sendable)

bbCommands.register("shop", cmd_shop, 0, aliases=["store"], allowDM=False, helpSection="economy", signatureStr="**shop** *[item-type]*", shortHelp="Display all items currently for sale. Shop stock is refreshed every six hours. Give an item type to only list items of that type.", longHelp="Display all items currently for sale. Shop stock is refreshed every six hours, with items based on its tech level. Give an item type (ship/weapon/turret/module/tool) to only list items of that type.")


async def cmd_shop_buy(message : discord.Message, args : str, isDM : bool):
    """Buy the item of the given item type, at the given index, from the guild's shop.

    When buying a ship:
    All items are moved to the new ship (or to the user's hangar), and the old active ship is sold.
    if "keep" is specified, the old ship is moved to the hangar instead.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number, and optionally "keep"
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.shopDisabled:
        await message.channel.send(":x: This server does not have a shop.")
        return
        
    requestedShop = requestedBBGuild.shop

    # verify this is the calling user's home guild. If no home guild is set, transfer here.
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if not requestedBBUser.hasHomeGuild():
        await requestedBBUser.transferGuild(message.guild)
        await message.channel.send(":airplane_arriving: Your home guild has been set.")
    elif requestedBBUser.homeGuildID != message.guild.id:
        await message.channel.send(":x: This command can only be used from your home guild!")
        return

    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "shop`")
        return
    if len(argsSplit) > 4:
        await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `keep` when buying a ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    itemNum = argsSplit[1]
    requestedShop = bbGlobals.guildsDB.getGuild(message.guild.id).shop
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)
    shopItemStock = requestedShop.getStockByName(item)
    if itemNum > shopItemStock.numKeys:
        if shopItemStock.numKeys == 0:
            await message.channel.send(":x: This shop has no " + item + "s in stock!")
        else:
            await message.channel.send(":x: Invalid item number! This shop has " + str(shopItemStock.numKeys) + " " + item + "(s).")
        return

    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    transferItems = True
    sellOldShip = True
    if len(argsSplit) > 2:
        for arg in argsSplit[2:]:
            if arg == "keep":
                if item != "ship":
                    await message.channel.send(":x: `keep` can only be used when buying a ship!")
                    return
                sellOldShip = False
            else:
                await message.channel.send(":x: Invalid argument! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `keep` when buying a ship.")
                return

    requestedItem = shopItemStock[itemNum - 1].item

    if item == "ship":
        newShipValue = requestedItem.getValue()
        activeShip = requestedBBUser.activeShip

        # Check the item can be afforded
        if (not sellOldShip and not requestedShop.userCanAffordItemObj(requestedBBUser, requestedItem)) or \
                (sellOldShip and not requestedShop.amountCanAffordShipObj(requestedBBUser.credits + requestedBBUser.activeShip.getValue(shipUpgradesOnly=transferItems), requestedItem)):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedItem.getValue()) + ")")
            return

        requestedBBUser.inactiveShips.addItem(requestedItem)

        if transferItems:
            requestedBBUser.unequipAll(requestedItem)
            activeShip.transferItemsTo(requestedItem)
            requestedBBUser.unequipAll(activeShip)

        if sellOldShip:
            # TODO: move to a separate sellActiveShip function
            oldShipValue = activeShip.getValue(shipUpgradesOnly=transferItems)
            requestedBBUser.credits += oldShipValue
            shopItemStock.addItem(activeShip)
        else:
            oldShipValue = None

        requestedBBUser.equipShipObj(requestedItem, noSaveActive=sellOldShip)
        requestedBBUser.credits -= newShipValue
        shopItemStock.removeItem(requestedItem)

        outStr = ":moneybag: Congratulations on your new **" + requestedItem.name + "**!"
        if sellOldShip:
            outStr += "\nYou received **" + \
                str(oldShipValue) + " credits** for your old **" + \
                str(activeShip.name) + "**."
        else:
            outStr += " Your old **" + activeShip.name + "** can be found in the hangar."
        if transferItems:
            outStr += "\nItems thay could not fit in your new ship can be found in the hangar."
        outStr += "\n\nYour balance is now: **" + \
            str(requestedBBUser.credits) + " credits**."

        await message.channel.send(outStr)

    elif item in ["weapon", "module", "turret", "tool"]:
        if not requestedShop.userCanAffordItemObj(requestedBBUser, requestedItem):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedItem.value) + ")")
            return

        requestedBBUser.credits -= requestedItem.value
        requestedBBUser.getInactivesByName(item).addItem(requestedItem)
        shopItemStock.removeItem(requestedItem)

        await message.channel.send(":moneybag: Congratulations on your new **" + requestedItem.name + "**! \n\nYour balance is now: **" + str(requestedBBUser.credits) + " credits**.")
    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("buy", cmd_shop_buy, 0, allowDM=False, helpSection="economy", signatureStr="**buy <item-type> <item-number>** *[keep]*", shortHelp="Buy the requested item from the shop. Item numbers can be seen in the `$COMMANDPREFIX$shop`.\n🌎 This command must be used in your **home server**.", longHelp="Buy the requested item from the shop. Item numbers are shown next to items in the `$COMMANDPREFIX$shop`.\nWhen buying a ship, your old active ship will be sold, and your items will be moved to the new one. Specify `keep` to instead move active ship to your hangar. E.g: `$COMMANDPREFIX$buy ship <ship number> keep`\n🌎 This command must be used in your **home server**.")


async def cmd_shop_sell(message : discord.Message, args : str, isDM : bool):
    """Sell the item of the given item type, at the given index, from the user's inactive items, to the guild's shop.
    if "clear" is specified, the ship's items are unequipped before selling.
    "clear" is only valid when selling a ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number, and optionally "clear", separated by a single space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.shopDisabled:
        await message.channel.send(":x: This server does not have a shop.")
        return
        
    requestedShop = requestedBBGuild.shop

    # verify this is the calling user's home guild. If no home guild is set, transfer here.
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if not requestedBBUser.hasHomeGuild():
        await requestedBBUser.transferGuild(message.guild)
        await message.channel.send(":airplane_arriving: Your home guild has been set.")
    elif requestedBBUser.homeGuildID != message.guild.id:
        await message.channel.send(":x: This command can only be used from your home guild!")
        return
        
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar`")
        return
    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `clear` when selling a ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    itemNum = argsSplit[1]
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)

    userItemInactives = requestedBBUser.getInactivesByName(item)
    if itemNum > userItemInactives.numKeys:
        await message.channel.send(":x: Invalid item number! You have " + str(userItemInactives.numKeys) + " " + item + "s.")
        return
    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    clearItems = False
    if len(argsSplit) == 3:
        if argsSplit[2] == "clear":
            if item != "ship":
                await message.channel.send(":x: `clear` can only be used when selling a ship!")
                return
            clearItems = True
        else:
            await message.channel.send(":x: Invalid argument! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `clear` when selling a ship.")
            return

    requestedShop = bbGlobals.guildsDB.getGuild(message.guild.id).shop
    shopItemStock = requestedShop.getStockByName(item)
    requestedItem = userItemInactives[itemNum - 1].item

    if item == "ship":
        if clearItems:
            requestedBBUser.unequipAll(requestedItem)

        requestedBBUser.credits += requestedItem.getValue()
        userItemInactives.removeItem(requestedItem)
        shopItemStock.addItem(requestedItem)

        outStr = ":moneybag: You sold your **" + requestedItem.getNameOrNick() + \
            "** for **" + str(requestedItem.getValue()) + " credits**!"
        if clearItems:
            outStr += "\nItems removed from the ship can be found in the hangar."
        await message.channel.send(outStr)

    elif item in ["weapon", "module", "turret", "tool"]:
        requestedBBUser.credits += requestedItem.getValue()
        userItemInactives.removeItem(requestedItem)

        if requestedItem is None:
            raise ValueError("selling NoneType Item")
        shopItemStock.addItem(requestedItem)

        await message.channel.send(":moneybag: You sold your **" + requestedItem.name + "** for **" + str(requestedItem.getValue()) + " credits**!")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("sell", cmd_shop_sell, 0, allowDM=False, helpSection="economy", signatureStr="**sell <item-type> <item-number>** *[clear]*", shortHelp="Sell the requested item from your hangar. Item numbers can be gotten from `$COMMANDPREFIX$hangar`.\n🌎 This command must be used in your **home server**.", longHelp="Sell the requested item from your hangar to the shop. Item numbers are shown next to items in your `$COMMANDPREFIX$hangar`. When selling a ship, specify `clear` to first remove all items from the ship. See `$COMMANDPREFIX$help buy` for how to sell your active ship.\n🌎 This command must be used in your **home server**.")


async def cmd_pay(message : discord.Message, args : str, isDM : bool):
    """Pay a givne user the given number of credits from your balance.
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a target user and an amount!")
        return

    if not lib.stringTyping.isInt(argsSplit[1]):
        await message.channel.send(":x: Invalid amount!")
        return

    requestedUser = lib.discordUtil.getMemberByRefOverDB(argsSplit[0], dcGuild=message.guild)
    if requestedUser is None:
        await message.channel.send(":x: Unknown user!")
        return

    amount = int(argsSplit[1])
    if amount < 1:
        await message.channel.send(":x: You have to pay at least 1 credit!")
        return

    if bbGlobals.usersDB.userIDExists(message.author.id):
        sourceBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        sourceBBUser = bbGlobals.usersDB.addUser(message.author.id)

    if not sourceBBUser.credits >= amount:
        await message.channel.send(":x: You don't have that many credits!")
        return

    if bbGlobals.usersDB.userIDExists(requestedUser.id):
        targetBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
    else:
        targetBBUser = bbGlobals.usersDB.addUser(requestedUser.id)

    sourceBBUser.credits -= amount
    targetBBUser.credits += amount

    await message.channel.send(":moneybag: You paid " + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + " **" + str(amount) + "** credits!")

bbCommands.register("pay", cmd_pay, 0, forceKeepArgsCasing=True, allowDM=True, helpSection="economy", signatureStr="**pay <user> <amount>**", shortHelp="Pay the given user an amount of credits from your balance.", longHelp="Pay the given user an amount of credits from your balance.\nIf used from inside of a server, `user` can be a mention, ID, username, or username with discriminator (#number). If used from DMs, `user` must be an ID or mention.")


async def cmd_total_value(message : discord.Message, args : str, isDM : bool):
    """⚠ WARNING: MARKED FOR CHANGE ⚠
    The following function is provisional and marked as planned for overhaul.
    Details: The command output is finalised. However, the inner workings of the command are to be replaced with attribute getters.
    It is inefficient to calculate total value measurements on every call, so current totals should be cached in object attributes whenever modified.

    print the total value of the specified user, use the calling user if no user is specified.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention or ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # If no user is specified, send the balance of the calling user
    if args == "":
        if not bbGlobals.usersDB.userIDExists(message.author.id):
            bbGlobals.usersDB.addUser(message.author.id)
        await message.channel.send(":moneybag: **" + message.author.display_name + "**, your items and balance are worth a total of **" + str(bbGlobals.usersDB.getUser(message.author.id).getStatByName("value")) + " Credits**.")

    # If a user is specified
    else:
        # Verify the passed user tag
        requestedUser = lib.discordUtil.getMemberByRefOverDB(args, dcGuild=message.guild)
        if requestedUser is None:
            await message.channel.send(":x: Unknown user!")
            return
        # ensure that the user is in the users database
        if not bbGlobals.usersDB.userIDExists(requestedUser.id):
            bbGlobals.usersDB.addUser(requestedUser.id)
        # send the user's balance
        await message.channel.send(":moneybag: **" + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "**'s items and balance have a total value of **" + str(bbGlobals.usersDB.getUser(requestedUser.id).getStatByName("value")) + " Credits**.")

bbCommands.register("total-value", cmd_total_value, 0, forceKeepArgsCasing=True, allowDM=True, helpSection="economy", signatureStr="**total-value** *[user]*", shortHelp="Get the total value of all of your items, including your credits balance, or that of another user.", longHelp="Get the total value of all of your items, including your credits balance. Give a user to check someone else's total inventory value.")
