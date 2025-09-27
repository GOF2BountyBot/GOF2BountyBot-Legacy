from __future__ import annotations
from typing import Iterable, List, Dict, Optional, Type, TypeVar, overload

import random
from enum import Enum
from abc import ABC, abstractmethod

from ....baseClasses.bbSerializable import bbSerializable


class BountyRouteAnswerType(Enum):
    Explicit = "Explicit"
    UniformRandom = "UniformRandom"


_bountyAnswerConfigs: Dict[BountyRouteAnswerType, "Type[BountyAnswerConfig]"] = {}

TAnswerConfig = TypeVar("TAnswerConfig", bound="Type[BountyAnswerConfig]")

def _serializableBountyAnswerConfig(t: TAnswerConfig) -> TAnswerConfig:
    """The same could be achieved with a metaclass."""
    _bountyAnswerConfigs[t.answerType] = t
    return t


class BountyAnswerConfig(bbSerializable, ABC):
    answerType: BountyRouteAnswerType

    @abstractmethod
    def generate(self, route: Iterable[str]) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def validateInRouteInternal(self, route: Iterable[str]) -> Optional[str]: ...

    @overload
    def validateInRoute(self, route: Iterable[str]) -> Optional[str]: ...

    @overload
    def validateInRoute(self, route: Iterable[str], outputList: List[str]) -> None: ...
        
    def validateInRoute(self, route: Iterable[str], outputList: Optional[List[str]] = None) -> Optional[str]:
        err = self.validateInRouteInternal(route)
        
        if outputList is None:
            return err
        
        if err is not None:
            outputList.append(err)
    
    def toDict(self, **kwargs) -> Dict:
        return {"answerType": self.answerType.value}
    
    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> BountyAnswerConfig:
        newAnswerTypeRaw = data["answerType"]
        newAnswerType = BountyRouteAnswerType(newAnswerTypeRaw)
        return _bountyAnswerConfigs[newAnswerType].fromDict(data, **kwargs)


@_serializableBountyAnswerConfig
class UniformRandomBountyAnswerConfig(BountyAnswerConfig):
    answerType = BountyRouteAnswerType.UniformRandom
    
    def generate(self, route: Iterable[str]) -> str:
        return random.choice(route if isinstance(route, list) else list(route))
    
    def validateInRouteInternal(self, route: Iterable[str]) -> Optional[str]:
        return None
    
    def toDict(self, **kwargs) -> Dict:
        return super().toDict(**kwargs)
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> UniformRandomBountyAnswerConfig:
        return UniformRandomBountyAnswerConfig()
    

@_serializableBountyAnswerConfig
class ExplicitBountyAnswerConfig(BountyAnswerConfig):
    answerType = BountyRouteAnswerType.Explicit

    def __init__(self, answer: str) -> None:
        self.answer = answer

    def generate(self, route: Iterable[str]) -> str:
        return self.answer
    
    def validateInRouteInternal(self, route: Iterable[str]) -> Optional[str]:
        return f"Answer '{self.answer}' not in route" if self.answer not in route else None
    
    def toDict(self, **kwargs) -> Dict:
        d = super().toDict(**kwargs)
        d["answer"] = self.answer
        return d
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> ExplicitBountyAnswerConfig:
        return ExplicitBountyAnswerConfig(data["answer"])
