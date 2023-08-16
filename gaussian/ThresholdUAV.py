
from vars import *

async def task_function(uav):
    await uav.mainLoop()

def centerToCircle(x,y,radius):
    return (x*cw-cw/2-cw*radius, y*cw-cw/2-cw*radius,
                      x*cw-cw/2+cw*radius, y*cw-cw/2+cw*radius)

def chooseTarget():
    x = random.randint(*random.choice([ [1,math.floor(center[0]-homeRadius)],[math.ceil(center[0]+homeRadius), gridx] ]))
    y = random.randint(*random.choice([ [1,math.floor(center[1]-homeRadius)],[math.ceil(center[1]+homeRadius), gridy] ]))

    # angleRange = [-math.pi/4, math.pi/4]
    # angle = random.uniform(*angleRange)

    # xDist = random.randint(homeRadius, gridx//2)

    # x = xDist + center[0]
    # y = int(math.tan(angle)*xDist+center[1])
    return [x,y]

def previewField(field, x, y):
    top = y-tRange
    left = x-tRange

    cmap = cm.Blues
    norm = matplotlib.colors.Normalize(vmin=0, vmax=1)

    for row in range(len(field)):
        for pos in range(len(field[0])):
            gridYpos = top + row
            gridXpos = left + pos

            if gridYpos < 1 or gridYpos > gridy or gridXpos < 1 or gridXpos > gridx:
                continue

            rgb = cmap(norm(abs(max(0,field[row][pos]))))[:3]  # will return rgba, we take only first 3 so we get rgb
            color = matplotlib.colors.rgb2hex(rgb)

            grid[gridYpos-1][gridXpos-1].setColor(color)

def setTarget(target, id):
    grid[target[1]-1][target[0]-1].targeted = id

def removeTarget(target, id):
    grid[target[1]-1][target[0]-1].targeted = -1

class UAV:
    
    def __init__(self, posx, posy, id):
        global c
        c = canvas[0]
        self.posx = posx
        self.posy = posy
        self.id = id
        
        self.fuel = startFuel
        self.reroute = False

        color = "green"

        self.circle = c.create_oval(centerToCircle(posx,posy,uavRadius),
                       fill=color )
    
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

        # if self.cell.isTree:
        #     self.fuel -= collectionFuelLoss
        #     self.cell.visit(self.certainty)

        # await asyncio.sleep(collectionTime)

        field = self.fieldOverlay([self.posx, self.posy])
        #previewField(field, self.posx, self.posy)

        while self.fuel > 0:
            fieldCenter = [round(self.posx), round(self.posy)]
            field = self.fieldOverlay(fieldCenter)
            #previewField(field, self.posx, self.posy)

            if np.amax(field) <= 0:
                break
            
            maskList = []
            left = fieldCenter[0] - tRange
            top = fieldCenter[1] - tRange
            for y in range(2*tRange+1):
                for x in range(2*tRange+1):
                    fieldValue = field[y][x]
                    if fieldValue <= 0:
                        continue
                    cell = grid[top+y-1][left+x-1]
                    maskList.append([fieldValue, cell])
            maskList.sort(key=lambda pos:pos[0], reverse=True)

            target = 0
            for value, cell in maskList:
                if cell.targeted == -1:
                    target = cell
                    break

            if target == 0:
                break
                #HANDLE EDGE CASE !!!!! (all trees are taken by other uavs)
                #maybe move towards center for a bit instead of current?
            targetPos = [target.posx, target.posy]

            setTarget(targetPos, self.id)

            complete = await self.goTo(*targetPos)
            
            if complete:
                self.fuel -= collectionFuelLoss

                self.cell.visitT()
                await asyncio.sleep(collectionTime)

            removeTarget(targetPos, self.id)
        
        await self.goTo(*center)
        await asyncio.sleep(redeploymentTime)

        # updatePlot()

        if deployments > 0:
            await self.mainLoop()

        return

        #DURING LOOP, if height is already known, update thresholds immediatley otherwise wait until you get there

    def fieldOverlay(self, fieldCenter):
        #previewField(proximityField, self.posx, self.posy)

        infoField = np.zeros(shape=[tRange*2+1, tRange*2+1])
        left = fieldCenter[0] - tRange
        top = fieldCenter[1] - tRange
        for y in range(2*tRange+1):
            for x in range(2*tRange+1):
                gridYpos = top+y
                gridXpos = left+x

                if gridYpos < 1 or gridYpos > gridy or gridXpos < 1 or gridXpos > gridx:
                    infoField[y][x] = -1
                    continue

                cell = grid[gridYpos - 1][gridXpos - 1]
                if self.fuel - collectionFuelLoss < getDist(*center, gridXpos, gridYpos)+getDist(self.posx, self.posy, gridXpos, gridYpos) or not cell.isTree or [gridXpos, gridYpos] == [self.posx, self.posy]:
                    infoField[y][x] = -1
                    continue

                # if cell.heightKnown:
                #     value = 1 - threshold[cell.height-heightRange[0]][cell.density]
                # else:
                #     value = 1 - densityThreshold[cell.density]
                gridVal = 1 - threshold[int(cell.height)][cell.density]
                # densityVal = 1 - densityThreshold[cell.density]
                # heightVal = 1 - heightThreshold[cell.height  - heightRange[0]]

                # value = gridVal*0.6 + densityVal*0.15 + heightVal*0.15
                value = gridVal
                
                infoField[y][x] = value

                #problem: sometimes it keeps going back to the same cell because height known vs not known weights are
                # not comparing well (height known keeps being more attractive especially near the end)

        infoWeight = 0.8
        proximityWeight = 1 - infoWeight

        return infoWeight*infoField + proximityWeight*proximityField

    async def goTo(self, x, y):
        self.target = [x,y]
        self.fuel -= getDist(x,y,self.posx,self.posy)
        self.cell = grid[y-1][x-1]

        while self.posx != x or self.posy != y:
            await asyncio.sleep(ti)
            if self.reroute:
                self.reroute = False
                #print("rerouted")
                return False
            
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
        return True

    def sendInfo(self):
        return {"target":self.target, "fuel":self.fuel, "maskList":self.getMaskList(10)}
    
def posWithCW(pos):
    x = pos[0]*cw - cw/2
    y = pos[1]*cw - cw/2
    return [x,y]