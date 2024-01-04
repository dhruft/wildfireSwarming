from vars import *

async def task_function(uav):
    await uav.mainLoop()
    await uav.goTo(*center)

def centerToCircle(x,y,radius):
    return (x*cw-cw/2-cw*radius, y*cw-cw/2-cw*radius,
                      x*cw-cw/2+cw*radius, y*cw-cw/2+cw*radius)

def chooseTarget():
    # angleRange = [-math.pi/6, math.pi/6]
    # angle = random.uniform(*angleRange)

    # xDist = random.randint(homeRadius, gridx//2)

    # x = xDist + center[0]
    # y = int(math.tan(angle)*xDist+center[1])

    x = random.randint(*random.choice([ [1,math.floor(center[0]-homeRadius)],[math.ceil(center[0]+homeRadius), gridx] ]))
    y = random.randint(*random.choice([ [1,math.floor(center[1]-homeRadius)],[math.ceil(center[1]+homeRadius), gridy] ]))

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
            try:
                grid[gridYpos-1][gridXpos-1].setColor(color)
            except:
                continue

def setTarget(target, id):
    for y in range(target[1]-targetRadius, target[1]+targetRadius+1):
        for x in range(target[0]-targetRadius, target[0]+targetRadius+1):
            if y < 1 or y > gridy or x < 1 or x > gridx:
                continue
            cell = grid[y-1][x-1] 
            cell.targeted = id
            #cell.setColor("black")

def removeTarget(target, id):
    for y in range(target[1]-targetRadius, target[1]+targetRadius+1):
        for x in range(target[0]-targetRadius, target[0]+targetRadius+1):
            if y < 1 or y > gridy or x < 1 or x > gridx:
                continue
            cell = grid[y-1][x-1]
            if cell.targeted == id:
                cell.targeted = -1


class UAV:
    
    def __init__(self, posx, posy, id):
        global c
        c = canvas[0]
        self.posx = posx
        self.posy = posy
        self.id = id
        
        self.fuel = startFuel
        self.certainty = random.uniform(certaintyRange[0], certaintyRange[1])
        self.reroute = False

        cmap = cm.Greens
        norm = matplotlib.colors.Normalize(vmin=certaintyRange[0], vmax=certaintyRange[1])

        rgb = cmap(norm(self.certainty))[:3]  # will return rgba, we take only first 3 so we get rgb
        color = matplotlib.colors.rgb2hex(rgb)

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
                    if fieldValue <= minInfo:
                        continue
                    cell = grid[top+y-1][left+x-1]
                    maskList.append([fieldValue, cell])
            maskList.sort(key=lambda pos:pos[0], reverse=True)
            #print(maskList[0][0])

            target = 0
            for value, cell in maskList:
                if cell.targeted == -1:
                    target = cell
                    break
                conflictUAV = uavs[cell.targeted]
                if self.certainty <= conflictUAV.certainty:
                    continue
                target = cell
                conflictUAV.reroute = True

            if target == 0:
                break
                #HANDLE EDGE CASE !!!!! (all trees are taken by other uavs)
                #maybe move towards center for a bit instead of current?
            targetPos = [target.posx, target.posy]

            setTarget(targetPos, self.id)

            complete = await self.goTo(*targetPos)
            
            if complete:
                self.fuel -= collectionFuelLoss

                self.cell.visit(self.certainty)
                await asyncio.sleep(collectionTime)

            removeTarget(targetPos, self.id)

        # updatePlot()

        await self.goTo(*center)
        await asyncio.sleep(redeploymentTime)

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
                gridVal = 1 - threshold[cell.height-heightRange[0]][cell.density]
                densityVal = 1 - densityThreshold[cell.density]
                heightVal = 1 - heightThreshold[cell.height  - heightRange[0]]

                value = gridVal

                # if gridVal < 1:
                #     value = gridVal*0.6 + densityVal*0.15 + heightVal*0.15
                # else:
                #     value = densityVal*0.5 + heightVal*0.5

                infoField[y][x] = value

                #problem: sometimes it keeps going back to the same cell because height known vs not known weights are
                # not comparing well (height known keeps being more attractive especially near the end)

        infoWeightRange = [0.6, 0.8]
        absoluteCertaintyRange = [0.5, 1]
        infoWeight = (infoWeightRange[1]-infoWeightRange[0])*normalize(self.certainty, absoluteCertaintyRange) + infoWeightRange[0]

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