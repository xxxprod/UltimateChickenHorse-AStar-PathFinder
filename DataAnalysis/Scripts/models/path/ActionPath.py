import numpy as np
from models.actions.HorizontalVelocityState import HorizontalVelocityState

from models.path.ActionPathSegment import ActionPathSegment
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerAction import PlayerAction
from models.player.PlayerCollision import PlayerCollision
from utils.Vec import Vec


class ActionPath:

    __nextId = 1

    def __init__(self, segment: ActionPathSegment, connectionType: ActionPathConnectionType, parent: 'ActionPath'=None):
        self.id = ActionPath.__nextId        
        ActionPath.__nextId += 1

        self.segment = segment
        self.connectionType = connectionType
        self.parent = parent

        if parent is None:
            self.__length = len(segment)
        else:
            self.__length = parent.__length + len(segment) - 1

        self.h = None

    def getCost(self, costWeight=0.5):
        g = len(self) * (1 - costWeight)
        h = self.h * costWeight
        return g + h
    
    @property
    def segments(self):
        return list(reversed(list(self.__iterateSegments())))

    @property
    def endPos(self) -> Vec:
        return self.segment.endPos
    
    @property
    def lastCollision(self) -> PlayerCollision:
        return self.segment.lastNode.collision
    
    @property
    def horizontalVelocityState(self) -> HorizontalVelocityState:
        return self.segment.lastNode.horizontalVelocityState
    
    def resetIds():
        ActionPath.__nextId = 1

    def copy(self):
        return ActionPath(self.segment.copy(), self.connectionType, self.parent)
    
    def extend(self, segment: ActionPathSegment, connectionType: ActionPathConnectionType) -> 'ActionPath':
        return ActionPath(segment, connectionType, self)
    
    def getMergedPathNodes(self):
        pathNodes = []
        for pathSegment in self.segments: 
            nextNodes = pathSegment.pathNodes

            if len(pathNodes) > 0:
                pathNodes[-1].action = nextNodes[0].action
                nextNodes = nextNodes[1:]
                                
            for node in nextNodes:
                pathNodes.append(node)
                
        return pathNodes
        
    def __iterateSegments(self):
        path = self
        while path is not None:
            yield path.segment
            path = path.parent

    def __len__(self):
        return self.__length
    
    def __repr__(self):
        return f'ActionPath(state={self.connectionType.name}, g={len(self)}, h={self.h})'