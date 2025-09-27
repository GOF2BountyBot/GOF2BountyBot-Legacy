from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional, Tuple, Union, cast

from BB.bbObjects.bounties.bountyRoutes.bountyAnswerConfig import BountyAnswerConfig
if TYPE_CHECKING:
    from .. import bbSystem

import random
from enum import Enum
from abc import ABC, abstractmethod

from ....bbConfig import bbData
from .... import lib
from ....baseClasses.bbSerializable import bbSerializable
from . bountyAnswerConfig import *


class BountyRouteType(Enum):
    Explicit = "Explicit"
    ShortestPath = "ShortestPath"
    PathOfLength = "PathOfLength"


_bountyRouteConfigs: Dict[BountyRouteType, "Type[BountyRouteConfig]"] = {}

TRouteConfig = TypeVar("TRouteConfig", bound="Type[BountyRouteConfig]")

def _serializableBountyRouteConfig(t: TRouteConfig) -> TRouteConfig:
    """The same could be achieved with a metaclass."""
    _bountyRouteConfigs[t.routeType] = t
    return t


class BountyRouteConfig(bbSerializable, ABC):
    routeType: BountyRouteType

    def __init__(self, answer: Optional[Union[str, BountyAnswerConfig]]) -> None:
        if isinstance(answer, BountyAnswerConfig):
            self.answerConfig = answer
        elif isinstance(answer, str):
            self.answerConfig = ExplicitBountyAnswerConfig(answer)
        else:
            self.answerConfig = UniformRandomBountyAnswerConfig()

    @abstractmethod
    def generate(self) -> Union[Tuple[List[str], str], str]:
        """Generate the route. Returns either (route, answer) or a string describing what went wrong."""
        raise NotImplementedError()

    @abstractmethod
    def validate(self) -> List[str]:
        raise NotImplementedError()
    
    def toDict(self, **kwargs) -> Dict:
        return {
            "routeType": self.routeType.value, 
            "answerConfig": self.answerConfig.toDict(**kwargs)
        }
    
    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> BountyRouteConfig:
        newRouteTypeRaw = data["routeType"]
        newRouteType = BountyRouteType(newRouteTypeRaw)
        return _bountyRouteConfigs[newRouteType].fromDict(data, **kwargs)


@_serializableBountyRouteConfig
class ExplicitRouteConfig(BountyRouteConfig):
    def __init__(self, answer: Optional[Union[str, BountyAnswerConfig]], route: List[str]):
        super().__init__(answer)
        self.route = route

    def generate(self) -> Union[Tuple[List[str], str], str]:
        return (self.route, self.answerConfig.generate(self.route))
    
    def validate(self) -> List[str]:
        errs = ((["Empty route given"] if not self.route else [])
            + [f"Unknown system in route: '{n}'" for n in self.route if n not in bbData.builtInSystemObjs])
        
        self.answerConfig.validateInRoute(self.route, errs)
        return errs
    
    def toDict(self, **kwargs) -> Dict:
        d = super().toDict(**kwargs)
        d["route"] = self.route
        return d
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> ExplicitRouteConfig:
        rawAnswer = data.get("answerConfig", None)
        answer = BountyAnswerConfig.fromDict(rawAnswer) if rawAnswer else None
        route = data["route"]
        return ExplicitRouteConfig(answer, route)


@_serializableBountyRouteConfig
class ShortestPathRouteConfig(BountyRouteConfig):
    def __init__(self, answer: Optional[Union[str, BountyAnswerConfig]], startNode: str, node2: str, *nodes: str):
        super().__init__(answer)
        self.nodes = [startNode, node2] + list(nodes)

    def generate(self) -> Union[Tuple[List[str], str], str]:
        graph = cast(Dict[str, "bbSystem.System"], bbData.builtInSystemObjs)
        systems = [graph[n] for n in self.nodes]
        previousNode = systems[0]
        route = [systems[0].name]

        for nextNode in systems[1:]:
            nextSegment = lib.pathfinding.bbAStar(previousNode.name, nextNode.name, graph, excludeSystems=route[1:])
            route += nextSegment
            previousNode = nextNode

        return (route, self.answerConfig.generate(route))
    
    def validate(self) -> List[str]:
        errs = [f"Unknown system in route: '{n}'" for n in self.nodes if n not in bbData.builtInSystemObjs]
        self.answerConfig.validateInRoute(self.nodes, errs)
        return errs
    
    def toDict(self, **kwargs) -> Dict:
        d = super().toDict(**kwargs)
        d["nodes"] = self.nodes
        return d
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> ShortestPathRouteConfig:
        rawAnswer = data.get("answerConfig", None)
        answer = BountyAnswerConfig.fromDict(rawAnswer) if rawAnswer else None
        firstNode, *nodes = data["nodes"]
        return ShortestPathRouteConfig(answer, firstNode, *nodes)


class PathOfLengthRouteSegment(bbSerializable):
    def __init__(self, nextNode: str, segmentLength: int) -> None:
        self.nextNode = nextNode
        self.segmentLength = segmentLength

    def toDict(self, **kwargs) -> Dict:
        return {"nextNode": self.nextNode, "segmentLength": self.segmentLength}
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> PathOfLengthRouteSegment:
        return PathOfLengthRouteSegment(data["nextNode"], data["segmentLength"])
    
    @classmethod
    def fromInstanceOrTuple(cls, inst: Union[Tuple[str, int], PathOfLengthRouteSegment]) -> PathOfLengthRouteSegment:
        return inst if isinstance(inst, PathOfLengthRouteSegment) else PathOfLengthRouteSegment(inst[0], inst[1])


@_serializableBountyRouteConfig
class PathOfLengthRouteConfig(BountyRouteConfig):
    @overload
    def __init__(self, answer: Optional[Union[str, BountyAnswerConfig]], startNode: str, firstSegment: PathOfLengthRouteSegment, *segments: PathOfLengthRouteSegment): ...
    @overload
    def __init__(self, answer: Optional[Union[str, BountyAnswerConfig]], startNode: str, firstSegment: Tuple[str, int], *segments: Tuple[str, int]): ...
    
    def __init__(self, answer: Optional[Union[str, BountyAnswerConfig]], startNode: str, firstSegment: Union[Tuple[str, int], PathOfLengthRouteSegment], *segments: Union[Tuple[str, int], PathOfLengthRouteSegment]):
        super().__init__(answer)
        self.startNode = startNode
        self.segments = [PathOfLengthRouteSegment.fromInstanceOrTuple(firstSegment)] + \
            [PathOfLengthRouteSegment.fromInstanceOrTuple(s) for s in segments]

    def generate(self) -> Union[Tuple[List[str], str], str]:
        graph = cast(Dict[str, "bbSystem.System"], bbData.builtInSystemObjs)
        segmentsWithSystems = [(graph[n.nextNode], n.segmentLength) for n in self.segments]
        previousNode = graph[self.startNode]
        route = [segmentsWithSystems[0][0].name]

        for segment in segmentsWithSystems:
            nextSegmentEnd, nextSegmentLength = segment
            nextRouteSegment = lib.pathfinding.pathOfLength(graph, previousNode.name, nextSegmentEnd.name, nextSegmentLength, excludeSystems=route[1:])
            if nextRouteSegment is None:
                return f"Could not find path of length {nextSegmentLength} from {previousNode} to {nextSegmentEnd}"
            route += nextRouteSegment[0]
            previousNode = segment[0]

        return (route, self.answerConfig.generate(route))
    
    def validate(self) -> List[str]:
        knownNodes = [self.startNode] + [s.nextNode for s in self.segments]
        errs = [f"Unknown system in route: '{n}'" for n in knownNodes if n not in bbData.builtInSystemObjs]
        self.answerConfig.validateInRoute(knownNodes, errs)
        return errs
    
    def toDict(self, **kwargs) -> Dict:
        d = super().toDict(**kwargs)
        d["startNode"] = self.startNode
        d["segments"] = self.segments
        return d
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> PathOfLengthRouteConfig:
        rawAnswer = data.get("answerConfig", None)
        answer = BountyAnswerConfig.fromDict(rawAnswer) if rawAnswer else None
        startNode = data["startNode"]
        rawSegments = data["segments"]
        allSegments = [PathOfLengthRouteSegment.fromDict(s) for s in rawSegments]
        firstSegment, *remainingSegments = allSegments
        return PathOfLengthRouteConfig(answer, startNode, firstSegment, *remainingSegments)
