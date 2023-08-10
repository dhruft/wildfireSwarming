import random
import math
import tkinter as tk
import asyncio
from threading import Thread
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.colors
import matplotlib.cm as cm
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import seaborn as sn

cw = 10
gridx = 101
gridy = 101
grid = np.empty(shape=(gridy, gridx), dtype=object)
ti = 0.01
center = [math.ceil(gridx/2), math.ceil(gridy/2)]
showPath = True

uavCount = 3
deployments = 25
uavs = []
vel = 10
startFuel = 250
tRange = 15
certaintyRange = [0.4, 0.9]
collectionFuelLoss = 10
collectionTime = 0.1
redeploymentTime = 0.2
minInfo = 0.01

homeRadius = 3
crRadius = 1
uavRadius = 0.5
targetRadius = 5

#forest gen
treeProb = 0.3
heightRange = [5, 175] #in meters, inclusive

# variable inits
trees = []
canvas = [0]

#threshold init
# x axis is density from 0 to 16
# y axis (increasing from top to bototm) is height
maxDensity = 32
threshold = np.zeros(shape=(heightRange[1]-heightRange[0]+1, maxDensity + 1))
densityInsertRadius = 3
heightInsertRadius = 5
densityThreshold = np.zeros(shape=(maxDensity + 1))
heightThreshold = np.zeros(shape=(heightRange[1]-heightRange[0] + 1))

# plt.figure()
# f, axarr = plt.subplots(2,1)

# axarr[0].imshow(threshold, cmap='hot', interpolation='nearest')
# # axarr[1].imshow(densityThreshold, cmap='hot', interpolation='nearest')
# #axarr[1] = sn.heatmap([densityThreshold])
# plt.show()

plot = plt.imshow(threshold, cmap='hot', interpolation='nearest')
plt.show()

def displayPlot():
    plt.imshow(threshold, cmap='hot', interpolation='nearest')
    # #axarr[0].imshow(threshold, cmap='hot', interpolation='nearest')
    # #axarr[1].imshow(densityThreshold, cmap='hot', interpolation='nearest')
    # #axarr[1] = sn.heatmap([densityThreshold])
    plt.show()
    #plt.plot(densityThreshold)
    #plt.show()

# if flip is True, then lower values = higher priority, meaning
# the normalize function should return larger numbers for lower values
def normalize(value, vRange, flip=False):
    dec = (value-vRange[0])/(vRange[1]-vRange[0])
    dec = min(1, dec)

    if flip: dec = 1.0 - dec
    return dec

def getDist(x1,y1,x2,y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

#build proximity field for uavs
proximityField = np.zeros(shape=[tRange*2+1, tRange*2+1])
pCenter = [tRange, tRange]
for y in range(2*tRange+1):
    for x in range(2*tRange+1):
        value = getDist(*pCenter, x, y)
        maxValue = getDist(*pCenter, 0, 0)
        if value==0:
             value = maxValue
        proximityField[y][x] = normalize(value, [0, maxValue], True)