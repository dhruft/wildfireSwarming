
from vars import *
import MCTSNode
import State

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
            
        while self.fuel > getDist(self.posx, self.posy, center[0], center[1]):
            await self.chooseMove()
            await asyncio.sleep(3)
        
        await self.goTo(*center)
        await asyncio.sleep(redeploymentTime)

        # updatePlot()

        if deployments > 0:
            await self.mainLoop()

        return

        #DURING LOOP, if height is already known, update thresholds immediatley otherwise wait until you get there
    
    async def chooseMove(self):
        start_time = time.time()
        count = 0

        startNode = MCTSNode.MCTSNode(State.State.initState([self.posx, self.posy], self.fuel))
        UAV.addChildren(startNode)
        while time.time() - start_time < 0.25:
            self.runMCTS(startNode)
            count += 1

        maxScore = 0
        maxNode = None
        for child in startNode.children:
            if child.sValue + child.cValue > maxScore:
                maxScore = child.sValue + child.cValue
                maxNode = child

        move = maxNode.state.statePos
        print(maxNode.sValue)
        await self.goTo(self.posx + move[0]*MCTSmoveDistance, self.posy+move[1]*MCTSmoveDistance)

        ## PUT SERPENTINE ALGORITHM HERE!!!! UPDATE VALUES IN GRID OF ALL TREES VISITED!!!!

        print("Count: ", count)

        print(self.posx + move[0]*MCTSmoveDistance, self.posy+move[1]*MCTSmoveDistance)
        
    @staticmethod
    def addChildren(node):
        # right, right up, right down, down, up, left, left up, left down
        #moves = [[1,0], [1,-1], [1,1], [0, 1], [0,-1], [-1,0], [-1,-1], [-1,1]]
        moves = [[1,0],[-1,0],[0,1],[0,-1]]
        for move in moves:
            possible, newState, sValue = node.state.move(move)

            if not possible:
                continue

            child = MCTSNode.MCTSNode(newState, node)
            child.sValue = sValue

            node.children.append(child)

        # handle case that there are no possible moves left

    def runMCTS(self, current):
        value = 0
        if len(current.children) == 0:
            if current.number_of_visits == 0:

                value = current.state.calculateRollout()
                current.cValue = value
                value += current.sValue

            else:
                
                UAV.addChildren(current)

                # currentPosx = current.state.start[0] + MCTSmoveDistance*current.state.statePos[0]
                # currentPosy = current.state.start[1] + MCTSmoveDistance*current.state.statePos[1]
                # print(currentPosx, currentPosy, current.children)

                value = self.runMCTS(current.children[0]) #change to select the child that moves away from start location
                current.cValue += value
        else:
            maxUCB1 = 0
            maxNode = None
            for child in current.children:
                if child.getUCB1() > maxUCB1:
                    maxUCB1 = child.getUCB1()
                    maxNode = child

            value = self.runMCTS(maxNode)
            current.cValue += value

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