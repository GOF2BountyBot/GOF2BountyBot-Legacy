# Typing imports
from __future__ import annotations

from ...bbConfig import bbData
from . import bbShip
from ...baseClasses import bbSerializable


class bbShipUpgrade(bbSerializable.bbSerializable):
    """A ship upgrade that can be applied to bbShips, but cannot be unapplied again.
    There is no technical reason why a ship upgrade could not be removed, but from a game design perspective, it adds extra value and strategy to the decision to apply an upgrade.

    :var wiki: A web page to present as the upgrade's wikipedia article in its info page
    :vartype wiki: str
    :var hasWiki: Whether or not this upgrade's wiki attribute is populated
    :vartype hasWiki: bool
    :var name: The name of the upgrade. This must be unique.
    :vartype name: str
    :var shipToUpgradeValueMult: upgrades do not have a value, their value is calculated as a percentage of the value of the ship to be applied to. shipToUpgradeValueMult is that percentage multiplier.
    :vartype shipToUpgradeValueMult: float
    :var vendor: The manufacturer of this upgrade.
    :vartype vendor: str
    :var hasVendor: Whether or not this upgrade's vendor attribute is populated
    :vartype hasVendor: bool
    :var armour: An additive boost to the owning ship's armour
    :vartype armour: int
    :var armourMultiplier: A multiplier to apply to the ship's armour
    :vartype armourMultiplier: float
    :var cargo: An additive boost to the owning ship's cargo storage
    :vartype cargo: int
    :var cargoMultiplier: A multiplier to apply to the ship's cargo storage
    :vartype cargoMultiplier: float
    :var numSecondaries: An additive boost to the number of secondary weapons equippable by the owning ship
    :vartype numSecondaries: int
    :var numSecondariesMultiplier: A multiplier to apply to the number of secondary weapons equippable by the ship
    :vartype numSecondariesMultiplier: float
    :var handling: An additive boost to the owning ship's handling
    :vartype handling: int
    :var handlingMultiplier: A multiplier to apply to the ship's handling
    :vartype handlingMultiplier: float
    :var maxPrimaries: An additive boost to the number of primary weapons equippable by the owning ship
    :vartype maxPrimaries: int
    :var maxPrimariesMultiplier: A multiplier to apply to the number of primary weapons equippable by the ship
    :vartype maxPrimariesMultiplier: float
    :var maxTurrets: An additive boost to the maximum number of turrets equippable by the owning ship
    :vartype maxTurrets: int
    :var maxTurretsMultiplier: A multiplier to apply to the maximum number of turrets equippable by the ship
    :vartype maxTurretsMultiplier: float
    :var maxModules: An additive boost to the number of modules that the owning ship can equip
    :vartype maxModules: int
    :var maxModulesMultiplier: A multiplier to apply to the number of modules that the ship can equip
    :vartype maxModulesMultiplier: float
    :var techLevel: A rating from 1 to 10 of this upgrade's technological advancement. Used as a reference to compare against other ship upgrades.
    :vartype techLevel: int
    :var hasTechLevel: whether or not this ship upgrade has a tech level
    :vartype hasTechLevel: bool
    :var builtIn: Whether this upgrade is built into BountyBot (loaded in from bbData) or was custom spawned.
    :vartype builtIn: bool
    """
    
    def __init__(self, name : str, shipToUpgradeValueMult : float,
                    armour : int = 0.0, armourMultiplier : float = 1.0, cargo : int = 0, cargoMultiplier : float = 1.0, numSecondaries : int = 0, numSecondariesMultiplier : float = 1.0,
                    handling : int = 0, handlingMultiplier : float = 1.0, maxPrimaries : int = 0, maxPrimariesMultiplier : float = 1.0, maxTurrets : int = 0, maxTurretsMultiplier : float = 1.0,
                    maxModules : int = 0, maxModulesMultiplier : float = 1.0, vendor : str = "", wiki : str = "", techLevel : int = -1, builtIn : bool = False):
        """
        :param str name: The name of the upgrade. This must be unique.
        :param float shipToUpgradeValueMult: upgrades do not have a value, their value is calculated as a percentage of the value of the ship to be applied to. shipToUpgradeValueMult is that percentage multiplier.
        :param str wiki: A web page to present as the upgrade's wikipedia article in its info page
        :param str vendor: The manufacturer of this upgrade.
        :param int armour: An additive boost to the owning ship's armour
        :param float armourMultiplier: A multiplier to apply to the ship's armour
        :param int cargo: An additive boost to the owning ship's cargo storage
        :param float cargoMultiplier: A multiplier to apply to the ship's cargo storage
        :param int numSecondaries: An additive boost to the number of secondary weapons equippable by the owning ship
        :param float numSecondariesMultiplier: A multiplier to apply to the number of secondary weapons equippable by the ship
        :param int handling: An additive boost to the owning ship's handling
        :param float handlingMultiplier: A multiplier to apply to the ship's handling
        :param int maxPrimaries: An additive boost to the number of primary weapons equippable by the owning ship
        :param float maxPrimariesMultiplier: A multiplier to apply to the number of primary weapons equippable by the ship
        :param int maxTurrets: An additive boost to the maximum number of turrets equippable by the owning ship
        :param float maxTurretsMultiplier: A multiplier to apply to the maximum number of turrets equippable by the ship
        :param int maxModules: An additive boost to the number of modules that the owning ship can equip
        :param float maxModulesMultiplier: A multiplier to apply to the number of modules that the ship can equip
        :param int techLevel: A rating from 1 to 10 of this upgrade's technological advancement. Used as a reference to compare against other ship upgrades.
        :param bool builtIn: Whether this upgrade is built into BountyBot (loaded in from bbData) or was custom spawned.
        """
        self.name = name
        self.shipToUpgradeValueMult = shipToUpgradeValueMult
        self.vendor = vendor
        self.hasVendor = vendor != ""

        self.armour = armour
        self.armourMultiplier = armourMultiplier

        self.cargo = cargo
        self.cargoMultiplier = cargoMultiplier

        self.numSecondaries = numSecondaries
        self.numSecondariesMultiplier = numSecondariesMultiplier

        self.handling = handling
        self.handlingMultiplier = handlingMultiplier

        self.maxPrimaries = maxPrimaries
        self.maxPrimariesMultiplier = maxPrimariesMultiplier
        
        self.maxTurrets = maxTurrets
        self.maxTurretsMultiplier = maxTurretsMultiplier

        self.maxModules = maxModules
        self.maxModulesMultiplier = maxModulesMultiplier

        self.wiki = wiki
        self.hasWiki = wiki != ""

        self.techLevel = techLevel
        self.hasTechLevel = techLevel != -1

        self.builtIn = builtIn


    def __eq__(self, other : bbShipUpgrade) -> bool:
        """Decide whether two ship upgrades are the same, based purely on their name and object type.

        :param bbShipUpgrade other: The upgrade to compare this one against.
        :return: True if other is a bbShipUpgrade instance, and shares the same name as this upgrade
        :rtype: bool
        """
        return type(self) == type(other) and self.name == other.name

    
    def valueForShip(self, ship : bbShip.bbShip) -> int:
        """Calculate the value of this ship upgrade, when it is to be applied to the given ship

        :param bbShip ship: The ship that the upgrade is to be applied to
        :return: The number of credits at which this upgrade is valued when being applied to ship
        :rtype: int
        """
        return ship.value * self.shipToUpgradeValueMult

    
    def toDict(self, **kwargs) -> dict:
        """Serialize this bbShipUpgrade into a dictionary for saving to file
        Contains all information needed to reconstruct this upgrade. If the upgrade is builtIn, this includes only the upgrade name.

        :return: A dictionary-serialized representation of this upgrade
        :rtype: dict
        """
        itemDict = {"name": self.name, "builtIn": self.builtIn}

        if not self.builtIn:
            if self.hasVendor:
                itemDict["vendor"] = self.vendor

            if self.shipToUpgradeValueMult != 1.0:
                itemDict["shipToUpgradeValueMult"] = self.shipToUpgradeValueMult

            if self.armour != 0.0:
                itemDict["armour"] = self.armour

            if self.armourMultiplier != 1.0:
                itemDict["armourMultiplier"] = self.armourMultiplier

            if self.cargo != 1.0:
                itemDict["cargo"] = self.cargo

            if self.cargoMultiplier != 1.0:
                itemDict["cargoMultiplier"] = self.cargoMultiplier

            if self.numSecondaries != 0:
                itemDict["numSecondaries"] = self.numSecondaries

            if self.numSecondariesMultiplier != 1.0:
                itemDict["numSecondariesMultiplier"] = self.numSecondariesMultiplier

            if self.handling != 0:
                itemDict["handling"] = self.handling

            if self.handlingMultiplier != 1.0:
                itemDict["handlingMultiplier"] = self.handlingMultiplier

            if self.maxPrimaries != 0:
                itemDict["maxPrimaries"] = self.maxPrimaries

            if self.maxPrimariesMultiplier != 1.0:
                itemDict["maxPrimariesMultiplier"] = self.maxPrimariesMultiplier

            if self.maxTurrets != 0:
                itemDict["maxTurrets"] = self.maxTurrets

            if self.maxTurretsMultiplier != 1.0:
                itemDict["maxTurretsMultiplier"] = self.maxTurretsMultiplier

            if self.maxModules != 0:
                itemDict["maxModules"] = self.maxModules

            if self.maxModulesMultiplier != 1.0:
                itemDict["maxModulesMultiplier"] = self.maxModulesMultiplier

        return itemDict

    
    def statsStringShort(self) -> str:
        """Get a summary of the effects this upgrade will have on the owning ship, in string format.

        :return: A string summary of the upgrade's effects
        :rtype: str
        """
        stats = "*"
        if self.armour != 0:
            stats += "Armour: " + ("+" if self.armour > 0 else "-") + str(self.armour) + ", "
        if self.armourMultiplier != 1:
            stats += "Armour: " + ("+" if self.armourMultiplier > 1 else "-") + str(round(((self.armourMultiplier - 1) * 100) if self.armourMultiplier > 1 else (self.armourMultiplier * 100))) + ", "

        if self.cargo != 0:
            stats += "Cargo: " + ("+" if self.cargo > 0 else "-") + str(self.cargo) + ", "
        if self.cargoMultiplier != 1:
            stats += "Cargo: " + ("+" if self.cargoMultiplier > 1 else "-") + str(round(((self.cargoMultiplier - 1) * 100) if self.cargoMultiplier > 1 else (self.cargoMultiplier * 100))) + ", "

        if self.numSecondaries != 0:
            stats += "Max secondaries: " + ("+" if self.numSecondaries > 0 else "-") + str(self.numSecondaries) + ", "
        if self.numSecondariesMultiplier != 1:
            stats += "Max secondaries: " + ("+" if self.numSecondariesMultiplier > 1 else "-") + str(round(((self.numSecondariesMultiplier - 1) * 100) if self.numSecondariesMultiplier > 1 else (self.numSecondariesMultiplier * 100))) + ", "

        if self.handling != 0:
            stats += "Handling: " + ("+" if self.handling > 0 else "-") + str(self.handling) + ", "
        if self.handlingMultiplier != 1:
            stats += "Handling: " + ("+" if self.handlingMultiplier > 1 else "-") + str(round(((self.handlingMultiplier - 1) * 100) if self.handlingMultiplier > 1 else (self.handlingMultiplier * 100))) + ", "

        if self.maxPrimaries != 0:
            stats += "Max primaries: " + ("+" if self.maxPrimaries > 0 else "-") + str(self.maxPrimaries) + ", "
        if self.maxPrimariesMultiplier != 1:
            stats += "Max primaries: " + ("+" if self.maxPrimariesMultiplier > 1 else "-") + str(round(((self.maxPrimariesMultiplier - 1) * 100) if self.maxPrimariesMultiplier > 1 else (self.maxPrimariesMultiplier * 100))) + ", "
        
        if self.maxTurrets != 0:
            stats += "Max turrets: " + ("+" if self.maxTurrets > 0 else "-") + str(self.maxTurrets) + ", "
        if self.maxTurretsMultiplier != 1:
            stats += "Max turrets: " + ("+" if self.maxTurretsMultiplier > 1 else "-") + str(round(((self.maxTurretsMultiplier - 1) * 100) if self.maxTurretsMultiplier > 1 else (self.maxTurretsMultiplier * 100))) + ", "

        if self.maxModules != 0:
            stats += "Max modules: " + ("+" if self.maxModules > 0 else "-") + str(self.maxModules) + ", "
        if self.maxModulesMultiplier != 1:
            stats += "Max modules: " + ("+" if self.maxModulesMultiplier > 1 else "-") + str(round(((self.maxModulesMultiplier - 1) * 100) if self.maxModulesMultiplier > 1 else (self.maxModulesMultiplier * 100))) + ", "

        return (stats[:-2] + "*") if stats != "*" else "*No effect*"


    @classmethod
    def fromDict(cls, upgradeDict : dict, **kwargs) -> bbShipUpgrade:
        """Factory function reconstructing a bbShipUpgrade object from its dictionary-serialized representation. The opposite of bbShipUpgrade.toDict
        If the upgrade is builtIn, return a reference to the pre-constructed upgrade object.

        :param dict upgradeDict: A dictionary containing all information needed to produce the required bbShipUpgrade
        :return: A bbShipUpgrade object as described by upgradeDict
        :rtype: bbShipUpgrade
        """
        if upgradeDict["builtIn"]:
            return bbData.builtInUpgradeObjs[upgradeDict["name"]]
        else:
            return bbShipUpgrade(upgradeDict["name"], upgradeDict["shipToUpgradeValueMult"], armour=upgradeDict["armour"] if "armour" in upgradeDict else 0.0,
                                    armourMultiplier=upgradeDict["armourMultiplier"] if "armourMultiplier" in upgradeDict else 1.0,
                                    cargo=upgradeDict["cargo"] if "cargo" in upgradeDict else 0,
                                    cargoMultiplier=upgradeDict["cargoMultiplier"] if "cargoMultiplier" in upgradeDict else 1.0,
                                    numSecondaries=upgradeDict["numSecondaries"] if "numSecondaries" in upgradeDict else 0,
                                    numSecondariesMultiplier=upgradeDict["numSecondariesMultiplier"] if "numSecondariesMultiplier" in upgradeDict else 1.0,
                                    handling=upgradeDict["handling"] if "handling" in upgradeDict else 0,
                                    handlingMultiplier=upgradeDict["handlingMultiplier"] if "handlingMultiplier" in upgradeDict else 1.0,
                                    maxPrimaries=upgradeDict["maxPrimaries"] if "maxPrimaries" in upgradeDict else 0,
                                    maxPrimariesMultiplier=upgradeDict["maxPrimariesMultiplier"] if "maxPrimariesMultiplier" in upgradeDict else 1.0,
                                    maxTurrets=upgradeDict["maxTurrets"] if "maxTurrets" in upgradeDict else 0,
                                    maxTurretsMultiplier=upgradeDict["maxTurretsMultiplier"] if "maxTurretsMultiplier" in upgradeDict else 1.0,
                                    maxModules=upgradeDict["maxModules"] if "maxModules" in upgradeDict else 0,
                                    maxModulesMultiplier=upgradeDict["maxModulesMultiplier"] if "maxModulesMultiplier" in upgradeDict else 1.0,
                                    vendor=upgradeDict["vendor"] if "vendor" in upgradeDict else "",
                                    builtIn=False)
