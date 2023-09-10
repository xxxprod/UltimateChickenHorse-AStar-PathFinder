import math
from typing import Generator
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt, figure
import torch
from models.actions.JumpActionNode import JumpActionNode
from models.path.ActionPath import ActionPath
from models.path.ActionPathHeuristic import ActionPathHeuristic
from models.path.ActionPathSegment import ActionPathSegment
from models.level.Block import Block
from models.level.BlockType import BlockType
from utils.Rect import Rect


class PlotTools:

    def __init__(self, fig: figure.Figure, axis: list[plt.Axes]) -> None:
        self.fig = fig
        self.axis = axis

    def create(rows=1, cols=1, figsize=6, facecolor='#000000', gridStep=None):
        if type(figsize) is int or type(figsize) is float:
            figsize = (figsize * cols, figsize * rows)
        fig, axis = plt.subplots(rows, cols, figsize=figsize)

        axis = axis if rows > 1 or cols > 1 else [axis]

        for ax in axis:
            if gridStep is not None:
                ax.set_xticks(np.arange(-100, 100, gridStep))
                ax.set_yticks(np.arange(-100, 100, gridStep))
                ax.grid()
            ax.set_facecolor(facecolor)

        return PlotTools(fig, axis)
    
    def addGrid(self):
        for ax in self.axis:
            ax.grid()

    def plotRectangle(self, rectangle:Rect, color=None, edgeColor=None, alpha=1, cornerSize=None, label=None, zorder=0, text=None):
        ax = self.axis[0]
        (x1, y1, x2, y2) = rectangle
        x = np.array([x1, x2, x2, x1, x1])
        y = np.array([y1, y1, y2, y2, y1])
        
        fill = True if color is not None else False
        edgeColor = color if edgeColor is None else edgeColor
        color = color if color is not None else '00000000'
        
        ax.fill(x, y, color, alpha=alpha, fill=fill, linewidth=1, edgecolor=edgeColor, label=label, zorder=zorder)
        if cornerSize:
            ax.plot(x, y, 'o', color=edgeColor, alpha=alpha, label=label, zorder=zorder, markersize=cornerSize)

        if text is not None:
            ax.text(*rectangle.center, text, ha='center', va='center')

    def plotBlocks(self, blocks: Generator[Block,None,None], plotBlockIds=False, **kwargs):
        for block in blocks:
            rect = block.rect
            args = {}
            if plotBlockIds:
                args['text'] = str(block.id)

            if block.type.isType(BlockType.Block):
                args['color'] = 'lightgray'
                args['alpha'] = 0.8
            elif block.type.isType(BlockType.Goal):
                args['color'] = 'green'
                args['alpha'] = 1
            elif block.type.isType(BlockType.Spawn):
                args['color'] = 'lightblue'
                args['alpha'] = 1
            elif block.type.isType(BlockType.Death):
                args['color'] = 'red'
                args['alpha'] = 1
            elif block.type.isType(BlockType.LevelBorder):
                args['color'] = 'white'
                args['alpha'] = 1

            args.update(kwargs)
            self.plotRectangle(rect, **args)

    def plotPath(self, path: ActionPath, **kwargs):
        self.plotPathSegments(path.segments, label='Path_'+str(path.id), **kwargs)

    def plotPathSegments(self, segments:list[ActionPathSegment], **kwargs):
        if type(segments) is ActionPathSegment:
            segments = [segments]

        for segment in segments:
            x = [node.position.x for node in segment.pathNodes]
            y = [node.position.y for node in segment.pathNodes]            
            self.axis[0].plot(x, y, zorder=1, **kwargs)
        
    def plotNodes(self, nodes, offset=(0, 0), **kwargs):
        if type(nodes) is JumpActionNode:
            nodes = [nodes]

        for node in nodes:
            data = node.getData()            
            self.axis[0].plot(data['X'] + offset[0], data['Y'] + offset[1], zorder=1, **kwargs)

    
    
    def plotTensor(self, tensor: torch.Tensor, colors = ['white'], plotValues = False, alpha=1.0, extent: Rect=None, roundDigits=0):
        
        ax = self.axis[0]

        if len(colors) == 1:
            colors = ['black', colors[0]]

        cmap = mpl.colors.LinearSegmentedColormap.from_list('cmap', colors, 256)
        cmap._init() # create the _lut array, with rgba values
        cmap._lut[0] = (0,0,0,0)

        data = tensor.cpu()
        print('PlotTensor:', data.min().item(), data.max().item())
        imExtent=[extent.x1, extent.x2, extent.y2, extent.y1] if extent is not None else None
        ax.imshow(data.cpu(), cmap=cmap, alpha=alpha, extent=imExtent)
        ax.invert_yaxis()

        if plotValues: 
            if extent is not None:
                offsetX = extent.x1
                offsetY = extent.y1
                scaleX = (extent.x2 - extent.x1) / data.shape[1]
                scaleY = (extent.y2 - extent.y1) / data.shape[0]
            else:
                offsetX = 0
                offsetY = 0
                scaleX = 1
                scaleY = 1

            for (y,x),value in np.ndenumerate(data):
                if value > 0:
                    x = (x + 0.5) * scaleX + offsetX
                    y = (y + 0.5) * scaleY + offsetY
                    value = f'{value:.{roundDigits}f}'
                    ax.text(x, y, value, ha='center', va='center')