from vars import *

# epsilon = 4

# def assignClusters():
#     points = np.array([[cell.posx, cell.posy] for cell in trees])

#     # Apply DBSCAN
#     dbscan = DBSCAN(eps=epsilon, min_samples=1)
#     dbscan.fit(points)

#     labels = np.array(dbscan.labels_)

#     for i in range(len(trees)):
#         if labels[i] not in clusters.keys():
#             clusterDict = {}
#             clusterDict["color"] = "#"+hex(random.randrange(0, 2**24))[2:].rjust(6,'0')
#             clusterDict["size"] = 1
#             clusters[labels[i]] = clusterDict
#         else:
#             clusters[labels[i]]["size"] += 1
#         trees[i].setCluster(labels[i])
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
    padded_grid = np.pad(grid, ((2, 2), (2, 2)), mode='constant', constant_values=filler)

    for tree in trees:
        treeGrid = padded_grid[tree.posy-1: tree.posy + 4, tree.posx-1 : tree.posx+4]
        #print(np.array([[cell.isTree for cell in row] for row in treeGrid]))
        #density = normalize(np.sum(kernel * np.array([[cell.isTree for cell in row] for row in treeGrid])), [0,16], False)
        density = np.sum(kernel * np.array([[cell.isTree for cell in row] for row in treeGrid]))
        #print(density)
        tree.setDensity(density)

    # x = [tree.posx for tree in trees]
    # y = [tree.posy for tree in trees]
    # xy = np.vstack([x,y])
    # z = gaussian_kde(xy)(xy)

    # # # Find the minimum and maximum values of z
    # z_min = np.min(z)
    # z_max = np.max(z)

    # # # Linear normalization: map z to the range [0, 1]
    # # z_normalized = (z - z_min) / (z_max - z_min)
    
    # # # dValues = []

    # # # for i in range(len(trees)):
    # # #     trees[i].density = dValues[i]
    
    # # # print(min(z), max(z))
    # # print(z)
    # print(z_min, z_max)