#import UAV
import Cell
from scipy.stats import entropy
from gridINIT import gridInit

from vars import *

import signal

## AT SOME POINT, CHANGE CODE SO EMPTY CELLS ARE JUST 0S

def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")

# Set a signal handler for SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

# Set a timeout of 60 seconds
signal.alarm(30)

class App(object):

    def __init__(self, master, **kwargs):
        self.master = master
        
        master.title("Forest Swarming Simulation")

        canvas[0] = tk.Canvas(self.master, width=gridx*cw, height=gridy*cw, bg="light gray")

        canvas[0].pack(fill="both", expand=1)
        self.master.after(0,self.mainloop)

    def mainloop(self):
        #self.gridInit()
        gridInit()

        # uav = UAV.UAV(*center)

        # loop = asyncio.new_event_loop()
        # t = Thread(target=self.uavLoop, args=(loop,uav))
        # t.setDaemon(True)
        # t.start()
    
    # def uavLoop(self, loop, uav):
    #     asyncio.set_event_loop(loop)
    #     tasks = [UAV.task_function(uav)]
    #     loop.run_until_complete(asyncio.gather(*tasks))
    #     loop.close()

    #     self.displayMetrics()

    def displayMetrics(self):
        pass

    def gridInit(self):
        for posy in range(1, gridy+1):
            for posx in range(1, gridx+1):
                hasData = 1 if random.random() < dataProb else 0

                newCell = Cell.Cell(posx, posy, hasData)
                grid[posy-1][posx-1] = newCell

                if hasData:
                    dataCells.append(newCell)
        
        kernel = np.array([[1, 1, 1, 1, 1],
                        [1, 2, 2, 2, 1],
                        [1, 2, 0, 2, 1],
                        [1, 2, 2, 2, 1],
                        [1, 1, 1, 1, 1]])

        # Pad the grid with zeros to handle boundary cases
        filler = Filler()
        padded_grid = np.pad(grid, ((2, 2), (2, 2)), mode='constant', constant_values=filler)

        for dataCell in dataCells:
            dataCellGrid = padded_grid[dataCell.posy-1: dataCell.posy + 4, dataCell.posx-1 : dataCell.posx+4]
            density = np.sum(kernel * np.array([[cell.hasData for cell in row] for row in dataCellGrid]))
            dataCell.setDensity(density)


class Filler:
    def __init__(self):
        self.hasData = 0
    

root = tk.Tk()
app = App(root)
root.mainloop()