"""
This module is for your final visualization code.
After you have done your EDA and wish to create some visualizations for you final jupyter notebook
A framework for each type of visualization is provided.
"""
# visualization packages
import matplotlib.pyplot as plt
from matplotlib.axes._axes import _log as matplotlib_axes_logger
from matplotlib.ticker import FuncFormatter
import seaborn as sns

# Standard data manipulation packages
import pandas as pd
import numpy as np

matplotlib_axes_logger.setLevel('ERROR')

# Set specific parameters for the visualizations
large = 22; med = 16; small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")

