import UAV
import Cell
from scipy.stats import entropy
from gridINIT import gridInit

from vars import *

class App(object):

    def __init__(self, master, **kwargs):
        self.master = master
        
        master.title("Forest Swarming Simulation")

        canvas[0] = tk.Canvas(self.master, width=gridx*cw, height=gridy*cw, bg="light goldenrod")

        canvas[0].pack(fill="both", expand=1)
        self.master.after(0,self.mainloop)

    def mainloop(self):
        gridInit()

        uav = UAV.UAV(*center)
        print(center)

        loop = asyncio.new_event_loop()
        t = Thread(target=self.uavLoop, args=(loop,uav))
        t.setDaemon(True)
        t.start()
    
    def uavLoop(self, loop, uav):
        asyncio.set_event_loop(loop)
        tasks = [UAV.task_function(uav)]
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        self.displayMetrics()

    def displayMetrics(self):
        pass

class Filler:
    def __init__(self):
        self.hasData = 0
    

root = tk.Tk()
app = App(root)
root.mainloop()