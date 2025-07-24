from __future__ import annotations
from . import bbToolItem
from .... import lib
from ....bbConfig import bbData
from discord import Message
from ..bbItem import spawnableItem


@spawnableItem
class bbCreditsTool(bbToolItem.bbToolItem):
    async def use(self, *args, **kwargs):
        """
        After use, the tool will be removed from callingBBUser's inventory.
        """
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        if kwargs["callingBBUser"] is not None and kwargs["callingBBUser"].__class__.__name__ != "bbUser":
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        callingBBUser = kwargs["callingBBUser"]
        
        callingBBUser.credits += self.value

        if self in callingBBUser.inactiveTools:
            callingBBUser.inactiveTools.removeItem(self)


    async def userFriendlyUse(self, message : Message, *args, **kwargs) -> str:
        """
        After use, the tool will be removed from callingBBUser's inventory.

        :param Message message: The discord message that triggered this tool use
        :return: A user-friendly messge summarising the result of the tool use.
        :rtype: str
        """
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        
        # converted to soft type check due to circular import
        """if (not isinstance(kwargs["callingBBUser"], bbUser)) and kwargs["callingBBUser"] is not None:
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)"""
        if (kwargs["callingBBUser"].__class__.__name__ != "bbUser") and kwargs["callingBBUser"] is not None:
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        callingBBUser = kwargs["callingBBUser"]
        callingBBUser.credits += self.value

        if self in callingBBUser.inactiveTools:
            callingBBUser.inactiveTools.removeItem(self)

        return f"You got {self.value} credits!"


    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        return f"*{self.value} credits*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbItem class
        :rtype: type
        """
        return bbCreditsTool

    
    def toDict(self, **kwargs):
        """
        
        :param bool saveType: When true, include the string name of the object type in the output.
        """
        data = super().toDict(**kwargs)
        return data
            

    @classmethod
    def fromDict(cls, toolDict : dict, **kwargs) -> bbShipUpgradeTool:
        """Construct a bbShipUpgradeTool from its dictionary-serialized representation.

        :param dict toolDict: A dictionary containing all information needed to construct the required bbShipUpgradeTool. Critically, a name, type, and builtIn specifier.
        :return: A new bbShipUpgradeTool object as described in toolDict
        :rtype: bbShipUpgradeTool
        """
        if toolDict["builtIn"]:
            return bbData.builtInToolObjs[toolDict["name"]]
        
        return bbCreditsTool(
            toolDict["name"],
            toolDict.get("aliases", []),
            toolDict.get("value", 0),
            toolDict.get("wiki", ""),
            toolDict.get("manufacturer", ""),
            toolDict.get("icon", ""),
            toolDict.get("emoji", lib.emojis.dumbEmoji.EMPTY),
            toolDict.get("techLevel", -1),
            toolDict.get("builtIn", False),
            toolDict.get("autoUse", False))
