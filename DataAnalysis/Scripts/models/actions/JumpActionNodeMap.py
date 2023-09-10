import os
from typing import Callable
from models.actions.JumpActionNodeList import JumpActionNodeList
from models.actions.JumpActionSequence import *
from models.actions.JumpActionNode import *
from rtree.index import Index as RTree

from models.player.PlayerConstants import PlayerConstants




class JumpActionNodeMap:    
    
    def __init__(self, name, nodes: JumpActionNodeList, interpolateSteps:int, forceCreate=False, rtree:RTree=None) -> None:
        self.name = name
        self.nodeList = nodes
        self.interpolateSteps = interpolateSteps
        self.__initializeMap(rtree, forceCreate)

    def __initializeMap(self, rtree, forceCreate):

        loadRtree = rtree is None
        newTree = False

        self.nodeMap = {}

        if loadRtree:
            self.rtree = self.__getRtree(forceCreate)
            if len(self.rtree) == 0:
                newTree = True
        else:
            self.rtree = rtree

        for node in self.nodeList.nodes:
            for branchNode in node.branchNodes:
                if branchNode.id in self.nodeMap:
                    continue
                self.nodeMap[branchNode.id] = branchNode                
                if newTree:
                    if self.interpolateSteps > 0:
                        movementStep = branchNode.deltaPos / (self.interpolateSteps + 1)
                        pos = Vec.empty() if branchNode.parent is None else branchNode.parent.position
                        for _ in range(0, self.interpolateSteps + 1):                            
                            pos = pos + movementStep
                            rect = PlayerConstants.playerRect.offset(pos)
                            self.rtree.insert(branchNode.id, rect, None)
                    else:
                        rect = PlayerConstants.playerRect.offset(branchNode.position)
                        self.rtree.insert(branchNode.id, rect, None)
                    
        if newTree and self.name is not None:
            self.rtree.close()
            self.rtree = self.__getRtree(forceCreate=False)
            print(f'Created new {self.name}: {len(self)}')
        
        if loadRtree and len(self.rtree) != len(self.nodeMap) * (self.interpolateSteps + 1):
            self.rtree.close()
            self.__initializeMap(None, forceCreate=True)

    def __getRtree(self, forceCreate=False):

        if self.name is None:
            cacheFileName = None
        else:
            cacheFileName = f"{dataAnalysisRoot}/ActionMaps/{self.name}"
            if forceCreate:
                JumpActionNodeMap.__deleteCacheFiles(cacheFileName)

        return RTree(cacheFileName)
        
    def __deleteCacheFiles(mapFileName):
        def tryDelete(file):
            if os.path.exists(file):
                os.remove(file)

        tryDelete(mapFileName + '.dat')
        tryDelete(mapFileName + '.idx')
        time.sleep(0.2)

    def __len__(self):
        return len(self.nodeMap)
    
    def __repr__(self) -> str:
        return f'JumpActionNodeMap ({self.name}, {len(self)}), [{self.nodeList}]'
    