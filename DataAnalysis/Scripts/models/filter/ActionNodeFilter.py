from models.actions.JumpActionNode import JumpActionNode
from typing import Callable, Generator

class ActionNodeFilter:
    def empty():
        return lambda _: []
    
    def combine(filters: list[Callable]) -> Callable:
        
        def filterFunc(nodes: Generator[JumpActionNode,None,None]):
            for filter in filters:
                nodes = filter(nodes)
            return nodes
        
        return filterFunc