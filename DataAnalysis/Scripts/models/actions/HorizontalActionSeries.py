

from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.actions.MotionState import *
from models.player.PlayerAction import *
from utils.TestRunner import *


class HorizontalActionSequence:

    def __init__(self, testName, scenario, time_start, time_end, motionState:MotionState):

        if testName is None:
            return
        
        testResults = TestResults.load(testName)\
            .filterScenario(scenario, reset_time_steps=False)\
            .filterTime(time_start, time_end)\
            .selectColumns(['TimeStep', 'Actions', 'VelocityX'])
        
        self.initialize(scenario, motionState, testResults.Data)

    def initialize(self, scenario, motionState:MotionState, data):
        self.name = scenario
        self.motionState = motionState

        self.startVX = HorizontalVelocityState.fromRealVelocity(data.loc[0, 'VelocityX'])
        self.endVX = HorizontalVelocityState.fromRealVelocity(data.loc[len(data)-1, 'VelocityX'])
        self.length = len(data)
        self.distance_abs = sum([abs(velX) for velX in data['VelocityX']]) / 60
        self.distance = sum([velX for velX in data['VelocityX']]) / 60
        
        def createAction(actions):
            action: PlayerAction = PlayerAction.fromNames(actions)
            return action.unset(PlayerAction.Jump)
        
        # data.loc[0, 'VelocityX'] = 0
        if 'Action' not in data.columns:
            data['Action'] = data['Actions'].apply(createAction)
            data.drop(columns=['Actions'], inplace=True)
        # data.loc[len(data)-1, 'Action'] = PlayerAction.Nothing

        self.Data = data

    def clone(self):
        clone = HorizontalActionSequence(None, None, None, None, None)
        clone.name = self.name
        clone.motionState = self.motionState
        clone.startVX = self.startVX
        clone.endVX = self.endVX
        clone.length = self.length
        clone.distance = self.distance
        clone.Data = self.Data.copy()
        return clone
    
    def fromLastFrame(self, length=1):
        clone = HorizontalActionSequence(None, None, None, None, None)
        data = self.Data.iloc[len(self.Data)-1:len(self.Data)]
        
        data = pd.concat([data] * (length + 1), ignore_index=True)
        data['TimeStep'] = data.index
        # data.loc[1:, 'PositionX'] = data.loc[1:,'VelocityX'].cumsum() / 60

        clone.initialize("Copy", self.motionState, data)
        return clone


    def createStaticSeries(testResultsName, scenario, timeStep, motionState:MotionState, name, length, action = None):
        
        data = TestResults.load(testResultsName)\
            .filterScenario(scenario, reset_time_steps=False)\
            .filterTime(timeStep, 0)\
            .selectColumns(['TimeStep', 'Actions', 'VelocityX'])\
            .Data
        
        data = pd.concat([data] * (length + 1), ignore_index=True)
        data['TimeStep'] = data.index
        
        clone = HorizontalActionSequence(None, None, None, None, None)
        clone.initialize(name, motionState, data)

        if action is not None:
            clone.Data['Action'] = action

        return clone
    
    def invert(self):
        def switchLeftRight(action):
            if action == PlayerAction.Left:
                return PlayerAction.Right
            elif action == PlayerAction.Right:
                return PlayerAction.Left
            else:
                return action

        clone = self.clone()
        clone.name = switchLeftRight(clone.name)
        clone.motionState = clone.motionState
        clone.Data['VelocityX'] = -clone.Data['VelocityX']
        clone.Data['Action'] = clone.Data['Action'].apply(PlayerAction.invert)
        clone.startVX, clone.endVX = clone.startVX.invert(), clone.endVX.invert()
        return clone

    def __lt__(self, other):
        return self.distance < other.distance
    
    def __repr__(self):
        return f'{(self.name+":").ljust(18)} [{self.motionState}|{str(self.startVX).rjust(2)}, {str(self.endVX).rjust(2)}] - {str(self.length).rjust(2)} steps, {round(self.distance,3)} distance'
