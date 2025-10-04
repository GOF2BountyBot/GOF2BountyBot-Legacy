from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Dict, Optional, Tuple, Type, TypeVar

if TYPE_CHECKING:
    from .. import bbSystem

import random
from enum import Enum
from abc import ABC, abstractmethod

from ....baseClasses.bbSerializable import bbSerializable

class NodeGeneratorType(Enum):
    UniformRandom = "UniformRandom"


_nodeGenerators: Dict[NodeGeneratorType, "Type[NodeGenerator]"] = {}

TNodeGenerator = TypeVar("TNodeGenerator", bound="Type[NodeGenerator]")

def _serializableNodeGenerator(t: TNodeGenerator) -> TNodeGenerator:
    """The same could be achieved with a metaclass."""
    _nodeGenerators[t.nodeGeneratorType] = t
    return t


class NodeGenerator(bbSerializable, ABC):
    nodeGeneratorType: NodeGeneratorType

    def __init__(
        self,
        graph: Dict[str, "bbSystem.System"],
    ) -> None:
        self.systemChoices = list(graph.keys())

    @abstractmethod
    def selectValidNode(self, validateNode: Callable[[str], bool]) -> Tuple[bool, str]:
        """Pick a random node from the graph that matches the given predicate.
        If selection succeeds: Return `True` and the selected node name.
        If selection fails: Return `False` and an error message."""
        raise NotImplementedError()

    @abstractmethod
    def selectAnyNode(self) -> str:
        """Pick any random node from the graph."""
        raise NotImplementedError()
    
    def toDict(self, **kwargs) -> Dict:
        return {"nodeGeneratorType": self.nodeGeneratorType.value}
    
    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> NodeGenerator:
        newNodeGeneratorTypeRaw = data["nodeGeneratorType"]
        newNodeGeneratorType = NodeGeneratorType(newNodeGeneratorTypeRaw)
        return _nodeGenerators[newNodeGeneratorType].fromDict(data, **kwargs)


@_serializableNodeGenerator
class UniformRandomNodeGenerator(NodeGenerator):
    nodeGeneratorType = NodeGeneratorType.UniformRandom

    def __init__(
        self,
        graph: Dict[str, "bbSystem.System"],
        maxNodeGenerationAttempts: int,
    ) -> None:
        super().__init__(graph)
        self.maxNodeGenerationAttempts = maxNodeGenerationAttempts

    def selectValidNode(self, validateNode: Callable[[str], bool]) -> Tuple[bool, str]:
        node = self.selectAnyNode()

        attempt = 1
        while attempt < self.maxNodeGenerationAttempts:
            if validateNode(node):
                break

            self.systemChoices.remove(node)
            node = self.selectAnyNode()
            attempt += 1
        
        if attempt == self.maxNodeGenerationAttempts:
            return (
                False,
                f"No valid node was found within {self.maxNodeGenerationAttempts} random selections"
            )
        
        return (True, node)
    
    def selectAnyNode(self) -> str:
        return random.choice(self.systemChoices)


class NodeGeneratorFactoryType(Enum):
    AlwaysUniformRandom = "AlwaysUniformRandom"


_nodeGeneratorFactories: Dict[NodeGeneratorFactoryType, "Type[NodeGeneratorFactory]"] = {}

TNodeGeneratorFactory = TypeVar("TNodeGeneratorFactory", bound="Type[NodeGeneratorFactory]")

def _serializableNodeGeneratorFactory(t: TNodeGeneratorFactory) -> TNodeGeneratorFactory:
    """The same could be achieved with a metaclass."""
    _nodeGeneratorFactories[t.nodeGeneratorFactoryType] = t
    return t


class NodeGeneratorFactory(bbSerializable, ABC):
    nodeGeneratorFactoryType: NodeGeneratorFactoryType

    @abstractmethod
    def create(
        self,
        graph: Dict[str, "bbSystem.System"]
    ) -> NodeGenerator:
        raise NotImplementedError()
    
    def toDict(self, **kwargs) -> Dict:
        return {"nodeGeneratorFactoryType": self.nodeGeneratorFactoryType.value}
    
    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> NodeGeneratorFactory:
        newNodeGeneratorFactoryTypeRaw = data["nodeGeneratorFactoryType"]
        newNodeGeneratorFactoryType = NodeGeneratorFactoryType(newNodeGeneratorFactoryTypeRaw)
        return _nodeGeneratorFactories[newNodeGeneratorFactoryType].fromDict(data, **kwargs)


@_serializableNodeGeneratorFactory
class AlwaysUniformNodeGeneratorFactory(NodeGeneratorFactory):
    nodeGeneratorFactoryType = NodeGeneratorFactoryType.AlwaysUniformRandom

    def __init__(
        self,
        maxNodeGenerationAttempts: int
    ) -> None:
        self.maxNodeGenerationAttempts = maxNodeGenerationAttempts
        
    def create(
        self,
        graph: Dict[str, "bbSystem.System"]
    ) -> NodeGenerator:
        return UniformRandomNodeGenerator(graph, self.maxNodeGenerationAttempts)
    
    def toDict(self, **kwargs) -> Dict:
        data = super().toDict(**kwargs)
        data["maxNodeGenerationAttempts"] = self.maxNodeGenerationAttempts
        return data
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> NodeGeneratorFactory:
        return AlwaysUniformNodeGeneratorFactory(data["maxNodeGenerationAttempts"])
