from vars import *
import Cell

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

    for index, row in data.iterrows():
    
        height = row["Height_m"]
        dbh = row["DBH_cm"]
        posx = int(row["Grid_X"]*10) + 1
        posy = int(row["Grid_Y"]*10) + 1

        tree = Cell.Cell(posx, posy, height, dbh)
        startGrid[posy-1][posx-1] = tree

        trees.append(tree)
    
    assignDensities()

    newTrees = []
    for tree in trees:
        
        if tree.posx >= 5 and tree.posx <= startGridx-4 and tree.posy >= 5 and tree.posy <= startGridx-4:
        
            tree.posx -= 4
            tree.posy -= 4
            grid[tree.posy-1][tree.posx-1] = tree

            tree.draw()
            newTrees.append(tree)
    
    initTree = newTrees[0]
    initTree.visit()

    updateMachine(machineMain, initTree)

    # selected_X.append(initTree.height)
    # selected_Y.append(initTree.density)
    # selected_z.append(initTree.dbh)

    # heights = []
    # densities = []
    # dbhs = []
    # for tree in newTrees:
    #     heights.append(tree.height)
    #     densities.append(tree.density)
    #     dbhs.append(tree.dbh)

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
        if tree.posx <=3 or tree.posy <= 3:
            continue

        treeGrid = padded_grid[tree.posy-3: tree.posy + 6, tree.posx-3 : tree.posx+6]
        
        #print(np.array([[cell.isTree for cell in row] for row in treeGrid]))
        #density = normalize(np.sum(kernel * np.array([[cell.isTree for cell in row] for row in treeGrid])), [0,16], False)
        density = np.sum(kernel * np.array([[isinstance(cell, Cell.Cell) for cell in row] for row in treeGrid]))
        #print(density)
        tree.setDensity(density)