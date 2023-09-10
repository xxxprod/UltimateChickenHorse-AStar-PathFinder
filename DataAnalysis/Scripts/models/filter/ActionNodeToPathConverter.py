from typing import Generator
from models.actions.JumpActionNode import JumpActionNode
from models.path.ActionPath import ActionPath
from models.path.ActionPathNode import ActionPathNode
from models.path.ActionPathSegment import ActionPathSegment
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerCollision import PlayerCollision
from utils.Vec import Vec


class ActionNodeToPathConverter:
    def __init__(self, parentPath: ActionPath):
        self.parentPath = parentPath

    def __call__(self, actionNodes: Generator[JumpActionNode,None,None]) -> Generator[ActionPath,None,None]:

        startPos = self.parentPath.endPos

        for actionNode in actionNodes:
            pathNodes = []

            for node in actionNode.branchNodes:
                pathNode = ActionPathNode(
                    action=node.action, 
                    velocity=node.velocity, 
                    position=startPos + node.position, 
                    collision=PlayerCollision.Nothing
                )
                pathNodes.append(pathNode)

            yield self.parentPath.extend(ActionPathSegment(pathNodes), ActionPathConnectionType.Undefined)