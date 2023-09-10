class MergedHorizontalActionSequence:
    def __init__(self, name, hSequences):
        self.name = name
        self.hDatas = hSequences
        self.length = sum([len(d.Data) for d in self.hDatas]) - len(self.hDatas) + 1

    def iter(self, extensions = None, maxLength = 100):
        return MergedHorizontalActionSequence.__Iterator(self, extensions, maxLength)

    def print(self, extensions = None, maxLength = 100):
        for row in self.iter(extensions, maxLength):
            print(row)

    class __Iterator:
        def __init__(self, series, extensions, maxLength):
            self.series = series
            self.hDatas = [data.Data[['Action', 'VelocityX']].values for data in series.hDatas]
            self.hDataExtensions = [0] * len(series.hDatas) if extensions is None else extensions
            self.maxLength = maxLength
            if len(self.hDatas) != len(self.hDataExtensions):
                raise Exception(f'hDataExtension must be of length {len(series.hDatas)} for "{series.name}"')
            self.additionalFrames = sum(self.hDataExtensions) - len(self.hDatas) + 1
            self.startVX = series.hDatas[0].startVX
            self.endVX = series.hDatas[-1].endVX

            self.reset()

        def invert(self):
            return MergedHorizontalActionSequence(self.series.name, [hData.invert() for hData in self.series.hDatas]).iter(extensions=self.hDataExtensions, maxLength=self.maxLength)

        def reset(self):
            self.hDataIndex = 0
            self.hDataRowIndex = 0
            self.index = 0

        def __len__(self):
            if self.maxLength is None:
                return self.series.length + self.additionalFrames
            return max(self.maxLength, self.series.length + self.additionalFrames)

        def __iter__(self):
            return self

        def __next__(self):
            if self.maxLength is not None and self.index >= self.maxLength:
                raise StopIteration

            nextHData = self.__getNextHData()

            self.index += 1
            self.hDataRowIndex += 1
            return nextHData

        def __getNextHData(self, previousHData = None):
            if self.hDataIndex >= len(self.hDatas):
                return self.hDatas[-1][-1]

            hData = self.hDatas[self.hDataIndex]
            extension = self.hDataExtensions[self.hDataIndex]

            if previousHData is not None:
                hData[0] = [hData[0][0], previousHData[1]] # (previousVelocityX, currentAction)

            lastIndex = len(hData) - 1
            if self.hDataRowIndex >= lastIndex:
                extended = self.hDataRowIndex - lastIndex
                if extended < extension:
                    return hData[-1]

                self.hDataIndex += 1
                self.hDataRowIndex = 0
                return self.__getNextHData(previousHData=hData[-1])

            return hData[self.hDataRowIndex]