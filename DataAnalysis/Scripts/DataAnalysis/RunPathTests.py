import sys
import os
import argparse
sys.path.append(os.path.abspath('..'))
import multiprocessing

from services.UCHPathFinder import *

def runTest(testNr, levelName, quantizationFactor, heuristic, costWeights, frameCollisionOffset, maxTime):

    print(f'Running test {testNr} for level {levelName} with qF {quantizationFactor}, hF {costWeights}, heuristic {heuristic.name}, frameCollisionOffset {frameCollisionOffset}, maxTime {maxTime}')

    if frameCollisionOffset is not None:
        PlayerConstants.frameCollisionOffset=frameCollisionOffset

    pathFinder = UCHPathFinder(
        levelName, 
        quantizationFactor=quantizationFactor, 
        costWeights=costWeights,
        forceLoadLevel=False, 
        forceCreateNodeMap=False,
        heuristic=heuristic
    )

    statistic = {
        'levelName': levelName,
        'heuristic': heuristic.name,
        'qF': quantizationFactor,
        'hF': [round(factor, 2) for factor in costWeights],
        'collisionOffset': frameCollisionOffset,
        'maxTime': maxTime,
        'blocks': len(pathFinder.heuristics.blockMap.blocks)
    }
    results = [
        statistic
    ]

    for path in pathFinder.findPaths(maxTime):
        results.append({
            'iteration': pathFinder.pathFinder.iteration,
            'time': round(pathFinder.pathFinder.totalSearchTime),
            'length': len(path),
            'path': path,
        })

    statistic['time'] = pathFinder.pathFinder.totalSearchTime
    statistic['iteration'] = pathFinder.pathFinder.iteration
    statistic['skipped'] = pathFinder.pathFinder.skipped

    print(f'Finished test {testNr} for level {levelName} with qF {quantizationFactor}, hF {costWeights}, heuristic {heuristic.name}, frameCollisionOffset {frameCollisionOffset}, maxTime {maxTime}')

    return results

def saveResults(levelName, results):
    directory = LevelPathBuilder.getLevelDirectory(levelName, createIfNotExists=True)
    with open(f'{directory}/01_TestStatistics.json', 'w') as file:
        file.write('[\n')
        i = 0
        for result in results:
            if i > 0:
                file.write(',\n')
            i += 1
            json.dump(result, file, cls=ActionPathEncoder)
        file.write('\n]')

levels = [
    '9DPV-UYUB',
    '9XX9-EEB4',
    '9ZKX-X199',
    'CVPH-JDJ2',
    'CWYY-0ZNT',
    'E5A2-703N',

    'EA68-CTEG',
    'KMBB-J3DJ',
    'N4NV-H5H4',
    'SDXC-TCU6',
    'VGCW-6BF7',
]

heuristics = [
    ActionPathHeuristics.GoalDistanceFlood,
    ActionPathHeuristics.GoalDistanceEuclidean,
    ActionPathHeuristics.GoalDistanceManhatten
]

quantizationFactors = [
    (1, 1),
    (3, 3)
]

costWeights = [
    [0.5],
    [0.7],
    [0.9],
    [1.0],
    [0.5, 0.7, 0.9, 1]
]

maxTime = 1800




def runTestWrapper(args):
    return runTest(*args)

def createTestArgs(testNr, levelName, quantizationFactor, heuristic, costWeights, frameCollisionOffset, maxTime):
    return (testNr, levelName, quantizationFactor, heuristic, costWeights, frameCollisionOffset, maxTime)

def createTests():
    testNr = 1
    for level in levels:
        for heuristic in heuristics:
            for quantizationFactor in quantizationFactors:
                for costWeight in costWeights:                    
                    yield createTestArgs(testNr, level, quantizationFactor, heuristic, costWeight, 0.15, maxTime)
                    testNr += 1


if __name__ == "__main__":

    results = {}

    with multiprocessing.Pool(processes=16) as pool:
        # Map the square_number function to the list of numbers using multiple processes

        testResults = pool.map(runTestWrapper, createTests())

        for result in testResults:
            getOrAdd(results, result[0]['levelName'], lambda: []).append(result)
        
        for levelName, levelResults in results.items():        
            saveResults(levelName, levelResults)