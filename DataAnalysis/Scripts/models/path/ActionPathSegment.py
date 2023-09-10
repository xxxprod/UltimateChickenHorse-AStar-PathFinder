from models.path.ActionPathNode import ActionPathNode
from utils.Vec import Vec

class ActionPathSegment:
    __nextId = 1

    def __init__(self, pathNodes: list[ActionPathNode]):
        self.id = ActionPathSegment.__nextId
        ActionPathSegment.__nextId += 1

        self.pathNodes = pathNodes
    
    @property
    def firstNode(self) -> ActionPathNode:
        return self.pathNodes[0]
    
    @property
    def parentNode(self) -> ActionPathNode:
        return self.pathNodes[-2] if len(self.pathNodes) > 1 else None
    
    @property
    def lastNode(self) -> ActionPathNode:
        return self.pathNodes[-1]
    
    @lastNode.setter
    def lastNode(self, value: ActionPathNode):
        self.pathNodes[-1] = value
    
    @property
    def startPos(self) -> Vec:
        return self.firstNode.position
    
    @property
    def endPos(self) -> Vec:
        return self.lastNode.position
    
    def resetIds():
        ActionPathSegment.__nextId = 1
    
    def copy(self):
        pathNodes = self.pathNodes.copy()
        pathNodes[-1] = self.lastNode.copy()
        if len(pathNodes) > 1:
            pathNodes[-2] = self.parentNode.copy()
        return ActionPathSegment(pathNodes)

    def __len__(self):
        return len(self.pathNodes)
    
    def __repr__(self) -> str:
        return f"ActionPathSegment({len(self)})"