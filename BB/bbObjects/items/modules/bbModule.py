from ..bbItem import bbItem, spawnableItem
from ....bbConfig import bbData
from .... import lib
from typing import List

@spawnableItem
class bbModule(bbItem):
    """"An equippable item, providing ships with various stat perks and new functionality.
    All, none, or any combination of a bbModule's attributes may be populated.

    :var armour: Provides an extra layer of health points ships must fight through before they can damage the ship's hull
    :vartype armour: int
    :var armourMultiplier: A percentage multiplier applied to the capacity of the ship's already active armour
    :vartype armourMultiplier: float
    :var shield: Provides another extra layer of health points ships must fight through before they can damage the ship's hull
    :vartype shield: int
    :var shieldMultiplier: A percentage multiplier applied to the capacity of the ship's already active shield
    :vartype shieldMultiplier: float
    :var dps: Provides an extra outlet of damage which can be directed towards a target. This one is unused as of yet, but you never know.
    :vartype dps: int
    :var dpsMultiplier: A percentage multiplier applied to the dps of all primary weapons equipped on the ship
    :vartype dpsMultiplier: float
    :var cargo: An additive increase to the amount of storage space available on the ship
    :vartype cargo: int
    :var cargoMultiplier: A multiplicative increase to the amount of storage space available on the ship
    :vartype cargoMultiplier: float
    :var handling: Provides an additive boost to the driveability of a ship (controls sensitivity)
    :vartype handling: int
    :var handlingMultiplier: A percentage multiplier applied to the ship's base handling
    :vartype handlingMultiplier: float
    """

    def __init__(self, name: str, aliases : List[str], armour : int = 0,
            armourMultiplier : float = 1.0, shield : int = 0, shieldMultiplier : float = 1.0,
            dps : int = 0, dpsMultiplier : float = 1.0, cargo : int = 0,
            cargoMultiplier : float = 1.0, handling : int = 0, handlingMultiplier : float = 1.0,
            value : int = 0, wiki : str = "", manufacturer : str = "", icon : str = "",
            emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY, techLevel : int = -1,
            builtIn : bool = False):
        """
        :param str name: The name of the module. Must be unique. (a model number is a good starting point)
        :param list[str] aliases: A list of alternative names this module may be referred to by.
        :param int armour: Provides an extra layer of health points ships must fight through before they can damage the ship's hull (Default 0)
        :param float armourMultiplier: A percentage multiplier applied to the capacity of the ship's already active armour (Default 1)
        :param int shield: Provides another extra layer of health points ships must fight through before they can damage the ship's hull (Default 0)
        :param float shieldMultiplier: A percentage multiplier applied to the capacity of the ship's already active shield (Default 1)
        :param int dps: Provides an extra outlet of damage which can be directed towards a target. This one is unused as of yet, but you never know. (Default 0)
        :param float dpsMultiplier: A percentage multiplier applied to the dps of all primary weapons equipped on the ship (Default 1)
        :param int cargo: An additive increase to the amount of storage space available on the ship (Default 0)
        :param float cargoMultiplier: A multiplicative increase to the amount of storage space available on the ship (Default 1)
        :param int handling: Provides an additive boost to the driveability of a ship (controls sensitivity) (Default 0)
        :param float handlingMultiplier: A percentage multiplier applied to the ship's base handling (Default 1)
        :param int value: The number of credits that this module can be bought/sold for at a shop. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this module. (Default "")
        :param str manufacturer: The name of the manufacturer of this module (Default "")
        :param str icon: A URL pointing to an image to use for this module's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this module's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other modules of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard module (loaded in from bbData) or a custom spawned module (Default False)
        """
        super(bbModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)
        self.armour = armour
        self.armourMultiplier = armourMultiplier
        self.shield = shield
        self.shieldMultiplier = shieldMultiplier
        self.dps = dps
        self.dpsMultiplier = dpsMultiplier
        self.cargo = cargo
        self.cargoMultiplier = cargoMultiplier
        self.handling = handling
        self.handlingMultiplier = handlingMultiplier

    
    def statsStringShort(self) -> str:
        """Summarise all effects of this module as a string.
        This method should be overriden in any modules that implement custom behaviour, outside of simple stat boosts.

        :return: A string summarising the effects of this module when equipped to a ship
        :rtype: str
        """
        stats = "*"
        if self.armour != 0:
            stats += "Armour: " + ("+" if self.armourMultiplier > 0 else "-") + str(self.armour) + ", "
        if self.armourMultiplier != 1:
            stats += "Armour: " + ("+" if self.armourMultiplier >= 1 else "-") + str(round(((self.armourMultiplier - 1) * 100) if self.armourMultiplier > 1 else (self.armourMultiplier * 100))) + "%, "
        if self.shield != 0:
            stats += "Shield: " + ("+" if self.shield > 0 else "-") + str(self.shield) + ", "
        if self.shieldMultiplier != 1:
            stats += "Shield: " + ("+" if self.shieldMultiplier >= 1 else "-") + str(round(((self.shieldMultiplier - 1) * 100) if self.shieldMultiplier > 1 else (self.shieldMultiplier * 100))) + "%, "
        if self.dps != 0:
            stats += "Dps: " + ("+" if self.dps > 0 else "-") + str(self.dps) + ", "
        if self.dpsMultiplier != 1:
            stats += "Dps: " + ("+" if self.dpsMultiplier >= 1 else "-") + str(round(((self.dpsMultiplier - 1) * 100) if self.dpsMultiplier > 1 else (self.dpsMultiplier * 100))) + "%, "
        if self.cargo != 0:
            stats += "Cargo: " + ("+" if self.cargo > 0 else "-") + str(self.cargo) + ", "
        if self.cargoMultiplier != 1:
            stats += "Cargo: " + ("+" if self.cargoMultiplier >= 1 else "-") + str(round(((self.cargoMultiplier - 1) * 100) if self.cargoMultiplier > 1 else (self.cargoMultiplier * 100))) + "%, "
        if self.handling != 0:
            stats += "Handling: " + ("+" if self.handling > 0 else "-") + str(((1 - self.handling) * 100) if self.handling > 1 else (self.handling * 100)) + ", "
        if self.handlingMultiplier != 1:
            stats += "Handling: " + ("+" if self.handlingMultiplier >= 1 else "-") + str(round(((self.handlingMultiplier - 1) * 100) if self.handlingMultiplier > 1 else (self.handlingMultiplier * 100))) + "%, "

        return (stats[:-2] + "*") if stats != "*" else "*No effect*"

    
    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbModule class
        :rtype: type
        """
        return bbModule

    
    def toDict(self, **kwargs) -> dict:
        """Serialize this bbModule into dictionary format, for saving to file.
        This method should be overriden and used as a base in any modules that implement custom behaviour, outside of simple stat boosts.
        For an example of using this toDict implementation as a base for an overriden implementation, please see a bbModule class (e.g bbMiningDrillModule.py)

        :param bool saveType: When true, include the string name of the object type in the output.
        :return: A dictionary containing all information needed to reconstruct this module. If the module is builtIn, this is only its name.
        :rtype: dict
        """
        itemDict = super(bbModule, self).toDict(**kwargs)
        
        if not self.builtIn:
            if self.armour != 0.0:
                itemDict["armour"] = self.armour

            if self.armourMultiplier != 1.0:
                itemDict["armourMultiplier"] = self.armourMultiplier

            if self.shield != 0.0:
                itemDict["shield"] = self.shield

            if self.shieldMultiplier != 1.0:
                itemDict["shieldMultiplier"] = self.shieldMultiplier

            if self.dps != 0.0:
                itemDict["dps"] = self.dps

            if self.dpsMultiplier != 1.0:
                itemDict["dpsMultiplier"] = self.dpsMultiplier

            if self.cargo != 1.0:
                itemDict["cargo"] = self.cargo

            if self.cargoMultiplier != 1.0:
                itemDict["cargoMultiplier"] = self.cargoMultiplier

            if self.handling != 0:
                itemDict["handling"] = self.handling

            if self.handlingMultiplier != 1.0:
                itemDict["handlingMultiplier"] = self.handlingMultiplier

        return itemDict


    @classmethod
    def fromDict(cls, moduleDict : dict, **kwargs):
        """Factory function constructing a new bbModule object from a dictionary serialised representation - the opposite of bbModule.toDict.
        This generic module factory function is unlikely to ever be called, your module type-specific fromDict should be used instead.
        Except of course, in the case of custom-spawned, custom-typed modules which do not correspond to a BountyBot-known module type.
        
        :param dict moduleDict: A dictionary containing all information needed to construct the desired bbModule
        :return: A new bbModule object as described in moduleDict
        :rtype: bbModule
        """
        return bbModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], armour=moduleDict["armour"] if "armour" in moduleDict else 0,
                        armourMultiplier=moduleDict["armourMultiplier"] if "armourMultiplier" in moduleDict else 1, shield=moduleDict["shield"] if "shield" in moduleDict else 0,
                        shieldMultiplier=moduleDict["shieldMultiplier"] if "shieldMultiplier" in moduleDict else 1, dps=moduleDict["dps"] if "dps" in moduleDict else 0,
                        dpsMultiplier=moduleDict["dpsMultiplier"] if "dpsMultiplier" in moduleDict else 1, cargo=moduleDict["cargo"] if "cargo" in moduleDict else 0,
                        cargoMultiplier=moduleDict["cargoMultiplier"] if "cargoMultiplier" in moduleDict else 1, handling=moduleDict["handling"] if "handling" in moduleDict else 0,
                        handlingMultiplier=moduleDict["handlingMultiplier"] if "handlingMultiplier" in moduleDict else 1, value=moduleDict["value"] if "value" in moduleDict else 0,
                        wiki=moduleDict["wiki"] if "wiki" in moduleDict else "", manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                        emoji=lib.emojis.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else lib.emojis.dumbEmoji.EMPTY, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
