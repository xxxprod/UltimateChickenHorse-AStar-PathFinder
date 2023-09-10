import enum

class BlockSurfaceType(enum.Enum):
    Empty = 0
    Top = 1
    Bottom = 2
    Left = 4
    Right = 8
    TopRight = 9
    TopLeft = 5
    BottomRight = 10
    BottomLeft = 6

    def addType(self, type: 'BlockSurfaceType'):
        return BlockSurfaceType(self.value | type.value)

    def isType(self, type: 'BlockSurfaceType', strict=False):
        if strict:
            return self.value == type.value            
        return (self.value & type.value) == type.value
    
    def getTypes(self):
        return [bit for bit in BlockSurfaceType if bit.value <= 8 and self.isType(bit)]
    
    def __repr__(self) -> str:
        return self.name