from .. import bbItem
from abc import abstractmethod
from .... import lib
from discord import Message
from typing import List

class bbToolItem(bbItem.bbItem):
    """An item that has a function of some kind.
    Intended to be very generic at this level of implementation.
    """

    def __init__(self, name : str, aliases : List[str], value : int = 0, wiki : str = "",
            manufacturer : str = "", icon : str = "", emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY,
            techLevel : int = -1, builtIn : bool = False, autoUse: bool = False):
        """
        :param str name: The name of the item. Must be unique. (a model number is a good starting point)
        :param list[str] aliases: A list of alternative names this item may be referred to by.
        :param int value: The number of credits that this item can be bought/sold for at a shop. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this item. (Default "")
        :param str manufacturer: The name of the manufacturer of this item (Default "")
        :param str icon: A URL pointing to an image to use for this item's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this item's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other items of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard item (loaded in from bbData) or a custom spawned item (Default False)
        """
        super().__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)
        self.autoUse = autoUse


    @abstractmethod
    async def use(self, *args, **kwargs):
        """This item's behaviour function. Intended to be very generic at this level of implementation.
        """
        pass


    @abstractmethod
    async def userFriendlyUse(self, message : Message, *args, **kwargs) -> str:
        """A version of self.use intended to be called by users, where exceptions are never thrown in the case of
        user error, and results strings are always returned.

        :param Message message: The discord message that triggered this tool use
        :return: A user-friendly messge summarising the result of the tool use.
        :rtype: str
        """
        pass

    
    @abstractmethod
    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        return "*No effect*"


    @abstractmethod
    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbItem class
        :rtype: type
        """
        return bbItem

    
    @abstractmethod
    def toDict(self, **kwargs) -> dict:
        """Serialize this tool into dictionary format.
        This step of implementation adds a 'type' string indicating the name of this tool's subclass.

        :param bool saveType: When true, include the string name of the object type in the output.
        :return: The default bbItem toDict implementation, with an added 'type' field
        :rtype: dict
        """
        data = super().toDict(**kwargs)
        data["itemType"] = "bbToolItem"
        data["autoUse"] = self.autoUse
        return data
    