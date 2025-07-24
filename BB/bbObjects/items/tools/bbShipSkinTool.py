from __future__ import annotations
from . import bbToolItem
from .... import lib
from ....bbConfig import bbConfig, bbData
from ... import bbShipSkin
from ..bbShip import bbShip
from discord import Message
from .... import bbGlobals
import asyncio
from ..bbItem import spawnableItem
from ....reactionMenus.ConfirmationReactionMenu import InlineConfirmationMenu


@spawnableItem
class bbShipSkinTool(bbToolItem.bbToolItem):
    """A tool that can be used to apply a skin to a ship.
    This item is named after the skin it applies.
    The manufacturer is set to the skin designer.
    This tool is single use. If a calling user is given, the tool is removed from that user's inventory after use.
    """
    def __init__(self, shipSkin : bbShipSkin, value : int = 0, wiki : str = "", icon : str = bbConfig.defaultShipSkinToolIcon,
            emoji : lib.emojis.dumbEmoji = None, techLevel : int = -1, builtIn : bool = False, autoUse : bool = False):
        """
        :param bbShipSkin shipSkin: The skin that this tool applies.
        :param int value: The number of credits that this item can be bought/sold for at a shop. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this item. If no wiki is given and shipSkin has one, that will be used instead. (Default "")
        :param str icon: A URL pointing to an image to use for this item's icon (Default bbConfig.defaultShipSkinToolIcon)
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this item's small icon (Default bbConfig.defaultShipSkinToolEmoji)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other items of the same type (Default shipSkin.averageTL)
        :param bool builtIn: Whether this is a BountyBot standard item (loaded in from bbData) or a custom spawned item (Default False)
        """
        if emoji is None:
            emoji = bbConfig.defaultShipSkinToolEmoji
        super().__init__(lib.stringTyping.shipSkinNameToToolName(shipSkin.name), [shipSkin.name, "Skin: " + shipSkin.name, "Ship Skin " + shipSkin.name + "Skin " + shipSkin.name], value=value, wiki=wiki if wiki else shipSkin.wiki if shipSkin.hasWiki else "", manufacturer=shipSkin.designer, icon=icon, emoji=emoji, techLevel=techLevel if techLevel > -1 else shipSkin.averageTL, builtIn=builtIn, autoUse=autoUse)
        self.shipSkin = shipSkin

    
    async def use(self, *args, **kwargs):
        """Apply the skin to the given ship.
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
        
        ship, callingBBUser = kwargs["ship"], kwargs["callingBBUser"]

        if not callingBBUser.ownsShip(ship):
            raise RuntimeError("User '" + str(callingBBUser.id) + "' attempted to skin a ship that does not belong to them: " + ship.getNameAndNick())
        
        if ship.isSkinned:
            return ValueError("Attempted to apply a skin to an already-skinned ship")
        if ship.name not in self.shipSkin.compatibleShips:
            return TypeError("The given skin is not compatible with this ship")
        
        ship.applySkin(self.shipSkin)
        if self in callingBBUser.inactiveTools:
            callingBBUser.inactiveTools.removeItem(self)


    async def userFriendlyUse(self, message : Message, *args, **kwargs) -> str:
        """Apply the skin to the given ship.
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
            raise RuntimeError("User '" + str(callingBBUser.id) + "' attempted to skin a ship that does not belong to them: " + ship.getNameAndNick())
        
        if ship.isSkinned:
            return ":x: This ship already has a skin applied! Please equip a different ship."
        if ship.name not in self.shipSkin.compatibleShips:
            return ":x: Your ship is not compatible with this skin! Please equip a different ship, or use `" + bbConfig.commandPrefix + "info skin " + self.name + "` to see what ships are compatible with this skin."
        
        callingBBUser = kwargs["callingBBUser"]
        confirmMsg = await message.channel.send("Are you sure you want to apply the " + self.shipSkin.name + " skin to your " + ship.getNameAndNick() + "?") 
        confirmation = await InlineConfirmationMenu(confirmMsg, message.author, bbConfig.toolUseConfirmTimeoutSeconds).doMenu()
        
        if bbConfig.defaultRejectEmoji in confirmation:
            return "🛑 Skin application cancelled."
        elif bbConfig.defaultAcceptEmoji in confirmation:
            ship.applySkin(self.shipSkin)
            if self in callingBBUser.inactiveTools:
                callingBBUser.inactiveTools.removeItem(self)
            
            return "🎨 Success! Your skin has been applied."


    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        try:
            return "*Designer: " + bbGlobals.client.get_user(self.manufacturer).name + "*"
        except AttributeError:
            return "*Designer: user #" + str(self.manufacturer) + "*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbItem class
        :rtype: type
        """
        return bbShipSkinTool

    
    def toDict(self, **kwargs):
        """
        
        :param bool saveType: When true, include the string name of the object type in the output.
        """
        data = super().toDict(**kwargs)
        data["name"] = self.shipSkin.name
        data["skin"] = self.shipSkin.toDict(**kwargs)
        return data
        # raise RuntimeError("Attempted to save a non-builtIn bbShipSkinTool")
            

    @classmethod
    def fromDict(cls, toolDict : dict, **kwargs) -> bbShipSkinTool:
        """Construct a bbShipSkinTool from its dictionary-serialized representation.

        :param dict toolDict: A dictionary containing all information needed to construct the required bbShipSkinTool. Critically, a name, type, and builtIn specifier.
        :return: A new bbShipSkinTool object as described in toolDict
        :rtype: bbShipSkinTool
        """
        shipSkin = bbData.builtInShipSkins[toolDict["name"]] if toolDict["builtIn"] else bbShipSkin.bbShipSkin.fromDict(toolDict["skin"])
        if toolDict["builtIn"]:
            return bbData.builtInToolObjs[lib.stringTyping.shipSkinNameToToolName(shipSkin.name)]
        return bbShipSkinTool(shipSkin, value=bbConfig.shipSkinValueForTL(shipSkin.averageTL), builtIn=False, autoUse=toolDict.get("autoUse", False))
