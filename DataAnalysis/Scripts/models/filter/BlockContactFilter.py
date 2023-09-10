from models.actions.JumpActionNode import JumpActionNode
from models.actions.JumpActionNodeMap import JumpActionNodeMap
from models.filter.ActionNodeKeyFilter import ActionNodeKeyFilter
from typing import Generator

from utils.Rect import Rect
from utils.Vec import Vec


class BlockContactFilter:
    def __init__(self, nodeMap: JumpActionNodeMap, rectangles:list[Rect], invert=False, padding=None):
        self.actionMap = nodeMap
        self.rectangles = [rectangles] if rectangles is tuple else rectangles
        self.invert = invert
        self.padding = Rect([0,0,0,0]) if padding is None else padding
        if type(self.padding) is Vec:
            self.padding = Rect([self.padding[0], self.padding[1], self.padding[0], self.padding[1]])
        elif type(self.padding) is float or type(self.padding) is int:
            self.padding = Rect([self.padding, self.padding, self.padding, self.padding])

    def __call__(self, nodes: Generator[JumpActionNode,None,None]):
        nodeKeys = self.__findIntersections()
        filter = ActionNodeKeyFilter(nodeKeys, invert=self.invert)
        return filter(nodes)

    def __findIntersections(self):
        seen = set()
        for rect in self.rectangles:
            if self.padding is not None:
                rect = Rect([
                    rect.x1 + self.padding.x1,
                    rect.y1 + self.padding.y1,
                    rect.x2 - self.padding.x2,
                    rect.y2 - self.padding.y2
                ])
                if rect.width < 0:
                    rect = Rect([rect.x1, rect.y1, rect.x1, rect.y2])
                if rect.height < 0:
                    rect = Rect([rect.x1, rect.y1, rect.x2, rect.y1])
            for id in self.actionMap.rtree.intersection(rect):
                if id not in seen:
                    seen.add(id)
                    node: JumpActionNode = self.actionMap.nodeMap.get(id)
                    if node is not None:
                        yield node.fullKey