from vars import *
import Cell

class State:
    def __init__(self, start, fuel, visited, statePos, valueChanges):
        self.start = start
        self.fuel = fuel
        self.visited = visited
        self.statePos = statePos
        self.valueChanges = valueChanges

    @staticmethod
    def initState(start, fuel):
        visited = {(0,0):[]}
        statePos = [0,0]
        valueChanges = {}
        initState = State(start, fuel, visited, statePos, valueChanges)
        return initState
    
    def move(self, move):

        ##prevent from going out of bounds later
        newPos = [move[0]+self.statePos[0], move[1]+self.statePos[1]]

        print(self.visited)

        if newPos in self.visited[tuple(self.statePos)]: #FUEL!!!!!!!!!!!
            return False, 0, 0
        
        currentPosx = self.start[0] + MCTSmoveDistance*self.statePos[0]
        currentPosy = self.start[1] + MCTSmoveDistance*self.statePos[1]

        posx = self.start[0] + MCTSmoveDistance*newPos[0]
        posy = self.start[1] + MCTSmoveDistance*newPos[1]

        fuel = self.fuel - getDist(posx, posy, currentPosx, currentPosy)

        radius = 5
        sValue = 0

        if posx < 1 + radius or posx > gridx - radius or posy < 1 + radius or posy > gridy - radius:
            return False, 0, 0

        # posx = min(gridx, max(posx, 1))
        # posy = min(gridy, max(posy, 1))

        newValueChanges = copy.deepcopy(self.valueChanges)

        if move == [0,1]:
            for y in range(currentPosy+1, currentPosy+MCTSmoveDistance+1):
                for x in range(currentPosx-radius, currentPosx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if (x, y) in self.valueChanges.keys():
                            sValue += self.valueChanges[(x,y)]
                        else:
                            sValue += grid[y-1][x-1].value
                        newValueChanges[(x,y)] = 0 ## MAYBE NOT ZERO? UNCERTAINTY IN MEASUREMENT
        elif move == [0,-1]:
            for y in range(currentPosy-MCTSmoveDistance, currentPosy):
                for x in range(currentPosx-radius, currentPosx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if (x, y) in self.valueChanges.keys():
                            sValue += self.valueChanges[(x,y)]
                        else:
                            sValue += grid[y-1][x-1].value
                        newValueChanges[(x,y)] = 0 
        elif move == [1,0]:
            for x in range(currentPosx-MCTSmoveDistance, currentPosx):
                for y in range(currentPosy-radius, currentPosy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if (x, y) in self.valueChanges.keys():
                            sValue += self.valueChanges[(x,y)]
                        else:
                            sValue += grid[y-1][x-1].value
                        newValueChanges[(x,y)] = 0 
        elif move == [-1,0]:
            for x in range(currentPosx+1, currentPosx+MCTSmoveDistance+1):
                for y in range(currentPosy-radius, currentPosy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        if (x, y) in self.valueChanges.keys():
                            sValue += self.valueChanges[(x,y)]
                        else:
                            sValue += grid[y-1][x-1].value
                        newValueChanges[(x,y)] = 0 

        newVisited = copy.deepcopy(self.visited)
        newVisited[tuple(self.statePos)].append(newPos)

        if tuple(newPos) in self.visited.keys():
            newVisited[tuple(newPos)].append(self.statePos)
        else:
            newVisited[tuple(newPos)] = [self.statePos]

        newState = State(self.start, fuel, newVisited, newPos, newValueChanges)
        
        return True, newState, sValue
    
    def calculateRollout(self):
        return abs(self.statePos[0]) + abs(self.statePos[1])
        #return random.randrange(10,40)