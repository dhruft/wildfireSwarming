from vars import *

epsilon = 4

def assignClusters():
    points = np.array([[cell.posx, cell.posy] for cell in trees])

    # Apply DBSCAN
    dbscan = DBSCAN(eps=epsilon, min_samples=1)
    dbscan.fit(points)

    labels = np.array(dbscan.labels_)

    for i in range(len(trees)):
        if labels[i] not in colors.keys():
            colors[labels[i]] = "#"+hex(random.randrange(0, 2**24))[2:].rjust(6,'0')
        trees[i].setCluster(labels[i])