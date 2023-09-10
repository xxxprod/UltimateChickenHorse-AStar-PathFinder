from typing import Generator
from models.level.Block import Block
from models.level.BlockType import BlockType
from models.player.PlayerConstants import PlayerConstants
from utils.Rect import Rect
from rtree.index import Index as RTree
from utils.Vec import Vec
from utils.tools import *

class BlockMap:
    def __init__(self, blocks: Generator[Block,None,None], resizeGoals) -> None:
        self.blocks = list(blocks)
        self.rtree = None
        self.__initializeRtree()
        if resizeGoals:
            goalBlocks = self.getGoals()
            for goalBlock in goalBlocks:
                goalBlock.position += Vec([1, 1])
                goalBlock.size -= Vec([2, 2])
        self.__initializeRtree()

    def fromLevelData(levelData: pd.DataFrame, resizeGoals=True) -> 'BlockMap':
        def createBlock(row):
            type = BlockType[row.Type]
            block = Block(
                id=row.name, 
                type=type, 
                position=Vec([row.X, row.Y]),
                size=Vec([row.Width, row.Height])
            )
            return block
        levelData = levelData.sort_values(by=['Y', 'X'])
        levelData = levelData.reset_index()
        blocks:list[Block] = levelData.apply(createBlock, axis=1)
        return BlockMap(blocks, resizeGoals)
    
    def getSpawn(self) -> Block:
        return next(self.findBlocks(blockTypes=[BlockType.Spawn]))
    
    @property
    def startPosition(self) -> Vec:
        return self.getSpawn().rect.bottomCenter
    
    def getGoals(self) -> list[Block]:
        return list(self.findBlocks(blockTypes=[BlockType.Goal]))
    
    @property
    def goalPositions(self):
        return [goal.rect.center for goal in self.getGoals()]

    
    def findBlocks(self, rectangles=None, blockTypes: list[BlockType] = None) -> Generator[Block,None,None]:
        if rectangles is None:
            rectangles = [self.rtree.bounds]
        elif type(rectangles) == tuple:
            rectangles = [rectangles]
        elif type(rectangles) == Rect:
            rectangles = [rectangles]
        for coord in rectangles:
            ids = self.rtree.intersection(coord)
            for id in ids:
                block = self.blocks[id]
                if blockTypes is None or block.type.containsAny(blockTypes):
                    yield block

    def removeEnclosedBlocks(self) -> 'BlockMap':        
        blocks = list(filter(self.__hasOpenSide, self.blocks))
        for id, block in enumerate(blocks):
            block.id = id
        return BlockMap(blocks)
    
    def __hasOpenSide(self, block: Block) -> bool:
        contactBlockTypes = [BlockType.Block, BlockType.LevelBorder, BlockType.Death]
        blockRect = block.rect
        contactBlocks = list(self.findBlocks(blockRect.resize(0.1), contactBlockTypes))

        topOverlaps = []
        bottomOverlaps = []
        leftOverlaps = []
        rightOverlaps = []

        if block.id == 20:
            pass

        for other in contactBlocks:
            if other.id == block.id:
                continue
            otherRect = other.rect
            if otherRect.intersects(blockRect.resize(Vec([-0.1, 0])).offset(Vec([0, 0.5]))):
                topOverlaps.append((otherRect.x1, otherRect.x2))
            elif otherRect.intersects(blockRect.resize(Vec([-0.1, 0])).offset(Vec([0, -0.5]))):
                bottomOverlaps.append((otherRect.x1, otherRect.x2))
            elif otherRect.intersects(blockRect.resize(Vec([0, -0.1])).offset(Vec([0.5, 0]))):
                rightOverlaps.append((otherRect.y1, otherRect.y2))
            elif otherRect.intersects(blockRect.resize(Vec([0, -0.1])).offset(Vec([-0.5, 0]))):
                leftOverlaps.append((otherRect.y1, otherRect.y2))

        def isFullyOverlapped(overlaps:list, blockStart, blockEnd):
            if len(overlaps) == 0:
                return False
            
            overlaps.sort(key=lambda x: x[0])
            length = 0
            for (start, end) in overlaps:
                if start > (blockStart + length):
                    break
                if end > (blockStart + length):
                    length = end - blockStart

            return length >= blockEnd - blockStart       
            

        topOverlapped = isFullyOverlapped(topOverlaps, blockRect.x1, blockRect.x2)
        bottomOverlapped = isFullyOverlapped(bottomOverlaps, blockRect.x1, blockRect.x2)
        leftOverlapped = isFullyOverlapped(leftOverlaps, blockRect.y1, blockRect.y2)
        rightOverlapped = isFullyOverlapped(rightOverlaps, blockRect.y1, blockRect.y2)
        
        return not (
            topOverlapped and 
            bottomOverlapped and 
            leftOverlapped and 
            rightOverlapped
        )

    def __initializeRtree(self):
        if self.rtree is not None:
            self.rtree.close()

        self.rtree = RTree()
        for block in self.blocks:
            self.rtree.insert(block.id, block.rect)
            

    def __repr__(self) -> str:
        return f'BlockMap ({len(self.blocks)})'
        