import asyncio

cw = 10

def smrLoop(loop, smr1, smr2):
    asyncio.set_event_loop(loop)

    loop.create_task(smr1.mainLoop())
    loop.create_task(smr2.mainLoop())

    loop.run_forever()

class SMR:
    radius = 1
    
    def __init__(self, posx, posy, cw, c):
        self.posx = posx
        self.posy = posy
        self.c = c
        self.cw =cw

        self.circle = c.create_oval(posx-cw*self.radius, posy-cw*self.radius,
                      posx+cw*self.radius, posy+cw*self.radius,
                       fill="blue" )
    
    def update(self):
        # self.c.delete(self.circle)
        self.circle = self.c.create_oval(self.posx-self.cw*self.radius, self.posy-self.cw*self.radius,
                      self.posx+self.cw*self.radius, self.posy+self.cw*self.radius,
                       fill="blue" )
    
    async def mainLoop(self):
        while True:
            self.posx += self.cw
            self.update()
            await asyncio.sleep(1)
            