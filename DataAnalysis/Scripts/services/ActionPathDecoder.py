from models.path.ActionPath import ActionPath
from models.path.ActionPathNode import ActionPathNode
from models.path.ActionPathSegment import ActionPathSegment
from models.path.ActionPathState import ActionPathConnectionType
from models.player.PlayerAction import PlayerAction
from models.player.PlayerCollision import PlayerCollision
from utils.Vec import Vec
from utils.tools import json


import json


class ActionPathDecoder(json.JSONDecoder):
    def decode(self, jsonStr):
        data = super().decode(jsonStr)
        paths = []
        for row in data:
            paths.append(self.deserializePath(row))
        return paths

    def deserializePath(self, data):
        path = None
        for segment in data['segments']:
            path = ActionPath(
                segment=self.deserializeSegment(segment),
                parent=path,
                connectionType=ActionPathConnectionType(segment['state'])
            )
            path.h = segment['heuristic']
        return path

    def deserializeSegment(self, data):
        return ActionPathSegment(self.deserializeNodes(data['nodes']))

    def deserializeNodes(self, data):
        return list(map(self.deserializeNode, data))

    def deserializeNode(self, data):
        return ActionPathNode(
            position=Vec([data['px'], data['py']]),
            velocity=Vec([data['vx'], data['vy']]),
            collision=PlayerCollision(data['coll']),
            action=PlayerAction(data['action'])
        )