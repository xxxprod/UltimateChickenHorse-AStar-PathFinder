from typing_extensions import override
from models.actions.JumpActionNode import JumpActionNode
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.level.BlockMap import BlockMap
from models.level.BlockType import BlockType
from models.path.ActionPath import ActionPath
from models.path.ActionPathConnectionSource import ActionPathConnectionSource
from models.path.ActionPathNode import ActionPathNode
from models.path.ActionPathSegment import ActionPathSegment
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerAction import PlayerAction
from models.player.PlayerCollision import PlayerCollision
from models.player.PlayerConstants import PlayerConstants
from utils.Rect import Rect
from utils.Vec import Vec
from rtree.index import Index

from typing import Generator

from utils.tools import getOrAdd

class PathSurface:
    def __init__(self):
        pass

class ActionPathGroundConnectionSource(ActionPathConnectionSource):

    def __init__(self, blockMap: BlockMap):
        self.blockMap = blockMap


    @override
    def __call__(self, path: ActionPath) -> Generator[ActionPath, None, None]:
        if path.connectionType != ActionPathConnectionType.TouchedGround:
            return
        
        pathNode = path.segment.lastNode
        
        onGround, wallContact, goalContact = self.__checkCollisions(pathNode.position, pathNode.velocity)

        if not onGround:
            return
        
        if pathNode.horizontalVelocityState.isSet(HorizontalVelocityState.Idle):
            stopPath = self.__generateStopPath(path)
            yield stopPath
            for leftPath in self.__generateAccelerationPath(stopPath, PlayerAction.SprintLeft, generateReversePath=True):
                yield leftPath
            for rightPath in self.__generateAccelerationPath(stopPath, PlayerAction.SprintRight, generateReversePath=True):
                yield rightPath
        elif pathNode.horizontalVelocityState.isSet(HorizontalVelocityState.Left):
            for leftPath in self.__generateAccelerationPath(path, PlayerAction.SprintLeft, generateReversePath=True):
                yield leftPath
        elif pathNode.horizontalVelocityState.isSet(HorizontalVelocityState.Right):
            for rightPath in self.__generateAccelerationPath(path, PlayerAction.SprintRight, generateReversePath=True):
                yield rightPath


    def __generateAccelerationPath(self, path: ActionPath, action: PlayerAction, generateReversePath=False):
        
        sign = (1 if action == PlayerAction.SprintRight else -1)
        maxVelocity = PlayerConstants.maxSprintVelocity * sign
        acceleration = PlayerConstants.sprintAcceleration * sign


        path = path.copy()
        pathNode = path.segment.lastNode
        pathNode.action = pathNode.action.set(action)
        
        if len(path.segment) > 1:
            parentNode = path.segment.parentNode
            parentNode.action = parentNode.action.set(action)
            vx = parentNode.velocity.x + acceleration
            if abs(vx) > abs(maxVelocity):
                vx = maxVelocity
            pathNode.velocity = Vec([vx, pathNode.velocity.y])
            pathNode.position = parentNode.position + pathNode.deltaPos


        pathNodes = list[ActionPathNode]([pathNode])

        while abs(pathNode.velocity.x) < abs(maxVelocity):

            vx = pathNode.velocity.x + acceleration
            if abs(vx) > abs(maxVelocity):
                vx = maxVelocity

            velocity = Vec([vx, 0])
            position = pathNode.position + velocity / 60

            onGround, wallContact, goalContact = self.__checkCollisions(position, velocity)

            if goalContact:
                pathNode = ActionPathNode(pathNode.action, velocity, position, PlayerCollision.Goal)
                pathNodes = pathNodes + [pathNode]
                yield path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.Undefined)
                return

            if not onGround:
                return

            pathNode = ActionPathNode(pathNode.action, velocity, position, PlayerCollision.Ground)
            pathNodes = pathNodes + [pathNode]
            if len(pathNodes) > 1:
                yield self.__generateStopPath(path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.OnGround))

            if wallContact:
                return



        if len(pathNodes) > 1:
            nextPath = path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.OnGround)
            stopPath = self.__generateStopPath(nextPath)
            if generateReversePath:
                yield from self.__generateAccelerationPath(stopPath, action.invert())
            yield nextPath
        
                
        coyoteTime = 0
        while coyoteTime < PlayerConstants.coyoteTime:
            
            velocity = Vec([maxVelocity, 0])
            position = pathNode.position + velocity / 60
            
            onGround, wallContact, goalContact = self.__checkCollisions(position, velocity)
            
            if goalContact:
                pathNode = ActionPathNode(pathNode.action, velocity, position, PlayerCollision.Goal)
                pathNodes = pathNodes + [pathNode]
                yield path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.Undefined)
                return
            
            if not onGround:
                coyoteTime += 1
            else:
                coyoteTime = 0
            
            pathNode = ActionPathNode(pathNode.action, velocity, position, PlayerCollision.Ground)
            pathNodes = pathNodes + [pathNode]

            # if still fully on ground yield to enable jumps
            if coyoteTime == 0:
                nextPath = path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.OnGround)
                stopPath = self.__generateStopPath(nextPath)
                yield stopPath
                if generateReversePath:
                    yield from self.__generateAccelerationPath(stopPath, action.invert())

            # skip locations where coyote time is 1 or 2 as this can cause unexpected jump boost behavior 
            if coyoteTime == 0 or coyoteTime > 2:
                nextPath = path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.OnGround)
                yield nextPath

            if wallContact:
                return
            


    def __generateStopPath(self, path: ActionPath):

        path = path.copy()
        lastNode = path.segment.lastNode
        
        if abs(lastNode.velocity.x) > 0:
            lastNode.action = lastNode.action.set(PlayerAction.Down)

        lastNode = lastNode.copy()
        lastNode.action = PlayerAction.Nothing
        lastNode.velocity = Vec.empty()
        path.segment.pathNodes.extend([lastNode] * 2)
        path.connectionType = ActionPathConnectionType.OnGround
        return path
    

    def __checkCollisions(self, position: Vec, velocity: Vec):
        rect = PlayerConstants.playerRect.offset(position)
        
        groundRect = Rect([rect.center.x, rect.y1, rect.center.x, rect.y1]).offset(Vec([0, -0.5]))
        
        if velocity.x > 0:
            wallTestOffset = Vec([PlayerConstants.groundCollisionPadding_left_right, 0])
        else: 
            wallTestOffset = Vec([-PlayerConstants.groundCollisionPadding_left_right, 0])

        wallRect = rect.offset(wallTestOffset)
        

        groundBlocks = self.blockMap.findBlocks(groundRect, blockTypes=[BlockType.Block])
        wallBlocks = self.blockMap.findBlocks(wallRect, blockTypes=[BlockType.Block, BlockType.Death, BlockType.LevelBorder])
        goalBlocks = self.blockMap.findBlocks(rect, blockTypes=[BlockType.Goal])

        onGround = next(groundBlocks, None) is not None
        wallContact = next(wallBlocks, None) is not None
        goalContact = next(goalBlocks, None) is not None

        return onGround, wallContact, goalContact