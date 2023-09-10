from enum import Enum


class BlockType(Enum):
    Block =             0x001
    Goal =              0x002
    Death =             0x004
    LevelBorder =       0x008
    LeftBorder =        0x010 | LevelBorder
    RightBorder =       0x020 | LevelBorder
    TopBorder =         0x040 | LevelBorder
    BottomBorder =      0x080 | LevelBorder
    DeathPit =          Death | BottomBorder
    Spawn =             0x100

    def isType(self, blockType: 'BlockType'):
        if type(blockType) == BlockType:
            blockType = blockType.value        
        return (self.value & blockType) == blockType

    def containsAny(self, blockTypes: list['BlockType']):
        for blockType in blockTypes:
            if self.isType(blockType):
                return True
        return False