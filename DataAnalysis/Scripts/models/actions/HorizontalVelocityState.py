from models.actions.MotionState import Enum
from models.player.PlayerAction import Enum


from enum import Enum


class HorizontalVelocityState(Enum):
    Idle =      0x01
    Walk =      0x02
    Sprint =    0x10
    Left =      0x04
    Right =     0x08

    IdleLeft =  Left | Idle
    IdleRight = Right | Idle

    WalkLeft =  Left | Walk
    WalkRight = Right | Walk

    SprintLeft = Left | Sprint
    SprintRight = Right | Sprint

    def isSet(self, velocity):
        return (self.value & velocity.value) == velocity.value

    def set(self, velocity):
        return HorizontalVelocityState(self.value | velocity.value)

    def unset(self, velocity):
        return HorizontalVelocityState(self.value & ~velocity.value)

    def invert(self):
        if self.isSet(HorizontalVelocityState.Right):
            return self.unset(HorizontalVelocityState.Right).set(HorizontalVelocityState.Left)
        elif self.isSet(HorizontalVelocityState.Left):
            return self.unset(HorizontalVelocityState.Left).set(HorizontalVelocityState.Right)
        else:
            return self

    def fromRealVelocity(velocity):
        if velocity < 0:
            return HorizontalVelocityState.fromRealVelocity(-velocity).invert()
        if velocity < 0.01:
            return HorizontalVelocityState.Idle
        elif velocity < 0.5:
            return HorizontalVelocityState.IdleRight
        elif velocity < 12.7:
            return HorizontalVelocityState.WalkRight
        else:
            return HorizontalVelocityState.SprintRight

    def __repr__(self) -> str:
        return self.name