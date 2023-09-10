from models.level.BlockType import BlockType
from utils.Rect import Rect
from utils.Vec import Vec


class Block:
    def __init__(self, id, type: BlockType, position: Vec, size: Vec):
        self.id = id
        self.type = type
        self.position = position
        self.size = size

    @property
    def rect(self) -> Rect:
        (x, y) = self.position
        (w, h) = self.size
        return Rect([x, y, x + w, y + h])
    
    def intersects(self, other: 'Block') -> bool:
        return self.rect.intersects(other.rect)
    

    def __repr__(self) -> str:
        return f'{self.type.name} ({self.id}) [{self.position}, {self.size}]'