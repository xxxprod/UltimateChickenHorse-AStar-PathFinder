from models.actions.JumpActionNodeList import JumpActionNodeList
from models.actions.JumpActionNodeMap import JumpActionNodeMap
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.filter.ActionNodeFilter import ActionNodeFilter
from models.filter.JumpBlockCollisionFilter import JumpBlockCollisionFilter
from models.filter.BlockContactFilter import BlockContactFilter
from models.level.BlockMap import BlockMap
from models.level.BlockType import BlockType
from models.filter.ActionNodeToPathConverter import ActionNodeToPathConverter
from models.path.ActionPath import ActionPath
from models.path.ActionPathConnectionSource import ActionPathConnectionSource
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerCollision import PlayerCollision
from utils.Vec import Vec
from typing import Generator


class ActionPathJumpConnectionSource(ActionPathConnectionSource):
    def __init__(
            self, name, 
            blockMap: BlockMap, 
            actionNodes: JumpActionNodeList, 
            pathState: ActionPathConnectionType,
            startVX: HorizontalVelocityState=None, 
            collision: PlayerCollision = None,
            forceCreate=False):
        self.name = f'JumpSource_{name}_{pathState.name}_{startVX.name if startVX is not None else "Any"}_{collision.name if collision is not None else "Any"}'
        self.blockMap = blockMap
        self.actionNodes = actionNodes
        self.jumpMap = JumpActionNodeMap(
            self.name, 
            self.actionNodes,
            interpolateSteps=0, 
            forceCreate=forceCreate
        )
        self.pathState = pathState
        self.collision = collision
        self.startVX = startVX
        blocks = self.blockMap.findBlocks(blockTypes=[BlockType.Block, BlockType.Goal])
        deaths = self.blockMap.findBlocks(blockTypes=[BlockType.Death, BlockType.LevelBorder])
        self.blockRects = [block.rect for block in blocks]
        self.deathRects = [death.rect for death in deaths]

    def __call__(self, path: ActionPath) -> Generator[ActionPath, None, None]:
        if path.connectionType != self.pathState:
            return

        if self.startVX is not None and not path.horizontalVelocityState.isSet(self.startVX):
            return
        
        if self.collision is not None and not path.lastCollision.isSet(self.collision):
            return

        pos = path.endPos
        offset = Vec([-pos[0], -pos[1]])
        blockRects = [r.offset(offset) for r in self.blockRects]
        deathRects = [r.offset(offset) for r in self.deathRects]
        
        blockContactFilter = BlockContactFilter(self.jumpMap, blockRects)
        deathContactFilter = BlockContactFilter(self.jumpMap, deathRects, invert=True)
        pathConverter = ActionNodeToPathConverter(path)
        collisionFilter = JumpBlockCollisionFilter(self.blockMap)

        blockContacts = blockContactFilter(self.actionNodes.nodes)
        blockContacts = deathContactFilter(blockContacts)
        pathCandidates = pathConverter(blockContacts)
        nextPaths = collisionFilter(pathCandidates)
        
        return nextPaths
