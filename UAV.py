from vars import *

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

async def treesInMask(x,y,searchRadius):
    maskList = []
    cx = round(x)
    cy = round(y)
    for sx in range(max(0,cx-searchRadius),min(gridx,cx+searchRadius+1)):
        for sy in range(max(0,cy-searchRadius), min(gridy,cy+searchRadius+1)):
            #print(sx,sy)
            #print((cx-sx)**2 + (cy-sy)**2, searchRadius**2)
            if ((cx-sx)**2 + (cy-sy)**2 < searchRadius**2) and grid[sy-1][sx-1].status:
                maskList.append(grid[sy-1][sx-1])
                grid[sy-1][sx-1].black()
    #print(maskList)

class UAV:
    radius = 0.5
    vel = 0
    
    def __init__(self, posx, posy):
        global c
        c = canvas[0]
        self.posx = posx
        self.posy = posy

        self.circle = c.create_oval(centerToCircle(posx,posy,self.radius),
                       fill="blue" )
        
        self.q = sorted(trees, key=lambda cell:getDist(cell.posx, cell.posy, self.posx, self.posy))
    
    def update(self):
        c.coords(self.circle, centerToCircle(self.posx,self.posy,self.radius))
        
    
    async def mainLoop(self):
        await treesInMask(self.posx, self.posy, 10)
        for cell in self.q:
            if cell.status:
                cell.status = 0
                await self.goTo(cell.posx,cell.posy)
                cell.update()
        await self.goTo(math.ceil(gridx/2), math.ceil(gridy/2))

    async def goTo(self, x, y):
        while self.posx != x or self.posy != y:
            await asyncio.sleep(ti)
            
            dist = getDist(x,y,self.posx,self.posy)
            distTraveled = self.vel*ti
            sideRatio = (dist-distTraveled)/dist

            if dist <= distTraveled:
                self.posx = x
                self.posy = y
            else:
                self.posx = x-(x-self.posx)*sideRatio
                self.posy = y-(y-self.posy)*sideRatio

            self.update()