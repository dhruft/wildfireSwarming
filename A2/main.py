import BFSUAV
import Cell
from scipy.stats import entropy
from gridINIT import gridInit

from vars import *

modules = [BFSUAV]
module = 0


class App(object):

    def __init__(self, master, **kwargs):
        self.master = master
        
        master.title("Forest Swarming Simulation")

        canvas[0] = tk.Canvas(self.master, width=gridx*cw, height=gridy*cw, bg="light goldenrod")

        canvas[0].pack(fill="both", expand=1)
        self.master.after(0,self.mainloop)

    def mainloop(self):
        gridInit()

        uav = modules[module].UAV(*center)
        print(center)

        loop = asyncio.new_event_loop()
        t = Thread(target=self.uavLoop, args=(loop,uav))
        t.setDaemon(True)
        t.start()
    
    def uavLoop(self, loop, uav):
        asyncio.set_event_loop(loop)
        tasks = [modules[module].task_function(uav)]
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        self.displayMetrics()

    def displayMetrics(self):
        # n, p = 2, 1
        # nproj = 50
        # fixed = True

        # # some arbitrary default parameters and no hyperpriors
        # sigma_o, sigma_o_prior = 5., NoPrior()
        # l, l_prior = [4.] * n, [NoPrior()] * n
        # sigma_n, sigma_n_prior = 1, NoPrior()

        # # construct machine and feature mapping
        # ssf=SparseSpectrumFeatures(n, nproj=nproj, sigma_o=sigma_o, 
        #                                 sigma_o_prior=sigma_o_prior, l=l, 
        #                                 l_prior=l_prior, fixed=fixed)
        # machine=LinearGPR(n, p, ssf, sigma_n=sigma_n, sigma_n_prior=sigma_n_prior)

        n, p = 2, 1
        nproj = 50
        fixed = True

        # some arbitrary default parameters and no hyperpriors
        sigma_o, sigma_o_prior = 5., NoPrior()
        l, l_prior = [15.] * n, [NoPrior()] * n
        sigma_n, sigma_n_prior = 0.25, NoPrior()

        # construct machine and feature mapping
        ssf=SparseSpectrumFeatures(n, nproj=nproj, sigma_o=sigma_o, 
                                        sigma_o_prior=sigma_o_prior, l=l, 
                                        l_prior=l_prior, fixed=fixed)
        machine=LinearGPR(n, p, ssf, sigma_n=sigma_n, sigma_n_prior=sigma_n_prior)

        for index in range(len(selectedX)):
            input = np.array([selectedX[index], selectedY[index]])
            z = np.array([selectedZ[index]])
            machine.update(input, z)

        for i in range(len(selectedX)):
            print(f"{selectedX[i]} {selectedY[i]} {selectedZ[i]}")

        input = np.column_stack((np.array(selectedX), np.array(selectedY)))

        # Create a test set to evaluate the model's predictions
        x = np.linspace(0, maxHeight, 1000)
        y = np.linspace(0,maxDensity,1000)
        x_grid, y_grid = np.meshgrid(x, y)
        X_test = np.column_stack((x_grid.ravel(), y_grid.ravel()))

        z_pred, z_std = machine.predict(X_test)

        # Create a 3D scatter plot for actual data
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        #ax.scatter(x, y, z_actual, c='blue', marker='o', label='Actual Data')

        # Scatter plot of selected points
        ax.scatter(selectedX, selectedY, selectedZ, c='y', s=100, edgecolor='black', label='Selected Data')

        xs = []
        ys = []
        zs = []

        for tree in trees:
            xs.append(tree.height)
            ys.append(tree.density)
            zs.append(tree.dbh)

        #ax.scatter(xs, ys, zs, c='g', marker='x', label='All Data')

        # Plot the GP predictions and uncertainty
        z_pred = z_pred.reshape(x_grid.shape)
        z_std = z_std.reshape(y_grid.shape)*3
        ax.plot_surface(x_grid, y_grid, z_pred, color ='r', alpha=0.5, label='GPR Predictions')
        #ax.plot_surface(x_grid, y_grid, z_pred + z_std, color='g', alpha=0.3, label='Upper Confidence Limit')
        #ax.plot_surface(x_grid, y_grid, z_pred - z_std, color='b', alpha=0.3, label='Lower Confidence Limit')

        # Create legend with rectangles
        legend_elements = [
            Patch(facecolor='r', edgecolor='none', alpha=0.5, label='GPR Predictions'),
            #Patch(facecolor='g', edgecolor='none', alpha=0.3, label='Upper Confidence Limit'),
            #Patch(facecolor='b', edgecolor='none', alpha=0.3, label='Lower Confidence Limit')
        ]

        # Add legend
        ax.legend(handles=legend_elements)

        # Customize labels and legend
        ax.set_xlabel('Height (meters)')
        ax.set_ylabel('Area Density')
        ax.set_zlabel('DBH (cm)')
        #ax.legend()

        #plt.legend()
        plt.title('Gaussian Process Regression fit on Collected Data')
        plt.show()

        # mse = 0
        # for tree in trees:
        #     pred, std = machine.predict(np.array([tree.height, tree.density]))
        #     mse += (tree.dbh - pred[0])**2
        
        # mse = math.sqrt(mse/len(trees))
        # print(mse)
        # root.quit()

        # data = [startFuel, mse]
        # csv_file = '1-1-BFS.csv'
        # with open(csv_file, 'a', newline='') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(data)
        
        #displayPlot()

class Filler:
    def __init__(self):
        self.hasData = 0
    

root = tk.Tk()
app = App(root)
root.mainloop()