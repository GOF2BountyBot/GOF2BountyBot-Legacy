from . import bbShipUpgradeTool, bbToolItem, bbShipSkinTool, bbCrate
from .. import bbShip, bbWeapon, bbModuleFactory, bbTurret
from .... import lib


def fromDict(toolDict : dict) -> bbToolItem.bbToolItem:
    """Construct a bbToolItem from its dictionary-serialized representation.
    This method decodes which tool constructor is appropriate based on the 'type' attribute of the given dictionary.

    :param dict toolDict: A dictionary containing all information needed to construct the required bbToolItem. Critically, a name, type, and builtIn specifier.
    :return: A new bbToolItem object as described in toolDict
    :rtype: bbToolItem.bbToolItem
    :raise NameError: When toolDict does not contain a 'type' attribute.
    """

    itemConstructors = {"bbShip": bbShip.bbShip.fromDict,
                    "bbWeapon": bbWeapon.bbWeapon.fromDict,
                    "bbModule": bbModuleFactory.fromDict,
                    "bbTurret": bbTurret.bbTurret.fromDict,
                    "bbToolItem": fromDict}

    def crateFromDict(crateDict):
        if "itemPool" not in crateDict:
            print("CRATEDICT",crateDict)
            raise RuntimeError()
        itemPool = []
        for itemDict in crateDict["itemPool"]:
            if "itemType" in itemDict:
                itemPool.append(itemConstructors[itemDict["itemType"]](itemDict))
            else:
                itemPool.append(itemConstructors[itemDict["type"]](itemDict))
        
        return bbCrate.bbCrate(itemPool, name=crateDict["name"] if "name" in crateDict else "",
            value=crateDict["value"] if "value" in crateDict else 0,
            wiki=crateDict["wiki"] if "wiki" in crateDict else "",
            manufacturer=crateDict["manufacturer"] if "manufacturer" in crateDict else "",
            icon=crateDict["icon"] if "icon" in crateDict else "",
            emoji=lib.emojis.dumbEmojiFromDict(crateDict["emoji"]) if "emoji" in crateDict else lib.emojis.dumbEmoji.EMPTY,
            techLevel=crateDict["techLevel"] if "techLevel" in crateDict else -1,
            builtIn=crateDict["builtIn"] if "builtIn" in crateDict else False)

    toolTypeConstructors = {"bbShipSkinTool": bbShipSkinTool.bbShipSkinTool.fromDict,
                            "bbShipUpgradeTool": bbShipUpgradeTool.bbShipUpgradeTool.fromDict,
                        "bbCrate": crateFromDict}
    
    if "type" not in toolDict:
        raise NameError("Required dictionary attribute missing: 'type'")
    return toolTypeConstructors[toolDict["type"]](toolDict)
