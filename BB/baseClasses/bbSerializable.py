from __future__ import annotations
from abc import ABC, abstractmethod


class bbSerializable(ABC):

    @abstractmethod
    def toDict(self, **kwargs) -> dict:
        """Serialize this object into dictionary format, to be recreated completely.

        :return: A dictionary containing all information needed to recreate this object
        :rtype: dict
        """
        return {}


    @classmethod
    @abstractmethod
    def fromDict(cls, data : dict, **kwargs) -> bbSerializable:
        """Recreate a dictionary-serialized bbSerializable object 
        
        :param dict data: A dictionary containing all information needed to recreate the serialized object
        :return: A new object as specified by the attributes in data
        :rtype: bbSerializable
        """
        pass
