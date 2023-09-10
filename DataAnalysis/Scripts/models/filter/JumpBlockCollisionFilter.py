from functools import reduce
from models.actions.JumpActionNode import JumpActionNode
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.level.Block import Block
from models.level.BlockMap import BlockMap
from models.level.BlockType import BlockType
from models.path.ActionPath import ActionPath
from models.path.ActionPathCache import ActionPathCache
from models.path.ActionPathNode import ActionPathNode
from models.path.ActionPathSegment import ActionPathSegment
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerAction import PlayerAction
from models.player.PlayerCollision import PlayerCollision


import math
from typing import Generator
from models.player.PlayerConstants import PlayerConstants
from utils.Rect import Rect

from utils.Vec import Vec
from utils.tools import getOrAdd


class JumpBlockCollisionFilter:
    def __init__(self, blockMap: BlockMap, reduceCollisionPadding: float = 0.0001):
        self.blockMap = blockMap
        self.reduceCollisionPadding = reduceCollisionPadding
        self.contactBlockTypes=[BlockType.Block, BlockType.Goal]
        self.collisionBlockTypes=[BlockType.Block, BlockType.Death, BlockType.LevelBorder]


    def __call__(self, paths: Generator[ActionPath,None,None]) -> Generator[ActionPath,None,None]:

        for path in paths:
            segment = path.segment

            if len(segment) < 2:
                continue

            if self.__hasCollisionsInFrames(segment):
                continue

            collisions = self.__findCollidingBlocks(segment)

            if PlayerCollision.Goal in collisions:
                segment.lastNode.collision = PlayerCollision.Goal
                yield path
                continue

            if PlayerCollision.Ceiling in collisions:
                continue
            
            leftWallCollision = PlayerCollision.LeftWall in collisions
            rightWallCollision = PlayerCollision.RightWall in collisions

            if leftWallCollision and rightWallCollision:
                continue

            if PlayerCollision.Ground in collisions:

                if leftWallCollision or rightWallCollision:
                    continue

                movement = collisions[PlayerCollision.Ground]
                self.__updateSegment(segment, movement, PlayerCollision.Ground)
                path.connectionType = ActionPathConnectionType.TouchedGround

                if segment.lastNode.velocity.y < PlayerConstants.minGroundContactVelocity:
                    yield path
                continue

                        
            if leftWallCollision:

                movement = collisions[PlayerCollision.LeftWall]
                self.__updateSegment(segment, movement, PlayerCollision.LeftWall)
                path.connectionType = ActionPathConnectionType.TouchedWall
                if segment.lastNode.velocity.x < -PlayerConstants.minHorizontalContactVelocity:
                    yield path
                
            elif rightWallCollision:
                movement = collisions[PlayerCollision.RightWall]
                self.__updateSegment(segment, movement, PlayerCollision.RightWall)
                path.connectionType = ActionPathConnectionType.TouchedWall
                if segment.lastNode.velocity.x > PlayerConstants.minHorizontalContactVelocity:
                    yield path

            else:
                # no collisions
                continue

    def __updateSegment(self, segment: ActionPathSegment, movement: Vec, collision: PlayerCollision):
        lastNode = segment.lastNode
        parentNode = segment.parentNode
        lastNode.collision = collision
        lastNode.velocity = movement * 60
        lastNode.position = parentNode.position + movement
        lastNode.action = lastNode.action.unset(PlayerAction.Jump)
        parentNode.action = parentNode.action.unset(PlayerAction.Jump)

    def __findCollidingBlocks(self, segment) -> dict[BlockType, list[Block]]:
        playerRect = PlayerConstants.playerRect.offset(segment.endPos)
        playerRect = playerRect.resize(-self.reduceCollisionPadding)
        blocks = self.blockMap.findBlocks(playerRect, self.contactBlockTypes)
        
        collisions = dict[PlayerCollision, list[Block]]()

        for block in blocks:
            (collision, movement) = self.__checkCollisions(segment, block)
            if collision is not None:
                collisions[collision] = movement

        return collisions
    

    def __checkCollisions(self, segment: ActionPathSegment, blockObj: Block):
        
        lastNode = segment.lastNode
        
        if blockObj.type == BlockType.Goal:
            return PlayerCollision.Goal, lastNode.deltaPos
        
        r_current = PlayerConstants.playerRect.offset(lastNode.position)
        r_parent = PlayerConstants.playerRect.offset(segment.pathNodes[-2].position)
        block = blockObj.rect.resize(self.reduceCollisionPadding)
        
        isMovingUp = r_current.y1 > r_parent.y1
        isMovingDown = r_current.y1 < r_parent.y1
        isMovingRight = r_current.x1 > r_parent.x1
        isMovingLeft = r_current.x1 < r_parent.x1

        if isMovingUp:
            intersectsWithBlock = r_parent.y2 < block.y1 and r_current.y2 > block.y1
            if intersectsWithBlock:
                return PlayerCollision.Ceiling, Vec([lastNode.deltaPos.x, block.y1 - r_parent.y2])
        elif isMovingDown:
            intersectsWithBlock = r_parent.y1 > block.y2 and r_current.y1 < block.y2
            if intersectsWithBlock:
                return PlayerCollision.Ground, Vec([lastNode.deltaPos.x, block.y2 - r_parent.y1])
        
        if isMovingRight:
            intersectsWithBlock = r_parent.x2 < block.x1 and r_current.x2 > block.x1
            if intersectsWithBlock:
                return PlayerCollision.RightWall, Vec([block.x1 - r_parent.x2, lastNode.deltaPos.y])
        elif isMovingLeft:
            intersectsWithBlock = r_parent.x1 > block.x2 and r_current.x1 < block.x2
            if intersectsWithBlock:
                return PlayerCollision.LeftWall, Vec([block.x2 - r_parent.x1, lastNode.deltaPos.y])
            
        return None, None
    

    def __hasCollisionsInFrames(self, segment: ActionPathSegment):
        
        startFrame = PlayerConstants.frameCollisionStartFrame
        endFrame = PlayerConstants.frameCollisionEndFrame        
        playerRect = PlayerConstants.playerRect.resize(PlayerConstants.frameCollisionOffset)

        if len(segment) < (startFrame - endFrame):
            return False
        
        for node in segment.pathNodes[startFrame:endFrame]:
            rect = playerRect.offset(node.position)
            for _ in self.blockMap.findBlocks(rect, self.collisionBlockTypes):
                return True
            
        return False