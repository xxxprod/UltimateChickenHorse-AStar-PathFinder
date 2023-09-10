from models.player.PlayerAction import PlayerAction
from utils.Vec import Vec


class ActionFrame:
    def __init__(self, action: PlayerAction, velocityX, velocityY):
        self.action = action
        self.velocity = Vec([velocityX, velocityY])
        self.movement = Vec([velocityX / 60, velocityY / 60])

    def invert(self):
        return ActionFrame(self.action.invert(), -self.velocity[0], self.velocity[1])