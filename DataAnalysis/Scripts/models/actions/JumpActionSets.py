from typing import Generator
from models.actions.JumpActionSequence import JumpActionSequence
from models.actions.ActionSet import ActionSet
from models.actions.HorizontalActionSeries import HorizontalActionSequence
from models.actions.HorizontalVelocityState import HorizontalVelocityState
from models.actions.MergedHorizontalActionSequence import MergedHorizontalActionSequence
from models.actions.MotionState import MotionState
from models.actions.VerticalActionSequence import VerticalActionSequence


class JumpActionSets:
    def __init__(self):

        self.vData = [VerticalActionSequence('VerticalGroundJumpTests', 'Jump_'+str(i), 0, 60, MotionState.OnGround) for i in range(1, 23, 1)]
        self.vData += [VerticalActionSequence('VerticalWallJumpTests', 'Jump_'+str(i), 0, 60, MotionState.OnWall) for i in range(1, 19, 1)]
                
        self.hData = [
            # HorizontalActionSeries('HorizontalGroundAccelerationTests', 'Idle -> Walk', 0, 17, MotionState.OnGround),
            HorizontalActionSequence('HorizontalGroundAccelerationTests', 'Idle -> Sprint', 0, 17, MotionState.OnGround),
            # HorizontalActionSeries('HorizontalGroundAccelerationTests', 'Walk -> Sprint', 0, 7, MotionState.OnGround),
            # HorizontalActionSeries('HorizontalGroundAccelerationTests', 'Sprint -> Walk', 0, 1, MotionState.OnGround),
            # HorizontalActionSeries('HorizontalGroundAccelerationTests', 'Walk -> Idle', 0, 3),
            # HorizontalActionSeries('HorizontalGroundAccelerationTests', 'Sprint -> Idle', 0, 4),
            # HorizontalActionSeries('HorizontalGroundAccelerationTests', 'Walk -> Crouch', 0, 1, MotionState.OnGround),
            HorizontalActionSequence('HorizontalGroundAccelerationTests', 'Sprint -> Crouch', 0, 2, MotionState.OnGround),
            
            
            HorizontalActionSequence('HorizontalAirAccelerationTests', 'Idle -> Walk', 0, 22, MotionState.InAir),
            HorizontalActionSequence('HorizontalAirAccelerationTests', 'Idle -> Sprint', 0, 22, MotionState.InAir),
            
            # HorizontalActionSeries.createStaticSeries('HorizontalAirAccelerationTests', 'Idle -> Walk', 22, MotionState.InAir, name='Walk -> Walk', length=1),
            HorizontalActionSequence.createStaticSeries('HorizontalAirAccelerationTests', 'Idle -> Sprint', 22, MotionState.InAir, name='Sprint -> Sprint', length=1),
            HorizontalActionSequence('HorizontalAirAccelerationTests', 'Walk -> Sprint', 0, 6, MotionState.InAir),
            HorizontalActionSequence('HorizontalAirAccelerationTests', 'Sprint -> Walk', 0, 1, MotionState.InAir),
            HorizontalActionSequence('HorizontalAirStopTests', 'Walk -> Idle', 0, 11, MotionState.InAir),
            HorizontalActionSequence('HorizontalAirStopTests', 'Sprint -> Idle', 0, 11, MotionState.InAir),
            HorizontalActionSequence('HorizontalAirTurnaroundTests', 'Right,Sprint -> Left -> Left,Sprint', 0, 26, MotionState.InAir),
            HorizontalActionSequence('HorizontalAirTurnaroundTests', 'Right -> Left,Sprint', 0, 28, MotionState.InAir),
            
            HorizontalActionSequence('HorizontalAirAccelerationFromStopTests', 'AirStop -> Left,Sprint', 0, 24, MotionState.InAir),
            HorizontalActionSequence('HorizontalAirAccelerationFromStopTests', 'AirStop -> Right,Sprint', 0, 24, MotionState.InAir),

            HorizontalActionSequence('HorizontalWallJumpTests', 'Wall -> Walk', 0, 2, MotionState.OnWall),
            HorizontalActionSequence('HorizontalWallJumpTests', 'Wall -> Sprint', 0, 2, MotionState.OnWall),
            HorizontalActionSequence('HorizontalQuickWallJumpTests', 'Wall -> QuickBack', 0, 19, MotionState.OnWall),
        ]
        self.hData.extend([d.invert() for d in self.hData])
        self.hData.extend([    
            HorizontalActionSequence.createStaticSeries('HorizontalGroundAccelerationTests', 'Walk -> Crouch', 1, MotionState.OnGround, name='Idle -> Idle', length=1),
        ])
        self.hData = sorted(self.hData, key=lambda x: (x.motionState.value, abs(x.startVX.value), abs(x.endVX.value)))
        
        
        self.jumpAccelerationSets = [
            MergedHorizontalActionSequence('GroundJump Short Idle->Idle->Forward', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.WalkRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.WalkRight, HorizontalVelocityState.IdleRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleRight, HorizontalVelocityState.SprintRight)[0]
            ]),
            MergedHorizontalActionSequence('GroundJump Short Idle->Idle->Forward2', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                HorizontalActionSequence('HorizontalShortStopJumpTests', '1 Block Stop', 9, 22, MotionState.InAir),
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0]
            ]),
            MergedHorizontalActionSequence('GroundJump Short Idle->Idle->Forward2', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                HorizontalActionSequence('HorizontalShortStopJumpTests', '1.5 Block Stop', 10, 25, MotionState.InAir),
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0]
            ]),
            MergedHorizontalActionSequence('GroundJump Short Idle->Idle->Backward', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.WalkRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.WalkRight, HorizontalVelocityState.IdleRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleRight, HorizontalVelocityState.SprintLeft)[0]
            ]),
            MergedHorizontalActionSequence('GroundJump Short Idle->Idle->Backward2', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                HorizontalActionSequence('HorizontalShortStopJumpTests', '1 Block Stop', 9, 22, MotionState.InAir),
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintLeft)[0]
            ]),
            MergedHorizontalActionSequence('GroundJump Short Idle->Idle->Backward2', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                HorizontalActionSequence('HorizontalShortStopJumpTests', '1.5 Block Stop', 10, 25, MotionState.InAir),
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintLeft)[0]
            ]),

            MergedHorizontalActionSequence('GroundJump Long Idle->Idle', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.IdleRight)[0],
            ]),
            MergedHorizontalActionSequence('GroundJump Sprint->Idle->Turn', [
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.SprintRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.IdleRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleRight, HorizontalVelocityState.SprintLeft)[0],
            ]),
            MergedHorizontalActionSequence('GroundJump Idle->Sprint', [
                self.findHData(MotionState.OnGround, HorizontalVelocityState.Idle, HorizontalVelocityState.Idle)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
            ]),
            MergedHorizontalActionSequence('GroundJump Sprint->Idle', [
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0].fromLastFrame(1),
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.IdleRight)[0],
            ]),
            MergedHorizontalActionSequence('GroundJump Sprint->Sprint', [
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0].fromLastFrame(1),
            ]),
            MergedHorizontalActionSequence('GroundJump Right,Sprint->Left,Sprint', [
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0].fromLastFrame(1),
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.SprintLeft)[0],
            ]),
            MergedHorizontalActionSequence('GroundJump Right,Sprint->Left,Sprint->Idle', [
                self.findHData(MotionState.InAir, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0].fromLastFrame(1),
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.SprintLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintLeft, HorizontalVelocityState.IdleLeft)[0],
            ]),


            MergedHorizontalActionSequence('WallJump Back', [
                self.findHData(MotionState.OnWall, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.SprintLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintLeft, HorizontalVelocityState.IdleLeft)[0],
            ]),
            MergedHorizontalActionSequence('WallQuickJump Back and Turnaround', [
                self.findHData(MotionState.OnWall, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintLeft, HorizontalVelocityState.IdleLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleLeft, HorizontalVelocityState.SprintRight)[0],
            ]),
            MergedHorizontalActionSequence('WallJump Forward,Sprint', [
                self.findHData(MotionState.OnWall, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
            ]),
            MergedHorizontalActionSequence('WallJump Forward->Turn', [
                self.findHData(MotionState.OnWall, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.IdleRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleRight, HorizontalVelocityState.SprintLeft)[0],
            ]),
            MergedHorizontalActionSequence('WallJump Forward->Stop->Forward', [
                self.findHData(MotionState.OnWall, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.IdleRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleRight, HorizontalVelocityState.SprintRight)[0],
            ]),
            MergedHorizontalActionSequence('WallJump Forward->Turn->Idle->Turn', [
                self.findHData(MotionState.OnWall, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.IdleRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleRight, HorizontalVelocityState.SprintLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintLeft, HorizontalVelocityState.IdleLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleLeft, HorizontalVelocityState.SprintRight)[0],
            ]),
            MergedHorizontalActionSequence('WallJump Forward->Turn->Idle->Back', [
                self.findHData(MotionState.OnWall, HorizontalVelocityState.Idle, HorizontalVelocityState.SprintRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintRight, HorizontalVelocityState.IdleRight)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleRight, HorizontalVelocityState.SprintLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.SprintLeft, HorizontalVelocityState.IdleLeft)[0],
                self.findHData(MotionState.InAir, HorizontalVelocityState.IdleLeft, HorizontalVelocityState.SprintLeft)[0],
            ]),
        ]
        
        
    def findVData(self, motionState) -> list[VerticalActionSequence]:
        results = []
        for i in range(len(self.vData)):
            if self.vData[i].motionState == motionState:
                results.append(self.vData[i])

        if len(results) == 0:
            raise Exception(f'No vdata found with motionState={motionState}')
        return results

    def findHData(self, motionState: MotionState, startVX: HorizontalVelocityState, endVX: HorizontalVelocityState) -> list[HorizontalActionSequence]: 
        results = [] 
        
        for i in range(len(self.hData)):
            if self.hData[i].motionState == motionState and\
                (startVX is None or self.hData[i].startVX == startVX) and\
                (endVX is None or self.hData[i].endVX == endVX):
                results.append(self.hData[i])

        if len(results) == 0:
            raise Exception(f'No hdata found with motionState={motionState}, startVX={startVX}, endVX={endVX}')
        return results

    def findJumpAccelerationSets(self, name):
        for j in self.jumpAccelerationSets:
            if j.name == name:
                yield j
        # raise Exception(f'No jumpAccelerationSet found with name={name}')
    
    def createExtensions(self, variationIterators, extensions = []):
        if len(extensions) == len(variationIterators):
            yield extensions
            return
            

        for variation in variationIterators[len(extensions)]:            
            for result in self.createExtensions(variationIterators, extensions + [variation]):
                yield result

    def createActionSequence(self, vData, hData, maxLength=None, extensions=None):        
        return JumpActionSequence(vData.iter(maxLength=None), 
                            hData.iter(extensions=extensions, maxLength=maxLength))

    def createActionSequences(self, vData, hDatas, extensions, maxLength=None):
        extensions = list(extensions)
        hDatas = list(hDatas)
        for hData in hDatas:
            for extension in extensions:
                yield self.createActionSequence(vData, hData, extensions=extension, maxLength=maxLength)



    def getShortGroundIdleIdleForwardJumps(self, extensions):
        
        for vData in self.findVData(MotionState.OnGround):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Short Idle->Idle->Forward'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet

    def getShortGroundIdleIdleForwardJumps2(self, extensions):
        
        for vData in self.findVData(MotionState.OnGround):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Short Idle->Idle->Forward2'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet

    def getShortGroundIdleIdleBackwardJumps(self, extensions):
        
        for vData in self.findVData(MotionState.OnGround):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Short Idle->Idle->Backward'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet

    def getShortGroundIdleIdleBackwardJumps2(self, extensions):
        
        for vData in self.findVData(MotionState.OnGround):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Short Idle->Idle->Backward2'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet


    def getLongGroundIdleIdleJumps(self, minMovement, maxMovement, stepSize, prolongEnd):
        
        for vData in self.findVData(MotionState.OnGround):

            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Long Idle->Idle'),
                self.createExtensions([
                    [0],
                    range(minMovement, maxMovement, stepSize),
                    [prolongEnd],
                ])
            )
            for actionSet in actionSets:        
                yield actionSet

    def getGroundSprintIdleTurn(self, extensions):
        
        for vData in self.findVData(MotionState.OnGround):

            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Sprint->Idle->Turn'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet


    def getGroundIdleSprintJumps(self, prolongEnd):
        
        for vData in self.findVData(MotionState.OnGround):
            startLength = (vData.Data['VelocityY'].cumsum() / 60).argmax() - 10
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Idle->Sprint'),
                self.createExtensions([
                    [0, startLength],
                    [prolongEnd],
                ])
            )
            for actionSet in actionSets:        
                yield actionSet

        
    def getGroundSprintIdleJumps(self, prolongStart, step, prolongEnd):
        for vData in self.findVData(MotionState.OnGround):
            startLength = (vData.Data['VelocityY'].cumsum() / 60).argmax() - 9
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Sprint->Idle'),
                self.createExtensions([
                    range(startLength, prolongStart, step),
                    [prolongEnd],
                ])
            )
            for actionSet in actionSets:        
                yield actionSet


    def getGroundSprintSprintJumps(self, prolongEnd):

        for vData in self.findVData(MotionState.OnGround):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Sprint->Sprint'),
                self.createExtensions([
                    [prolongEnd],
                ])
            )
            for actionSet in actionSets:        
                yield actionSet

    def getGroundSprintTurnaroundJumps(self, prolongStart, step, prolongEnd):

        for vData in self.findVData(MotionState.OnGround):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Right,Sprint->Left,Sprint'),
                self.createExtensions([
                    range(0, prolongStart, step),
                    [prolongEnd],
                ])
            )
            for actionSet in actionSets:        
                yield actionSet

    def getGroundSprintTurnaroundIdleJumps(self, prolongStart, step1, prolongMovement, step2, prolongEnd):

        for vData in self.findVData(MotionState.OnGround):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('GroundJump Right,Sprint->Left,Sprint->Idle'),
                self.createExtensions([
                    range(0, prolongStart, step1),
                    range(0, prolongMovement, step2),
                    [prolongEnd],
                ])
            )
            for actionSet in actionSets:        
                yield actionSet

    def getWallJumpsBack(self, extensions):

        for vData in reversed(self.findVData(MotionState.OnWall)):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('WallJump Back'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet
            break

    def getWallQuickJumpsBack(self, extensions):

        for vData in reversed(self.findVData(MotionState.OnWall)):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('WallQuickJump Back and Turnaround'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet
            # break

    def getWallJumpsForwardSprint(self, prolongEnd):

        for vData in self.findVData(MotionState.OnWall):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('WallJump Forward,Sprint'),
                self.createExtensions([
                    [prolongEnd],
                ])
            )
            for actionSet in actionSets:        
                yield actionSet

    def getWallJumpsForwardTurn(self, extensions):

        for vData in self.findVData(MotionState.OnWall):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('WallJump Forward->Turn'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet

    def getWallJumpsForwardStopForward(self, extensions):

        for vData in self.findVData(MotionState.OnWall):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('WallJump Forward->Stop->Forward'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet

    def getWallJumpsForwardTurnIdleTurn(self, extensions):

        for vData in self.findVData(MotionState.OnWall):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('WallJump Forward->Turn->Idle->Turn'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet

    def getWallJumpsForwardTurnIdleBack(self, extensions):

        for vData in self.findVData(MotionState.OnWall):
            actionSets = self.createActionSequences(
                vData,
                self.findJumpAccelerationSets('WallJump Forward->Turn->Idle->Back'),
                self.createExtensions(extensions)
            )
            for actionSet in actionSets:        
                yield actionSet

    def getGroundJumps(self) -> 'ActionSet':
        
        def __iterator():           
            for actionSet in self.getShortGroundIdleIdleForwardJumps([
                    [0],
                    range(0, 20, 5),
                    range(0, 70, 20),
                    [10]
                ]):
                yield actionSet 
            for actionSet in self.getShortGroundIdleIdleForwardJumps2([
                    [0],
                    range(0, 100, 30),
                    [0]
                ]):
                yield actionSet 
                
            for actionSet in self.getShortGroundIdleIdleBackwardJumps([
                    [0],
                    range(0, 20, 5),
                    range(0, 70, 20),
                    [10]
                ]):
                yield actionSet                 
            for actionSet in self.getShortGroundIdleIdleBackwardJumps2([
                    [0],
                    range(0, 100, 30),
                    [0]
                ]):
                yield actionSet 

            # for actionSet in self.getLongGroundIdleIdleJumps(8, 40, 1, 10):
            #     yield actionSet
            for actionSet in self.getGroundIdleSprintJumps(100):
                yield actionSet
            for actionSet in self.getGroundSprintSprintJumps(100):
                yield actionSet
            # for actionSet in self.getGroundSprintIdleJumps(50, 1, 40):
            #     yield actionSet
            # for actionSet in self.getGroundSprintTurnaroundJumps(10, 1, 30):
            #     yield actionSet
            # for actionSet in self.getGroundSprintTurnaroundIdleJumps(22, 50, 30):
            #     yield actionSet
            for actionSet in self.getGroundSprintIdleTurn([
                    range(1, 7, 1),
                    range(1, 7, 1),
                    [10]
                ]):
                yield actionSet
            for actionSet in self.getGroundSprintIdleTurn([
                    range(10, 50, 4),
                    range(15, 75, 15),
                    [30]
                ]):
                yield actionSet

        return ActionSet('GroundJumps', __iterator())
    

    def getWallJumps(self) -> 'ActionSet':
        
        def __iterator():            
            for actionSet in self.getWallQuickJumpsBack([
                    range(0, 20, 2),
                    range(0, 100, 20),
                    [10]
                ]):
                yield actionSet
            for actionSet in self.getWallJumpsForwardTurnIdleTurn([
                    range(0, 1, 1),
                    range(0, 1, 1),
                    range(0, 10, 2),
                    range(0, 41, 20),
                    [10],
                ]):
                yield actionSet
            for actionSet in self.getWallJumpsForwardTurn([
                    range(0, 7, 1),
                    range(0, 5, 1),
                    [50],
                ]):
                yield actionSet
            for actionSet in self.getWallJumpsForwardTurn([
                    range(10, 50, 5),
                    range(20, 100, 30),
                    [50],
                ]):
                yield actionSet
            for actionSet in self.getWallJumpsForwardStopForward([
                    range(0, 7, 1),
                    range(0, 5, 1),
                    [50],
                ]):
                yield actionSet
            for actionSet in self.getWallJumpsForwardStopForward([
                    range(10, 50, 5),
                    range(20, 100, 30),
                    [50],
                ]):
                yield actionSet

        return ActionSet('WallJumps', __iterator())
    

    def getJumpSlideToNormalSet(self) -> ActionSet:
        hData = VerticalActionSequence('VerticalWallSlideTests', 'JumpToMedium', 1, 38, None, resetVelocityInFirstFrame=False)
        return JumpActionSequence(hData.iter(maxLength=39), None)

    def getDropSlideToNormalSet(self) -> ActionSet:
        hData = VerticalActionSequence('VerticalWallSlideTests', 'WallSlide Medium', 0, 11, None, resetVelocityInFirstFrame=False)
        return JumpActionSequence(hData.iter(maxLength=39), None)

    def getJumpAccelerations(self) -> list[float]:        
        vData = list(self.findVData(MotionState.OnGround))[-1].Data.copy()
        vData['AccelerationY'] = vData['VelocityY'].diff()
        vData.drop(columns=['Action', 'TimeStep'], inplace=True)
        vData = vData.loc[2:]
        return vData.values.tolist()