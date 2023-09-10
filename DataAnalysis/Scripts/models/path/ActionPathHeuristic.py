from enum import Enum
import math
from typing import Generator
import matplotlib as mpl
import torch
import torch
import torch.nn as nn

from models.level.Block import Block

from models.level.BlockMap import BlockMap
from models.level.BlockType import BlockType
from utils.Rect import Rect
from utils.Vec import Vec

class ActionPathHeuristics(Enum):
    GoalDistanceFlood = 1
    GoalDistanceManhatten = 2
    GoalDistanceEuclidean = 3

class ActionPathHeuristic:
    def __init__(self, blockMap: BlockMap, device = 'cpu', coordinateMultiplier = 2, heuristic = ActionPathHeuristics.GoalDistanceFlood):
        
        self.coordinateMultiplier = coordinateMultiplier
        self.heuristic = heuristic

        self.blockMap = blockMap
        self.bounds = self.__upscaleCoordinate(Rect(self.blockMap.rtree.bounds))

        goalRects = [self.__upscaleCoordinate(goal.rect) for goal in blockMap.getGoals()]
        goalRects = [rect.offset(Vec([-self.bounds.x1, -self.bounds.y1])) for rect in goalRects]
        self.__goalPositions = [rect.center for rect in goalRects]
        
        self.device = device
        if self.device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print(f'Device used: {self.device}')

        blocks = list(self.blockMap.findBlocks(blockTypes=[
            BlockType.Block,
            BlockType.Death
        ]))

        self.occupiedCells = self.__getOccupiedCells(self.__createTensor(blocks, invert=False))
        self.emptyCells = ~self.occupiedCells

        self.goalFloodMap = self.floodFill(goalRects)

        
        print(
            f'{self.heuristic.name}: Start Position: {self.blockMap.startPosition}, '+
            f'Goal Positions: {self.blockMap.goalPositions}, '+
            f'Goal Distance: {round(self.getGoalDistance(self.blockMap.startPosition),2)}'
        )
        
    
    def getDistanceTensor(self) -> torch.Tensor:
        emptyCells = torch.ones_like(self.emptyCells, dtype=torch.float32, device=self.device) * -1

        for (y, x) in emptyCells.nonzero():
            emptyCells[(y, x)] = self.getGoalDistance((x, y), False)

        return emptyCells




    def getGoalDistance(self, pos, upscale=True):
        if upscale:
            pos = self.__upscaleCoordinate(pos)
            pos = pos - Vec([self.bounds.x1, self.bounds.y1])

        if self.heuristic == ActionPathHeuristics.GoalDistanceFlood:
            distance = self.__getGoalDistanceFlood(pos)
        elif self.heuristic == ActionPathHeuristics.GoalDistanceManhatten:
            distance = self.__getGoalDistanceManhatten(pos)
        elif self.heuristic == ActionPathHeuristics.GoalDistanceEuclidean:
            distance = self.__getGoalDistanceEuclidean(pos)
        else:
            raise Exception('Invalid heuristic')
    
        return distance / self.coordinateMultiplier

    def __getGoalDistanceFlood(self, pos):
        (x, y) = pos
        (height, width) = self.goalFloodMap.shape
        if x < 0 or y < 0 or x >= width or y >= height:
            return -1
        distance = self.goalFloodMap[(y, x)].item()
        if distance == 0:
            return -1
        return distance

    def __getGoalDistanceManhatten(self, pos):
        (x, y) = pos
        def getDistance(goalPos):
            (gx, gy) = goalPos
            dx = (x - gx)
            dy = (y - gy)
            return abs(dx) + abs(dy)
        
        return min(map(getDistance, self.__goalPositions))
    
    def __getGoalDistanceEuclidean(self, pos):
        (x, y) = pos
        def getDistance(goalPos):
            (gx, gy) = goalPos
            dx = (x - gx)
            dy = (y - gy)
            return math.sqrt(dx**2 + dy**2)
        
        return min(map(getDistance, self.__goalPositions))





    def __upscaleCoordinate(self, value):
        factor = self.coordinateMultiplier

        if type(value) is Vec:
            return Vec([
                int(math.floor(value.x * factor)), 
                int(math.floor(value.y * factor))
            ])
        
        if type(value) is tuple and len(value) == 4:
            value = Rect(value)
        
        if type(value) is Rect:
            return Rect([
                int(math.floor(value.x1 * factor)),
                int(math.floor(value.y1 * factor)),
                int(math.ceil(value.x2 * factor)),
                int(math.ceil(value.y2 * factor))
            ])        

        return int(math.floor(value * factor))
            

    def findSurfaces(self):
        
        top = (self.occupiedCells.roll(1, 0)) * self.emptyCells
        bottom = (self.occupiedCells.roll(-1, 0)) * self.emptyCells
        left = (self.occupiedCells.roll(1, 1)) * self.emptyCells
        right = (self.occupiedCells.roll(-1, 1)) * self.emptyCells


        top = torch.roll(top, -1, 0)
        bottom = torch.roll(bottom, 1, 0)
        left = torch.roll(left, -1, 1)
        right = torch.roll(right, 1, 1)

        return top, bottom, left, right
    
    
    def floodFill(self, startRects:list[Rect], max_steps=10000):

        filled = torch.zeros_like(self.occupiedCells, dtype=torch.float32)
        
        for startRect in startRects:
            for x in range(startRect.x1, startRect.x2):
                for y in range(startRect.y1, startRect.y2):
                    filled[y, x] = 1


        for step in range(2, max_steps):
            conv = self.__convolute(filled, kernel_size=(3, 3), padding=(1, 1), kernel=[
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0],
            ])
            newCells = (conv > 0) & (filled == 0) & self.emptyCells
            if newCells.sum().item() == 0:
                print(f'Flood fill steps: {step}')
                return filled 
            
            filled += newCells * step

        return None
    


    def __getOccupiedCells(self, blocks):
        smallSpaces = self.__convolute(blocks, (5, 1), (2, 0), [
            [1],
            [1],
            [0],
            [1],
            [1],
        ])
        smallSpaces = (smallSpaces > 2) & (blocks == 0)
        smallSpaces = ((smallSpaces * 2) + (blocks == 1))
        return smallSpaces > 0
    
    
    def __getOutlines(self, tensor):
        
        conv1 = self.__convolute(tensor, (3, 3), (1, 1), [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ])

        outine = (conv1 > 0) & (tensor == 0)

        conv2 = self.__convolute(outine, (3, 3), (1, 1), [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ])
        
        return (conv2 > 0) & (tensor > 0)
    
    def __convolute(self, tensor, kernel_size, padding, kernel):        
        convolution = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=kernel_size, padding=padding)
        convolution.weight = nn.Parameter(torch.tensor(
            [
                [
                    kernel                    
                ]
            ],
            dtype=torch.float32,
            device=self.device))
        convolution.bias = nn.Parameter(torch.tensor([0], dtype=torch.float32, device=self.device))
    
        return convolution(tensor.float().reshape(1, 1, *tensor.shape)).reshape(*tensor.shape)
                    
    
    def __createTensor(self, blocks:Generator[Block, None, None], invert=False) -> torch.Tensor:
        
        bounds = self.__upscaleCoordinate(Rect(self.blockMap.rtree.bounds))
        
        if not invert:
            tensor = torch.zeros((bounds.height, bounds.width), dtype=torch.bool, device=self.device)
        else:
            tensor = torch.ones((bounds.height, bounds.width), dtype=torch.bool, device=self.device)
        for block in blocks:

            r = self.__upscaleCoordinate(block.rect)
            
            x1 = r.x1 - bounds.x1
            x2 = r.x2 - bounds.x1
            y1 = r.y1 - bounds.y1
            y2 = r.y2 - bounds.y1

            tensor[y1:y2, x1:x2] = not invert
        return tensor