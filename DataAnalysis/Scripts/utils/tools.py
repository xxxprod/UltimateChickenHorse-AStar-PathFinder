import warnings
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
import json
import math
import time
import math
import glob
import pandas as pd
from itertools import chain
from varname import nameof

# display all the  rows
pd.set_option("display.max_rows", 100)

# display all the  columns
pd.set_option("display.max_columns", None)

# set width  - 100
pd.set_option("display.width", 160)

# set column header -  left
pd.set_option("display.colheader_justify", "left")

# set precision - 5
pd.set_option("display.precision", 5)

warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
warnings.simplefilter(action="ignore", category=pd.errors.SettingWithCopyWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="matplotlib")

repoRoot = 'D:/Development/mai/master-thesis'
dataAnalysisRoot = f"{repoRoot}/DataAnalysis"
dataRoot = f"{dataAnalysisRoot}/Data"




def plot_box(ax: plt.Axes, x, y, width, height, color=None, edgeColor=None, alpha=1, cornerSize=None, label=None, zorder=0):
    x = np.array([x, x + width, x + width, x, x])
    y = np.array([y, y, y + height, y + height, y])
    
    fill = True if color is not None else False
    edgeColor = color if edgeColor is None else edgeColor
    color = color if color is not None else '00000000'
    
    ax.fill(x, y, color, alpha=alpha, fill=fill, linewidth=1, edgecolor=edgeColor, label=label, zorder=zorder)
    if cornerSize:
        ax.plot(x, y, 'o', color=edgeColor, alpha=alpha, label=label, zorder=zorder, markersize=cornerSize)

def getOrAdd(map, key, defaultFactory=None):
    if key not in map:
        if defaultFactory is None:
            return None
        
        map[key] = defaultFactory()

    return map[key]


