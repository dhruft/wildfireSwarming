import matplotlib
matplotlib.use('TkAgg')

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
import os
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
import pandas as pd
import importlib

cw = 6
gridx = 317
#actual gridx is 317
gridy = 28
#actual gridy = 28
startGrid = np.empty(shape=(gridy+4, gridx+4), dtype=object)
grid = np.empty(shape=(gridy, gridx), dtype=object)
ti = 0.01
startCenter = [math.ceil(gridx/2)+2, math.ceil(gridy/2)+2]
center = [math.ceil(gridx/2), math.ceil(gridy/2)]
showPath = True

uavCount = 3
deployments = 3
uavs = []
vel = 50
startFuel = 600
tRange = 10
#certaintyRange = [0.4, 0.9]
collectionFuelLoss = 40
collectionTime = 0
redeploymentTime = 2
minInfo = 0.01

homeRadius = 5
crRadius = 1
uavRadius = 0.5
targetRadius = 5

#forest gen
treeProb = 0.3
#heightRange = [5, 175] #in meters, inclusive
maxHeight = 90

# variable inits
trees = []
canvas = [0]

#threshold init
# x axis is density from 0 to 16
# y axis (increasing from top to bototm) is height
maxDensity = 32
threshold = np.zeros(shape=(maxHeight+1, maxDensity + 1))
densityInsertRadius = 3
heightInsertRadius = 5

# plt.figure()
# f, axarr = plt.subplots(2,1)

# axarr[0].imshow(threshold, cmap='hot', interpolation='nearest')
# # axarr[1].imshow(densityThreshold, cmap='hot', interpolation='nearest')
# #axarr[1] = sn.heatmap([densityThreshold])
# plt.show()

# plot = plt.imshow(threshold, cmap='hot', interpolation='nearest')
# plt.show()

# def displayPlot():
#     plt.imshow(threshold, cmap='hot', interpolation='nearest')
#     # #axarr[0].imshow(threshold, cmap='hot', interpolation='nearest')
#     # #axarr[1].imshow(densityThreshold, cmap='hot', interpolation='nearest')
#     # #axarr[1] = sn.heatmap([densityThreshold])
#     plt.show()
#     #plt.plot(densityThreshold)
#     #plt.show()

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
for itery in range(2*tRange+1):
    for iterx in range(2*tRange+1):
        value = getDist(*pCenter, iterx, itery)
        maxValue = getDist(*pCenter, 0, 0)
        if value==0:
             value = maxValue
        proximityField[itery][iterx] = normalize(value, [0, maxValue], True)

# Define the Matérn kernel with the desired smoothness parameter (nu)
nu = 1.5 # Smoothness parameter, adjust as needed
length_scale = 1  # Length scale parameter
noise_level = 0.5
kernel = Matern(length_scale=length_scale, nu=nu)

gpr = GaussianProcessRegressor(kernel=kernel, alpha=noise_level)

selected_X = []
selected_Y = []
selected_z = []