from typing import Callable, Generator
from models.actions.JumpActionSequence import *
from models.actions.JumpActionNode import *


class JumpActionNodeList:

    def fromActionSequences(actionSequences:Generator[JumpActionSequence,None,None], addNormal, addInverted, resetVelocityInFirstFrame=True) -> 'JumpActionNodeList':

        actionSequences = list(actionSequences)

        nodeMap = {}
        leafs = []
        nextId = 1
        
        def createNode(frame: ActionFrame, parent: JumpActionNode, id):
            nodeKey = JumpActionNode.createNodeKey(frame.action, parent)
            node = nodeMap.get(nodeKey)
            if node is None:
                node = JumpActionNode(id, nodeKey, frame, parent)
                nodeMap[nodeKey] = node
            return node
            
        for actionSet in actionSequences:
            frames = list(actionSet.iter(resetVelocityInFirstFrame))        
            treeNode1 = None
            treeNode2 = None
            for frame in frames:
                if addNormal:
                    treeNode1 = createNode(frame, parent=treeNode1, id=nextId)
                if addInverted:
                    treeNode2 = createNode(frame.invert(), parent=treeNode2, id=-nextId)
                nextId += 1
            if treeNode1 is not None:
                leafs.append(treeNode1)
            if treeNode2 is not None:
                leafs.append(treeNode2)

        return JumpActionNodeList(leafs)
        

    def __init__(self, nodes: list[JumpActionNode], isSorted=False) -> None:
        self.nodes: list[JumpActionNode] = nodes
        if not isSorted:
            self.nodes = sorted(self.nodes, key=lambda node: node.fullKey)

    def filterNodes(self, nodeFilter: Callable) -> 'JumpActionNodeList':
        if nodeFilter is None:
            return self
        nodes = list(nodeFilter(self.nodes))
        return JumpActionNodeList(nodes, isSorted=False)
    
    def __len__(self):
        return len(self.nodes)
    
    def __repr__(self) -> str:
        return f'ActionNodeList: {len(self)}'