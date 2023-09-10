from utils.tools import dataAnalysisRoot


import os


class LevelPathBuilder:
    def getLevelDirectory(levelName, subPath=None, createIfNotExists=False):
        path = f'{dataAnalysisRoot}/Levels/{levelName}'
        if subPath is not None:
            path += f'/{subPath}'

        if createIfNotExists and not os.path.exists(path):
            os.makedirs(path)
        return path

    def getLevelTestsDirectory(levelName, subPath=None, createIfNotExists=False):
        if subPath is not None:
            subPath = f'Tests/{subPath}'
        else:
            subPath = 'Tests'
        return LevelPathBuilder.getLevelDirectory(levelName, subPath, createIfNotExists)

    def getLevelResultsDirectory(levelName, subPath=None, createIfNotExists=False):
        if subPath is not None:
            subPath = f'Results/{subPath}'
        else:
            subPath = 'Results'
        return LevelPathBuilder.getLevelDirectory(levelName, subPath, createIfNotExists)

    def getLevelNames():
        return os.listdir(f'{dataAnalysisRoot}/Levels')