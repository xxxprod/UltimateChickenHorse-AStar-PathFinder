from enum import Enum


class MotionState(Enum):
    OnGround = 0
    InAir = 1
    OnWall = 2
    
    def __repr__(self) -> str:
        return self.name