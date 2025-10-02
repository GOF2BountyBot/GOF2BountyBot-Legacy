from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional, Tuple, Union, cast

from BB.bbObjects.bounties.bountyRoutes.bountyAnswerConfig import BountyAnswerConfig
if TYPE_CHECKING:
    from .. import bbSystem

import random
from enum import Enum
from abc import ABC, abstractmethod

from ....bbConfig import bbData, bbConfig
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
    """Find the shortest path between nodes.
    
    :param answer: The answer. Give as `None` to use a uniformally random choice. Can be given either as a system name, or a `BountyAnswerConfig`.
    :param Optional[str] startNode: The first system in the route. Give as `None` to use a uniformally random choice
    :param Optional[str] node2: The second system in the route. Give as `None` to use a uniformally random choice
    :param Optional[str] nodes: The remaining systems in the route. Give as `None` to use a uniformally random choice
    """
    def __init__(
        self, 
        answer: Optional[Union[str, BountyAnswerConfig]],
        startNode: Optional[str],
        node2: Optional[str],
        *nodes: Optional[str]
    ) -> None:
        super().__init__(answer)
        self.nodes = [startNode, node2] + list(nodes)
        self.allowDuplicateEntries = bbConfig.shortestPathRouteConfig_allowDuplicateNodes
        self.nodeGenerationAttempts = bbConfig.shortestPathRouteConfig_nodeGenerationAttempts

    def generate(self) -> Union[Tuple[List[str], str], str]:
        graph = {
            k: v
            for k, v in cast(Dict[str, "bbSystem.System"], bbData.builtInSystemObjs).items()
            if v.hasJumpGate()
        }

        systems: List[bbSystem.System] = []
        
        if not any(n is None for n in self.nodes):
            for node in self.nodes:
                systems.append(graph[cast(str, node)])
        else:
            systemChoices = list(graph.keys())

            for i, node in enumerate(self.nodes):
                if node is not None:
                    systems.append(graph[node])
                    continue
                
                node = random.choice(systemChoices)

                if i == 0:
                    systemChoices.remove(node)
                else:
                    attempt = 1
                    while attempt < self.nodeGenerationAttempts:
                        routeAttempt = lib.pathfinding.bbAStar(
                            systems[i - 1].name,
                            node,
                            graph,
                            excludeSystems=[] if self.allowDuplicateEntries else [s.name for s in systems])
                        
                        if len(routeAttempt) != 0 and not routeAttempt[0].startswith("!") and not routeAttempt[0].startswith("#"):
                            break

                        systemChoices.remove(node)
                        node = random.choice(systemChoices)
                        attempt += 1

                    if attempt == self.nodeGenerationAttempts:
                        return f"Failed to generate node #{i}. Could not find route from {systems[i - 1].name} " + \
                                f"to any of {self.nodeGenerationAttempts} randomly selected systems, " + \
                                ("allowing duplicates" if self.allowDuplicateEntries else "disallowing duplicates")
                
                systems.append(graph[node])
        
        previousNode = systems[0]
        route = [systems[0].name]

        for nextNode in systems[1:]:
            nextSegment = lib.pathfinding.bbAStar(previousNode.name, nextNode.name, graph, excludeSystems=route[1:])
            route += nextSegment
            previousNode = nextNode

        return (route, self.answerConfig.generate(route))
    
    def validate(self) -> List[str]:
        errs = [f"Unknown system in route: '{n}'" for n in self.nodes if n is not None and n not in bbData.builtInSystemObjs]
        self.answerConfig.validateInRoute((n for n in self.nodes if n is not None), errs)
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
    def __init__(self, nextNode: Optional[str], segmentLength: int) -> None:
        self.nextNode = nextNode
        self.segmentLength = segmentLength

    def toDict(self, **kwargs) -> Dict:
        return {"nextNode": self.nextNode, "segmentLength": self.segmentLength}
    
    @classmethod
    def fromDict(cls, data: Dict, **kwargs) -> PathOfLengthRouteSegment:
        return PathOfLengthRouteSegment(data["nextNode"], data["segmentLength"])
    
    @classmethod
    def fromInstanceOrTuple(
        cls,
        inst: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment]
    ) -> PathOfLengthRouteSegment:
        return inst if isinstance(inst, PathOfLengthRouteSegment) else PathOfLengthRouteSegment(inst[0], inst[1])


@_serializableBountyRouteConfig
class PathOfLengthRouteConfig(BountyRouteConfig):
    def __init__(
        self,
        answer: Optional[Union[str, BountyAnswerConfig]],
        startNode: Optional[str],
        firstSegment: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment],
        *segments: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment]
    ) -> None:
        super().__init__(answer)
        self.startNode = startNode
        self.segments = [PathOfLengthRouteSegment.fromInstanceOrTuple(firstSegment)] + \
            [PathOfLengthRouteSegment.fromInstanceOrTuple(s) for s in segments]
        self.allowDuplicateEntries = bbConfig.pathOfLengthRouteConfig_allowDuplicateNodes
        self.nodeGenerationAttempts = bbConfig.pathOfLengthRouteConfig_nodeGenerationAttempts

    def generate(self) -> Union[Tuple[List[str], str], str]:
        graph = {
            k: v
            for k, v in cast(Dict[str, "bbSystem.System"], bbData.builtInSystemObjs).items()
            if v.hasJumpGate()
        }

        segmentsWithSystems: List[Tuple[bbSystem.System, int]] = []
        
        if self.startNode is not None and not any(s.nextNode is None for s in self.segments):
            startNode = self.startNode
            for segment in self.segments:
                segmentsWithSystems.append((graph[cast(str, segment.nextNode)], segment.segmentLength))
        else:
            systemChoices = list(graph.keys())

            if self.startNode is not None:
                startNode = self.startNode
            else:
                startNode = random.choice(systemChoices)
                if self.segments[0].nextNode is not None:
                    attempt = 1
                    while attempt < self.nodeGenerationAttempts:
                        routeAttempt = lib.pathfinding.pathOfLength(
                            graph,
                            startNode,
                            self.segments[0].nextNode,
                            self.segments[0].segmentLength,
                            excludeSystems=[] if self.allowDuplicateEntries else [s[0].name for s in segmentsWithSystems])
                        
                        if routeAttempt is not None:
                            break

                        systemChoices.remove(startNode)
                        startNode = random.choice(systemChoices)
                        attempt += 1

                    if attempt == self.nodeGenerationAttempts:
                        return f"Failed to generate node #0. Could not find route to {self.segments[0].nextNode} " + \
                                f"from any of {self.nodeGenerationAttempts} randomly selected systems"

            for i, segment in enumerate(self.segments):
                if segment.nextNode is not None:
                    segmentsWithSystems.append((graph[segment.nextNode], segment.segmentLength))
                    continue
                
                previousNode = startNode if i == 0 else segmentsWithSystems[i - 1][0].name
                node = random.choice(systemChoices)

                attempt = 1
                while attempt < self.nodeGenerationAttempts:
                    routeAttempt = lib.pathfinding.pathOfLength(
                        graph,
                        previousNode,
                        node,
                        segment.segmentLength,
                        excludeSystems=[] if self.allowDuplicateEntries else [s[0].name for s in segmentsWithSystems])
                    
                    if routeAttempt is not None:
                        break

                    systemChoices.remove(node)
                    node = random.choice(systemChoices)
                    attempt += 1

                if attempt == self.nodeGenerationAttempts:
                    return f"Failed to generate node #{i}. Could not find route from {previousNode} " + \
                            f"to any of {self.nodeGenerationAttempts} randomly selected systems, " + \
                            ("allowing duplicates" if self.allowDuplicateEntries else "disallowing duplicates")
                
                segmentsWithSystems.append((graph[node], segment.segmentLength))

        previousNode = graph[startNode]
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
        knownNodes = ([self.startNode] if self.startNode is not None else []) + \
            [s.nextNode for s in self.segments if s.nextNode is not None]
        
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
