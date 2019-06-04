
#
# Author: Shion Andrew
#
# Determines probabaility that a star of a given magnitude error and amplitude is of a particular optical variable type

from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt
import csv
import os
import matplotlib.patches as mpatches
from scipy.interpolate import interp1d
import numpy as np
import scipy
from astropy import stats
import statistics


'''Performs linear regression on all stars in Southern Catalog, separated by Optical Type, in Magnitude error as fxn of Amplitude'''
def plotStarsSouth(filename):
## typeNames = ["RRab", "RRc", "RRd", "Blazkho", "EW/EB", "EA", "Rotational", "LPV", "Deta-Scuti", "ACEP", "MISC", "Cep-II", "LMC Cap-1"]
    magErrTot =  [[] for x in xrange(15)] ##separates magErr by opticalType. List of lists with index = opticalType number
    VampTot =  [[] for x in xrange(15)] ##separates Vamp by opticalType. List of lists with index = opticalType number
    RaTot = [[] for x in xrange(15)] ##separates RA by opticalType.
    DecTot = [[] for x in xrange(15)] ##separates Dec by opticalType.

    with open(filename) as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            try:
                #Calculate Error in Magnitude
                fluxError = float(row[28])
                flux = float(row[27])
                magError = 1.09*fluxError/flux

                Ra = float(row[0])
                Dec = float(row[1])
                period = float(row[5])
                Vamp = float(row[8])
                magnitude = float(row[29])
                opticalType = int(row[9])

                typesList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
                typeNames = ["", "RRab", "RRc", "RRd", "Blazkho", "EW/EB", "EA", "Rotational", "LPV", "Deta-Scuti", "ACEP", "MISC", "Cep-II", "LMC Cap-1"]

                ##DataCuts
                if period > 10:
                    continue

                else:
                    if opticalType in typesList:
                        ## add magError and Vamp at desired location within array
                        magErrTot[opticalType].append(magError)
                        VampTot[opticalType].append(Vamp)
                        RaTot[opticalType].append(Ra)
                        DecTot[opticalType].append(Dec)

            except ValueError:
                  continue

'''
        linFitStats = []
        for i in typesList:
            linFitStats.append(LinearFit(VampTot[i],magErrTot[i],typeNames[i], "Catalina South Optical Variables"))
            pVals = getPvalue(magErrTot[i], typeNames[i])
            recordData(RaTot[i], DecTot[i], magErrTot[i], VampTot[i], pVals, typeNames[i])


        ### Write standard deviation and mean for each linear fit to data file
        ## add name for every optical variable
        for i in range(len(linFitStats)):
            row = linFitStats[i]
            with open('/Users/touatokuchi/Desktop/South_LinReg.csv', 'a') as csvFile:
                writer = csv.writer(csvFile)
                if not row:
                    continue
                elif i == 0:
                    writer.writerow(['name', 'stdev', 'mean'])
                    writer.writerow(row)
                else:
                    writer.writerow(row)
            csvFile.close()
'''

def recordData(Ra, Dec, magErr, Vamp, pVals, variableName):
    ## check arrays are all equal size
    if len(Ra) == len(magErr) and len(Vamp) == len(pVals):

        ## loop through all data points
        with open('/Users/touatokuchi/Desktop/SouthStars/' + variableName + '.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)
            for i in range(len(Ra)):
                row = [Ra[i], Dec[i], magErr[i], Vamp[i], pVals[i]]
                if i == 0:
                    writer.writerow(['Ra', 'Dec', 'magErr', 'Vamp', 'prob'])
                    writer.writerow(row)
                else:
                    writer.writerow(row)
        csvFile.close()

### Helper function for plot stars; performs linear regression; returns stdev, mean, and variable name
def LinearFit(Vamp,magErr, variable, name):
    #make sure lists are equal size and nonempty
    if Vamp and len(Vamp) == len(magErr):
        x = Vamp
        y = magErr
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(np.array(x),np.array(y))
        line = slope*np.array(x) + intercept
    	medAbsDev = stats.median_absolute_deviation(y)
    	stdev = 1.4826*medAbsDev
    	lineUpper = line + stdev
        lineLower = line - stdev
    	mean = statistics.mean(y)

'''
        fig,ax = plt.subplots()
        equation = "y = " + str(slope) + "x + " + str(intercept)
        plt.text(.5, .9, equation, horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, bbox=dict(facecolor='gray', alpha=0.5))
        plt.legend(['data', 'linear', 'cubic'], loc='best')
        plt.plot(np.array(x),np.array(y),'.', color = 'orange')
        plt.plot(np.array(x), line, '-', color = 'black')
        plt.plot(np.array(x), lineUpper, color = 'black', linestyle='dashed')
        plt.plot(np.array(x), lineLower, color = 'black', linestyle='dashed')
        plt.title(name + ": " + variable)
        plt.ylabel('Magnitude Error')
        plt.xlabel('V amp')
        ax = plt.gca()
        fig = plt.gcf()
        variable = variable.replace('/','and')
        filename = "/Users/touatokuchi/Desktop/SouthStars/LinearRegressionSingle/" + variable + "_" + name
        plt.savefig(filename, bbox_inches = 'tight')
        plt.close(fig)    # close the figure
'''

        return [variable, stdev, mean]


### gets Pvalues from Zscores of each value in sample relative to given mean and stdev ####
def getPvalue(dataset, variableType):
    pValues = []
    for dataValue in dataset:
        with open("/Users/touatokuchi/Desktop/SouthStars/South_LinReg.csv") as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            for row in plots:
                if row[0] == variableType:
                    stdev = float(row[1])
                    mean = float(row[2])
                    zScore= (dataValue-mean)/stdev
                    pValues.append(scipy.stats.norm.sf(abs(zScore))*2)

    return pValues



def main():
     plotStarsSouth("/Users/touatokuchi/Desktop/MSU_REU_2019/OpticalVariables/SouthStars.csv") #EW, EA, #CepII, #RRab, #RRc, #RRd, #Blazkho

if __name__== "__main__":
  main()
