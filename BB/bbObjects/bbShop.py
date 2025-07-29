# Typing imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import bbUser

from ..bbConfig import bbData, bbConfig
from .items import bbModuleFactory, bbShip, bbWeapon, bbTurret, bbItem
from .items.modules import bbModule
from . import bbInventory
import random
from ..logging import bbLogger
from ..baseClasses import bbSerializable


class bbShop(bbSerializable.bbSerializable):
    """A shop containing a random selection of items which players can buy.
    Items can be sold to the shop to the shop's inventory and listed for sale.
    Shops are assigned a random tech level, which influences ths stock generated.
    
    :var maxShips: The maximum number of ships generated on every stock refresh.
    :vartype maxShips: int
    :var maxModules: The maximum number of modules generated on every stock refresh.
    :vartype maxModules: int
    :var maxWeapons: The maximum number of weapons generated on every stock refresh.
    :vartype maxWeapons: int
    :var maxTurrets: The maximum number of turrets generated on every stock refresh.
    :vartype maxTurrets: int
    :var currentTechLevel: The current tech level of the shop, influencing the tech levels of the stock generated upon refresh.
    :vartype currentTechLevel: int
    :var shipsStock: A bbInventory containing the shop's stock of ships
    :vartype shipsStock: bbInventory
    :var weaponsStock: A bbInventory containing the shop's stock of weapons
    :vartype weaponsStock: bbInventory
    :var modulesStock: A bbInventory containing the shop's stock of modules
    :vartype modulesStock: bbInventory
    :var turretsStock: A bbInventory containing the shop's stock of turrets
    :vartype turretsStock: bbInventory
    """

    def __init__(self, maxShips : int = bbConfig.shopDefaultShipsNum, maxModules : int = bbConfig.shopDefaultModulesNum,
            maxWeapons : int = bbConfig.shopDefaultWeaponsNum, maxTurrets : int = bbConfig.shopDefaultTurretsNum,
            shipsStock : bbInventory.bbInventory = bbInventory.bbInventory(),
            weaponsStock : bbInventory.bbInventory = bbInventory.bbInventory(),
            modulesStock : bbInventory.bbInventory = bbInventory.bbInventory(),
            turretsStock : bbInventory.bbInventory = bbInventory.bbInventory(),
            currentTechLevel : int = bbConfig.minTechLevel, noRefresh : bool = False):
        """
        :param int maxShips: The maximum number of ships generated on every stock refresh. (Default bbConfig.shopDefaultShipsNum)
        :param int maxModules: The maximum number of modules generated on every stock refresh. (Default bbConfig.shopDefaultModulesNum)
        :param int maxWeapons: The maximum number of weapons generated on every stock refresh. (Default bbConfig.shopDefaultWeaponsNum)
        :param int maxTurrets: The maximum number of turrets generated on every stock refresh. (Default bbConfig.shopDefaultTurretsNum)
        :param int currentTechLevel: The current tech level of the shop, influencing the tech levels of the stock generated upon refresh. (Default empty bbInventory)
        :param bbInventory shipsStock: The shop's current stock of ships (Default empty bbInventory)
        :param bbInventory weaponsStock: The shop's current stock of weapons (Default empty bbInventory)
        :param bbInventory modulesStock: The shop's current stock of modules (Default empty bbInventory)
        :param bbInventory turretsStock: The shop's current stock of turrets (Default bbConfig.minTechLevel)
        :param bool noRefresh: By default, if all shop stocks are empty, the shop will refresh. Give True here to disable this functionality and allow empty shops. (Default False)
        """
        
        self.maxShips = maxShips
        self.maxModules = maxModules
        self.maxWeapons = maxWeapons
        self.maxTurrets = maxTurrets
        self.currentTechLevel = currentTechLevel

        # TODO: Somewhere, stocks are getting passed in and shared amongst all shops. Fix this. Temporary inventory clear here to make sure each shop gets its own inventory objects.
        self.shipsStock = bbInventory.bbInventory()
        self.weaponsStock = bbInventory.bbInventory()
        self.modulesStock = bbInventory.bbInventory()
        self.turretsStock = bbInventory.bbInventory()

        if (not noRefresh) and shipsStock.isEmpty() and weaponsStock.isEmpty() and modulesStock.isEmpty() and turretsStock.isEmpty():
            self.refreshStock()
        else:
            for itemListing in shipsStock.items.values():
                self.shipsStock.addItem(itemListing.item, itemListing.count)
            for itemListing in weaponsStock.items.values():
                self.weaponsStock.addItem(itemListing.item, itemListing.count)
            for itemListing in modulesStock.items.values():
                self.modulesStock.addItem(itemListing.item, itemListing.count)
            for itemListing in turretsStock.items.values():
                self.turretsStock.addItem(itemListing.item, itemListing.count)


    def refreshStock(self, level : int = -1):
        """Refresh the stock of the shop by picking random items according to the given tech level. All previous stock is deleted.
        If level = -1 is given, a new shop tech level is generated at random.

        :param int level: The new tech level of the shop. Give -1 to pick a level at random according to bbConfig.pickRandomShopTL()
        :raise ValueError: When given a tech level that is out of range
        """
        self.shipsStock.clear()
        self.weaponsStock.clear()
        self.modulesStock.clear()
        self.turretsStock.clear()
        # self.currentTechLevel = random.randint(bbConfig.minTechLevel, bbConfig.maxTechLevel)
        if level == -1:
            self.currentTechLevel = bbConfig.pickRandomShopTL()
        else:
            if level not in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1):
                raise ValueError("Attempted to refresh a shop at tech level " + str(level) + ". must be within the range " + str(bbConfig.minTechLevel) + " to " + str(bbConfig.maxTechLevel))
            self.currentTechLevel = level
            
        for i in range(self.maxShips):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.shipKeysByTL[itemTL - 1]) != 0:
                self.shipsStock.addItem(bbShip.bbShip.fromDict(bbData.builtInShipData[random.choice(bbData.shipKeysByTL[itemTL - 1])]))

        for i in range(self.maxModules):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.moduleObjsByTL[itemTL - 1]) != 0:
                self.modulesStock.addItem(random.choice(bbData.moduleObjsByTL[itemTL - 1]))

        for i in range(self.maxWeapons):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.weaponObjsByTL[itemTL - 1]) != 0:
                self.weaponsStock.addItem(random.choice(bbData.weaponObjsByTL[itemTL - 1]))

        # if random.randint(1, 100) <= bbConfig.turretSpawnProbability:
        for i in range(self.maxTurrets):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.turretObjsByTL[itemTL - 1]) != 0:
                self.turretsStock.addItem(random.choice(bbData.turretObjsByTL[itemTL - 1]))


    def getStockByName(self, item : str) -> bbInventory.bbInventory:
        """Get the bbInventory containing all current stock of the named type.
        This object is mutable and can alter the stock of the shop.

        :param str item: The name of the item type to fetch. Must be one of ship, weapon, module or turret
        :return: The bbInventory used by the shop to store all stock of the requested type
        :rtype: bbInventory
        :raise ValueError: When requesting an unknown item type
        :raise NotImplementedError: When requesting a valid item type, but one that is not implemented yet (e.g commodity)
        """
        if item == "all" or item not in bbConfig.validItemNames:
            raise ValueError("Invalid item type: " + item)
        if item == "ship":
            return self.shipsStock
        if item == "weapon":
            return self.weaponsStock
        if item == "module":
            return self.modulesStock
        if item == "turret":
            return self.turretsStock
        else:
            raise NotImplementedError("Valid, but unrecognised item type: " + item)


    def userCanAffordItemObj(self, user : bbUser.bbUser, item : bbItem.bbItem) -> bool:
        """Decide whether a user has enough credits to buy an item

        :param bbUser user: The user whose credits balance to check
        :param bbItem item: The item whose value to check
        :return: True if user's credits balance is greater than or equal to item's value. False otherwise
        :rtype: bool
        """
        return user.credits >= item.getValue()


    # SHIP MANAGEMENT
    def userCanAffordShipIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """Decide whether a user can afford to buy a ship from the shop's stock

        :param bbUser user: The user whose credits balance to check
        :param int index: The index of the ship whose value to check, in the shop's ship bbInventory's array of keys
        :return: True if user can afford to buy ship number index from the shop's stock, false otherwise
        :rtype: bool
        """
        return self.userCanAffordItemObj(user, self.shipsStock[index].item)


    def amountCanAffordShipObj(self, amount : int, ship : bbShip.bbShip) -> bool:
        """Decide whether amount of credits is enough to buy a ship from the shop's stock.
        This is used for checking whether a user would be able to afford a ship, if they sold their active one.

        :param int amount: The amount of credits to check against the ship's value
        :param bbShip ship: ship object whose value to check against credits
        :return: True if amount is at least as much as ship's value, false otherwise
        :rtype: bool
        """
        return amount >= ship.getValue()

    
    def amountCanAffordShipIndex(self, amount : int, index : int) -> bool:
        """Decide whether amount of credits is enough to buy the ship at the given index in the shop's stock.
        This is used for checking whether a user would be able to afford a ship, if they sold their active one.

        :param int amount: The amount of credits to check against the ship's value
        :param int index: The index of the ship whose value to check, in the shop's ship bbInventory's array of keys
        :return: True if amount is at least as much as the ship's value, false otherwise
        :rtype: bool
        """
        return self.amountCanAffordShipObj(amount, self.shipsStock[index].item)


    def userBuyShipIndex(self, user : bbUser.bbUser, index : int):
        """Sell the ship at the requested index to the given user,
        removing the appropriate balance of credits and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the ship
        :param int index: The index of the requested ship in the shop's ships bbInventory's array of keys
        """
        self.userBuyShipObj(user, self.shipsStock[index].item)
        
        
    def userBuyShipObj(self, user : bbUser.bbUser, requestedShip : bbShip.bbShip):
        """Sell the given ship to the given user,
        removing the appropriate balance of credits fromt the user and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the ship
        :param bbShip requestedWeapon: The ship to sell to user
        :raise RuntimeError: If user cannot afford to buy requestedWeapon
        """
        if self.userCanAffordItemObj(user, requestedShip):
            self.shipsStock.removeItem(requestedShip)
            user.credits -= requestedShip.getValue()
            user.inactiveShips.addItem(requestedShip)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy ship " + requestedShip.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedShip.getValue()))


    def userSellShipObj(self, user : bbUser.bbUser, ship : bbShip.bbShip):
        """Buy the given ship from the given user,
        adding the appropriate credits to their balance and adding the ship to the shop stock.

        :param bbUser user: The user to buy ship from
        :param bbShip weapon: The ship to buy from user
        """
        user.credits += ship.getValue()
        self.shipsStock.addItem(ship)
        user.inactiveShips.removeItem(ship)
    

    def userSellShipIndex(self, user : bbUser.bbUser, index : int):
        """Buy the weapon at the given index in the given user's ships bbInventory,
        adding the appropriate credits to their balance and adding the ship to the shop stock.

        :param bbUser user: The user to buy ship from
        :param int index: The index of the weapon to buy from user, in the user's ships bbInventory's array of keys
        """
        self.userSellShipObj(user, user.inactiveShips[index].item)


    
    # WEAPON MANAGEMENT
    def userCanAffordWeaponIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """Decide whether a user can afford to buy a weapon from the shop's stock

        :param bbUser user: The user whose credits balance to check
        :param int index: The index of the weapon whose value to check, in the shop's weapon bbInventory's array of keys
        :return: True if user can afford to buy weapon number index from the shop's stock, false otherwise
        :rtype: bool
        """
        return self.userCanAffordItemObj(user, self.weaponsStock[index].item)


    def userBuyWeaponIndex(self, user : bbUser.bbUser, index : int):
        """Sell the weapon at the requested index to the given user,
        removing the appropriate balance of credits and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the weapon
        :param int index: The index of the requested weapon in the shop's weapons bbInventory's array of keys
        """
        self.userBuyWeaponObj(user, self.weaponsStock[index].item)
        

    def userBuyWeaponObj(self, user : bbUser.bbUser, requestedWeapon : bbWeapon.bbWeapon):
        """Sell the given weapon to the given user,
        removing the appropriate balance of credits fromt the user and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the weapon
        :param bbWeapon requestedWeapon: The weapon to sell to user
        :raise RuntimeError: If user cannot afford to buy requestedWeapon
        """
        if self.userCanAffordItemObj(user, requestedWeapon):
            self.weaponsStock.removeItem(requestedWeapon)
            user.credits -= requestedWeapon.getValue()
            user.inactiveShips.addItem(requestedWeapon)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy weapon " + requestedWeapon.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedWeapon.getValue()))


    def userSellWeaponObj(self, user : bbUser.bbUser, weapon : bbWeapon.bbWeapon):
        """Buy the given weapon from the given user,
        adding the appropriate credits to their balance and adding the weapon to the shop stock.

        :param bbUser user: The user to buy weapon from
        :param bbWeapon weapon: The weapon to buy from user
        """
        user.credits += weapon.getValue()
        self.weaponsStock.addItem(weapon)
        user.inactiveWeapons.removeItem(weapon)
    

    def userSellWeaponIndex(self, user : bbUser.bbUser, index : int):
        """Buy the weapon at the given index in the given user's weapons bbInventory,
        adding the appropriate credits to their balance and adding the weapon to the shop stock.

        :param bbUser user: The user to buy weapon from
        :param int index: The index of the weapon to buy from user, in the user's weapons bbInventory's array of keys
        """
        self.userSellWeaponObj(user, user.inactiveWeapons[index].item)


    
    # MODULE MANAGEMENT
    def userCanAffordModuleIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """Decide whether a user can afford to buy a module from the shop's stock

        :param bbUser user: The user whose credits balance to check
        :param int index: The index of the module whose value to check, in the shop's module bbInventory's array of keys
        :return: True if user can afford to buy module number index from the shop's stock, false otherwise
        :rtype: bool
        """
        return self.userCanAffordItemObj(user, self.modulesStock[index].item)


    def userBuyModuleIndex(self, user : bbUser.bbUser, index : int):
        """Sell the module at the requested index to the given user,
        removing the appropriate balance of credits and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the module
        :param int index: The index of the requested module in the shop's modules bbInventory's array of keys
        """
        self.userBuyModuleObj(user, self.modulesStock[index].item)
        

    def userBuyModuleObj(self, user : bbUser.bbUser, requestedModule : bbModule.bbModule):
        """Sell the given module to the given user,
        removing the appropriate balance of credits fromt the user and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the module
        :param bbModule requestedModule: The module to sell to user
        :raise RuntimeError: If user cannot afford to buy requestedModule
        """
        if self.userCanAffordItemObj(user, requestedModule):
            self.modulesStock.removeItem(requestedModule)
            user.credits -= requestedModule.getValue()

            user.inactiveShips.addItem(requestedModule)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy module " + requestedModule.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedModule.getValue()))


    def userSellModuleObj(self, user : bbUser.bbUser, module : bbModule.bbModule):
        """Buy the given module from the given user,
        adding the appropriate credits to their balance and adding the module to the shop stock.

        :param bbUser user: The user to buy module from
        :param bbModule module: The module to buy from user
        """
        user.credits += module.getValue()
        self.modulesStock.addItem(module)
        user.inactiveModules.removeItem(module)
    

    def userSellModuleIndex(self, user : bbUser.bbUser, index : int):
        """Buy the module at the given index in the given user's modules bbInventory,
        adding the appropriate credits to their balance and adding the module to the shop stock.

        :param bbUser user: The user to buy module from
        :param int index: The index of the module to buy from user, in the user's modules bbInventory's array of keys
        """
        self.userSellModuleObj(user, user.inactiveModules[index].item)



    # TURRET MANAGEMENT
    def userCanAffordTurretIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """Decide whether a user can afford to buy a turret from the shop's stock

        :param bbUser user: The user whose credits balance to check
        :param int index: The index of the turret whose value to check, in the shop's turret bbInventory's array of keys
        :return: True if user can afford to buy turret number index from the shop's stock, false otherwise
        :rtype: bool
        """
        return self.userCanAffordItemObj(user, self.turretsStock[index].item)


    def userBuyTurretIndex(self, user : bbUser.bbUser, index : int):
        """Sell the turret at the requested index to the given user,
        removing the appropriate balance of credits and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the turret
        :param int index: The index of the requested turret in the shop's turrets bbInventory's array of keys
        """
        self.userBuyTurretObj(user, self.turretsStock[index].item)
        
        
    def userBuyTurretObj(self, user : bbUser.bbUser, requestedTurret : bbTurret.bbTurret):
        """Sell the given turret to the given user,
        removing the appropriate balance of credits fromt the user and adding the item into the user's inventory.

        :param bbUser user: The user attempting to buy the turret
        :param bbTurret requestedTurret: The turret to sell to user
        :raise RuntimeError: If user cannot afford to buy requestedTurret
        """
        if self.userCanAffordItemObj(user, requestedTurret):
            self.turretsStock.removeItem(requestedTurret)
            user.credits -= requestedTurret.getValue()
            user.inactiveShips.addItem(requestedTurret)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy turret " + requestedTurret.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedTurret.getValue()))


    def userSellTurretObj(self, user : bbUser.bbUser, turret : bbTurret.bbTurret):
        """Buy the given turret from the given user,
        adding the appropriate credits to their balance and adding the turret to the shop stock.

        :param bbUser user: The user to buy turret from
        :param bbTurret turret: The turret to buy from user
        """
        user.credits += turret.getValue()
        self.turretsStock.addItem(turret)
        user.inactiveTurrets.removeItem(turret)
    

    def userSellTurretIndex(self, user : bbUser.bbUser, index : int):
        """Buy the turret at the given index in the given user's turrets bbInventory,
        adding the appropriate credits to their balance and adding the turret to the shop stock.

        :param bbUser user: The user to buy turret from
        :param int index: The index of the turret to buy from user, in the user's turrets bbInventory's array of keys
        """
        self.userSellTurretObj(user, user.inactiveTurrets[index].item)



    def toDict(self, **kwargs) -> dict:
        """Get a dictionary containing all information needed to reconstruct this shop instance.
        This includes maximum item counts, current tech level, and current stocks.

        :return: A dictionary containing all information needed to reconstruct this shop object
        :rtype: dict
        """
        shipsStockDict = []
        for ship in self.shipsStock.keys:
            if ship in self.shipsStock.items:
                shipsStockDict.append(self.shipsStock.items[ship].toDict(**kwargs))
            else:
                bbLogger.log("bbShp", "toDict", "Failed to save invalid ship key '" + str(ship) + "' - not found in items dict", category="shop", eventType="UNKWN_KEY")

        weaponsStockDict = []
        for weapon in self.weaponsStock.keys:
            if weapon in self.weaponsStock.items:
                weaponsStockDict.append(self.weaponsStock.items[weapon].toDict(**kwargs))
            else:
                bbLogger.log("bbShp", "toDict", "Failed to save invalid weapon key '" + str(weapon) + "' - not found in items dict", category="shop", eventType="UNKWN_KEY")

        modulesStockDict = []
        for module in self.modulesStock.keys:
            if module in self.modulesStock.items:
                modulesStockDict.append(self.modulesStock.items[module].toDict(**kwargs))
            else:
                bbLogger.log("bbShp", "toDict", "Failed to save invalid module key '" + str(module) + "' - not found in items dict", category="shop", eventType="UNKWN_KEY")

        turretsStockDict = []
        for turret in self.turretsStock.keys:
            if turret in self.turretsStock.items:
                turretsStockDict.append(self.turretsStock.items[turret].toDict(**kwargs))
            else:
                bbLogger.log("bbShp", "toDict", "Failed to save invalid turret key '" + str(turret) + "' - not found in items dict", category="shop", eventType="UNKWN_KEY")

        return {"maxShips":self.maxShips, "maxWeapons":self.maxWeapons, "maxModules":self.maxModules, "currentTechLevel":self.currentTechLevel,
                    "shipsStock":shipsStockDict, "weaponsStock":weaponsStockDict, "modulesStock":modulesStockDict, "turretsStock":turretsStockDict}


    @classmethod
    def fromDict(cls, shopDict : dict, **kwargs) -> bbShop:
        """Recreate a bbShop instance from its dictionary-serialized representation - the opposite of bbShop.toDict
        
        :param dict shopDict: A dictionary containing all information needed to construct the shop
        :return: A new bbShop object as described by shopDict
        :rtype: bbShop
        """
        shipsStock = bbInventory.bbInventory()
        for shipListingDict in shopDict["shipsStock"]:
            shipsStock.addItem(bbShip.bbShip.fromDict(shipListingDict["item"]), quantity=shipListingDict["count"])

        weaponsStock = bbInventory.bbInventory()
        for weaponListingDict in shopDict["weaponsStock"]:
            weaponsStock.addItem(bbWeapon.bbWeapon.fromDict(weaponListingDict["item"]), quantity=weaponListingDict["count"])

        modulesStock = bbInventory.bbInventory()
        for moduleListingDict in shopDict["modulesStock"]:
            modulesStock.addItem(bbModuleFactory.fromDict(moduleListingDict["item"]), quantity=moduleListingDict["count"])

        turretsStock = bbInventory.bbInventory()
        for turretListingDict in shopDict["turretsStock"]:
            turretsStock.addItem(bbTurret.bbTurret.fromDict(turretListingDict["item"]), quantity=turretListingDict["count"])

        return bbShop(shopDict["maxShips"], shopDict["maxWeapons"], shopDict["maxModules"], currentTechLevel=shopDict["currentTechLevel"] if "currentTechLevel" in shopDict else 1,
                        shipsStock=shipsStock, weaponsStock=weaponsStock, modulesStock=modulesStock, turretsStock=turretsStock)
