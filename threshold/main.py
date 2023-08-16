import FunctionalUAV
import NoPriorityUAV
import RandomWalkUAV
import Cell
from scipy.stats import entropy

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

        # angle = 0
        # while angle < 2*math.pi:
        #     uavs.append(UAV(center[0] + int(gridx/2)*math.cos(angle), center[1] + int(gridy/2)*math.sin(angle)))
        #     angle += 2*math.pi/uavCount
        for i in range(uavCount):
            #uavs.append(FunctionalUAV.UAV(*center, i))
            uavs.append(FunctionalUAV.UAV(*center, i))

        loop = asyncio.new_event_loop()
        t = Thread(target=self.uavLoop, args=(loop,uavs))
        t.setDaemon(True)
        t.start()
    
    def uavLoop(self, loop, uavs):
        asyncio.set_event_loop(loop)
        tasks = [FunctionalUAV.task_function(uav) for uav in uavs]

        # for uav in uavs:
        #     loop.create_task(uav.mainLoop())

        #loop.run_forever()
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        self.displayMetrics()
    
    def displayMetrics(self):
        # infoMagnitudeScore = np.sum(threshold)/(len(threshold[0])*len(threshold))
        # print(infoMagnitudeScore)
        # #finalThresholdValue = 0
        # #for value in 

        # # Normalize the data points to a probability distribution
        # normalized_data = threshold / np.sum(threshold)

        # # Create a uniform distribution
        # # uniform_distribution = np.ones_like(normalized_data) / np.prod(threshold.shape)

        # # # Calculate the average of the Jensen-Shannon Divergence between the data distribution and the uniform distribution
        # # jsd_score = 0.5 * (entropy(normalized_data.flatten(), 0.5 * (normalized_data.flatten() + uniform_distribution.flatten())) +
        # #                 entropy(uniform_distribution.flatten(), 0.5 * (normalized_data.flatten() + uniform_distribution.flatten())))

        # # print("Jensen-Shannon Divergence-based Evenness Score:", jsd_score)

        # # weight_info = 0.75
        # # weight_jsd = 0.25

        # # combined_score = (weight_info * infoMagnitudeScore) + (weight_jsd * (1 - jsd_score))
        # # Create a uniform distribution
        # uniform_distribution = np.ones_like(normalized_data) / np.prod(threshold.shape)

        # # Calculate the KL Divergence (relative entropy) between data distribution and uniform distribution
        # kl_divergence = entropy(normalized_data.flatten(), uniform_distribution.flatten())

        # # Calculate a score that combines KL Divergence and values in each position
        # evenness_score = 1 / (1 + kl_divergence)  # Invert KL Divergence to align with a higher score indicating more evenness
        # values_score = np.mean(threshold)  # Mean value of the data

        # # Define weights for evenness and values scores
        # evenness_weight = 0.6
        # values_weight = 0.4

        # # Calculate the combined score
        # combined_kl_score = (evenness_weight * evenness_score) + (values_weight * values_score)
        # print("Combined Score:", combined_kl_score)

        # weight_info = 0.25
        # weight_kl = 0.75
        # combined_score = (weight_info * infoMagnitudeScore) + (weight_kl * combined_kl_score)

        # print(f"{deployments}/{uavCount}: {combined_score}")

        collectedTrees = []
        for row in threshold:
            for tree in row:
                if tree >= certaintyRange[0]:
                    collectedTrees.append(tree)
        collectedTrees.sort()
        median = collectedTrees[len(collectedTrees)//2]

        totalDeviation = 0
        for row in threshold:
            for tree in row:
                totalDeviation += (tree-median)**2
        totalDeviation = math.sqrt(totalDeviation)
        print(totalDeviation)

        displayPlot()

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