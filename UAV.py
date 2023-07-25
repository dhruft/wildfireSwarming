from vars import *

## BUG: UAVS RANDOMLYY GO ACROSS THE MAP IDK WHY WHAT IS THIS BRUH
# MULTIPLE TARGETS WHAT!??!?!??!
# SOMEHWO TRADING TARGETS???!?! 

def uavLoop(loop, uavs):
    asyncio.set_event_loop(loop)

    for uav in uavs:
        loop.create_task(uav.mainLoop())

    loop.run_forever()

def getDist(x1,y1,x2,y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def centerToCircle(x,y,radius):
    return (x*cw-cw/2-cw*radius, y*cw-cw/2-cw*radius,
                      x*cw-cw/2+cw*radius, y*cw-cw/2+cw*radius)

# if flip is True, then lower values = higher priority, meaning
# the normalize function should return larger numbers for lower values
def normalize(value, vRange, flip):
    dec = (value-vRange[0])/(vRange[1]-vRange[0])
    dec = min(1, dec)

    if flip: dec = 1.0 - dec
    return dec

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
        while self.fuel > 0:
            maskList = self.getMaskList(tRange)

            # TO BE CHANGED!!! consider edge case interactions between neighboring robots
            # e.g. one of them are both robots are fighting over one resource, one gets it
            # other moves to center
            if self.posx == center[0] and self.posy == center[1]:
                break
            elif len(maskList) == 0:
                await self.moveToCenter()
            else:
                target = maskList[0]
                target.status = 0
                clusters[target.cluster]["size"] -= 1
                await asyncio.sleep(1)
                await self.goTo(target.posx, target.posy)
                target.visit()

        await self.goTo(*center)

    def getMaskList(self,searchRadius):
        maskList = []
        cx = round(self.posx)
        cy = round(self.posy)
        for sx in range(max(0,cx-searchRadius),min(gridx,cx+searchRadius+1)):
            for sy in range(max(0,cy-searchRadius), min(gridy,cy+searchRadius+1)):
                cell = grid[sy-1][sx-1]

                if ((cx-sx)**2 + (cy-sy)**2 < searchRadius**2) and cell.status:
                    maskList.append(cell)


        maskList = sorted(maskList, key=lambda tree: self.scoreTree(tree), reverse=True)

        ## SORT BASED ON TREE SCORES
        return maskList
    
    def scoreTree(self, tree):
        # distance to center, current fuel, distance to drone, cluster size

        # distance to center: https://www.desmos.com/calculator/jgnjgjkmyd
        dc = getDist(tree.posx, tree.posy, *center)
        dCenter = getDist(*center, self.posx, self.posy)
        dcr = [dCenter - tRange, dCenter + tRange]
        dcNorm = normalize(dc,dcr,True)
        w1 = 30*(normalize(self.fuel, [0,startFuel], True)**3)
        dcValue = w1*dcNorm

        # distance to drone
        dd = getDist(tree.posx, tree.posy, self.posx, self.posy)
        ddr = [0, tRange]
        ddNorm = normalize(dd,ddr,True)
        w2 = 10
        ddValue = w2*ddNorm

        # cluster size
        cs = clusters[tree.cluster]["size"]
        csr = [0,treeProb*500]
        csNorm = normalize(cs,csr,False)
        w3 = 5
        csValue = w3*csNorm

        ## TO BE DONE!!!
        print(dcValue, ddValue, csValue)
        return dcValue + ddValue + csValue

        # dc weighted with fuel
        # dd weighted with number (should be pretty high)
        # cluster size weighted with number (kinda high)

    async def moveToCenter(self):
        distance = getDist(*center,self.posx,self.posy)
        deltaX = center[0] - self.posx
        deltaY = center[1] - self.posy

        x = self.posx + deltaX*(1/distance)
        y = self.posy + deltaY*(1/distance)

        if deltaX < 1 and deltaY < 1:
            x = center[0]
            y = center[1]

        await self.goTo(x,y)

    async def goTo(self, x, y):
        self.target = [x,y]
        self.fuel -= getDist(x,y,self.posx,self.posy)

        while self.posx != x or self.posy != y:
            await asyncio.sleep(ti)
            
            dist = getDist(x,y,self.posx,self.posy)
            distTraveled = vel*ti
            sideRatio = (dist-distTraveled)/dist

            if dist <= distTraveled:
                self.posx = x
                self.posy = y
            else:
                self.posx = x-(x-self.posx)*sideRatio
                self.posy = y-(y-self.posy)*sideRatio

            self.update()

    def sendInfo(self):
        return {"target":self.target, "fuel":self.fuel, "maskList":self.getMaskList(10)}