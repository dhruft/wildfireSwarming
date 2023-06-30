from focus import getFocusPoint
import SMR
from SMR import *
import CR
import Cell

import math
import tkinter as tk
import asyncio
from threading import Thread

gridx = 50
gridy = 50
cw = 10
grid = []

# make global variables
# move start loop and increment loop into Cell.py
# add an array of SMRs and fix variables and scopes and stuff


class App(object):

    def __init__(self, master, **kwargs):
        self.master = master
        
        master.title("Wildfire Swarming Simulation")
        self.c = tk.Canvas(self.master, width=gridx*cw, height=gridy*cw, bg="light gray")

        self.c.pack(fill="both", expand=1)
        self.master.after(0,self.mainloop)
    
    def mainloop(self):
        loop = asyncio.new_event_loop()

        t = Thread(target=self.startLoop, args=(loop,))
        t.setDaemon(True)
        t.start()

        self.CR = CR.CR(cw*gridx/2, cw*gridy/2,
                         cw, self.c)

        #for angle in range(0, 2*math.pi, math.pi/4):

        loop = asyncio.new_event_loop()

        smr1 = SMR(10,10,cw,self.c)
        smr2 = SMR(10,30,cw,self.c)

        t = Thread(target=smrLoop, args=(loop,smr1,smr2))
        t.setDaemon(True)
        t.start()
        
        
    def startLoop(self,loop):
        asyncio.set_event_loop(loop)

        for posx in range(0, gridx*cw, cw):
            row = []
            for posy in range(0, gridy*cw, cw):
                newCell = Cell.Cell(posx, posy, self.c, cw)
                row.append(newCell)
            grid.append(row)

        loop.create_task(self.incrementCells())

        loop.run_forever()
    
    async def incrementCells(self):
        while True:
            for row in grid:
                for cell in row:
                    cell.age += 1.5
                    cell.update()
            self.c.update()
            await asyncio.sleep(2)

                  

root = tk.Tk()
app = App(root)
root.mainloop()