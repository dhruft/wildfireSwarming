import FunctionalUAV
import ThresholdUAV
import RandomUAV
import Cell
from scipy.stats import entropy
from gridINIT import gridInit
from mpl_toolkits.mplot3d import Axes3D

from vars import *
# make global variables
# move start loop and increment loop into Cell.py
# add an array of UAVs and fix variables and scopes and stuff

modules = [FunctionalUAV, ThresholdUAV, RandomUAV]
module = 0

class App(object):

    def __init__(self, master, **kwargs):
        self.master = master
        
        master.title("Forest Swarming Simulation")

        canvas[0] = tk.Canvas(self.master, width=(gridx)*cw, height=(gridy)*cw, bg="light gray")
        canvas[0].pack(fill="both", expand=1)
        self.master.after(0,self.mainloop)

    def mainloop(self):
        gridInit()
        
        for i in range(uavCount):
            uavs.append(modules[module].UAV(*center, i))

        loop = asyncio.new_event_loop()
        t = Thread(target=self.uavLoop, args=(loop,uavs))
        t.setDaemon(True)
        t.start()
    
    def uavLoop(self, loop, uavs):
        asyncio.set_event_loop(loop)
        tasks = [modules[module].task_function(uav) for uav in uavs]

        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        self.displayMetrics()

    def displayMetrics(self):
        
        #---------------------------------------------
        ## GET DBH PREDICTION FROM FINAL GAUSSIAN (DOESNT WORK)

        # gpr.fit(input, np.array(selected_z))
        # X_test = np.array([],[])

        # # Get the model's predictions and uncertainty for the test set
        # y_pred, y_std = gpr.predict(X_test.reshape(-1, 1), return_std=True)

        # # Plot the results
        # plt.figure(figsize=(10, 6))
        # #plt.plot(X_pool, true_function(X_pool), label='True Function')
        # plt.scatter(selected_X, selected_z, color='g', marker='x', label='Selected Data')
        # plt.plot(X_test, y_pred, color='b', label='GP Predictions')
        # plt.fill_between(X_test, y_pred - y_std, y_pred + y_std, alpha=0.3, color='b', label='Uncertainty')
        # plt.xlabel('Height')
        # plt.ylabel('DBH')
        # plt.legend()
        # plt.title('Active Learning with Gaussian Process Regression')
        # plt.show()

        #_-------------------------------------------------------
        ## FOR 3D PLOT OF DBH PREDICTIONS, GAUSSIAN UNCERTAINTY, AND SELECTED POINTS

        input = np.column_stack((np.array(selected_X), np.array(selected_Y)))
        gpr.fit(input, np.array(selected_z))

        # Create a test set to evaluate the model's predictions
        x = np.linspace(0, maxHeight, 1000)
        y = np.linspace(0,maxDensity,1000)
        x_grid, y_grid = np.meshgrid(x, y)
        X_test = np.column_stack((x_grid.ravel(), y_grid.ravel()))

        z_pred, z_std = gpr.predict(X_test, return_std=True)

        # Create a 3D scatter plot for actual data
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        #ax.scatter(x, y, z_actual, c='blue', marker='o', label='Actual Data')

        # Scatter plot of selected points
        ax.scatter(selected_X, selected_Y, selected_z, c='r', marker='x', label='Selected Data')


        # Plot the GP predictions and uncertainty
        z_pred = z_pred.reshape(x_grid.shape)
        z_std = z_std.reshape(y_grid.shape)*3
        ax.plot_surface(x_grid, y_grid, z_pred, cmap='coolwarm', alpha=0.5, label='GP Predictions')
        ax.plot_surface(x_grid, y_grid, z_pred + z_std, color='b', alpha=0.3)
        ax.plot_surface(x_grid, y_grid, z_pred - z_std, color='b', alpha=0.3)

        # Customize labels and legend
        ax.set_xlabel('Height')
        ax.set_ylabel('Density')
        ax.set_zlabel('DBH')
        #ax.legend()

        plt.title('Active Learning with Gaussian Process Regression in 3D')
        plt.show()

        #-------------------------------------------------------------
        ## FOR SIMULATION (mse calculations, write to file, close program)

        #A = np.array([tree.DBH for tree in trees])
        #B = np.array([gpr.predict([[tree.height, tree.density]], return_std=True)[0][0] for tree in trees])

        #B = np.array(gpr.predict([[tree.height, tree.density] for tree in trees]))

        #mse = ((A - B)**2).mean()
        #print(mse)

        # f = open("results.txt", "a")
        # f.write("\n"+str(mse))
        # f.close()

        #global root
        #root.quit()

        #-------------------------------------------------------------

root = tk.Tk()
app = App(root)
root.mainloop()