from models.actions.JumpActionNode import JumpActionNode


from typing import Generator, Iterable


class ActionNodeKeyFilter:
    def __init__(self, otherKeys, invert):
        if type(otherKeys) is JumpActionNode:
            otherKeys = [otherKeys.fullKey]
        elif type(otherKeys) is tuple:
            otherKeys = [otherKeys]
        elif not isinstance(otherKeys, Iterable):
            raise Exception(f'Unknown type {type(otherKeys)}')

        self.rightKeys = sorted(otherKeys, key=lambda key: key)
        self.invert = invert

    def __call__(self, nodes: Generator['JumpActionNode',None,None]):
        leftNodes = sorted(nodes, key=lambda node: node.fullKey)
        leftIdx, rightIdx = 0, 0
        lastKey = []

        while leftIdx < len(leftNodes):

            left: JumpActionNode = leftNodes[leftIdx]

            if rightIdx >= len(self.rightKeys):
                if not self.invert:
                    break
                yield left
                leftIdx += 1
                continue

            right: tuple = self.rightKeys[rightIdx]
            comp = left.compareKey(right, cutToSameLength=True)

            if comp > 0:
                rightIdx += 1
                continue

            if comp < 0:
                if self.invert:
                    yield left
                leftIdx += 1
                continue

            if not self.invert:
                if right[:len(lastKey)] != lastKey:
                    nextNode = left.findBranchNode(right)
                    if nextNode is None:
                        raise Exception(f'Could not find branch node for {right} in {left}')
                    yield nextNode
                    lastKey = right

            leftIdx += 1