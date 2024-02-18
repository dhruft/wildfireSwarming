
from vars import *
import MCTSNode
import State
import Cell

async def task_function(uav):
    await uav.mainLoop()

def centerToCircle(x,y,radius):
    return (x*cw-cw/2-cw*radius, y*cw-cw/2-cw*radius,
                      x*cw-cw/2+cw*radius, y*cw-cw/2+cw*radius)


def chooseTarget():
    x = random.randint(*random.choice([ [1,math.floor(center[0])],[math.ceil(center[0]+1), gridx] ]))
    y = random.randint(*random.choice([ [1,math.floor(center[1])],[math.ceil(center[1]+1), gridy] ]))

    return [x,y]

class UAV:
    
    def __init__(self, posx, posy):
        global c
        c = canvas[0]
        self.posx = posx
        self.posy = posy
        
        self.fuel = startFuel

        color = "green"
        self.circle = c.create_oval(centerToCircle(posx,posy,uavRadius),
                       fill=color)
    
    def update(self):
        c.coords(self.circle, centerToCircle(self.posx,self.posy,uavRadius))
    
    async def mainLoop(self):

        global deployments

        if deployments <= 0:
            return

        deployments -= 1
        self.fuel = startFuel

        # target = chooseTarget()
        # await self.goTo(*target)

        await self.goTo(1000,1000)
            
        while self.fuel > getDist(self.posx, self.posy, center[0], center[1]):
            await self.chooseMove()
            await asyncio.sleep(3)
        
        await self.goTo(*center)
        await asyncio.sleep(redeploymentTime)

        # updatePlot()

        if deployments > 0:
            await self.mainLoop()

        return
    
    async def chooseMove(self):
        start_time = time.time()
        count = 0

        startNode = MCTSNode.MCTSNode(State.State.initState([self.posx, self.posy], self.fuel))
        
        #use this instead of node.children in case child gets removed from tree
        children = UAV.addChildren(startNode)

        while time.time() - start_time < 0.25:
            if (self.runMCTS(startNode) == -2):
                break
            count += 1

        maxScore = 0
        maxNode = None
        for child in children:
            score = child.sValue + child.cValue
            print(child.state.statePos, child.sValue, child.cValue)
            if score > maxScore:
                maxScore = score
                maxNode = child

        move = maxNode.state.statePos
        print(maxNode.sValue)
        
        #newPos = [move[0]*MCTSmoveDistance+self.posx, move[1]*MCTSmoveDistance+self.posy]
        radius = 5

        ## PUT SERPENTINE ALGORITHM HERE!!!! UPDATE VALUES IN GRID OF ALL TREES VISITED!!!!
        if move == [0,1]:
            for y in range(self.posy+1, self.posy+MCTSmoveDistance+1):
                for x in range(self.posx-radius, self.posx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        grid[y-1][x-1].value = 0
        elif move == [0,-1]:
            for y in range(self.posy-MCTSmoveDistance, self.posy):
                for x in range(self.posx-radius, self.posx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        grid[y-1][x-1].value = 0
        elif move == [-1,0]:
            for x in range(self.posx-MCTSmoveDistance, self.posx):
                for y in range(self.posy-radius, self.posy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        grid[y-1][x-1].value = 0
        elif move == [1,0]:
            for x in range(self.posx+1, self.posx+MCTSmoveDistance+1):
                for y in range(self.posy-radius, self.posy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        grid[y-1][x-1].value = 0
        else:
            print(move)

        await self.goTo(self.posx + move[0]*MCTSmoveDistance, self.posy+move[1]*MCTSmoveDistance)
        print(self.fuel)
        print("MCTS Iterations Count: ", count)
        
    @staticmethod
    def addChildren(node):
        # right, right up, right down, down, up, left, left up, left down
        #moves = [[1,0], [1,-1], [1,1], [0, 1], [0,-1], [-1,0], [-1,-1], [-1,1]]
        moves = [[1,0],[-1,0],[0,1],[0,-1]]
        children = []
        for move in moves:
            possible, newState, sValue = node.state.move(move)

            if not possible:
                continue

            child = MCTSNode.MCTSNode(newState, node)
            child.sValue = sValue

            node.children.append(child)
            children.append(child)

        return children

        # handle case that there are no possible moves left??

    def runMCTS(self, current):
        value = 0
        if len(current.children) == 0:
            if current.number_of_visits == 0:

                value = current.state.calculateRollout()
                current.cValue = value
                value += current.sValue
            elif current.number_of_visits == 1:
                UAV.addChildren(current)

                # if no possible moves remove node from tree
                if len(current.children) == 0:
                    current.parent.children.remove(current)
                    return -1

                # currentPosx = current.state.start[0] + MCTSmoveDistance*current.state.statePos[0]
                # currentPosy = current.state.start[1] + MCTSmoveDistance*current.state.statePos[1]
                # print(currentPosx, currentPosy, current.children)

                value = self.runMCTS(current.children[0]) #change to select the child that moves away from start location
                current.cValue += value
            else:
                if current.state.statePos == [0,0]:
                    return -2

                ## if its an endpoint or no moves available, prevent tree from exploring this node
                current.parent.children.remove(current)
                return -1
        else:
            maxUCB1 = 0
            maxNode = None
            for child in current.children:
                if child.getUCB1() > maxUCB1:
                    maxUCB1 = child.getUCB1()
                    maxNode = child

            value = self.runMCTS(maxNode)
            current.cValue += value

        if value == -1:
            return value
        else:
            current.number_of_visits += 1
            return value

    async def goTo(self, x, y):
        self.target = [x,y]
        self.fuel -= getDist(x,y,self.posx,self.posy)
        self.cell = grid[y-1][x-1]

        while self.posx != x or self.posy != y:
            await asyncio.sleep(ti)

            dist = getDist(x,y,self.posx,self.posy)
            distTraveled = vel*ti
            sideRatio = (dist-distTraveled)/dist

            oldPos = [self.posx, self.posy]

            if dist <= distTraveled:
                self.posx = x
                self.posy = y
            else:
                self.posx = x-(x-self.posx)*sideRatio
                self.posy = y-(y-self.posy)*sideRatio
            
            if showPath: c.create_line(*posWithCW(oldPos), *posWithCW([self.posx, self.posy]), fill="black", width=2)
            self.update()
    
def posWithCW(pos):
    x = pos[0]*cw - cw/2
    y = pos[1]*cw - cw/2
    return [x,y]