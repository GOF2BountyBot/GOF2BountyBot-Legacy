from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional, Tuple, Union, cast

from BB.bbObjects.bounties.bountyRoutes.bountyAnswerConfig import BountyAnswerConfig
if TYPE_CHECKING:
    from .. import bbSystem

from enum import Enum
from abc import ABC, abstractmethod

from ....bbConfig import bbData, bbConfig
from .... import lib
from ....baseClasses.bbSerializable import bbSerializable
from .bountyAnswerConfig import *
from .nodeGenerator import *

def getStarChartOnlyWithJumpGates():
    return {
        k: v
        for k, v in cast(Dict[str, "bbSystem.System"], bbData.builtInSystemObjs).items()
        if v.hasJumpGate()
    }


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

    def __init__(
        self,
        answer: Optional[Union[str, BountyAnswerConfig]]
    ) -> None:
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
    """Find the shortest paths between nodes.
    
    :param answer: The answer. Give as `None` to use a uniformally random choice. Can be given either as a system name, or a `BountyAnswerConfig`.
    :param Optional[str] startNode: The first system in the route. Give as `None` to use a uniformally random choice
    :param Optional[str] node2: The second system in the route. Give as `None` to use a uniformally random choice
    :param Optional[str] nodes: The remaining systems in the route. Give as `None` to use a uniformally random choice
    """
    @overload
    def __init__(
        self,
        answer: Optional[Union[str, BountyAnswerConfig]],
        startNode: Optional[str],
        node2: Optional[str],
        /,
        *nodes: Optional[str],
    ) -> None: ...

    @overload
    def __init__(
        self,
        nodeGeneratorFactory: NodeGeneratorFactory,
        answer: Optional[Union[str, BountyAnswerConfig]],
        startNode: Optional[str],
        node2: Optional[str],
        /,
        *nodes: Optional[str],
    ) -> None: ...
    
    def __init__(
        self,
        answerOrNodeGeneratorFactory: Union[NodeGeneratorFactory, Optional[Union[str, BountyAnswerConfig]]],
        startNodeOrAnswer: Union[Optional[Union[str, BountyAnswerConfig]], Optional[str]],
        node2OrStartNode: Optional[str],
        *nodes: Optional[str]
    ) -> None:
        nodeGeneratorFactory, answer, startNode, node2, nodes = self._validateConstructorArguments(
            bbConfig.shortestPathRouteConfig_nodeGenerationAttempts,
            answerOrNodeGeneratorFactory,
            startNodeOrAnswer,
            node2OrStartNode,
            nodes
        )

        super().__init__(answer)

        self.allowDuplicateEntries = bbConfig.shortestPathRouteConfig_allowDuplicateNodes
        self.nodeGeneratorFactory = nodeGeneratorFactory
        self.nodes = [startNode, node2] + list(nodes)
        self.allowDuplicateEntries = bbConfig.shortestPathRouteConfig_allowDuplicateNodes
        self.nodeGenerationAttempts = bbConfig.shortestPathRouteConfig_nodeGenerationAttempts

    def _validateConstructorArguments(
        self,
        maxNodeGenerationAttempts: int,
        answerOrNodeGeneratorFactory: Union[NodeGeneratorFactory, Optional[Union[str, BountyAnswerConfig]]],
        startNodeOrAnswer: Union[Optional[Union[str, BountyAnswerConfig]], Optional[str]],
        node2OrStartNode: Optional[str],
        nodes: Tuple[Optional[str], ...]
    ) -> Tuple[NodeGeneratorFactory, Optional[Union[str, BountyAnswerConfig]], Optional[str], Optional[str], Tuple[Optional[str], ...]]:
        if isinstance(answerOrNodeGeneratorFactory, NodeGeneratorFactory):
            if startNodeOrAnswer is not None and not isinstance(startNodeOrAnswer, (str, BountyAnswerConfig)):
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    f"use one of the provided overloads. (expected str or {BountyAnswerConfig.__name__} " + \
                    f"for parameter 2, found {type(startNodeOrAnswer).__name__})")
            
            if len(nodes) < 1:
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    "use one of the provided overloads. (expected 'node2' to be given, but nodes was empty")

            nodeGeneratorFactory = answerOrNodeGeneratorFactory
            answer = startNodeOrAnswer
            startNode = node2OrStartNode
            node2 = nodes[0]
            nodes = nodes[1:]
        else:
            if startNodeOrAnswer is not None and not isinstance(startNodeOrAnswer, str):
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    f"use one of the provided overloads. (expected Optional[str] " + \
                    f"for parameter 2, found {type(startNodeOrAnswer).__name__})")
            
            nodeGeneratorFactory = AlwaysUniformNodeGeneratorFactory(maxNodeGenerationAttempts)
            answer = answerOrNodeGeneratorFactory
            startNode = startNodeOrAnswer
            node2 = node2OrStartNode

        return (nodeGeneratorFactory, answer, startNode, node2, nodes)

    def _generateNodes(self, graph: Dict[str, "bbSystem.System"]) -> Union[str, List["bbSystem.System"]]:
        if not any(n is None for n in self.nodes):
            return [graph[cast(str, node)] for node in self.nodes]
        
        systems: List[bbSystem.System] = []
        nodeGenerator = self.nodeGeneratorFactory.create(graph)

        if self.nodes[0] is None:
            node = nodeGenerator.selectAnyNode()
            systems.append(graph[node])

        for i, node in enumerate(self.nodes[1:]):
            if node is not None:
                systems.append(graph[node])
                continue
            
            def validateNode(n: str):
                routeAttempt = lib.pathfinding.bbAStar(
                    systems[i - 1].name,
                    n,
                    graph,
                    excludeSystems=[] if self.allowDuplicateEntries else [s.name for s in systems])
                
                return len(routeAttempt) != 0 and not routeAttempt[0].startswith("!") and not routeAttempt[0].startswith("#")
            
            (nodeSelected, node) = nodeGenerator.selectValidNode(validateNode)

            if not nodeSelected:
                return f"Failed to generate node #{i}: \"{node}\". " + \
                    f"Previous node is {systems[i - 1].name}. " + \
                    "Duplicates " + ("allowed." if self.allowDuplicateEntries else "disallowed.")
            
            systems.append(graph[node])
        
        return systems

    def generate(self) -> Union[Tuple[List[str], str], str]:
        graph = getStarChartOnlyWithJumpGates()

        systems = self._generateNodes(graph)
        if isinstance(systems, str):
            return systems
        
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
    """Find paths of the given lengths between nodes.

    :param answer: The answer. Give as `None` to use a uniformally random choice. Can be given either as a system name, or a `BountyAnswerConfig`.
    :param Optional[str] startNode: The first system in the route. Give as `None` to use a uniformally random choice
    :param firstSegment: The first route segment, defining the next system, and the length of the segment. Give the next node as `None` to use a uniformally random choice
    :param segments: The remaining segments in the route, each defining the next system, and the length of the segment. Give the next node as `None` to use a uniformally random choice
    """
    @overload
    def __init__(
        self,
        answer: Optional[Union[str, BountyAnswerConfig]],
        startNode: Optional[str],
        firstSegment: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment],
        /,
        *segments: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment],
    ) -> None: ...

    @overload
    def __init__(
        self,
        nodeGeneratorFactory: NodeGeneratorFactory,
        answer: Optional[Union[str, BountyAnswerConfig]],
        startNode: Optional[str],
        firstSegment: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment],
        /,
        *segments: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment],
    ) -> None: ...
    
    def __init__(
        self,
        answerOrNodeGeneratorFactory: Union[NodeGeneratorFactory, Optional[Union[str, BountyAnswerConfig]]],
        startNodeOrAnswer: Union[Optional[Union[str, BountyAnswerConfig]], Optional[str]],
        firstSegmentOrStartNode: Union[Optional[str], Union[Tuple[Optional[str], int], PathOfLengthRouteSegment]],
        *segments: Union[Tuple[Optional[str], int], PathOfLengthRouteSegment]
    ) -> None:
        maxNodeGenerationAttempts = bbConfig.pathOfLengthRouteConfig_nodeGenerationAttempts
        self.allowDuplicateEntries = bbConfig.pathOfLengthRouteConfig_allowDuplicateNodes

        nodeGeneratorFactory, answer, startNode, firstSegment, segments = self._validateConstructorArguments(
            maxNodeGenerationAttempts,
            answerOrNodeGeneratorFactory,
            startNodeOrAnswer,
            firstSegmentOrStartNode,
            segments
        )

        super().__init__(answer)

        self.allowDuplicateEntries = bbConfig.pathOfLengthRouteConfig_allowDuplicateNodes
        self.nodeGeneratorFactory = nodeGeneratorFactory
        self.startNode = startNode
        self.segments = [PathOfLengthRouteSegment.fromInstanceOrTuple(firstSegment)] + \
            [PathOfLengthRouteSegment.fromInstanceOrTuple(s) for s in segments]
        
    def _validateConstructorArguments(
        self,
        maxNodeGenerationAttempts: int,
        answerOrNodeGeneratorFactory: Union[NodeGeneratorFactory, Optional[Union[str, BountyAnswerConfig]]],
        startNodeOrAnswer: Union[Optional[Union[str, BountyAnswerConfig]], Optional[str]],
        firstSegmentOrStartNode: Union[Optional[str], Union[Tuple[Optional[str], int], PathOfLengthRouteSegment]],
        segments: Tuple[Union[Tuple[Optional[str], int], PathOfLengthRouteSegment], ...]
    ) -> Tuple[NodeGeneratorFactory, Optional[Union[str, BountyAnswerConfig]], Optional[str], Union[Tuple[Optional[str], int], PathOfLengthRouteSegment], Tuple[Union[Tuple[Optional[str], int], PathOfLengthRouteSegment], ...]]:
        if isinstance(answerOrNodeGeneratorFactory, NodeGeneratorFactory):
            if startNodeOrAnswer is not None and not isinstance(startNodeOrAnswer, (str, BountyAnswerConfig)):
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    f"use one of the provided overloads. (expected str or {BountyAnswerConfig.__name__} " + \
                    f"for parameter 2, found {type(startNodeOrAnswer).__name__})")
            
            if firstSegmentOrStartNode is not None and not isinstance(firstSegmentOrStartNode, str):
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    f"use one of the provided overloads. (expected Optional[str] " + \
                    f"for parameter 3, found {type(firstSegmentOrStartNode).__name__})")
            
            if len(segments) < 1:
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    "use one of the provided overloads. (expected 'firstSegment' to be given, but segments was empty")

            nodeGeneratorFactory = answerOrNodeGeneratorFactory
            answer = startNodeOrAnswer
            startNode = firstSegmentOrStartNode
            firstSegment = segments[0]
            segments = segments[1:]
        else:
            if startNodeOrAnswer is not None and not isinstance(startNodeOrAnswer, str):
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    f"use one of the provided overloads. (expected Optional[str] " + \
                    f"for parameter 2, found {type(startNodeOrAnswer).__name__})")
            
            if firstSegmentOrStartNode is None or isinstance(firstSegmentOrStartNode, str):
                raise TypeError(
                    "Parameter types do not match known signature, " + \
                    f"use one of the provided overloads. (expected " + \
                    f"Union[Tuple[Optional[str], int], PathOfLengthRouteSegment] " + \
                    f"for parameter 3, found {type(firstSegmentOrStartNode).__name__})")
            
            nodeGeneratorFactory = AlwaysUniformNodeGeneratorFactory(maxNodeGenerationAttempts)
            answer = answerOrNodeGeneratorFactory
            startNode = startNodeOrAnswer
            firstSegment = firstSegmentOrStartNode

        return (nodeGeneratorFactory, answer, startNode, firstSegment, segments)
        
    def _generateSegments(self, graph: Dict[str, "bbSystem.System"]) -> Union[Tuple[str, List[Tuple["bbSystem.System", int]]], str]:
        if self.startNode is not None and not any(s.nextNode is None for s in self.segments):
            return (
                self.startNode,
                [
                    (graph[cast(str, segment.nextNode)], segment.segmentLength)
                    for segment in self.segments
                ]
            )

        segmentsWithSystems: List[Tuple[bbSystem.System, int]] = []
        nodeGenerator = self.nodeGeneratorFactory.create(graph)

        if self.startNode is not None:
            startNode = self.startNode
        elif self.segments[0].nextNode is not None:
            def validateStartNode(n: str) -> bool:
                routeAttempt = lib.pathfinding.pathOfLength(
                    graph,
                    n,
                    cast(str, self.segments[0].nextNode),
                    self.segments[0].segmentLength,
                    excludeSystems=[] if self.allowDuplicateEntries else [s[0].name for s in segmentsWithSystems])
                
                return routeAttempt is not None
            
            (nodeSelected, startNode) = nodeGenerator.selectValidNode(validateStartNode)
            if not nodeSelected:
                return f"Failed to generate node #0: \"{startNode}\". Next node is {self.segments[0].nextNode})."
        else:
            startNode = nodeGenerator.selectAnyNode()
                    

        for i, segment in enumerate(self.segments):
            if segment.nextNode is not None:
                segmentsWithSystems.append((graph[segment.nextNode], segment.segmentLength))
                continue
            
            previousNode = startNode if i == 0 else segmentsWithSystems[i - 1][0].name

            def validateNode(n: str) -> bool:
                routeAttempt = lib.pathfinding.pathOfLength(
                    graph,
                    previousNode,
                    n,
                    segment.segmentLength,
                    excludeSystems=[] if self.allowDuplicateEntries else [s[0].name for s in segmentsWithSystems])
                
                return routeAttempt is not None
            
            (nodeSelected, node) = nodeGenerator.selectValidNode(validateNode)

            if not nodeSelected:
                return f"Failed to generate node #{i}: \"{node}\". " + \
                    f"Previous node is {previousNode}. " + \
                    "Duplicates " + ("allowed." if self.allowDuplicateEntries else "disallowed.")
            
            segmentsWithSystems.append((graph[node], segment.segmentLength))

        return (startNode, segmentsWithSystems)

    def generate(self) -> Union[Tuple[List[str], str], str]:
        graph = getStarChartOnlyWithJumpGates()
        segmentsResult = self._generateSegments(graph)

        if isinstance(segmentsResult, str):
            return segmentsResult

        startNode, segmentsWithSystems = segmentsResult
        previousNode = graph[startNode]
        route = [segmentsWithSystems[0][0].name]

        for segment in segmentsWithSystems:
            nextSegmentEnd, nextSegmentLength = segment
            nextRouteSegment = lib.pathfinding.pathOfLength(
                graph,
                previousNode.name,
                nextSegmentEnd.name,
                nextSegmentLength,
                excludeSystems=route[1:])
            
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
