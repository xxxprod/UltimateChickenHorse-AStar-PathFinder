from models.level.BlockSurface import BlockSurface
from models.level.BlockSurfaceType import BlockSurfaceType
from models.level.LevelModel import *


class BlockSurfaceMap:
    def ____init__(self):
        self.levelModel: LevelModel = None
        self.blockSet: set[tuple[int,int]] = None
        self.deathSet: set[tuple[int,int]] = None
        self.surfaceMap: dict[tuple[int,int], BlockSurface] = None

    def fromLevel(levelModel:LevelModel):
        m = BlockSurfaceMap()

        m.levelModel = levelModel
        m.blockSet = set()
        m.deathSet = set()
        m.surfaceMap = {}
        m.__nextBlockId = 1

        occupiedCells = m.levelModel.getOccupiedCells()
        contactSpace = m.levelModel.floodFill(occupiedCells, m.levelModel.goalPosition)
        s_top, s_bottom, s_left, s_right = m.levelModel.findSurfaces(contactSpace)
        s_blocks = m.levelModel.blocks
        s_traps = m.levelModel.traps

        for idx in m.__getIndices(s_top):
            m.__setCell(idx, BlockSurfaceType.Top)

        for idx in m.__getIndices(s_bottom):
            m.__setCell(idx, BlockSurfaceType.Bottom)

        for idx in m.__getIndices(s_left):
            m.__setCell(idx, BlockSurfaceType.Left)

        for idx in m.__getIndices(s_right):
            m.__setCell(idx, BlockSurfaceType.Right)

        for idx in m.__getIndices(s_blocks):
            m.blockSet.add(idx)
        for idx in m.__getIndices(s_traps):
            m.deathSet.add(idx)

        return m

    def offset(self, offset) -> 'BlockSurfaceMap':

        (dx, dy) = offset
        
        m = BlockSurfaceMap()
        m.levelModel = self.levelModel
        m.blockSet = set([(c[0] - dx, c[1] - dy) for c in self.blockSet])
        m.deathSet = set([(c[0] - dx, c[1] - dy) for c in self.deathSet])
        m.surfaceMap = {(c[0] - dx, c[1] - dy): self.surfaceMap[c] for c in self.surfaceMap}
        m.__nextBlockId = self.__nextBlockId

        return m



    def plotSurfaces(self, figSize=5):

        occupiedCells = self.levelModel.getOccupiedCells()
        contactSpace = self.levelModel.floodFill(occupiedCells, self.levelModel.goalPosition)
        s_top, s_bottom, s_left, s_right = self.levelModel.findSurfaces(contactSpace)
        s_blocks = self.levelModel.blocks
        s_traps = self.levelModel.traps

        self.levelModel.preparePlot('Connecting Surfaces', figsize=(figSize, figSize))
        self.levelModel.plotTensor(s_left, colors=['#aaff00'])
        self.levelModel.plotTensor(s_right, colors=['#aaff00'])
        self.levelModel.plotTensor(s_top, colors=['#55bb00'])
        self.levelModel.plotTensor(s_bottom, colors=['#229900'])
        self.levelModel.plotTensor(s_blocks, colors=['#00aaFF'])
        self.levelModel.plotTensor(s_traps, colors=['#ff0000'])
        
    def __getIndices(self, tensor):
        values = (tensor > 0).nonzero().cpu().numpy().tolist()
        return sorted([(value[1], value[0]) for value in values], key=lambda x: (x[0], x[1]))
    
    def __setCell(self, idx, surfaceType):
        left: BlockSurface = self.__getLeft(idx)
        bottom: BlockSurface = self.__getBottom(idx)

        if left is not None and left.surface.isType(surfaceType):
            cell = getOrAdd(self.surfaceMap, idx, lambda: BlockSurface(left.blockId))
            cell.addSurface(surfaceType)      
        elif bottom is not None and bottom.surface.isType(surfaceType):
            cell = getOrAdd(self.surfaceMap, idx, lambda: BlockSurface(bottom.blockId))
            cell.addSurface(surfaceType)            
        else:
            cell = getOrAdd(self.surfaceMap, idx, lambda: BlockSurface(self.__nextBlockId))
            cell.addSurface(surfaceType)
            self.__nextBlockId += 1

    def __getBottom(self, idx):
        return self.surfaceMap.get((idx[0], idx[1] - 1), None)

    def __getLeft(self, idx):
        return self.surfaceMap.get((idx[0] - 1, idx[1]), None)

    def __repr__(self):
        return f'SurfaceMap: {len(self.surfaceMap)}'
        