from models.actions.JumpActionNode import JumpActionNode
from models.actions.JumpActionNodeList import JumpActionNodeList
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


from typing import Generator


class ActionPathWallConnectionSource(ActionPathConnectionSource):

    def __init__(self, blockMap: BlockMap, 
                 jumpSlideDownNode: JumpActionNode, 
                 dropSlideDownNode: JumpActionNode, 
                 jumpAccelerationList: list):
        self.blockMap = blockMap
        self.jumpSlideDownNode = jumpSlideDownNode
        self.dropSlideDownNode = dropSlideDownNode
        self.jumpAccelerationList = jumpAccelerationList


    def __call__(self, path: ActionPath) -> Generator[ActionPath, None, None]:
        if path.connectionType != ActionPathConnectionType.TouchedWall:
            return
        

        path = path.copy()
        pathNode = path.segment.lastNode
        pathNodes = list[ActionPathNode]([pathNode])
        
        action = PlayerAction.SprintLeft if pathNode.collision == PlayerCollision.LeftWall else PlayerAction.SprintRight
        pathNode.action = action
        path.segment.parentNode.action = action

        
        if pathNode.velocity.y > PlayerConstants.mediumSlideVelocity:
            # jumping must be stopped two frames prior continuing jumping
            # if len(segment) > 2:
            #     segment.pathNodes[-3].action = segment.pathNodes[-3].action.unset(PlayerAction.Jump)
            path.segment.parentNode.action = action

            for vy, acceleration in self.jumpAccelerationList:
                if vy > pathNode.velocity.y:
                    continue

                vy = path.segment.parentNode.velocity.y + acceleration
                vy = max(-20, vy)
                pathNode.velocity = Vec([pathNode.velocity.x, vy])
                pathNode.position = path.segment.parentNode.position + pathNode.deltaPos
                break
            

            onWall, verticalContact, goalContact = self.__checkCollisions(pathNode.position, pathNode.velocity, pathNode.collision)

            if goalContact:
                pathNode.collision = PlayerCollision.Goal
                yield path.extend(ActionPathSegment(pathNodes + [pathNode]), ActionPathConnectionType.Undefined)
                return
        
            if not onWall or verticalContact:
                return
            
            # yield corrected first node to continue with wall jumps 
            if pathNode.velocity.y < PlayerConstants.maxWallContactVerticalVelocity:
                yield path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.OnWall)

        # pathNodes = pathNodes + [pathNode]
        else:
        
            if len(path.segment) > 1:
                parentNode = path.segment.parentNode
                vy = parentNode.velocity.y + PlayerConstants.wallDeceleration
                if vy > PlayerConstants.mediumSlideVelocity:
                    vy = PlayerConstants.mediumSlideVelocity
                pathNode.velocity = Vec([pathNode.velocity.x, vy])
                pathNode.position = parentNode.position + pathNode.deltaPos



            while True:

                vy = pathNode.velocity.y + PlayerConstants.wallDeceleration
                if vy > PlayerConstants.mediumSlideVelocity:
                    vy = PlayerConstants.mediumSlideVelocity

                velocity = Vec([0, vy])
                position = pathNode.position + velocity / 60

                onWall, verticalContact, goalContact = self.__checkCollisions(position, velocity, pathNode.collision)

                if goalContact:
                    pathNode = ActionPathNode(action, velocity, position, PlayerCollision.Goal)
                    yield path.extend(ActionPathSegment(pathNodes + [pathNode]), ActionPathConnectionType.Undefined)
                    return
                
                if verticalContact or not onWall:
                    return

                pathNode = ActionPathNode(action, velocity, position, pathNode.collision)
                pathNodes = pathNodes + [pathNode]
                yield path.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.OnWall)


    def __checkCollisions(self, position: Vec, velocity: Vec, collision: PlayerCollision):
        rect = PlayerConstants.playerRect.offset(position)
        offset = Vec([0, PlayerConstants.wallVerticalCollisionPadding]) if velocity.y > 0 else Vec([0, -PlayerConstants.wallVerticalCollisionPadding])
        verticalRect = rect.offset(offset)

        if velocity.y > 0:
            pBottom = PlayerConstants.wallCollisionPadding_up_bottom
            pTop = PlayerConstants.wallCollisionPadding_up_top
        else:
            pBottom = PlayerConstants.wallCollisionPadding_down_bottom
            pTop = PlayerConstants.wallCollisionPadding_down_top

        wallTestOffset = Vec([-0.5, 0]) if collision == PlayerCollision.LeftWall else Vec([0.5, 0])
        wallRect = Rect([rect.x1, rect.y1 + pBottom, rect.x2, rect.y2 - pTop]).offset(wallTestOffset)

        verticalBlocks = self.blockMap.findBlocks(verticalRect, blockTypes=[BlockType.Block, BlockType.Death, BlockType.LevelBorder])
        wallBlocks = self.blockMap.findBlocks(wallRect, blockTypes=[BlockType.Block])
        goalBlocks = self.blockMap.findBlocks(rect, blockTypes=[BlockType.Goal])

        onWall = next(wallBlocks, None) is not None
        verticalContact = next(verticalBlocks, None) is not None
        goalContact = next(goalBlocks, None) is not None

        return onWall, verticalContact, goalContact