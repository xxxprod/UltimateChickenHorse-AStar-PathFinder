from enum import Enum


class ActionPathConnectionType(Enum):
    Undefined = 0
    OnGround = 1
    TouchedGround = 2
    OnWall = 3
    TouchedWall = 4