from ..reactionMenus import ReactionMenu, ReactionRolePicker, ReactionInventoryPicker, ReactionDuelChallengeMenu, ReactionPollMenu
from .. import bbGlobals

# ReactionMenu subclasses that cannot be saved to dictionary
# TODO: change to a class-variable reference e.g menu.__class__.SAVEABLE
unsaveableMenuTypes = ["ReactionDuelChallengeMenu"]


class ReactionMenuDB(dict):
    """A database of ReactionMenu instances.
    Currently just an extension of dict to add toDict()."""

    def toDict(self, **kwargs) -> str:
        """Serialise all saveable ReactionMenus in this DB into a single dictionary.

        :return: A dictionary containing full dictionary descriptions of all saveable ReactionMenu instances in this database
        :rtype: dict
        """
        data = {}
        for msgID in self:
            if menuData["type"] not in unsaveableMenuTypes:
                data[msgID] = self[msgID].toDict(**kwargs)
        return data


async def fromDict(dbDict : dict) -> ReactionMenuDB:
    """Factory function constructing a new ReactionMenuDB from dictionary-serialized format; the opposite of ReactionMenuDB.toDict

    :param dict dbDict: A dictionary containing all info needed to reconstruct a ReactionMenuDB, in accordance with ReactionMenuDB.toDict
    :return: A new ReactionMenuDB instance as described by dbDict
    :rtype: ReactionMenuDB
    """
    newDB = ReactionMenuDB()

    for msgID in dbDict:
        dcGuild = bbGlobals.client.get_guild(dbDict[msgID]["guild"])
        msg = await dcGuild.get_channel(dbDict[msgID]["channel"]).fetch_message(dbDict[msgID]["msg"])

        if bbGlobals.client.get_channel(dbDict[msgID]["channel"]) is None:
            continue
        if "type" in dbDict[msgID]:
            if dbDict[msgID]["type"] == "ReactionInventoryPicker":
                # newDB[int(msgID)] = ReactionInventoryPicker.fromDict(dbDict[msgID], msg=msg)
                continue
                
            elif dbDict[msgID]["type"] == "ReactionRolePicker":
                newDB[int(msgID)] = await ReactionRolePicker.ReactionRolePicker.fromDict(dbDict[msgID], msg=msg)

            elif dbDict[msgID]["type"] == "ReactionDuelChallengeMenu":
                continue

            elif dbDict[msgID]["type"] == "ReactionPollMenu":
                newDB[int(msgID)] = await ReactionPollMenu.ReactionPollMenu.fromDict(dbDict[msgID], msg=msg)

            else:
                continue
                # newDB[int(msgID)] = ReactionMenu.fromDict(dbDict[msgID], msg=msg)
    
    return newDB