import json
from typing import Generator
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from models.actions.JumpActionNodeList import JumpActionNodeList
from models.actions.ActionSet import ActionSet
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.actions.JumpActionSets import JumpActionSets
from models.level.BlockMap import BlockMap
from models.level.LevelLoader import LevelLoader
from models.level.LevelPathBuilder import LevelPathBuilder
from models.path.ActionPath import ActionPath
from models.path.ActionPathCache import ActionPathCache
from models.path.ActionPathFinder import ActionPathFinder
from models.path.ActionPathGroundConnectionSource import ActionPathGroundConnectionSource
from models.path.ActionPathJumpConnectionSource import ActionPathJumpConnectionSource
from models.path.ActionPathHeuristic import ActionPathHeuristic, ActionPathHeuristics
from models.path.ActionPathState import ActionPathConnectionType
from models.path.ActionPathWallConnectionSource import ActionPathWallConnectionSource
from models.player.PlayerCollision import PlayerCollision
from models.player.PlayerConstants import PlayerConstants
from services.ActionPathDecoder import ActionPathDecoder
from services.ActionPathEncoder import ActionPathEncoder
from utils.PlotTools import PlotTools
from utils.Rect import Rect
from utils.UCHServer import UCHServer
from utils.tools import *

class UCHPathFinder:
    def __init__(
            self, levelName, 
            quantizationFactor=(1,1), 
            costWeights=np.arange(0.9, 1.0, 0.01), 
            forceLoadLevel=False, 
            forceCreateNodeMap=False, 
            heuristic=ActionPathHeuristics.GoalDistanceFlood
        ):
        self.levelName = levelName
        self.levelData = LevelLoader.fromLevel(levelName, forceCreate=forceLoadLevel)
        self.blockMap = BlockMap.fromLevelData(self.levelData)
        self.actionSets = JumpActionSets()
        self.groundJumpSets = self.actionSets.getGroundJumps()
        self.wallJumpSets = self.actionSets.getWallJumps()
        self.__groundConnectionSource = self.__createGroundContactConnectionSource()
        self.__wallConnectionSource = self.__createWallContactConnectionSource()
        self.__groundJumpConnectionSources = [
            self.__createGroundJumpConnectionSource(self.__findGroundJumps(HorizontalVelocityState.Idle), HorizontalVelocityState.Idle, forceCreateNodeMap),
            self.__createGroundJumpConnectionSource(self.__findGroundJumps(HorizontalVelocityState.SprintRight), HorizontalVelocityState.SprintRight, forceCreateNodeMap),
            self.__createGroundJumpConnectionSource(self.__findGroundJumps(HorizontalVelocityState.SprintRight), HorizontalVelocityState.SprintLeft, forceCreateNodeMap),
        ]
        self.__wallJumpConnectionSources = [
            self.__createWallJumpConnectionSource(self.wallJumpSets, PlayerCollision.LeftWall, forceCreateNodeMap),
            self.__createWallJumpConnectionSource(self.wallJumpSets, PlayerCollision.RightWall, forceCreateNodeMap)
        ]

        self.connectionSources = [
            self.__groundConnectionSource,
            self.__wallConnectionSource,
            *self.__groundJumpConnectionSources,
            *self.__wallJumpConnectionSources
        ]
        self.heuristics = ActionPathHeuristic(
            blockMap=self.blockMap, 
            device='cpu', 
            coordinateMultiplier=2,
            heuristic=heuristic
        )
        self.pathCache = ActionPathCache(quantizationFactor)

        self.pathFinder = ActionPathFinder(
            heuristics=self.heuristics,
            pathCache=self.pathCache,
            connectionSources=self.connectionSources,
            nextPathCallback=self.__nextPathCallback
        )
        
        self.costWeights = costWeights
        self.heuristicChangeInterval = 5
        self.visitedPaths = []

    @property
    def foundPaths(self):
        return self.pathFinder.foundPaths

    def findPaths(self, maxTime=None):
        try:
            while len(self.pathFinder.queue) > 0:
                if maxTime is not None and self.pathFinder.totalSearchTime > maxTime:
                    break
                for costWeight in self.costWeights:
                    path = self.pathFinder.findNextPath(costWeight=costWeight, maxTime=self.heuristicChangeInterval)
                    if path is not None:
                        yield path

        except KeyboardInterrupt:
            print(f'Path search interrupted by User. FoundPaths: {len(self.pathFinder.foundPaths)}, QueueSize: {len(self.pathFinder.queue)}')
            pass

    def savePaths(self):
        directory = LevelPathBuilder.getLevelResultsDirectory(self.levelName, createIfNotExists=True)        
        with open(f'{directory}/FoundPaths.json', 'w') as file:
            json.dump(list(self.foundPaths), file, indent=None, cls=ActionPathEncoder)

    def loadSavedPaths(levelName):
        try:
            directory = LevelPathBuilder.getLevelResultsDirectory(levelName)
            with open(f'{directory}/FoundPaths.json', 'r') as file:
                paths = json.load(file, cls=ActionPathDecoder)
                print('Loaded paths from file:' + str(len(paths)))
                for path in paths:
                    print(path)
                return paths
        except FileNotFoundError:
            return []

    def plotPaths(self, maxCount: int = 100, plotQueue: bool = True, plot: PlotTools=None):
        if plot is None:
            plot = PlotTools.create(figsize=15)

        self.plotHeuristic(plot)
        plot.plotBlocks(self.blockMap.blocks, alpha=1)
        
        count = 0

        if plotQueue:
            for path in self.pathFinder.queue:
                plot.plotPath(path, alpha=0.3)
                count += 1
                if count >= maxCount:
                    break
                
        for path in self.pathFinder.foundPaths[1:]:
            plot.plotPath(path, color='lightblue', alpha=0.8)

        if len(self.pathFinder.foundPaths) > 0:
            plot.plotPath(self.pathFinder.foundPaths[0], color='red', alpha=1)

        directory = LevelPathBuilder.getLevelResultsDirectory(self.levelName, createIfNotExists=True)
        plot.fig.savefig(f'{directory}/FoundPaths.png', dpi=300, bbox_inches='tight')

                
    def plotAnimation(self, fps=30, skipFrames=0):

        visitedPaths = [self.visitedPaths[i] for i in range(0, len(self.visitedPaths), 1 + skipFrames)]
        visitedPaths.extend(reversed(self.foundPaths))
        print(len(visitedPaths))

        plt.rcParams['animation.ffmpeg_path'] = r'D:/Development/tools/ffmpeg-6.0/bin/ffmpeg.exe'

        x = []
        y = []

        plot = PlotTools.create(figsize=15)
        
        self.plotHeuristic(plot)
        plot.plotBlocks(self.blockMap.blocks)
        lines = plot.axis[0].plot(x, y)

        def pathIterator():
            for path in visitedPaths:
                yield path

        def animate(path):
            x = []
            y = []
            for segment in path.segments:
                for node in segment.pathNodes:
                    x.append(node.position.x)
                    y.append(node.position.y)
            lines[0].set_data(x, y)        
            lines[0].set_color('red' if path.segment.lastNode.collision == PlayerCollision.Goal else 'lightblue')

        animation = FuncAnimation(
            plot.fig, 
            animate, 
            pathIterator, 
            interval=1000 / fps
        )

        directory = LevelPathBuilder.getLevelResultsDirectory(self.levelName, createIfNotExists=True)
        animation.save(f'{directory}/PathFinder.mp4', fps=fps)

    def executePath(self, path: ActionPath, plot: PlotTools=None, shutdownServer=True, plotNodeLabels=False):

        def convertPathNode(node):
            return {
                'Actions': node.action.toActionList(),
                'Velocity': {
                    'X': node.velocity.x,
                    'Y': node.velocity.y
                },
                'Position': {
                    'X': node.position.x,
                    'Y': node.position.y,
                },
            }
        
        pathNodes = list(map(convertPathNode, path.getMergedPathNodes()))

        request = {
            'Paths':[
                {'Nodes': pathNodes}
            ]
        }

        print('Sending path to the game...')

        uchServer = UCHServer()
        uchServer.sendKeepAliveMessage()
        uchServer.sendMessage("getPathGeneratorRequest", json.dumps({"LevelCode": self.levelName}))

        response = self.__getUCHMessage(uchServer)

        if response[0][0] != 'generatePath':
            raise Exception('Unexpected response: ' + str(response))
        

        uchServer.sendMessage(
            "executePath", json.dumps(request)
        )

        response = self.__getUCHMessage(uchServer)
        if shutdownServer:
            uchServer.sendShutdownMessage()

        if response[0][0] != 'executedPathResults':
            raise Exception('Unexpected response: ' + str(response))

        # uchServer.sendShutdownMessage()
        df = pd.DataFrame(response[0][1]['Paths'][0]['Nodes'])
        df['PosX'] = df['Position'].apply(lambda x: x['X']).round(4)
        df['RealPosX'] = df['RealPosition'].apply(lambda x: x['X']).round(4)
        df['DeltaX'] = (df['RealPosX'] - df['PosX']).round(4)

        df['PosY'] = df['Position'].apply(lambda x: x['Y']).round(4)
        df['RealPosY'] = df['RealPosition'].apply(lambda x: x['Y']).round(4)
        df['DeltaY'] = (df['RealPosY'] - df['PosY']).round(4)

        df['VelX'] = df['Velocity'].apply(lambda x: x['X']).round(4)
        df['RealVelX'] = df['RealVelocity'].apply(lambda x: x['X']).round(4)
        df['DriftX'] = (df['RealVelX'] - df['VelX']).round(4)

        df['VelY'] = df['Velocity'].apply(lambda x: x['Y']).round(4)
        df['RealVelY'] = df['RealVelocity'].apply(lambda x: x['Y']).round(4)
        df['DriftY'] = (df['RealVelY'] - df['VelY']).round(4)

        # df[['PosX','RealPosX']] = df[['PosX','RealPosX']] - df.loc[0, 'PosX']
        # df[['PosY','RealPosY']] = df[['PosY','RealPosY']] - df.loc[0, 'PosY']


        df['RealVelX'] = df['RealVelX'].round(4)

        df.drop('RealVelocity', axis=1, inplace=True)
        df.drop('RealPosition', axis=1, inplace=True)
        df.drop('Velocity', axis=1, inplace=True)
        df.drop('Position', axis=1, inplace=True)

        if plot is None:
            plot = PlotTools.create(figsize=(20,10), gridStep=None)

        self.plotHeuristic(plot)

        ax = plot.axis[0]

        plot.plotBlocks(self.blockMap.blocks)
        ax.plot(df['PosX'], df['PosY'], '-', color='cyan', markersize=2, label='Planned Path')
        ax.plot(df['RealPosX'], df['RealPosY'], '-', color='red', markersize=2, label='Executed Path')
        ax.legend()
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        
        # for i, row in df.iterrows():
        #     plot.plotRectangle(PlayerConstants.playerRect.offset(Vec([row['PosX'], row['PosY']])), edgeColor='cyan', alpha=0.2)
        #     plot.plotRectangle(PlayerConstants.playerRect.offset(Vec([row['RealPosX'], row['RealPosY']])), edgeColor='red', alpha=0.2)


        for i, pathSegment in enumerate(path.segments):

            if len(pathSegment) == 1:
                continue
            
            node = pathSegment.lastNode

            ax.plot(node.position.x, node.position.y, 'o', color='yellow')
            if plotNodeLabels:
                ax.text(node.position.x + 1, node.position.y, f'{str(i)}', va='center', color='white')

            # plot.axis[0].plot(segment.startPos.x, segment.startPos.y, 'o', color='red')
            # plot.axis[0].plot(node.position.x, node.position.y, 'o', color='blue')

        directory = LevelPathBuilder.getLevelResultsDirectory(self.levelName, createIfNotExists=True)
        plot.fig.savefig(f'{directory}/Execution.png', dpi=300, bbox_inches='tight')
        return df

    def plotHeuristic(self, plot):
        plot.plotTensor(
            tensor=self.heuristics.getDistanceTensor(), 
            extent=Rect(self.blockMap.rtree.bounds), 
            colors=['#0055aa', '#040404'],
            alpha=0.5
        )

    def __getUCHMessage(self, uchServer):
        print('Waiting for response...')
        response = uchServer.readMessages()
        while len(response) == 0:
            response = uchServer.readMessages()
        return response


    def __nextPathCallback(self, path):
        self.visitedPaths.append(path)


    def __createWallContactConnectionSource(self):
        jumpSlideAccelerationNode = self.actionSets.getJumpSlideToNormalSet()
        jumpSlideAccelerationNode = JumpActionNodeList.fromActionSequences([jumpSlideAccelerationNode], True, False, resetVelocityInFirstFrame=False)
        jumpSlideAccelerationNode = jumpSlideAccelerationNode.nodes[0]
        dropSlideAccelerationNode = self.actionSets.getDropSlideToNormalSet()
        dropSlideAccelerationNode = JumpActionNodeList.fromActionSequences([dropSlideAccelerationNode], True, False, resetVelocityInFirstFrame=False)
        dropSlideAccelerationNode = dropSlideAccelerationNode.nodes[0]
        jumpAccelerations = self.actionSets.getJumpAccelerations()
        return ActionPathWallConnectionSource(self.blockMap, jumpSlideAccelerationNode, dropSlideAccelerationNode, jumpAccelerations)

    def __createGroundContactConnectionSource(self):
        return ActionPathGroundConnectionSource(self.blockMap)

    def __createGroundJumpConnectionSource(self, actionSet: ActionSet, startVX: HorizontalVelocityState, forceCreateNodeMap):
        addNormal = startVX == HorizontalVelocityState.Idle or startVX.isSet(HorizontalVelocityState.Right)
        addInverted = startVX == HorizontalVelocityState.Idle or startVX.isSet(HorizontalVelocityState.Left)
        actionNodes = JumpActionNodeList.fromActionSequences(actionSet.getActionSequences(), addNormal, addInverted)    
        return ActionPathJumpConnectionSource(
            name='GroundJumps', 
            blockMap=self.blockMap, 
            actionNodes=actionNodes, 
            pathState=ActionPathConnectionType.OnGround,
            collision=None,
            startVX=startVX, 
            forceCreate=forceCreateNodeMap
        )

    def __createWallJumpConnectionSource(self, actionSet: ActionSet, collision: PlayerCollision, forceCreateNodeMap):
        addNormal = collision == PlayerCollision.LeftWall
        actionNodes = JumpActionNodeList.fromActionSequences(actionSet.getActionSequences(), addNormal, not addNormal)
        return ActionPathJumpConnectionSource(
            name='WallJumps', 
            blockMap=self.blockMap, 
            actionNodes=actionNodes, 
            pathState=ActionPathConnectionType.OnWall,
            collision=collision,
            startVX=None, 
            forceCreate=forceCreateNodeMap
        )

    def __findGroundJumps(self, startVX):
        return self.groundJumpSets.filterVelocities(startVX, None)