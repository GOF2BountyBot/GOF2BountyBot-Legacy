from __future__ import annotations
from . import bbInventoryListing
from ..baseClasses import bbSerializable
from .items.tools import bbToolItem
from . import bbUser

import asyncio

class bbInventory(bbSerializable.bbSerializable):
    """A database of bbInventoryListings.
    Aside from the use of bbInventoryListing for the purpose of item quantities, this class is type unaware.

    :var items: The actual item listings
    :vartype items: dict[object, bbInventoryListing]
    :var keys: The item types stored
    :vartype keys: ist[object]
    :var totalItems: The total number of items stored; the sum of all item quantities
    :vartype totalItems: int
    :var numKeys: The number of item types stored; the length of self.keys
    :vartype numKeys: int
    """
    def __init__(self):
        # The actual item listings
        self.items = {}
        # The item types stored
        self.keys = []
        # The total number of items stored; the sum of all item quantities
        self.totalItems = 0
        # The number of item types stored; the length of self.keys
        self.numKeys = 0

    
    
    def addItem(self, item : object, quantity : int = 1):
        """Add one or more of an item to the inventory.
        If at least one of item is already in the inventory, that item's bbInventoryListing count will be incremented.
        Otherwise, a new bbInventoryListing is created for item.

        :param object item: The item to add to the inventory
        :param int quantity: Integer amount of item to add to the inventory. Must be at least 1. (Default 1)
        :raise ValueError: If quantity is less than 1
        """
        if quantity < 0:
            raise ValueError("Quantity must be at least 1")
        
        # increment totalItems tracker
        self.totalItems += quantity
        # increment count for existing bbItemListing
        if item in self.items:
            self.items[item].count += quantity
        # Add a new bbItemListing if one does not exist
        else:
            self.items[item] = bbInventoryListing.bbInventoryListing(item, quantity)
            # Update keys and numKeys trackers
            self.keys.append(item)
            self.numKeys += 1


    def _addListing(self, newListing : bbInventoryListing.bbInventoryListing):
        """Add an inventory listing to the inventory, including item and acount.
        If at least one of item is already in the inventory, that item's bbInventoryListing count will be incremented.
        Otherwise, a reference to the given bbInventoryListing is stored. The listing is not copied and remains mutable.

        :param bbInventoryListing newListing: The inventory listing to add to the inventory
        """
        # update total items count
        self.totalItems += newListing.count
        # if item is already stored, increment its listing count
        if newListing.item in self.items:
            self.items[newListing.item].count += newListing.count
        # otherwise, store a reference to the given listing
        else:
            self.items[newListing.item] = newListing
            self.keys.append(newListing.item)
            # update keys counter
            self.numKeys += 1


    
    def removeItem(self, item : object, quantity : int = 1):
        """Remove one or more of an item from the inventory.
        If the amount of item stored in the inventory is now zero, the bbInventoryListing is removed from the inventory.
        At least quantity of item must already be stored in the inventory. 

        :param object item: The item to remove from the inventory
        :param int quantity: Integer amount of item to remove from the inventory. Must be between 1 and the amount of item currently stored, both inclusive. (Default 1)
        :raise ValueError: When attempting to remove more of an item than is in the inventory
        """
        # Ensure enough of item is stored to remove quantity of it
        if item in self.items and self.items[item].count >= quantity:
            # Update item's count and inventory's totalItems tracker
            self.items[item].count -= quantity
            self.totalItems -= quantity
            # remove the bbItemListing if it is now empty
            if self.items[item].count == 0:
                # update the keys and numKeys trackers
                for i in range(len(self.keys)):
                    if self.keys[i] is item:
                        self.keys.pop(i)
                        break
                # self.keys.remove(item)
                self.numKeys -= 1
                del self.items[item]
        else:
            raise ValueError("Attempted to remove " + str(quantity) + " " + str(item) + "(s) when " + (str(self.items[item].count) if item in self.items else "0") + " are in inventory")

    
    
    def numPages(self, itemsPerPage : int) -> int:
        """Get the number of pages of items in the inventory, for a given max number of items per page
        E.g, where 3 keys are in the inventory: numPages(1) gives 3. numPages(2) gives 2.

        :param int itemsPerPage: The maximum number of items per page
        :return: The number of pages required to list all items in the inventory
        :rtype: int
        """
        return int(self.numKeys/itemsPerPage) + (0 if self.numKeys % itemsPerPage == 0 else 1)

    
    
    def getPage(self, pageNum : int, itemsPerPage : int) -> list:
        """Get a list of the bbItemListings on the requested page.
        pageNum is 1 index-based; the first page is 1.
        pageNum must be between 1 and numPages(itemsPerPage).

        :param int pageNum: The number of the page to fetch
        :param int itemsPerPage: The max number of items that can be contained in a single page
        :return: A list containing the bbInventoryListings contained in the requested inventory page
        :rtype: list[bbInventoryListings]
        :raise IndexError: When attempting to get a page out of range of this inventory
        """
        # Validate the requested pageNum
        if pageNum < 1 or pageNum > self.numPages(itemsPerPage):
            raise IndexError("pageNum out of range. min=1 max=" + str(self.numPages(itemsPerPage)))
        
        page = []
        # Splice self.keys around the first and last indices in the requested page
        for item in self.keys[(pageNum - 1) * itemsPerPage: min(pageNum * itemsPerPage, self.numKeys)]:
            # Add the bbItemListings for each of the page's keys to the results list
            page.append(self.items[item])

        return page

    
    def stores(self, item) -> bool:
        """Decide whether a given item is stored in this inventory.

        :param object item: The item to check for membership
        :return: True if at least one of item is in this inventory, False otherwise
        :rtype: bool
        """
        return item in self.keys

    
    
    def numStored(self, item) -> int:
        """Get the amount stored of a given item.

        :param object item: The item to count
        :return: Integer count of number of items in this inventory. 0 if it is not stored in this inventory.
        :rtype: int
        """
        return self.items[item].count if self.stores(item) else 0


    
    def isEmpty(self) -> bool:
        """Decide whether or not this bbInventory currently stores any items.

        :return: True if no items are stored, False if at least one item is stored currently
        :rtype: bool
        """
        return self.totalItems == 0


    
    def clear(self):
        """Remove all items from the inventory.
        """
        self.items = {}
        self.keys = []
        self.totalItems = 0
        self.numKeys = 0


    
    def __getitem__(self, key : int) -> bbInventoryListing:
        """Override [subscript] operator for reading values.
        Currently returns the bbInventoryListing for the item at position key in self.keys.

        :param int key: The index of the key to dereference
        :return: The bbInventoryListing for the item at the requested index
        :rtype: bbInventoryListing
        :raise KeyError: When the given index is in range of the inventory, but the key at the requested position in the keys array does not exist in the items dictionary
        :raise IndexError: When given an index that isn't an int, or the given index is out of range
        :raise ValueError: When the inventory is empty
        """
        if bool(self.keys): 
            if key in range(len(self.keys)):
                if self.keys[key] in self.items:
                    return self.items[self.keys[key]]
                raise KeyError("Failed get of key number " + str(key) + " - " + str(self.keys[key]) + ". Key does not exist in inventory.")
            raise IndexError("Key of incorrect type or out of range: "+ str(key) + ". Valid range: 0 - " + str(len(self.keys)-1))
        raise ValueError("Attempted to fetch key " + str(key) + ", but keys list is empty")


    
    def __setitem__(self, key, value):
        """Disallow assignment through the [subscript] operator.

        :param key: ignored
        :param value: ignored
        :raise NotImplementedError: Always.
        """
        raise NotImplementedError("Cannot use [subscript] assignment for class bbInventory. use addItem/removeItem instead.")
        # self.items[self.keys[key]] = value


    
    def __contains__(self, item) -> bool:
        """Override the 'in' operator.

        :param object item: The object to test for membership
        """
        return item in self.keys

    
    def toDict(self, **kwargs) -> dict:
        data = super().toDict(**kwargs)
        data["items"] = []
        for listing in self.items.values():
            data["items"].append(listing.toDict(**kwargs))
        
        return data


    @classmethod
    def fromDict(cls, invDict, **kwargs) -> bbInventory:
        newInv = bbInventory()
        if "items" in invDict:
            for listingDict in invDict["items"]:
                newInv._addListing(bbInventoryListing.bbInventoryListing.fromDict(listingDict))
        
        return newInv


class TypeRestrictedInventory(bbInventory):
    """An inventory where the item listings are guaranteed to be of a given type.

    :var itemType: The type by which listings are restricted
    :vartype itemType: type
    """

    def __init__(self, itemType : type):
        super().__init__()
        self.itemType = itemType

    
    def addItem(self, item: object, quantity : int = 1):
        if not isinstance(item, self.itemType):
            raise TypeError("Given item does not match this inventory's item type restriction. Expected '" + self.itemType.__name__ + "', given '" + type(item).__name__ + "'")
        super().addItem(item, quantity=quantity)

    
    def _addListing(self, newListing: bbInventoryListing.bbInventoryListing):
        if not isinstance(newListing.item, self.itemType):
            raise TypeError("Given item does not match this inventory's item type restriction. Expected '" + self.itemType.__name__ + "', given '" + type(newListing.item).__name__ + "'")
        super()._addListing(newListing)


class ToolInventory(TypeRestrictedInventory):
    def __init__(self, owningUser: "bbUser.bbUser"):
        super().__init__(bbToolItem.bbToolItem)
        self.owningUser = owningUser

    
    def addItem(self, item: object, quantity: int = 1):
        if not isinstance(item, bbToolItem.bbToolItem):
            raise TypeError("Given item does not match this inventory's item type restriction. Expected '" + bbToolItem.bbToolItem.__name__ + "', given '" + type(item).__name__ + "'")
        super().addItem(item, quantity=quantity)
        if item.autoUse:
            # TODO: schedule this with logging with lib.discordUtil
            asyncio.create_task(item.use(callingBBUser=self.owningUser))