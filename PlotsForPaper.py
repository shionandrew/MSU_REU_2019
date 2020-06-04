## Specifically for final paper
# Author: Shion Andrew

import math
import statistics
import csv
import os

# MatPlotlib
from matplotlib import pylab
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
from matplotlib import rc

# Scientific libraries
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline

# Astropy and Gaia
import astroquery
import keyring
from astropy import units as u
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord
from astropy import stats

def plotLightCurve():
    magerr = []
    mag = []
    abjd = []
    with open('/Users/touatokuchi/Desktop/MSU/PlotsForPaper/StripeVariable.csv') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            try:
                mag.append(float(row[1]))
                magerr.append(float(row[2]))
                abjd.append(float(row[5]))
            except:
                print("error")

    P = 1.0750575
    t0 = 53505.41686

    aphase = []
    for i in range(len(abjd)):
        aphase.append(foldAt(abjd[i],P,T0=t0,getEpoch=False))
    aphase.reverse()
    aphase2 = aphase + aphase
    magerr.reverse()
    magerr2 = magerr + magerr
    mag.reverse()
    mag2 = mag+mag

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.ylabel(r'\textbf{Magnitude}')
    plt.xlabel(r'\textbf{Phase}')
    plt.gca().invert_xaxis()
    plt.ylim(17, 18)
    plt.scatter(aphase2, mag2, color = 'red', s = .5)
    plt.errorbar(aphase2, mag2, yerr=magerr2, ecolor = 'black', lw = .6, capsize = 1, fmt = 'none')
    plt.show()

def foldAt(time, period, T0=0.0, getEpoch=False):
    epoch = np.floor( (time - T0)/period )
    phase = (time - T0)/period - epoch
    if getEpoch:
        return phase, epoch
    return phase

def main():
    plotLightCurve()

if __name__== "__main__":
    main()
