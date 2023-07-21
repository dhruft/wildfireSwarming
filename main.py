import UAV
from UAV import *
import Cell

from vars import *
from DBScan import assignClusters
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
        angle = 0
        while angle < 2*math.pi:
            uavs.append(UAV(math.ceil(gridx/2) + int(gridx/2)*math.cos(angle), math.ceil(gridy/2) + int(gridy/2)*math.sin(angle)))
            angle += 2*math.pi/uavCount

        loop = asyncio.new_event_loop()
        t = Thread(target=uavLoop, args=(loop,uavs))
        t.setDaemon(True)
        t.start()
    
    def gridInit(self):
        for posx in range(1, gridx+1):
            row = []
            for posy in range(1, gridy+1):
                status = random.random()
                status = 1 if status < treeProb else 0

                isCR = math.ceil(gridx/2)-crRadius <= posx and posx <= math.ceil(gridx/2)+crRadius and math.ceil(gridy/2)-crRadius <= posy and posy <= math.ceil(gridy/2)+crRadius

                newCell = Cell.Cell(posx, posy, status, isCR)
                row.append(newCell)

                if status and not isCR:
                    trees.append(newCell)

            grid.append(row)

        assignClusters()        

root = tk.Tk()
app = App(root)
root.mainloop()