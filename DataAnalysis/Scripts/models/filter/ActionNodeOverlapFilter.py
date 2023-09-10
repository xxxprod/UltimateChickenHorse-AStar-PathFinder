from models.actions.JumpActionNode import JumpActionNode
from typing import Callable, Generator


class ActionNodeOverlapFilter:
    def __init__(self, xMultiplier, yMultiplier, sortFunc:Callable[[JumpActionNode],float]):
        self.xMultiplier = xMultiplier
        self.yMultiplier = yMultiplier
        self.sortFunc = sortFunc
        self.seen = set()

    def __call__(self, nodes: Generator['JumpActionNode',None,None]):
        nodes = sorted(nodes, key=self.sortFunc)
        for node in nodes:
            (x, y) = node.position

            x = round(x * self.xMultiplier, 0)
            y = round(y * self.yMultiplier, 0)

            if (x, y) in self.seen:
                continue
            self.seen.add((x, y))
            yield node