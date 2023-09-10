from models.level.BlockSurfaceType import BlockSurfaceType


class BlockSurface:
    def __init__(self, blockId):
        self.blockId = blockId
        self.surface = BlockSurfaceType.Empty

    def addSurface(self, surface: BlockSurfaceType):
        self.surface = self.surface.addType(surface)

    def equals(self, other: 'BlockSurface'):
        if self.blockId != other.blockId:
            return False
        
        for type in self.surface.getTypes():
            if other.surface.isType(type):
                return True
            
        return False
            

    def __repr__(self):
        return f'BlockCell: {self.blockId} {self.surface}'