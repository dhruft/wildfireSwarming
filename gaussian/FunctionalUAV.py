
from vars import *

async def task_function(uav):
    await uav.mainLoop()

def centerToCircle(x,y,radius):
    return (x*cw-cw/2-cw*radius, y*cw-cw/2-cw*radius,
                      x*cw-cw/2+cw*radius, y*cw-cw/2+cw*radius)

def chooseTarget():
    x = random.randint(*random.choice([ [1,math.floor(center[0]-homeRadius)],[math.ceil(center[0]+homeRadius), gridx] ]))
    y = random.randint(*random.choice([ [1,math.floor(center[1]-homeRadius)],[math.ceil(center[1]+homeRadius), gridy] ]))

    return [x,y]

def previewField(field, x, y):
    x = round(x)
    y = round(y)
    top = y-tRange
    left = x-tRange

    cmap = cm.Blues
    norm = matplotlib.colors.Normalize(vmin=np.min(field), vmax=np.max(field))

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
    
    def __init__(self, posx, posy, id):
        global c
        c = canvas[0]
        self.posx = posx
        self.posy = posy
        self.id = id
        
        self.fuel = startFuel

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

        while self.fuel > 0:
            fieldCenter = [round(self.posx), round(self.posy)]
            field = self.fieldOverlay(fieldCenter)
            #previewField(field, self.posx, self.posy)

            if np.amax(field) <= minInfo:
                break
            
            left = fieldCenter[0] - tRange
            top = fieldCenter[1] - tRange

            selectedIndex = np.unravel_index(np.argmax(field), field.shape)
            posx = left + selectedIndex[1]
            posy = top + selectedIndex[0]

            target = grid[posy-1][posx-1]
            #print(target.posx, target.posy, target.isTree)

            target.visit()
            
            targetPos = [target.posx, target.posy]

            await self.goTo(*targetPos)
            
            self.fuel -= collectionFuelLoss
            await asyncio.sleep(collectionTime)

            # Add the selected data point to the training set
            selected_X.append(self.cell.height)
            selected_Y.append(self.cell.density)
            selected_z.append(self.cell.DBH)

        
        await self.goTo(*center)
        await asyncio.sleep(redeploymentTime)

        # updatePlot()

        if deployments > 0:
            await self.mainLoop()

        return

        #DURING LOOP, if height is already known, update thresholds immediatley otherwise wait until you get there

    def fieldOverlay(self, fieldCenter):

        input = np.column_stack((np.array(selected_X), np.array(selected_Y)))
        gpr.fit(input, np.array(selected_z))

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
                if cell.visited or self.fuel - collectionFuelLoss < getDist(*center, gridXpos, gridYpos)+getDist(self.posx, self.posy, gridXpos, gridYpos) or not cell.isTree or [gridXpos, gridYpos] == [self.posx, self.posy]:
                    infoField[y][x] = -1
                    continue

                candidate_X = cell.height
                candidate_Y = cell.density

                # Calculate the model's uncertainty for each candidate point

                candidate = np.array([candidate_X, candidate_Y])

                try:
                    candidate_z, candidate_std = gpr.predict(candidate.reshape(1,-1), return_std=True)
    
                except:
                    infoField[y][x] = -1
                    continue

                infoField[y][x] = candidate_std

        infoWeight = 0.8
        proximityWeight = 1 - infoWeight

        return infoWeight*infoField + proximityWeight*proximityField

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

    def sendInfo(self):
        return {"target":self.target, "fuel":self.fuel, "maskList":self.getMaskList(10)}
    
def posWithCW(pos):
    x = pos[0]*cw - cw/2
    y = pos[1]*cw - cw/2
    return [x,y]