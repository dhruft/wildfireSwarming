# TODO: If maxCluster span is too large, remove points until cluster span
# is reduced while maintaining maximum totalAge

import random
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN

import mpu
def getSpan(xs, ys):
    right_bottom = (max(xs), min(ys))
    left_top = (min(xs), max(ys))
    distance = mpu.haversine_distance(left_top, right_bottom)*0.621371
    return distance

# Parameters
threshold = 94  # Threshold for "large numbers"
epsilon = 4   # Epsilon parameter for DBSCAN
min_cluster = 6
maxSpan = 1500

def getFocusPoint(grid):


    # create list of coordinates with grid values
    # large enough
    points = np.empty((0,2), int)
    for r in range(n):
        for c in range(n):
            if grid[r][c] > threshold:
                points = np.append(points, np.array([[r,c]]), axis=0)

    # Apply DBSCAN
    dbscan = DBSCAN(eps=epsilon, min_samples=1)
    dbscan.fit(points)

    labels = np.array(dbscan.labels_)

    # combine list of categories and points 
    # into single dictionary
    lenCat = 0
    data = list(zip(labels, points))
    categories={}
    for c, point in data:
        if c in categories:
            categories[c].append(point)
        else:
            lenCat += 1
            categories[c] = [point]

    maxCluster = c
    maxAge = 0
    # remove small clusters
    # and clusters exceeding maxSpan
    for c in list(categories.keys()):
        if len(categories[c]) < min_cluster:
            categories.pop(c)
            continue

        
        
        xs = np.array(categories[c])[:, 0]
        ys = np.array(categories[c])[:, 1]
        span = getSpan(xs, ys)
        print(span)
        if span > maxSpan:
            print(xs)
            # categories.pop(c)

    for c in list(categories.keys()):
        totalAge = sum([grid[coord[0]][coord[1]] for coord in categories[c]])
        if totalAge > maxAge:
            maxAge = totalAge
            maxCluster = c

    # CODE TO VIEW ALL MAJOR CLUSTERS

    # keys = []
    # x = []
    # y = []

    #x = np.array(maxCluster)[:, 0]
    #y = np.array(maxCluster)[:, 1]

    # seperate cluster points for graphing
    # for key, values in categories.items():
    #     for coord in values:
    #         keys.append(key)
    #         x.append(coord[0])
    #         y.append(coord[1])

    # generate a random color for each cluster
    # colormap = np.zeros((9999,3))
    # for key, values in categories.items():
    #     color = np.array([[random.random(), random.random(), random.random()]])
    #     if key == maxCluster:
    #         color = np.array([[0,0,0]])
    #     #colormap = np.append(colormap, color, axis=0)
    #     colormap[key] = color

    # # plot
    # f1 = plt.figure(1)  # create new image and assign the variable "fig_1" to it
    # ax = f1.add_subplot(111)

    # ax.scatter(x, y, c=colormap[keys])
    # ax.set_ylim(-1, n)
    # ax.set_xlim(-1, n)
    # plt.show()

    focusArea = categories[maxCluster]
    x = np.array(focusArea)[:, 0]
    y = np.array(focusArea)[:, 1]

    xmean = np.mean(x)
    ymean = np.mean(y)

    # CODE TO VIEW SELECTED CLUSTER AND FOCUS POINT

    # x = np.append(x, xmean)
    # y = np.append(y, ymean)

    # colormap = np.full(shape=(len(x)), fill_value="black")
    # colormap[len(x)-1] = "red"

    # f2 = plt.figure(1)  # create new image and assign the variable "fig_1" to it
    # ax = f2.add_subplot(111)
    # ax.scatter(x, y, c=colormap)
    # ax.set_ylim(-1, n)
    # ax.set_xlim(-1, n)
    # plt.show()
    return np.array([xmean, ymean]), focusArea

def main():
    n = 50
    grid = []

    for i in range(n):
        row = []
        for e in range(n):
            number = random.randint(0,99)
            row.append(number)
        grid.append(row)

    getFocusPoint(grid)

#main()