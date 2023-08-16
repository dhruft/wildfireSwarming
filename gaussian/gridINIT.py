from vars import *
import Cell

# # Extract the values of HT_ft and DBH_inch columns
# ht_values = data["HT_ft"]
# dbh_values = data["DBH_inch"]
# easting = data["Easting"]
# northing = data["Northing"]

#4838,PIPO,1.4,2.5,9.3,verify ref tree,,0,0,NA,NA
#58,PIPO,5.9,,,,Measurement Issue,4330890,490052,NA,NA
#DELETD CUZ IDK WHAT IT IS

#bottom left https://www.google.com/maps/place/39%C2%B007'28.2%22N+105%C2%B006'56.7%22W/@39.1245796,-105.1156969,54m/data=!3m1!1e3!4m4!3m3!8m2!3d39.124509!4d-105.115757?hl=en&entry=ttu
#320 by 320

def gridInit():
    global gridx, gridy, grid

    startGridx = gridx + 4
    startGridy = gridy + 4

    # Load the CSV file into a DataFrame
    # Get the path of the directory containing the Python file
    script_dir = os.path.dirname(__file__)

    # # Construct the relative path to the CSV file
    csv_file = os.path.join(script_dir, "..", "N1_trees_2018_for_Arun.csv")

    data = pd.read_csv(csv_file, encoding="iso-8859-1")

    for posy in range(1, startGridy+1):
        for posx in range(1, startGridx+1):
            isCR = startCenter[0]-crRadius <= posx and posx <= startCenter[0]+crRadius and startCenter[1]-crRadius <= posy and posy <= startCenter[1]+crRadius

            newCell = Cell.Cell(posx, posy, isCR)
            startGrid[posy-1][posx-1] = newCell

    for index, row in data.iterrows():
        
        height = row["HT_ft"]
        dbh = row["DBH_inch"]
        easting = row["Easting"]
        northing = row["Northing"]

        posx = easting - 489994 + 1
        posy = startGridy - (northing - 4330600)//10

        cell = startGrid[posy-1][posx-1]
        if (cell.isCR):
            continue        
        cell.initTree(height, dbh)

        trees.append(cell)
    
    assignDensities()

    for posy in range(3, startGridy-1):
        for posx in range(3, startGridx-1):
            cell = startGrid[posy-1][posx-1]
            cell.posy -= 2
            cell.posx -= 2
            grid[posy-3][posx-3] = cell

    # grid = grid[2:-2, 2:-2]
    # print(grid.shape)

    newTrees = []
    for posy in range(1, gridy+1):
        for posx in range(1, gridx+1):
            cell = grid[posy-1][posx-1]
            # cell.posx = posx
            # cell.posy = posy
            cell.draw()
            if (cell.isTree):
                newTrees.append(cell)
    
    initTree = newTrees[0]
    initTree.visit()

    selected_X.append(initTree.height)
    selected_Y.append(initTree.density)
    selected_z.append(initTree.DBH)

    # heights = []
    # densities = []
    # dbhs = []
    # for tree in newTrees:
    #     heights.append(tree.height)
    #     densities.append(tree.density)
    #     dbhs.append(tree.DBH)

    # # Create a 3D scatter plot
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    # # Scatter plot with x, y, and z coordinates
    # ax.scatter(heights, densities, dbhs, c='r', marker='o')

    # # Set labels for the axes
    # ax.set_xlabel('Height')
    # ax.set_ylabel('Density')
    # ax.set_zlabel('DBH')

    # # Show the plot
    # plt.show()

class Filler:
    def __init__(self):
        self.isTree = 0

def assignDensities():
    kernel = np.array([[1, 1, 1, 1, 1],
                        [1, 2, 2, 2, 1],
                        [1, 2, 0, 2, 1],
                        [1, 2, 2, 2, 1],
                        [1, 1, 1, 1, 1]])

    # Pad the grid with zeros to handle boundary cases
    filler = Filler()
    padded_grid = np.pad(startGrid, ((2, 2), (2, 2)), mode='constant', constant_values=filler)

    for tree in trees:
        treeGrid = padded_grid[tree.posy-1: tree.posy + 4, tree.posx-1 : tree.posx+4]
        #print(np.array([[cell.isTree for cell in row] for row in treeGrid]))
        #density = normalize(np.sum(kernel * np.array([[cell.isTree for cell in row] for row in treeGrid])), [0,16], False)
        density = np.sum(kernel * np.array([[cell.isTree for cell in row] for row in treeGrid]))
        #print(density)
        tree.setDensity(density)