import pandas as pd
from models.actions.MotionState import MotionState
from models.player.PlayerAction import PlayerAction
from utils.TestRunner import TestResults


class VerticalActionSequence:
    def __init__(self, testName, scenario, time_start, time_end, motionState:MotionState, resetVelocityInFirstFrame = True):

        if testName is None:
            return

        testResults = TestResults.load(testName)\
            .filterScenario(scenario, reset_time_steps=False)\
            .filterTime(time_start, time_end)\
            .selectColumns(['TimeStep', 'Actions', 'VelocityY'])

        self.Data :pd.DataFrame = None
        self.__initialize(scenario, motionState, testResults.Data, resetVelocityInFirstFrame)


    def __initialize(self, scenario, motionState:MotionState, data, resetVelocityInFirstFrame):
        self.name = scenario
        self.motionState = motionState

        self.length = len(data)

        if self.length == 0:
            raise ValueError(f'VerticalActionSeries: {scenario} has no data')

        # data['firstLast'] = False
        # data.loc[0, 'firstLast'] = True
        # data.loc[len(data)-1, 'firstLast'] = True
        if resetVelocityInFirstFrame:
            data.loc[0, 'VelocityY'] = 0
        def createAction(actions):
            return PlayerAction.Jump if PlayerAction.fromNames(actions).isSet(PlayerAction.Jump) else PlayerAction.Nothing

        data['Action'] = data['Actions'].apply(createAction)
        data.drop(columns=['Actions'], inplace=True)
        self.Data = data

    def __repr__(self):
        return f'{(self.name+":").ljust(18)} [{self.motionState}|{str(self.length).rjust(2)} steps'


    def iter(self, maxLength = 100):
        return VerticalActionSequence.__Iterator(self, maxLength)

    class __Iterator:
        def __init__(self, vSeries, maxLength):
            self.vSeries = vSeries
            self.vData2 = vSeries.Data[['Action', 'VelocityY']].values
            self.maxLength = maxLength

            self.reset()

        def reset(self):
            self.index = 0

        def __len__(self):
            if self.maxLength is None:
                return self.vSeries.length
            return max(self.maxLength, self.vSeries.length)

        def __iter__(self):
            return self

        def __next__(self):
            if self.maxLength is not None and self.index >= self.maxLength:
                raise StopIteration

            nextVData = self.__getnextVData()
            self.index += 1
            return nextVData

        def __getnextVData(self):

            if len(self.vData2) == 0:
                return [[], 0]

            return self.vData2[self.index] if self.index < len(self.vData2) else self.vData2[-1]