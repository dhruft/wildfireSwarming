from vars import *
import Cell

class State:
    def __init__(self, start, fuel, statePos, heatmap, pathVisitedPositions, worldPos):
        self.start = start
        self.fuel = fuel
        self.statePos = statePos
        self.heatmap = heatmap
        self.pathVisitedPositions = pathVisitedPositions
        self.worldPos = worldPos

    @staticmethod
    def initState(start, fuel, machine):
        statePos = [0,0]
        initState = State(start, fuel, statePos, heatmap, visitedPositions, start)
        return initState
    
    def move(self, move):

        ##prevent from going out of bounds later
        newPos = [move[0]+self.statePos[0], move[1]+self.statePos[1]]
        
        currentPosx = self.start[0] + moveDistance*self.statePos[0]
        currentPosy = self.start[1] + moveDistance*self.statePos[1]

        posx = self.start[0] + moveDistance*newPos[0]
        posy = self.start[1] + moveDistance*newPos[1]

        # make fuel usage a prediction based on value
        fuel = self.fuel - getDist(posx, posy, currentPosx, currentPosy)

        value = 0

        if posx < 1 + radius or posx > gridx - radius or posy < 1 + radius or posy > gridy - radius:
            return False, 0, 0
        
        if fuel <= 0:
            return False, 0, 0
        
        if [posx, posy] in self.pathVisitedPositions:
            return False, 0, 0
        
        newHeatMap = copy.deepcopy(self.heatmap)
        newPathVisitedPositions = copy.deepcopy(self.pathVisitedPositions)
        newPathVisitedPositions.append([posx, posy])
        
        # posx = min(gridx, max(posx, 1))
        # posy = min(gridy, max(posy, 1))

        if move == [0,1]:
            for y in range(currentPosy+1, currentPosy+moveDistance+1):
                for x in range(currentPosx-radius, currentPosx+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        tree.visit(False, newHeatMap)
                        value += treeValue
        elif move == [0,-1]:
            for y in range(currentPosy-moveDistance, currentPosy):
                for x in range(currentPosx-radius, currentPosx+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        tree.visit(False, newHeatMap)
                        value += treeValue
        elif move == [-1,0]:
            for x in range(currentPosx-moveDistance, currentPosx):
                for y in range(currentPosy-radius, currentPosy+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        tree.visit(False, newHeatMap)
                        value += treeValue
        elif move == [1,0]:
            for x in range(currentPosx+1, currentPosx+moveDistance+1):
                for y in range(currentPosy-radius, currentPosy+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        tree.visit(False, newHeatMap)
                        value += treeValue
        
        newState = State(self.start, fuel, newPos, newHeatMap, newPathVisitedPositions, [posx, posy])

        return True, newState, value