
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
        
        for tree in trees:
            std = getSTD(machineMain, tree)
            tree.colorScale(std, 0, 25)

        
        # await self.goTo(*center)
        # await asyncio.sleep(redeploymentTime)

        if deployments > 0:
            await self.mainLoop()

        return
    
    async def chooseMove(self):
        start_time = time.time()
        count = 0

        startNode = MCTSNode.MCTSNode(State.State.initState([self.posx, self.posy], self.fuel, machineMain))
        
        #use this instead of node.children in case child gets removed from tree
        children = UAV.addChildren(startNode)

        while time.time() - start_time < 5:
            if (self.runMCTS(startNode) == -2):
                break
            count += 1

        maxScore = 0
        maxNode = None
        for child in children:
            score = child.sValue*0.25 + 0.75*child.cValue/child.number_of_visits

            temp = child
            while temp != None and len(temp.children) > 0:
                mScore = -1
                mNode = None
                for c in temp.children:
                    if c.number_of_visits == 0:
                        s = c.sValue
                    else:
                        s = c.sValue*0.25+ 0.75*c.cValue/c.number_of_visits
                    if s > mScore:
                        mScore = s
                        mNode = c
                temp = mNode
                if temp == None:
                    break
                print(temp.state.statePos, len(temp.children), temp.sValue, temp.cValue)

            print(child.state.statePos, child.sValue, child.cValue, child.number_of_visits, child.getUCB1())
            if score > maxScore:
                maxScore = score
                maxNode = child

        try:
            move = maxNode.state.statePos
        except:
            self.fuel = 0
            return
        print(maxNode.sValue)
        
        #newPos = [move[0]*MCTSmoveDistance+self.posx, move[1]*MCTSmoveDistance+self.posy]
        ## PUT SERPENTINE ALGORITHM HERE!!!! UPDATE VALUES IN GRID OF ALL TREES VISITED!!!!
        if move == [0,1]:
            for y in range(self.posy+1, self.posy+MCTSmoveDistance+1):
                for x in range(self.posx-radius, self.posx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        self.visitTree(grid[y-1][x-1])
        elif move == [0,-1]:
            for y in range(self.posy-MCTSmoveDistance, self.posy):
                for x in range(self.posx-radius, self.posx+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        self.visitTree(grid[y-1][x-1])
        elif move == [-1,0]:
            for x in range(self.posx-MCTSmoveDistance, self.posx):
                for y in range(self.posy-radius, self.posy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        self.visitTree(grid[y-1][x-1])
        elif move == [1,0]:
            for x in range(self.posx+1, self.posx+MCTSmoveDistance+1):
                for y in range(self.posy-radius, self.posy+radius+1):
                    if isinstance(grid[y-1][x-1], Cell.Cell):
                        self.visitTree(grid[y-1][x-1])
        else:
            print(move)

        await self.goTo(self.posx + move[0]*MCTSmoveDistance, self.posy+move[1]*MCTSmoveDistance)
        print(self.fuel)
        print("MCTS Iterations Count: ", count)

    def visitTree(self, tree):
        tree.visited = True
        
        std = getSTD(machineMain, tree)
        if std > 3:
            tree.selected = True
            updateMachine(machineMain, tree)
            tree.setColor()
        print(std)
        
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

                value = self.runMCTS(current.children[0])
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
            if value < 0:
                return -1
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