
from matplotlib.axis import Axis
from utils.UCHServer import *


class TestStep:
    def __init__(self, actions, repeatCounts, positionOffset=None):
        self.Actions = actions
        self.RepeatCounts = repeatCounts
        self.PositionOffset = positionOffset


class TestScenario:
    def __init__(self, levelName, testSteps):
        self.LevelName = levelName
        self.Steps = testSteps


class TestResults:
    def __init__(self, name, data: pd.DataFrame):
        self.Name = name
        self.Data: pd.DataFrame = data

    def hasData(self):
        return self.Data is not None
    
    def clone(self):
        return TestResults(self.Name, self.Data.copy())
    
    def getTestCases(self):
        return self.Data['ScenarioName'].unique().tolist()
    
    def renameTestCase(self, oldName, newName):
        self.Data.loc[self.Data['ScenarioName'] == oldName, 'ScenarioName'] = newName

    def save(self):
        if self.Data is None:
            raise Exception("No data to save")

        with open(f"{dataAnalysisRoot}/TestResults/{self.Name}.json", "w") as json_file:
            self.Data.to_json(json_file, orient="records", indent=4)

    def load(testResultsName):
        if not TestResults.__exists(testResultsName):
            return TestResults(testResultsName, None)

        with open(f"{dataAnalysisRoot}/TestResults/{testResultsName}.json", "r") as json_file:
            return TestResults(
                testResultsName, pd.read_json(json_file, orient="records")
            )

    def __exists(testResultsName):
        return glob.glob(f"{dataAnalysisRoot}/TestResults/{testResultsName}.json") != []

    def filter(self, filterCallback, reset_position=True, reset_time_steps=True):
        if self.Data is None:
            raise Exception("No data to filter")

        data = filterCallback(self.Data)
        data = data.reset_index(drop=True)

        if reset_time_steps:
            TestResults.__resetTimeSteps(data)

        if reset_position:
            TestResults.__resetPosition(data)

        self.Data = data

        return self

    def filterTime(self, minTimeSteps, maxTimeSteps, reset_position=True, reset_time_steps=True):
        return self.filter(lambda data: data[data["TimeStep"] >= minTimeSteps], reset_position, reset_time_steps)\
                   .filter(lambda data: data[data["TimeStep"] <= maxTimeSteps], reset_position, reset_time_steps)

    def filterScenario(self, scenarioName, reset_position=True, reset_time_steps=True):
        if type(scenarioName) is list:
            return self.filter(lambda data: data[data["ScenarioName"].isin(scenarioName)], reset_position, reset_time_steps)
        return self.filter(lambda data: data[data["ScenarioName"] == scenarioName], reset_position, reset_time_steps)

    def selectColumns(self, columns):
        if self.Data is None:
            raise Exception("No data to select columns")

        self.Data = self.Data[columns]
        return self

    def __resetTimeSteps(data):
        tests = data['ScenarioName'].unique()
        for test in tests:
            data.loc[data['ScenarioName'] == test, 'TimeStep'] -= data.loc[data['ScenarioName'] == test, 'TimeStep'].head(1).values

    def __resetPosition(data):
        tests = data['ScenarioName'].unique()
        for test in tests:
            data.loc[data['ScenarioName'] == test, 'PositionX'] -= data.loc[(data['ScenarioName'] == test) & (data['TimeStep'] == 0), 'PositionX'].head(1).values
            data.loc[data['ScenarioName'] == test, 'PositionY'] -= data.loc[(data['ScenarioName'] == test) & (data['TimeStep'] == 0), 'PositionY'].head(1).values

    def addAccelerations(self):
        data = self.Data
        tests = data['ScenarioName'].unique()
        for test in tests:
            data.loc[data['ScenarioName'] == test, 'AccelerationX'] = data.loc[data['ScenarioName'] == test, 'VelocityX'].diff()
            data.loc[data['ScenarioName'] == test, 'AccelerationY'] = data.loc[data['ScenarioName'] == test, 'VelocityY'].diff()

        
    def updateColumn(self, rowFilter, column, value):
        if self.Data is None:
            raise Exception("No data to update")

        self.Data.loc[rowFilter, column] = value

    def moveStartTime(self, timeStepOffset, reset_position=False):
        data = self.Data
        data["TimeStep"] -= timeStepOffset
        if reset_position:
            TestResults.__resetPosition(data)



    def plotTests(self, plotColumns, plotSize=(6,5), showLegend=True, plotTitle=True, saveLocation=None, plotCallback=None, plotTargetLines=True, legenPosition=None, alpha=1, lineStyle=None, targetLineStyle='--', targetLineColor='green', addLabels=True):
        if self.Data is None:
            raise Exception("No data to plot")

        nrPlots = len(plotColumns)

        fig, ax = plt.subplots(1, nrPlots, figsize=(plotSize[0] * nrPlots, plotSize[1]))
        if plotTitle:
            plt.title(self.Name)

        tests = self.Data["ScenarioName"].unique()

        for i, columns in enumerate(plotColumns):

            axis: Axis = ax[i] if nrPlots > 1 else ax

            minX = min(self.Data[columns[0]])
            maxX = max(self.Data[columns[0]])

            for test in tests:
                data = self.Data[self.Data["ScenarioName"] == test]
                axis.plot(data[columns[0]], data[columns[1]], label=test if addLabels else None, alpha=alpha, linestyle=lineStyle)

            if plotTargetLines:
                if columns[0] == 'VelocityX':
                    axis.plot([0, 8], [0, 8], color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Idle')
                    # axis.axvline(x=0, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Idle')
                    # axis.axvline(x=8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Right, Walk')
                    # axis.axvline(x=12.8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Right, Sprint')
                    # axis.axvline(x=-8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Left, Walk')
                    # axis.axvline(x=-12.8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Left, Sprint')
                elif columns[1] == 'VelocityX':
                    axis.plot([minX, maxX], [12.8, 12.8], color=targetLineColor, linestyle=targetLineStyle, label='Right, Sprint')
                    axis.plot([minX, maxX], [8, 8], color=targetLineColor, linestyle=targetLineStyle, label='Right, Walk')
                    axis.plot([minX, maxX], [0, 0], color=targetLineColor, linestyle=targetLineStyle, label='Idle')
                    axis.plot([minX, maxX], [-8, -8], color=targetLineColor, linestyle=targetLineStyle, label='Left, Walk')
                    axis.plot([minX, maxX], [-12.8, -12.8], color=targetLineColor, linestyle=targetLineStyle, label='Left, Sprint')

                    # axis.axhline(y=0, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Idle')
                    # axis.axhline(y=8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Right, Walk')
                    # axis.axhline(y=12.8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Right, Sprint')
                    # axis.axhline(y=-8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Left, Walk')
                    # axis.axhline(y=-12.8, color=targetLineColor, linestyle=targetLineStyle, label='Stable Velocity Left, Sprint')

                if columns[0] == 'VelocityY':
                    axis.axvline(x=0, color=targetLineColor, linestyle=targetLineStyle)
                    axis.axvline(x=18.460, color=targetLineColor, linestyle=targetLineStyle)
                    axis.axvline(x=18.460, color=targetLineColor, linestyle=targetLineStyle)
                    axis.axvline(x=-20, color=targetLineColor, linestyle=targetLineStyle)
                elif columns[1] == 'VelocityY':
                    axis.axhline(y=0, color=targetLineColor, linestyle=targetLineStyle)
                    axis.axhline(y=18.460, color=targetLineColor, linestyle=targetLineStyle)
                    axis.axhline(y=-20, color=targetLineColor, linestyle=targetLineStyle)

            axis.set_xlabel(columns[0])
            axis.set_ylabel(columns[1])
            axis.grid()

            if showLegend and i == nrPlots - 1:
                if legenPosition is None:
                    legenPosition = (1,1)
                axis.legend(bbox_to_anchor=legenPosition, ncol=math.ceil(tests.size / 12) if addLabels else 1)

        if plotCallback is not None:
            plotCallback(ax)
        
        if saveLocation is not None:
            plt.savefig(saveLocation, dpi=300, bbox_inches='tight')

    def preparePlots(self, nrPlots):
        fig, ax = plt.subplots(1, nrPlots, figsize=(6 * nrPlots, 5))
        # plt.title(self.Name)
        return ax if nrPlots > 1 else [ax]

    def comparePlot(self, axis, columns, showLegend=True, y_label=None, labels=None):
        if self.Data is None:
            raise Exception("No data to plot")

        if axis is None:
            _, axis = plt.subplots(1, 1, figsize=(4, 3))
        # plt.title(self.Name)
        data = self.Data

        for i, column in enumerate(columns):
            if labels is None:
                axis.plot(data['TimeStep'], data[column], label=column)
            else:
                axis.plot(data['TimeStep'], data[column], label=labels[i])

        axis.set_xlabel('TimeStep')
        axis.set_ylabel(y_label)
        axis.grid()
        if showLegend:
            axis.legend()
        # axis.legend(bbox_to_anchor=(1, 1))


class TestRunner:
    def runTests(testScenarios):
        uchServer = UCHServer()

        def __waitForResults():
            while True:
                time.sleep(1)

                uchServer.sendPingMessage()
                messages = uchServer.readMessages()

                if len(messages) > 0:
                    for message_type, message in messages:
                        if message_type == "testFinished":
                            return message

        uchServer.sendMessage(
            "runTest", json.dumps(testScenarios, default=lambda x: x.__dict__)
        )
        results = __waitForResults()
        return pd.DataFrame(results)