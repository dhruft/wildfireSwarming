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
from ssgpr import SSGPR, SparseSpectrumFeatures, LinearGPR, NoPrior
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
vel = 1000
startFuel = 5000
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

MCTSmoveDistance = 100

# variable inits
dataCells = []
canvas = [0]
maxDensity = 22
maxHeight = 35

# if flip is True, then lower values = higher priority, meaning
# the normalize function should return larger numbers for lower values
def normalize(value, vRange, flip=False):
    dec = (value-vRange[0])/(vRange[1]-vRange[0])
    dec = min(1, dec)

    if flip: dec = 1.0 - dec
    return dec

def getDist(x1,y1,x2,y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

n, p = 2, 1
nproj = 50
fixed = True

# some arbitrary default parameters and no hyperpriors
sigma_o, sigma_o_prior = 5., NoPrior()
l, l_prior = [6.] * n, [NoPrior()] * n
sigma_n, sigma_n_prior = 0.5, NoPrior()

# construct machine and feature mapping
ssf=SparseSpectrumFeatures(n, nproj=nproj, sigma_o=sigma_o, 
                                sigma_o_prior=sigma_o_prior, l=l, 
                                l_prior=l_prior, fixed=fixed)
machineMain=LinearGPR(n, p, ssf, sigma_n=sigma_n, sigma_n_prior=sigma_n_prior)

selectedX = []
selectedY = []
selectedZ = []

def updateMachine(machine, tree):
    pred, std = machine.update(np.array([tree.height, tree.density]), np.array([tree.dbh]))

    if machine == machineMain:
        selectedX.append(tree.height)
        selectedY.append(tree.density)
        selectedZ.append(tree.dbh)

    return std