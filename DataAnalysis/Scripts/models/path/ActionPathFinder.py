import time
from typing import Callable, Generator

from sortedcontainers import SortedList
from models.actions.JumpActionNode import JumpActionNode

from models.path.ActionPath import ActionPath
from models.path.ActionPathCache import ActionPathCache
from models.path.ActionPathConnectionSource import ActionPathConnectionSource
from models.path.ActionPathHeuristic import ActionPathHeuristic
from models.path.ActionPathNode import ActionPathNode
from models.path.ActionPathSegment import ActionPathSegment
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerAction import PlayerAction
from models.player.PlayerCollision import PlayerCollision
from models.player.PlayerConstants import PlayerConstants
from utils.Vec import Vec

class ActionPathFinder:
    def __init__(self, 
            heuristics: ActionPathHeuristic, 
            pathCache: ActionPathCache,
            connectionSources: list[ActionPathConnectionSource],
            nextPathCallback: Callable[[ActionPath], None] = None,
            ):
        
        ActionPath.resetIds()
        ActionPathSegment.resetIds()

        self.heuristics = heuristics
        self.pathCache = pathCache
        self.connectionSources = connectionSources
        self.nextPathCallback = nextPathCallback if nextPathCallback is not None else lambda path: None
        
        self.queue = [self.__createStartPath()]
        self.foundPaths = SortedList(key=lambda path: len(path)) 
        self.costWeight = 0.5
        self.totalSearchTime = 0
        self.skipped = 0
        self.iteration = 0

    
    def findNextPath(self, costWeight: float, maxTime: float=None) -> ActionPath:
        if maxTime is None:
            maxTime = 999999

        self.costWeight = costWeight
        searchStartTime = time.time()
        
        self.queue = SortedList(self.queue, key=lambda path: path.getCost(self.costWeight))

        print(f'Starting search: {self.__getStateString()}')
        
        while len(self.queue) > 0:
            self.iteration += 1
            searchTime = self.__getTime(searchStartTime)

            if searchTime > maxTime:
                self.totalSearchTime += searchTime
                return None

            nextPath: ActionPath = self.queue.pop(0)
            
            self.nextPathCallback(nextPath)

            for path in self.__getConnections(nextPath):

                if self.touchesGoal(path):
                    self.totalSearchTime += searchTime
                    print(f'Path found {self.__getStateString()}')
                    self.foundPaths.add(path)
                    self.nextPathCallback(path)
                    return path

                self.queue.add(path)
        
        return None

    def touchesGoal(self, path: ActionPath):
        if path.segment.lastNode.collision == PlayerCollision.Goal:
            return True
        return False

    def __getConnections(self, path: ActionPath) -> Generator[ActionPath, None, None]:       
        for connectionSource in self.connectionSources:
            nextPaths = connectionSource(path)
            if nextPaths is None:
                continue

            for nextPath in nextPaths:
                if self.pathCache.hasSeenPath(nextPath):
                    self.skipped += 1
                    continue
                nextPath.h = self.heuristics.getGoalDistance(nextPath.endPos)
                yield nextPath
    
    
    def __createStartPath(self) -> ActionPath:
        startPos = self.heuristics.blockMap.startPosition
        startNode = ActionPathNode(PlayerAction.Nothing, Vec([0, 0]), startPos, collision=PlayerCollision.Ground)
        startSegment = ActionPathSegment([startNode])
        startPath = ActionPath(startSegment, connectionType=ActionPathConnectionType.TouchedGround, parent=None)
        startPath.h = self.heuristics.getGoalDistance(startPos)
        return startPath
            
    def __getTime(self, startTime):
        return round(time.time() - startTime, 2)
    
    def __repr__(self):
        return f'ActionPathFinder {self.__getStateString()}'
    
    def __getStateString(self):
        bestLength = str(self.pathCache.bestPathLength) if self.pathCache.bestPathLength < 999999 else 'None'
        return (
            f'(iteration={self.iteration}, ' + 
            f'searchTime={round(self.totalSearchTime, 2)}, ' +
            f'heur_f={round(self.costWeight, 2)}, '+
            f'queue={len(self.queue)}, ' +
            f'seen={len(self.pathCache.seenPathLengths)}, ' +
            f'skipped={self.skipped}, ' +
            f'best={bestLength})'
        )


