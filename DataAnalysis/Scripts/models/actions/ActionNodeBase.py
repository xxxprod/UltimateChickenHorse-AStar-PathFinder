from models.actions.JumpActionSequence import PlayerAction, Vec
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.player.PlayerAction import PlayerAction
from utils.Vec import Vec


from abc import ABC


class ActionNodeBase(ABC):
    def __init__(self, action: PlayerAction, velocity: Vec, position: Vec):
        self.action = action
        self.velocity = velocity
        self.position = position

    @property
    def deltaPos(self) -> Vec:
        return self.velocity / 60

    @property
    def horizontalVelocityState(self):
        return HorizontalVelocityState.fromRealVelocity(self.velocity.x)