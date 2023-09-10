from models.actions.JumpActionSequence import JumpActionSequence
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from functools import reduce
from typing import Generator

from utils.tools import getOrAdd


class ActionSet:
    def __init__(self, name, actionSeries: Generator[JumpActionSequence,None,None]):
        self.name = name
        self.__actionSet:dict[tuple[HorizontalVelocityState,HorizontalVelocityState],list[JumpActionSequence]] = {}
        for actionSerie in actionSeries:            
            key = (actionSerie.startVX, actionSerie.endVX)
            actionSets = getOrAdd(self.__actionSet, key, lambda: [])
            actionSets.append(actionSerie)

    def getActionSequences(self):
        if len(self.__actionSet) == 0:
            return []
        return reduce(lambda x, y: x + y, self.__actionSet.values())

    def filterVelocities(self, startVX: HorizontalVelocityState, endVX: HorizontalVelocityState):

        def __iterator():
            for key in self.__actionSet:
                if startVX is not None and not key[0].isSet(startVX):
                    continue
                if endVX is not None and not key[1].isSet(endVX):
                    continue
                for actionSerie in self.__actionSet[key]:
                    yield actionSerie
        
        return ActionSet(self.name, __iterator())


    def __len__(self):
        return len(self.__actionSet)
    
    def __repr__(self) -> str:
        return f'ActionSet: {self.name}: {sum(len(t) for t in self.__actionSet.values())}'