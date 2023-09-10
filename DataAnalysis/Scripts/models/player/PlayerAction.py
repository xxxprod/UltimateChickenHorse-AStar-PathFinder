from enum import Enum
from functools import reduce


class PlayerAction(Enum):

    Nothing             = 0x00
    Left                = 0x01
    Right               = 0x02
    Up                  = 0x04
    Down                = 0x08
    Jump                = 0x10
    Sprint              = 0x20
    UpLeft              = Up | Left
    UpRight             = Up | Right
    DownLeft            = Down | Left
    DownRight           = Down | Right
    JumpNothing         = Jump | Nothing
    JumpDown            = Jump | Down
    JumpLeft            = Jump | Left
    JumpRight           = Jump | Right
    SprintLeft          = Sprint | Left
    SprintRight         = Sprint | Right
    SprintUp            = Sprint | Up
    SprintUpLeft        = Sprint | Up | Left
    SprintUpRight       = Sprint | Up | Right
    SprintDown          = Sprint | Down
    SprintDownLeft      = Sprint | Down | Left
    SprintDownRight     = Sprint | Down | Right
    SprintJumpLeft      = Sprint | Jump | Left
    SprintJumpRight     = Sprint | Jump | Right
    SprintJumpUpLeft    = Sprint | Jump | Up | Left
    SprintJumpUpRight   = Sprint | Jump | Up | Right
    SprintJumpDownLeft  = Sprint | Jump | Down | Left
    SprintJumpDownRight = Sprint | Jump | Down | Right

    def fromNames(names) -> 'PlayerAction':
        if names is None:
            return PlayerAction.Nothing

        actions = [PlayerAction[name] for name in names]
        return reduce(lambda a, b: PlayerAction(a.value | b.value), actions, PlayerAction.Nothing)

    def invert(self) -> 'PlayerAction':
        lrValue = PlayerAction.Left.value | PlayerAction.Right.value
        if self.value & lrValue == 0:
            return self
        return PlayerAction(self.value ^ lrValue)

    def isSet(self, action: 'PlayerAction') -> bool:
        return (self.value & action.value) == action.value
    
    def set(self, action: 'PlayerAction') -> 'PlayerAction':
        result = self
        if action.isSet(PlayerAction.Left) or action.isSet(PlayerAction.Right):
            result = result.unset(PlayerAction.Left).unset(PlayerAction.Right)

        return PlayerAction(result.value | action.value)

    def unset(self, action: 'PlayerAction') -> 'PlayerAction':
        return PlayerAction(self.value & ~action.value)
    
    def toActionList(self):
        actions = []
        if self.isSet(PlayerAction.Left):
            actions.append(PlayerAction.Left.name)
        if self.isSet(PlayerAction.Right):
            actions.append(PlayerAction.Right.name)
        if self.isSet(PlayerAction.Up):
            actions.append(PlayerAction.Up.name)
        if self.isSet(PlayerAction.Down):
            actions.append(PlayerAction.Down.name)
        if self.isSet(PlayerAction.Jump):
            actions.append(PlayerAction.Jump.name)
        if self.isSet(PlayerAction.Sprint):
            actions.append(PlayerAction.Sprint.name)
        return actions

    
    def __repr__(self) -> str:
        return self.name