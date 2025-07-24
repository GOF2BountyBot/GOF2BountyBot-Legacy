from __future__ import annotations
from . import bbToolItem
from .... import lib
from ....bbConfig import bbConfig, bbData
from .. import bbShipUpgrade
from ..bbShip import bbShip
from discord import Message
from .... import bbGlobals
import asyncio
from ..bbItem import spawnableItem
from ....reactionMenus.ConfirmationReactionMenu import InlineConfirmationMenu
from typing import cast


@spawnableItem
class bbShipUpgradeTool(bbToolItem.bbToolItem):
    """A tool that can be used to apply an upgrade to a ship.
    This tool is single use. If a calling user is given, the tool is removed from that user's inventory after use.
    """
    def __init__(self, upgrade : bbShipUpgrade.bbShipUpgrade, value : int = 0, wiki : str = "", icon : str = bbConfig.defaultShipUpgradeToolIcon,
            emoji : lib.emojis.dumbEmoji = None, techLevel : int = -1, builtIn : bool = False, autoUse : bool = False):
        """
        :param bbShipUpgrade upgrade: The upgrade that this tool applies.
        :param int value: The number of credits that this item can be bought/sold for at a shop. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this item. If no wiki is given and upgrade has one, that will be used instead. (Default "")
        :param str icon: A URL pointing to an image to use for this item's icon (Default bbConfig.defaultShipUpgradeToolIcon)
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this item's small icon (Default bbConfig.defaultShipUpgradeToolEmoji)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other items of the same type (Default upgrade.techLevel)
        :param bool builtIn: Whether this is a BountyBot standard item (loaded in from bbData) or a custom spawned item (Default False)
        """
        if emoji is None:
            emoji = bbConfig.defaultShipUpgradeToolEmoji
        super().__init__(f"Ship upgrade: {upgrade.name}", [], value=value, wiki=wiki if wiki else upgrade.wiki if upgrade.hasWiki else "", icon=icon, emoji=emoji, techLevel=techLevel if techLevel > -1 else upgrade.techLevel, builtIn=builtIn, autoUse=autoUse)
        self.upgrade = upgrade

    
    async def use(self, *args, **kwargs):
        """Apply the upgrade to the given ship.
        After use, the tool will be removed from callingBBUser's inventory. To disable this, pass callingBBUser as None.
        """
        if "ship" not in kwargs:
            raise NameError("Required kwarg not given: ship")
        if not isinstance(kwargs["ship"], bbShip):
            raise TypeError("Required kwarg is of the wrong type. Expected bbShip, received " + kwargs["ship"].__class__.__name__)
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        if kwargs["callingBBUser"] is not None and kwargs["callingBBUser"].__class__.__name__ != "bbUser":
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        ship, callingBBUser = cast(bbShip, kwargs["ship"]), kwargs["callingBBUser"]

        if not callingBBUser.ownsShip(ship):
            raise RuntimeError("User '" + str(callingBBUser.id) + "' attempted to upgrade a ship that does not belong to them: " + ship.getNameAndNick())
        
        ship.applyUpgrade(self.upgrade)
        if self in callingBBUser.inactiveTools:
            callingBBUser.inactiveTools.removeItem(self)


    async def userFriendlyUse(self, message : Message, *args, **kwargs) -> str:
        """Apply the upgrade to the given ship.
        After use, the tool will be removed from callingBBUser's inventory. To disable this, pass callingBBUser as None.

        :param Message message: The discord message that triggered this tool use
        :return: A user-friendly messge summarising the result of the tool use.
        :rtype: str
        """
        if "ship" not in kwargs:
            raise NameError("Required kwarg not given: ship")
        if not isinstance(kwargs["ship"], bbShip):
            raise TypeError("Required kwarg is of the wrong type. Expected bbShip, received " + kwargs["ship"].__class__.__name__)
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        
        # converted to soft type check due to circular import
        """if (not isinstance(kwargs["callingBBUser"], bbUser)) and kwargs["callingBBUser"] is not None:
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)"""
        if (kwargs["callingBBUser"].__class__.__name__ != "bbUser") and kwargs["callingBBUser"] is not None:
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        ship, callingBBUser = kwargs["ship"], kwargs["callingBBUser"]

        if not callingBBUser.ownsShip(ship):
            raise RuntimeError("User '" + str(callingBBUser.id) + "' attempted to upgrade a ship that does not belong to them: " + ship.getNameAndNick())
        
        callingBBUser = kwargs["callingBBUser"]
        confirmMsg = await message.channel.send("Are you sure you want to apply the " + self.upgrade.name + " upgrade to your " + ship.getNameAndNick() + "?") 
        confirmation = await InlineConfirmationMenu(confirmMsg, message.author, bbConfig.toolUseConfirmTimeoutSeconds).doMenu()
        
        if bbConfig.defaultRejectEmoji in confirmation:
            return "🛑 Upgrade application cancelled."
        elif bbConfig.defaultAcceptEmoji in confirmation:
            ship.applyUpgrade(self.upgrade)
            if self in callingBBUser.inactiveTools:
                callingBBUser.inactiveTools.removeItem(self)
            
            return "🔧 Success! Your upgrade has been applied."


    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        return self.upgrade.statsStringShort()


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbItem class
        :rtype: type
        """
        return bbShipUpgradeTool

    
    def toDict(self, **kwargs):
        """
        
        :param bool saveType: When true, include the string name of the object type in the output.
        """
        data = super().toDict(**kwargs)
        data["name"] = self.upgrade.name
        data["upgrade"] = self.upgrade.toDict(**kwargs)
        return data
        # raise RuntimeError("Attempted to save a non-builtIn bbShipUpgradeTool")
            

    @classmethod
    def fromDict(cls, toolDict : dict, **kwargs) -> bbShipUpgradeTool:
        """Construct a bbShipUpgradeTool from its dictionary-serialized representation.

        :param dict toolDict: A dictionary containing all information needed to construct the required bbShipUpgradeTool. Critically, a name, type, and builtIn specifier.
        :return: A new bbShipUpgradeTool object as described in toolDict
        :rtype: bbShipUpgradeTool
        """
        upgrade = bbData.builtInUpgradeObjs[toolDict["name"]] if toolDict["builtIn"] else bbShipUpgrade.bbShipUpgrade.fromDict(toolDict["upgrade"])
        if toolDict["builtIn"]:
            return bbData.builtInToolObjs[f"Ship Upgrade: {upgrade.name}"]
        return bbShipUpgradeTool(upgrade, value=0, builtIn=False, autoUse=toolDict.get("autoUse", False))
