from models.path.ActionPath import ActionPath
from models.path.ActionPathNode import ActionPathNode
from utils.tools import json


import json


class ActionPathEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is ActionPath:
            return self.serializePath(obj)
        return super().default(obj)

    def serializePath(self, path:ActionPath):
        def iterateParents():
            parent = path
            while parent is not None:
                yield parent
                parent = parent.parent

        pathSegments = reversed(list(iterateParents()))

        return {'segments': self.serializeSegments(pathSegments)}

    def serializeSegments(self, segments:list[ActionPath]):
        return list(map(self.serializeSegment, segments))

    def serializeSegment(self, segment:ActionPath):
        return {
            'nodes': self.serializeNodes(segment.segment.pathNodes),
            'state': segment.connectionType.value,
            'heuristic': segment.h
        }

    def serializeNodes(self, nodes:list[ActionPathNode]):
        return list(map(self.serializeNode, nodes))

    def serializeNode(self, node:ActionPathNode):
        return {
            'px': round(node.position.x, 5),
            'py': round(node.position.y, 5),
            'vx': round(node.velocity.x, 5),
            'vy': round(node.velocity.y, 5),
            'coll': node.collision.value,
            'action': node.action.value
        }