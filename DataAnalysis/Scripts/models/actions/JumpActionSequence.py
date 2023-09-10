from models.actions.ActionFrame import *
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.player.PlayerAction import *
from utils.TestRunner import *

class JumpActionSequence:
    def __init__(self, vSequenceIter , hSequenceIter):
        self.vData = vSequenceIter
        self.hData = hSequenceIter
        self.startVX = HorizontalVelocityState.Idle if self.hData is None else self.hData.startVX
        self.endVX = HorizontalVelocityState.Idle if self.hData is None else self.hData.endVX
        self.__length = max(0 if self.hData is None else len(self.hData), 0 if self.vData is None else len(self.vData))
        self.length = self.__length
        
    
    def setMaxLength(self, length):
        if length is None:
            self.length = self.__length
        else:
            self.length = min(self.__length, length)
        return self

    def invert(self):
        return JumpActionSequence(self.vData, None if self.hData is None else self.hData.invert())
    
    
    def toDataFrame(self):
        data = [[frame.action, frame.velocity.x, frame.velocity.y] for frame in self.iter()]
        df = pd.DataFrame(data, columns=['Action', 'VelocityX', 'VelocityY'])
        df['TimeStep'] = df.index
        return df

    def plot(self, plot_axis):
        df = self.toDataFrame()
        plot_axis.plot(df['VelocityX'].cumsum() / 60, df['VelocityY'].cumsum() / 60)
        
    def iter(self, resetFirstFrame=True):
        if self.vData is not None:
            self.vData.reset()
        if self.hData is not None:
            self.hData.reset()
        return JumpActionSequence.__Iterator(self, resetFirstFrame)
    

    def __repr__(self):
        return f'{self.vData.vSeries.name}, {self.hData.series.name}'
        
    def print(self):
        for row in self.iter():
            print(row)
    
    class __Iterator:
        def __init__(self, series, resetFirstFrame):
            self.series = series
            self.index = 0
            self.resetFirstFrame = resetFirstFrame

        def __iter__(self) -> 'JumpActionSequence.__Iterator':
            self.index = 0
            return self
        
        def __next__(self) -> ActionFrame:
            if self.index >= self.series.length:
                raise StopIteration
            
            nextHData = [0, 0] if self.series.hData is None else next(self.series.hData)
            nextVData = [0, 0] if self.series.vData is None else next(self.series.vData)
            if type(nextHData[0]) is PlayerAction:
                nextHData[0] = nextHData[0].value
            if type(nextVData[0]) is PlayerAction:
                nextVData[0] = nextVData[0].value

            nextData = ActionFrame(
                action = PlayerAction(nextVData[0] | nextHData[0]),
                velocityX = nextHData[1] if not self.resetFirstFrame or self.index > 0 else 0,
                velocityY = nextVData[1] if not self.resetFirstFrame or self.index > 0 else 0
            )

            self.index += 1
            return nextData
