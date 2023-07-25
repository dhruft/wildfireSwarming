from vars import *

epsilon = 4

def assignClusters():
    points = np.array([[cell.posx, cell.posy] for cell in trees])

    # Apply DBSCAN
    dbscan = DBSCAN(eps=epsilon, min_samples=1)
    dbscan.fit(points)

    labels = np.array(dbscan.labels_)

    for i in range(len(trees)):
        if labels[i] not in clusters.keys():
            clusterDict = {}
            clusterDict["color"] = "#"+hex(random.randrange(0, 2**24))[2:].rjust(6,'0')
            clusterDict["size"] = 1
            clusters[labels[i]] = clusterDict
        else:
            clusters[labels[i]]["size"] += 1
        trees[i].setCluster(labels[i])