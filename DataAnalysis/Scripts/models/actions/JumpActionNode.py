from models.actions.ActionFrame import ActionFrame
from models.actions.ActionNodeBase import ActionNodeBase
from models.actions.JumpActionSequence import *
from models.player.PlayerAction import PlayerAction
from utils.Vec import Vec

class JumpActionNode(ActionNodeBase):
    
    def __init__(self, id, fullKey, frame: ActionFrame, parent: 'JumpActionNode'=None):
        self.id = id
        self.fullKey = fullKey
        self.parent = parent

        if self.parent is None:
            self.branchNodes = [self]
        else:
            self.branchNodes = parent.branchNodes + [self]

        super().__init__(frame.action, frame.velocity, self.__calcPosition(frame, parent))

    def createNodeKey(key, parent=None):
        if type(key) is tuple:
            return key
        if type(key) is PlayerAction:
            key = key.value
        if parent is None:
            return tuple([key])
        return (*parent.fullKey, key)

    def getData(self) -> pd.DataFrame:
        actionFrames = [node.position for node in self.branchNodes]
        return pd.DataFrame(actionFrames, columns=['X', 'Y'])

    def compareKey(self, otherKey, cutToSameLength=False):
        if cutToSameLength:
            selfKey = self.fullKey[:len(otherKey)]
        else:
            selfKey = self.fullKey

        if selfKey < otherKey:
            return -1
        if selfKey > otherKey:
            return 1
        return 0
    
    def findBranchNode(self, key):
        if len(key) > len(self):
            return None
        
        if self.fullKey[:len(key)] != key:
            return None
        
        return self.branchNodes[len(key) - 1]


    def __calcPosition(self, frame: ActionFrame, parent):        
        if parent is not None:
            return parent.position + frame.movement
        return frame.movement
    
    def __len__(self):
        return len(self.fullKey) 
    
    def __repr__(self) -> str:
        if len(self.fullKey) > 10:
            s = str(self.fullKey[:10])[1:-2] + ", ..."
        else:
            s = str(self.fullKey)[1:-2]
        return f'ActionNode ({self.id})[{len(self)}]: ({s})'