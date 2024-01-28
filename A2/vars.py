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
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
import pandas as pd
import time
from collections import defaultdict
import os
from ssgpr import SSGPR
import copy

cw = 0.25
gridx = 4400
gridy = 4200
grid = np.empty(shape=(gridy, gridx), dtype=object)
center = [math.ceil(gridx/2), math.ceil(gridy/2)]
showPath = True

startGrid = np.empty(shape=(gridy+8, gridx+8), dtype=object)
startCenter = [math.ceil(gridx/2)+4, math.ceil(gridy/2)+4]

ti = 0.01
deployments = 1
vel = 100
startFuel = 25000
collectionFuelLoss = 10
collectionTime = 0.1
redeploymentTime = 0.2
greedyRange = 10

uavRadius = 10
# crRadius = 1

#forest gen
dataProb = 0.3
heightRange = [0, 100] #in meters, inclusive
DBHRange = [0, 100]
trees = []

MCTSmoveDistance = 50

# variable inits
dataCells = []
canvas = [0]
maxDensity = 22

# if flip is True, then lower values = higher priority, meaning
# the normalize function should return larger numbers for lower values
def normalize(value, vRange, flip=False):
    dec = (value-vRange[0])/(vRange[1]-vRange[0])
    dec = min(1, dec)

    if flip: dec = 1.0 - dec
    return dec

def getDist(x1,y1,x2,y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

m, n, p = 20, 2, 1
machine = SSGPR(n, p, nproj=100)
machine.sigma_n = 0.2
assert machine.sigma_n > 0.
machine.mapping.setparams([0.895, 0.15, 0.1])  # Adjust to provide three parameters
machine.reset()

selected_X = []
selected_Y = []
selected_z = []