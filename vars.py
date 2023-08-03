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

uavCount = 8
vel = 7
startFuel = 300
tRange = 15
certaintyRange = [0.6, 0.9]
collectionFuelLoss = 10

homeRadius = 10
crRadius = 1
uavRadius = 0.5

#forest gen
treeProb = 0.5
heightRange = [15, 35] #in meters, inclusive

# variable inits
trees = []
canvas = [0]
clusters = {}

#threshold init
# x axis is density from 0 to 16
# y axis (increasing from top to bototm) is height
threshold = np.zeros(shape=(heightRange[1]-heightRange[0]+1, 33))
densityInsertRadius = 1
heightInsertRadius = 1
densityThreshold = np.zeros(shape=(33))

# plt.figure()
# f, axarr = plt.subplots(2,1)

# axarr[0].imshow(threshold, cmap='hot', interpolation='nearest')
# # axarr[1].imshow(densityThreshold, cmap='hot', interpolation='nearest')
# #axarr[1] = sn.heatmap([densityThreshold])
# plt.show()

plot = plt.imshow(threshold, cmap='hot', interpolation='nearest')
plt.show()

def updatePlot():
    plt.imshow(threshold, cmap='hot', interpolation='nearest')
    #axarr[0].imshow(threshold, cmap='hot', interpolation='nearest')
    #axarr[1].imshow(densityThreshold, cmap='hot', interpolation='nearest')
    #axarr[1] = sn.heatmap([densityThreshold])
    plt.show()

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