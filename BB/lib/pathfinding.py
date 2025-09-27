# TODO: Look into third party library
# TODO: Add failed route lookups to bbLogger (might already be done in bountybot.py)
from __future__ import annotations
from ..bbObjects.bounties import bbSystem
import math
from random import randint
from ..bbConfig import bbData
from typing import Dict, List, Optional, cast, Tuple

class AStarNode(bbSystem.System):
    """A node for use in a* pathfinding.
    TODO: Does this really need to extend bbSystem?

    :var syst: this node's associated bbSystem object.
    :vartype syst: bbSystem
    :var parent: The previous AStarNode in the generated path
    :vartype parent: AStarNode
    :var g: The total distance travelled to get to this node
    :vartype g: float
    :var h: The estimated distance from this node to the nearest goal
    :vartype h: float
    :var f: The node's estimated "value" when picking the next node in the route, equal to g + h
    :vartype f: float
    """
    
    def __init__(self, syst : bbSystem.System, parent : Optional[AStarNode], g : float = 0, h : float = 0):
        """
        :param bbSystem syst: this node's associated bbSystem object.
        :param AStarNode parent: The previous AStarNode in the generated path
        :param float g: The total distance travelled to get to this node (Default 0)
        :param float h: The estimated distance from this node to the nearest goal (Default 0)
        :param float f: The node's estimated "value" when picking the next node in the route, equal to g + h (Default g + h)
        """
        self.syst = syst
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h


def heuristic(start : bbSystem.System, end : bbSystem.System) -> float:
    """Estimate the distance between two bbSystems, using straight line (pythagorean) distance.

    :param bbSystem start: The system to start calculating distance from
    :param bbSystem end: The system to find distance to
    :return: The straight-line distance from start to end
    """
    return math.sqrt((end.coordinates[1] - start.coordinates[1]) ** 2 +
                    (end.coordinates[0] - start.coordinates[0]) ** 2)


def bbAStar(start : str, end : str, graph : Dict[str, bbSystem.System], excludeSystems: Optional[List[str]] = None) -> List[str]:
    """Find the shortest path from the given start bbSystem to the end bbSystem, using the given graph for edges.
    If no route can be found, the string "! " + start + " -> " + end is returned.
    If the max route length (50) is reached, "#" is returned.

    :param str start: The starting system for route generation
    :param str end: The goal system where route generation terminates
    :param dict[str, bbSystem] graph: A dictionary mapping system names to bbSystem objects
    :return: A list containing string system names representing the shortest route from start (the first element) to end (the last element)
    :rtype: list
    """
    if excludeSystems and (start in excludeSystems or end in excludeSystems):
        return ["! " + start + " -> " + end]

    if start == end:
        return [start]
    
    open = [AStarNode(graph[start], None, h=heuristic(graph[start], graph[end]))]
    closed = []
    count = 0

    while open:
        q = open.pop(0)

        count += 1
        if count == 50:
            return ["#"]
        for succName in q.syst.getNeighbours():
            if excludeSystems and succName in excludeSystems:
                continue

            if succName == end:
                closed.append(AStarNode(graph[succName], q))
                route = []
                node = closed[-1]
                while node:
                    route.append(node.syst.name)
                    node = node.parent
                return route[::-1]

            succ = AStarNode(graph[succName], q)
            succ.g = q.g + 1
            succ.h = heuristic(succ.syst, graph[end])
            succ.f = succ.g + succ.h

            betterFound = False
            for existingNode in open + closed:
                if existingNode.syst.coordinates == succ.syst.coordinates and existingNode.f <= succ.f:
                    betterFound = True
            if betterFound:
                continue

            insertPos = len(open)
            for i in range(len(open)):
                if open[i].f > succ.f:
                    if i != 0:
                        insertPos = i -1
                    break
            open.insert(insertPos, succ)

        closed.append(q)

    return ["! " + start + " -> " + end]


def makeRoute(start : str, end : str) -> List[str]:
    """Find the shortest route between two systems.

    :param str start: string name of the starting system. Must exist in bbData.builtInSystemObjs
    :param str end: string name of the target system. Must exist in bbData.builtInSystemObjs
    :return: list of string system names where the first element is start, the last element is end, and all intermediary systems are adjacent
    :rtype: list[str]
    """
    return bbAStar(start, end, bbData.builtInSystemObjs)


def _tryFindColourfulPath(
    curr: bbSystem.System,
    start: bbSystem.System,
    end: bbSystem.System,
    coloured: Dict[str, Tuple[int, bbSystem.System]],
    route: Dict[int, Tuple[int, bbSystem.System]],
    desiredLength: int
) -> Tuple[bool, List[bbSystem.System]]:
    """Try to find a partial, non-cyclical path, of length `desiredLength`, 
    from `start` to `end`, with the partial path beginning at `curr`.

    :param curr: The current node
    :type curr: bbSystem.System
    :param start: The route start
    :type start: bbSystem.System
    :param end: The route end
    :type end: bbSystem.System
    :param coloured: The coloured graph
    :type coloured: Dict[str, Tuple[int, bbSystem.System]]
    :param route: The route so far, from `start` to `curr`
    :type route: Dict[int, Tuple[int, bbSystem.System]]
    :param desiredLength: The desired route length
    :type desiredLength: int
    :return: A bool indicating whether a route was found, alongside the successful route (if found)
    :rtype: Tuple[bool, List[bbSystem.System]]
    """
    if len(route) + 2 == desiredLength:
        if end.name not in curr.neighbours:
            return (False, [])
        
        intermediaryRoute = [s[1] for s in sorted(route.values(), key=lambda pair: pair[0])]
        return (
            True, # answer was found
            [start] + intermediaryRoute + [end] # the final route
        )
    
    for neighbourName in curr.neighbours:
        neighbour = coloured[neighbourName]
        if neighbour[0] not in route and neighbour[1] is not start and neighbour[1] is not end:
            routeCopy = {k: (v[0], v[1]) for k, v in route.items()}
            routeCopy[neighbour[0]] = (len(route), neighbour[1])
            neighbourResult = _tryFindColourfulPath(neighbour[1], start, end, coloured, routeCopy, desiredLength)
            if neighbourResult[0]:
                return neighbourResult

    return (False, [])


def pathOfLength(
    graph: Dict[str, bbSystem.System], 
    startName: str, 
    endName: str, 
    length: int, 
    maxIterations: Optional[int] = None,
    excludeSystems: Optional[List[str]] = None
) -> Optional[Tuple[int, List[bbSystem.System]]]:
    """Try to find a non-cyclical path of length `length` through `graph`, from `startName` to `endName`.

    :param graph: The graph to navigate through
    :type graph: Dict[str, bbSystem.System]
    :param startName: The starting node
    :type startName: str
    :param endName: The ending node
    :type endName: str
    :param length: The route length to find
    :type length: int
    :param maxIterations: An optional limit to the number of graph colourings to attempt, defaults to `length * 40`
    :type maxIterations: Optional[int], optional
    :return: The successful route alongside the number of graph colourations attempted, if a successful route could be found
    :rtype: Optional[Tuple[int, List[bbSystem.System]]]
    """
    if excludeSystems and (startName in excludeSystems or endName in excludeSystems):
        return None

    start = graph[startName]
    end = graph[endName]
    for attemptNumber in range(maxIterations or length * 40):
        # colour nodes
        coloured = {k: (randint(1, length), v) for k, v in graph.items() if not excludeSystems or k not in excludeSystems}
        # traverse
        attempt = _tryFindColourfulPath(start, start, end, coloured, {}, length)
        if attempt[0]:
            return (attemptNumber, attempt[1])
        
    return None
