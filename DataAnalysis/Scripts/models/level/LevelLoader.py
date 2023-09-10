import os
from models.level.LevelPathBuilder import LevelPathBuilder
from utils.UCHServer import UCHServer
from utils.tools import *

class LevelLoader:
    LevelDataFileName = '00_LevelData.json'

    def fromLevel(levelName, forceCreate=False):
        path = LevelPathBuilder.getLevelDirectory(levelName)
        if not os.path.exists(path) or forceCreate:
            levelData = LevelLoader.__loadLevelFromGame(levelName)
            LevelLoader.__saveLevel(levelData, path)
        else:
            levelData = pd.read_json(path + '/' + LevelLoader.LevelDataFileName, orient='records')
        
        levelData = levelData[~levelData.duplicated()]
        return levelData


    def __loadLevelFromGame(levelName):
        uchServer = UCHServer()
        uchServer.sendKeepAliveMessage()
        uchServer.sendMessage("getPathGeneratorRequest", json.dumps({"LevelCode": levelName}))

        messages = uchServer.readMessages()

        while len(messages) == 0:
            time.sleep(1)
            messages = uchServer.readMessages()

        for message_type, message in messages:
            if message_type == 'generatePath':
                return LevelLoader.__createLevelData(message)

        raise Exception("No level found")



    def __saveLevel(levelData: pd.DataFrame, path):
        if not os.path.exists(path):
            os.makedirs(path)
        levelData.to_json(path + '/' + LevelLoader.LevelDataFileName, orient='records', indent=4)

    def __createLevelData(request):
        blockData = LevelLoader.__parseBlockData(request)
        blockData = blockData[blockData.Type != 'Goal']
        playerData = LevelLoader.__parseSpawnData(request)
        goalData = LevelLoader.__parseGoalData(request)
        return pd.concat([blockData, playerData, goalData], ignore_index=True)

    def __parseBlockData(request):
        df = pd.DataFrame(request['Level']['Blocks'])
        df.rename({'CollisionType': 'Type'}, inplace=True, axis=1)
        df = LevelLoader.__unmapBounds(df)
        df.drop(['Name', 'BlockId', 'ParentId', 'SceneId', '$type'], axis=1, inplace=True)
        return df

    def __parseSpawnData(request):
        df = pd.DataFrame(data=[request['Spawn']])
        df.rename({'CollisionType': 'Type'}, inplace=True, axis=1)
        df = LevelLoader.__unmapBounds(df)
        df['Type'] = 'Spawn'
        return df

    def __parseGoalData(request):
        df = pd.DataFrame(data=request['Level']['Goals'])
        df = LevelLoader.__unmapBounds(df)
        df['Type'] = 'Goal'
        df.drop(['BlockId', 'ParentId', 'SceneId', 'CollisionType'], axis=1, inplace=True)
        return df

    def __unmapBounds(df, boundsColumn='Bounds'):
        df['X'] = df[boundsColumn].apply(lambda x: x['Position']['X'])
        df['Y'] = df[boundsColumn].apply(lambda x: x['Position']['Y'])
        df['Width'] = df[boundsColumn].apply(lambda x: x['Size']['X'])
        df['Height'] = df[boundsColumn].apply(lambda x: x['Size']['Y'])
        df.drop(['Bounds'], axis=1, inplace=True)
        return df