from enum import Enum


class PlayerCollision(Enum):
    Nothing     = 0x00
    Ground      = 0x01
    Wall        = 0x02
    Ceiling     = 0x04
    Left        = 0x10
    Right       = 0x20
    Goal        = 0x40
    
    LeftWall    = Left | Wall
    RightWall   = Right | Wall
    
    GroundLeftWall = Ground | LeftWall
    GroundRightWall = Ground | RightWall

    def isSet(self, collision: 'PlayerCollision') -> bool:
        return (self.value & collision.value) == collision.value
    
    def set(self, collision: 'PlayerCollision') -> 'PlayerCollision':
        return PlayerCollision(self.value | collision.value)