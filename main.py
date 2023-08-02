import UAV
from UAV import *
import Cell

from vars import *
from DensityCalc import assignDensities
# make global variables
# move start loop and increment loop into Cell.py
# add an array of UAVs and fix variables and scopes and stuff

class App(object):

    def __init__(self, master, **kwargs):
        self.master = master
        
        master.title("Forest Swarming Simulation")

        canvas[0] = tk.Canvas(self.master, width=gridx*cw, height=gridy*cw, bg="light gray")

        canvas[0].pack(fill="both", expand=1)
        self.master.after(0,self.mainloop)
    
    def mainloop(self):
        self.gridInit()

        uavs = []
        # angle = 0
        # while angle < 2*math.pi:
        #     uavs.append(UAV(center[0] + int(gridx/2)*math.cos(angle), center[1] + int(gridy/2)*math.sin(angle)))
        #     angle += 2*math.pi/uavCount
        for i in range(uavCount):
            uavs.append(UAV(*center))

        loop = asyncio.new_event_loop()
        t = Thread(target=uavLoop, args=(loop,uavs))
        t.setDaemon(True)
        t.start()
    
    def gridInit(self):
        for posy in range(1, gridy+1):
            for posx in range(1, gridx+1):
                isCR = center[0]-crRadius <= posx and posx <= center[0]+crRadius and center[1]-crRadius <= posy and posy <= center[1]+crRadius

                isTree = random.random()
                isTree = 1 if isTree < treeProb and not isCR else 0

                newCell = Cell.Cell(posx, posy, isTree, isCR)
                grid[posy-1][posx-1] = newCell

                if isTree:
                    trees.append(newCell)
        assignDensities()        

root = tk.Tk()
app = App(root)
root.mainloop()