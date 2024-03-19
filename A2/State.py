from vars import *
import Cell

def getSValue(std):
    if std < 3:
        return 0
    return std

class State:
    def __init__(self, start, fuel, statePos, machine):
        self.start = start
        self.fuel = fuel
        self.statePos = statePos
        self.machine = machine

    @staticmethod
    def initState(start, fuel, machine):
        statePos = [0,0]
        initState = State(start, fuel, statePos, machine)
        return initState
    
    def move(self, move):

        ##prevent from going out of bounds later
        newPos = [move[0]+self.statePos[0], move[1]+self.statePos[1]]
        
        currentPosx = self.start[0] + MCTSmoveDistance*self.statePos[0]
        currentPosy = self.start[1] + MCTSmoveDistance*self.statePos[1]

        posx = self.start[0] + MCTSmoveDistance*newPos[0]
        posy = self.start[1] + MCTSmoveDistance*newPos[1]

        # make fuel usage a prediction based on sValue
        fuel = self.fuel - getDist(posx, posy, currentPosx, currentPosy)

        sValue = 0

        if posx < 1 + radius or posx > gridx - radius or posy < 1 + radius or posy > gridy - radius:
            return False, 0, 0
        
        if fuel <= 0:
            return False, 0, 0
        
        newMachine = copy.deepcopy(self.machine)
        
        # posx = min(gridx, max(posx, 1))
        # posy = min(gridy, max(posy, 1))

        if move == [0,1]:
            for y in range(currentPosy+1, currentPosy+MCTSmoveDistance+1):
                for x in range(currentPosx-radius, currentPosx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if grid[y-1][x-1].visited:
                            continue
                        std = getSTD(newMachine, grid[y-1][x-1])
                        updateMachine(newMachine, grid[y-1][x-1])
                        sValue += getSValue(std)
        elif move == [0,-1]:
            for y in range(currentPosy-MCTSmoveDistance, currentPosy):
                for x in range(currentPosx-radius, currentPosx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if grid[y-1][x-1].visited:
                            continue
                        std = getSTD(newMachine, grid[y-1][x-1])
                        updateMachine(newMachine, grid[y-1][x-1])
                        sValue += getSValue(std)
        elif move == [-1,0]:
            for x in range(currentPosx-MCTSmoveDistance, currentPosx):
                for y in range(currentPosy-radius, currentPosy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if grid[y-1][x-1].visited:
                            continue
                        std = getSTD(newMachine, grid[y-1][x-1])
                        updateMachine(newMachine, grid[y-1][x-1])
                        sValue += getSValue(std)
        elif move == [1,0]:
            for x in range(currentPosx+1, currentPosx+MCTSmoveDistance+1):
                for y in range(currentPosy-radius, currentPosy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if grid[y-1][x-1].visited:
                            continue
                        std = getSTD(newMachine, grid[y-1][x-1])
                        updateMachine(newMachine, grid[y-1][x-1])
                        sValue += getSValue(std)
        newState = State(self.start, fuel, newPos, newMachine)

        return True, newState, sValue
    
    def calculateRollout(self):
        # return abs(self.statePos[0]) + abs(self.statePos[1])
        return 0
        #return random.randrange(10,40)