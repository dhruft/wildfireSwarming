from vars import *

class State:
    def __init__(self, start, fuel, visited, current):
        self.start = start
        self.fuel = fuel
        self.visited = visited
        self.current = current

    
    def initState(start, fuel):
        visited = {[0,0]:[]}
        current = [0,0]
        initState = State(start, fuel, visited, current)
        return initState
    
    def move(self, move):

        ##prevent from going out of bounds later
        newPos = [move[0]+self.current[0], move[1]+self.current[1]]

        if newPos in self.visited[self.current]:
            return False, 0, 0
        
        newVisited = self.visited.copy()
        newVisited[self.current].append(newPos)

        if move in self.visited.keys():
            newVisited[newPos].append(self.current)
        else:
            newVisited[newPos] = [self.current]

        fuel = self.fuel - MCTSmoveDistance
        
        CALCULATE SVALUE!!!

        newState = State(self.start, fuel, newVisited, newPos)
        
        return True, newState, sValue
    
    def calculateRollout(self):
        return math.randrange(10,40)