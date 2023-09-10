from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.path.ActionPath import ActionPath
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerCollision import PlayerCollision
from utils.tools import getOrAdd


class ActionPathCache:
    def __init__(self, quantizationFactor: tuple[float, float]):
        self.quantizationFactor = quantizationFactor
        self.seenPathLengths: dict[tuple, float] = {}
        self.bestPathLength = 999999


    def hasSeenPath(self, path: ActionPath) -> bool:

        if path.segment.lastNode.collision == PlayerCollision.Goal:
            if len(path) < self.bestPathLength:
                self.bestPathLength = len(path)
                return False
            return True

        stateKey = self.__createStateKey(path)

        prevPathLength = getOrAdd(self.seenPathLengths, stateKey, lambda: 999999999)

        if prevPathLength <= len(path):
            return True

        self.seenPathLengths[stateKey] = len(path)
        return False

    def __createStateKey(self, path):
        (x, y) = path.endPos
        
        connType = path.connectionType
        if connType in [ActionPathConnectionType.TouchedGround, ActionPathConnectionType.OnGround]:
            x = int(round(x * self.quantizationFactor[0]))
            y = int(round(y))
            hVx = HorizontalVelocityState.Idle if path.horizontalVelocityState.isSet(HorizontalVelocityState.Idle) else path.horizontalVelocityState
            key = (x, y, hVx.value, connType.value)
        elif connType in [ActionPathConnectionType.TouchedWall, ActionPathConnectionType.OnWall]:
            x = int(round(x))
            y = int(round(y * self.quantizationFactor[1]))
            upOrDown = path.segment.lastNode.velocity.y > 0
            key = (x, y, upOrDown, connType.value)
        else:
            raise Exception(f'Unknown path state {connType}')
        return key