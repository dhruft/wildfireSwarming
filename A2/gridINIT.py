from vars import *
import Cell

import signal

# # Extract the values of HT_ft and DBH_inch columns
# ht_values = data["HT_ft"]
# dbh_values = data["DBH_inch"]
# easting = data["Easting"]
# northing = data["Northing"]

startGridx = gridx + 8
startGridy = gridy + 8

def gridInit():
    global gridx, gridy, grid

    # Load the CSV file into a DataFrame
    # Get the path of the directory containing the Python file
    script_dir = os.path.dirname(__file__)

    # # Construct the relative path to the CSV file
    csv_file = os.path.join(script_dir, "..", "PFDP_Metric_Dataset_2016_Dhruva.csv")

    data = pd.read_csv(csv_file, encoding="iso-8859-1")


    try:
        for posy in range(1, startGridy+1):
            print(posy)
            for posx in range(1, startGridx+1):
                isCR = startCenter[0]-crRadius <= posx and posx <= startCenter[0]+crRadius and startCenter[1]-crRadius <= posy and posy <= startCenter[1]+crRadius

                newCell = Cell.Cell(posx, posy, isCR)
                startGrid[posy-1][posx-1] = newCell


        for index, row in data.iterrows():
        
            height = row["Height_m"]
            dbh = row["DBH_cm"]
            posx = int(row["Grid_X"]*10) + 1
            posy = int(row["Grid_Y"]*10) + 1

            cell = startGrid[posy-1][posx-1]
            if (cell.isCR):
                continue        
            cell.initTree(height, dbh)

            trees.append(cell)
        
        assignDensities()
    finally:
        signal.alarm(0)  # Cancel the alarm after the code completes or on an exception


    # for posy in range(1, startGridy+1):
    #     for posx in range(1, startGridx+1):
    #         isCR = startCenter[0]-crRadius <= posx and posx <= startCenter[0]+crRadius and startCenter[1]-crRadius <= posy and posy <= startCenter[1]+crRadius

    #         newCell = Cell.Cell(posx, posy, isCR)
    #         startGrid[posy-1][posx-1] = newCell

    # for index, row in data.iterrows():
        
    #     height = row["Height_m"]
    #     dbh = row["DBH_cm"]
    #     posx = int(row["Grid_X"]*10) + 1
    #     posy = int(row["Grid_Y"]*10) + 1

    #     cell = startGrid[posy-1][posx-1]
    #     if (cell.isCR):
    #         continue        
    #     cell.initTree(height, dbh)

    #     trees.append(cell)
    
    # assignDensities()

    for posy in range(5, startGridy-3):
        for posx in range(5, startGridx-3):
            cell = startGrid[posy-1][posx-1]
            cell.posy -= 4
            cell.posx -= 4
            grid[posy-5][posx-5] = cell

    # grid = grid[2:-2, 2:-2]
    # print(grid.shape)

    newTrees = []
    for posy in range(1, gridy+1):
        print(posy)
        for posx in range(1, gridx+1):
            cell = grid[posy-1][posx-1]
            # cell.posx = posx
            # cell.posy = posy
            
            if (cell.isTree):
                cell.draw()
                newTrees.append(cell)
    
    initTree = newTrees[0]
    initTree.visit()

    selected_X.append(initTree.height)
    selected_Y.append(initTree.density)
    selected_z.append(initTree.DBH)

    heights = []
    densities = []
    dbhs = []
    for tree in newTrees:
        heights.append(tree.height)
        densities.append(tree.density)
        dbhs.append(tree.DBH)

    # Create a 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Scatter plot with x, y, and z coordinates
    ax.scatter(heights, densities, dbhs, c='r', marker='o')

    # Set labels for the axes
    ax.set_xlabel('Height')
    ax.set_ylabel('Density')
    ax.set_zlabel('DBH')

    # Show the plot
    plt.show()

class Filler:
    def __init__(self):
        self.isTree = 0

def assignDensities():
    kernel = np.array([
                        [1, 1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 2, 2, 2, 2, 2, 2, 2, 1],
                        [1, 2, 3, 3, 3, 3, 3, 2, 1],
                        [1, 2, 3, 4, 4, 4, 3, 2, 1],
                        [1, 2, 3, 4, 0, 4, 3, 2, 1],
                        [1, 2, 3, 4, 4, 4, 3, 2, 1],
                        [1, 2, 3, 3, 3, 3, 3, 2, 1],
                        [1, 2, 2, 2, 2, 2, 2, 2, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1]
                    ])

    # Pad the grid with zeros to handle boundary cases
    filler = Filler()
    padded_grid = np.pad(startGrid, ((4, 4), (4, 4)), mode='constant', constant_values=filler)

    for tree in trees:
        if tree.posx <=4 or tree.posy <= 4:
            continue

        treeGrid = padded_grid[tree.posy-3: tree.posy + 6, tree.posx-3 : tree.posx+6]
        print(tree.posx, tree.posy)
        
        #print(np.array([[cell.isTree for cell in row] for row in treeGrid]))
        #density = normalize(np.sum(kernel * np.array([[cell.isTree for cell in row] for row in treeGrid])), [0,16], False)
        density = np.sum(kernel * np.array([[cell.isTree for cell in row] for row in treeGrid]))
        #print(density)
        tree.setDensity(density)