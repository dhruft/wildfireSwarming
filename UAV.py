from vars import *

def uavLoop(loop, uavs):
    asyncio.set_event_loop(loop)

    for uav in uavs:
        loop.create_task(uav.mainLoop())

    loop.run_forever()

def centerToCircle(x,y,radius):
    return (x*cw-cw/2-cw*radius, y*cw-cw/2-cw*radius,
                      x*cw-cw/2+cw*radius, y*cw-cw/2+cw*radius)

def chooseTarget():
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

            grid[gridYpos-1][gridXpos-1].setColor(color)

class UAV:
    
    def __init__(self, posx, posy):
        global c
        c = canvas[0]
        self.posx = posx
        self.posy = posy

        self.circle = c.create_oval(centerToCircle(posx,posy,uavRadius),
                       fill="blue" )
        
        self.fuel = startFuel
    
    def update(self):
        c.coords(self.circle, centerToCircle(self.posx,self.posy,uavRadius))
    
    async def mainLoop(self):
        target = chooseTarget()

        await self.goTo(*target)

        if self.cell.isTree:
            self.fuel -= collectionFuelLoss
            self.cell.visit()

        await asyncio.sleep(collectionTime)

        # field = self.fieldOverlay()
        # previewField(field, self.posx, self.posy)

        while self.fuel > 0:
            field = self.fieldOverlay()
            #previewField(field, self.posx, self.posy)
            # Step 3: Find the index of the minimum value in the flattened array
            maxInd = np.argmax(field)

            # Step 4: Convert the index to a 2D coordinate
            maxPos = np.unravel_index(maxInd, field.shape)

            if field[maxPos] <= 0:
                await self.goTo(*center)
                break
            else:
                left = self.posx - tRange
                top = self.posy - tRange

                target = [left+maxPos[1], top+maxPos[0]]
                await self.goTo(*target)
                if self.cell.isTree:
                    self.cell.visit()
                else:
                    print("FAILURE!!!!")
                    print(field, target)
                self.fuel -= collectionFuelLoss
                await asyncio.sleep(collectionTime)
        
        await self.goTo(*center)
        
        field = self.fieldOverlay()
        #previewField(field, self.posx, self.posy)
        updatePlot()

        #DURING LOOP, if height is already known, update thresholds immediatley otherwise wait until you get there


    def fieldOverlay(self):
        #previewField(proximityField, self.posx, self.posy)

        infoField = np.zeros(shape=[tRange*2+1, tRange*2+1])
        left = self.posx - tRange
        top = self.posy - tRange
        for y in range(2*tRange+1):
            for x in range(2*tRange+1):
                gridYpos = top+y
                gridXpos = left+x

                if gridYpos < 1 or gridYpos > gridy or gridXpos < 1 or gridXpos > gridx or (gridYpos == self.posy+1 and gridXpos == self.posx+1):
                    infoField[y][x] = -1
                    continue

                cell = grid[gridYpos - 1][gridXpos - 1]
                if self.fuel - collectionFuelLoss < getDist(*center, gridXpos, gridYpos)+getDist(self.posx, self.posy, gridXpos, gridYpos) or not cell.isTree or [gridXpos, gridYpos] == [self.posx, self.posy]:
                    infoField[y][x] = -1
                    continue

                if cell.heightKnown:
                    value = 1 - threshold[cell.height-heightRange[0]][cell.density]
                else:
                    value = 1 - densityThreshold[cell.density]

                infoField[y][x] = value

                #problem: sometimes it keeps going back to the same cell because height known vs not known weights are
                # not comparing well (height known keeps being more attractive especially near the end)

        #homeField = np.zeros(shape=[tRange*2+1, tRange*2+1])
        # left = self.posx - tRange
        # top = self.posy - tRange
        # fuelImportance = 2*getDist(*center, self.posx, self.posy)/self.fuel
        # #print(fuelImportance)
        # for y in range(2*tRange+1):
        #     for x in range(2*tRange+1):
        #         gridYpos = top+y
        #         gridXpos = left+x

        #         if gridYpos < 1 or gridYpos > gridy or gridXpos < 1 or gridXpos > gridx or (gridYpos == self.posy+1 and gridXpos == self.posx+1):
        #             continue

        #         cell = grid[gridYpos - 1][gridXpos - 1]
                
        #         if self.fuel < getDist(*center, gridXpos, gridYpos)+getDist(self.posx, self.posy, gridXpos, gridYpos) or not cell.isTree:
        #             homeField[y][x] = -10000
        #             continue

        #         value = fuelImportance*normalize(getDist(*center, gridXpos, gridYpos), [0,maxCenterDist], True)
        #         homeField[y][x] = value
        
        #previewField(infoField, self.posx, self.posy)

        infoWeight = 0.65
        proximityWeight = 0.35

        return infoWeight*infoField + proximityWeight*proximityField
        
        # overlay three fields each target and run gradient descent, build new field
        # for cell in circle, get cell value for each field and build new field
    
        # threshold field, distance to uav field, distance to center


        # maskList = []
        # cx = round(self.posx)
        # cy = round(self.posy)
        # for sx in range(max(0,cx-searchRadius),min(gridx,cx+searchRadius+1)):
        #     for sy in range(max(0,cy-searchRadius), min(gridy,cy+searchRadius+1)):
        #         cell = grid[sy-1][sx-1]

        #         if ((cx-sx)**2 + (cy-sy)**2 < searchRadius**2) and cell.status:
        #             maskList.append(cell)


        # maskList = sorted(maskList, key=lambda tree: self.scoreTree(tree), reverse=True)

        # ## SORT BASED ON TREE SCORES
        # return maskList

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

            self.update()
            c.create_line(*posWithCW(oldPos), *posWithCW([self.posx, self.posy]), fill="white", width=2)

    def sendInfo(self):
        return {"target":self.target, "fuel":self.fuel, "maskList":self.getMaskList(10)}
    
def posWithCW(pos):
    x = pos[0]*cw - cw/2
    y = pos[1]*cw - cw/2
    return [x,y]