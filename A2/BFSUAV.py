
from vars import *
import Node
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

        target = chooseTarget()
        await self.goTo(*target)

        #await self.goTo(1000,1000)
            
        while self.fuel > getDist(self.posx, self.posy, center[0], center[1]):
            await self.chooseMove()
        
        # for tree in trees:
        #     #std = getSTD(machineMain, tree)
        #     #tree.colorScale(std, 0, 25)
        #     treeValue = 1 - heatmap[int(tree.height)][tree.density]
        #     tree.colorScale(treeValue, 0, 1)

        
        await self.goTo(*center)
        await asyncio.sleep(redeploymentTime)

        if deployments > 0:
            await self.mainLoop()

        return
    
    def treePropagate(self, node, value):
        current = node
        while current.parent != None:
            current = current.parent
            current.value += value
            current.descendants += 1

    
    async def chooseMove(self):
        for height in range(maxHeight+1):
            for density in range(maxDensity+1):
                pred, std = machineMain.predict(np.array([height, density]))
                heatmap[int(tree.height)][tree.density] = normalize(pred, [0, 50], flip=True)

        start_time = time.time()
        count = 0

        startNode = Node.Node(State.State.initState([self.posx, self.posy], self.fuel, heatmap))
        
        #use this instead of node.children in case child gets removed from tree
        children = UAV.addChildren(startNode)

        queue = []
        queue.append(children)
        while time.time() - start_time < 5:
            
            if len(queue) == 0:
                break

            current = queue[0]
            for child in current:

                value = child.value
                self.treePropagate(child, value)
                
                newChildren = UAV.addChildren(child)
                queue.append(newChildren)

            queue.pop(0)
            count += 1

        maxScore = 0
        maxNode = None
        for child in children:
            score = child.value/child.descendants

            temp = child
            while temp != None and len(temp.children) > 0:
                mScore = -1
                mNode = None
                for c in temp.children:
                    s = c.value
                    if s > mScore:
                        mScore = s
                        mNode = c
                temp = mNode
                if temp == None:
                    break
                print(temp.state.statePos, temp.value/temp.descendants)

            print(score)

            if score > maxScore:
                maxScore = score
                maxNode = child

        try:
            move = maxNode.state.statePos
        except:
            self.fuel = 0
            return
        print("maxnode/descendants: ", maxNode.value/maxNode.descendants)
        
        #newPos = [move[0]*moveDistance+self.posx, move[1]*moveDistance+self.posy]
        ## PUT SERPENTINE ALGORITHM HERE!!!! UPDATE VALUES IN GRID OF ALL TREES VISITED!!!!
        if move == [0,1]:
            for y in range(self.posy+1, self.posy+moveDistance+1):
                for x in range(self.posx-radius, self.posx+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        input = np.array([tree.height, tree.density])
                        z = np.array([tree.dbh])
                        machineMain.update(input, z)
                        tree.visit(True, heatmap)
        elif move == [0,-1]:
            for y in range(self.posy-moveDistance, self.posy):
                for x in range(self.posx-radius, self.posx+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        input = np.array([tree.height, tree.density])
                        z = np.array([tree.dbh])
                        machineMain.update(input, z)
                        tree.visit(True, heatmap)
        elif move == [-1,0]:
            for x in range(self.posx-moveDistance, self.posx):
                for y in range(self.posy-radius, self.posy+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        input = np.array([tree.height, tree.density])
                        z = np.array([tree.dbh])
                        machineMain.update(input, z)
                        tree.visit(True, heatmap)
        elif move == [1,0]:
            for x in range(self.posx+1, self.posx+moveDistance+1):
                for y in range(self.posy-radius, self.posy+radius+1):
                    tree = grid[y-1][x-1]
                    if isinstance(tree, Cell.Cell):
                        treeValue = 1 - heatmap[int(tree.height)][tree.density]
                        if tree.visited or treeValue < valueThreshold:
                            continue
                        input = np.array([tree.height, tree.density])
                        z = np.array([tree.dbh])
                        machineMain.update(input, z)
                        tree.visit(True, heatmap)
        else:
            print(move)

        await self.goTo(self.posx + move[0]*moveDistance, self.posy+move[1]*moveDistance)

        #displayPlot()

        print(self.fuel)
        print("Iterations Count: ", count)
        
    @staticmethod
    def addChildren(node):
        # right, right up, right down, down, up, left, left up, left down
        #moves = [[1,0], [1,-1], [1,1], [0, 1], [0,-1], [-1,0], [-1,-1], [-1,1]]
        moves = [[1,0],[-1,0],[0,1],[0,-1]]
        children = []
        for move in moves:
            possible, newState, value = node.state.move(move)

            if not possible:
                continue

            child = Node.Node(newState, node)
            child.value = value

            node.children.append(child)
            children.append(child)

        maxMultiplier = 1.2
        minMultiplier = 0.8
        children.sort(key=lambda child: getDist(*child.state.worldPos, *child.state.start))
        ind = 0
        for child in children:
            multiplier =  minMultiplier + ind*(maxMultiplier-minMultiplier)/len(children)
            child.value = child.value*multiplier
            ind += 1

        return children

        # handle case that there are no possible moves left??

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

        visitedPositions.append([x, y])
    
def posWithCW(pos):
    x = pos[0]*cw - cw/2
    y = pos[1]*cw - cw/2
    return [x,y]