import random
import math
import tkinter as tk
import asyncio
from threading import Thread
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.colors
import matplotlib.cm as cm

cw = 10
gridx = 101
gridy = 101
grid = []

ti = 0.01
uavCount = 8
crRadius = 2
treeProb = 0.02
trees = []
canvas = [0]
colors = {}