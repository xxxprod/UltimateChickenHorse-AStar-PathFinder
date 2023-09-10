from models.actions.ActionNodeBase import ActionNodeBase
from models.player.PlayerAction import PlayerAction
from models.player.PlayerCollision import PlayerCollision
from utils.Vec import Vec


class ActionPathNode(ActionNodeBase):
    def __init__(self, action: PlayerAction, velocity: Vec, position: Vec, collision: PlayerCollision):
        super().__init__(action, velocity, position)
        self.collision = collision

    def copy(self):
        return ActionPathNode(self.action, self.velocity, self.position, self.collision)


    def __repr__(self) -> str:
        return f"ActionPathNode({self.action}, {self.velocity}, {self.position}, {self.collision})"