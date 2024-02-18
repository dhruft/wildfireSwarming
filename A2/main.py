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
        input = np.column_stack((np.array(selectedX), np.array(selectedY)))

        # Create a test set to evaluate the model's predictions
        x = np.linspace(0, maxHeight, 1000)
        y = np.linspace(0,maxDensity,1000)
        x_grid, y_grid = np.meshgrid(x, y)
        X_test = np.column_stack((x_grid.ravel(), y_grid.ravel()))

        z_pred, z_std = machineMain.predict(X_test)

        # Create a 3D scatter plot for actual data
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        #ax.scatter(x, y, z_actual, c='blue', marker='o', label='Actual Data')

        # Scatter plot of selected points
        ax.scatter(selectedX, selectedY, selectedZ, c='r', marker='x', label='Selected Data')


        # Plot the GP predictions and uncertainty
        z_pred = z_pred.reshape(x_grid.shape)
        z_std = z_std.reshape(y_grid.shape)*3
        ax.plot_surface(x_grid, y_grid, z_pred, color ='r', alpha=0.5, label='GP Predictions')
        ax.plot_surface(x_grid, y_grid, z_pred + z_std, color='b', alpha=0.3)
        ax.plot_surface(x_grid, y_grid, z_pred - z_std, color='b', alpha=0.3)

        # Customize labels and legend
        ax.set_xlabel('Height')
        ax.set_ylabel('Density')
        ax.set_zlabel('DBH')
        #ax.legend()

        plt.title('Active Learning with Gaussian Process Regression in 3D')
        plt.show()

class Filler:
    def __init__(self):
        self.hasData = 0
    

root = tk.Tk()
app = App(root)
root.mainloop()