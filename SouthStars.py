
#
# Author: Shion Andrew
#
# Determines probabaility that a star of a given magnitude error and amplitude is of a particular optical variable type
### Predetermined bins for every optical type

from sklearn.linear_model import LinearRegression
from fpdf import FPDF
from PIL import Image
import matplotlib.pyplot as plt
import csv
import os
import matplotlib.patches as mpatches
from scipy.interpolate import interp1d
import numpy as np
import scipy
from astropy import stats
import statistics
import sys

binNum = 4

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

                ### Gives name of optical type that corresponds to a given number
                SouthTypes= {
                    5: "EW/EB",
                    6: "EA",
                    7: "Rotational",
                }

                '''
                #### FULL DICT OF TYPES ####
                SouthTypes= {
                    1: "RRab",
                    2: "RRc",
                    3: "RRad",
                    4: "Blazkho",
                    5: "EW/EB",
                    6: "EA",
                    7: "Rotational",
                    8: "LPV",
                    9: "Deta-Scuti",
                    10: "ACEP",
                    11: "MISC",
                    12: "Cep-II",
                    13: "LMC Cap-1",
                                }
                '''

                #typesList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
                #typeNames = ["", "RRab", "RRc", "RRd", "Blazkho", "EW/EB", "EA", "Rotational", "LPV", "Deta-Scuti", "ACEP", "MISC", "Cep-II", "LMC Cap-1"]

                ##DataCuts
                if period > 10:
                    continue

                else:
                    if opticalType in SouthTypes:
                        ## add magError and Vamp at desired location within array
                        magErrTot[opticalType].append(magError)
                        VampTot[opticalType].append(Vamp)
                        RaTot[opticalType].append(Ra)
                        DecTot[opticalType].append(Dec)

            except ValueError:
                  continue


        for type in SouthTypes:
            linFitStats =  LinearFit(VampTot[type],magErrTot[type],SouthTypes.get(type), binNum, "Catalina South Optical Variables", "noshow")
            pVals = getPvalue(magErrTot[type], VampTot[type], SouthTypes.get(type))
            recordData(RaTot[type], DecTot[type], magErrTot[type], VampTot[type], pVals, SouthTypes.get(type))

'''
            ### WRITE LINFIT STATS TO CSV FILE. Must be rewritten if Vamp bins change! ####

            ##proceed so long as linFitStats is not empty
            if linFitStats:
                ### Write standard deviation and mean for each linear fit to data file
                ## add name for every optical variable
                for bin in range(len(linFitStats)):
                    with open('/Users/touatokuchi/Desktop/SouthStars/South_LinReg.csv', 'a') as csvFile:
                        writer = csv.writer(csvFile)

                        ## write col names for first line
                        if os.stat('/Users/touatokuchi/Desktop/SouthStars/South_LinReg.csv').st_size == 0:
                            writer.writerow(['name', 'mean', 'stdev', 'ampLow', 'ampHigh'])
                            writer.writerow(linFitStats[bin])
                        else:
                            writer.writerow(linFitStats[bin])
                        csvFile.close()

'''

### Helper function for plot stars; performs linear regression; returns stdev, mean, and variable name
def LinearFit(Vamp,magErr, variable, binNum, name, showPlot):
    LinStats = []
    #make sure lists are equal size and nonempty
    if Vamp and len(Vamp) == len(magErr):
        ###############################
        ### Create Amplitude Bins #####
        ###############################
        ### Current Method: Get Median amplitude recursively. Divides based on number density ####
        starTotal = len(Vamp)
        sortedAmp = sorted(Vamp)

        ## will be used later for recording range in which regression was performed
        lowerBounds = []
        upperBounds = []
        for i in range(binNum):
            lowerBounds.append(sortedAmp[starTotal*i/binNum])
        for i in range(binNum-1):
            upperBounds.append(sortedAmp[starTotal*(i+1)/binNum])
        upperBounds.append(sortedAmp[-1])
        lowerBounds[0] = 0 ### guarantees all points are strictly greater than some lowerbound


        VampTot =  [[] for x in xrange(binNum)] ##separates Vamp in binNum amplitude bins
        magErrTot =  [[] for x in xrange(binNum)] ##separates magErr binNum amplitude bins

        ## iterate through all stars and sort into amplitude bins
        for datapoint in range(len(Vamp)):
            for bin in range(binNum):
                if Vamp[datapoint] <= upperBounds[bin] and Vamp[datapoint] > lowerBounds[bin]:
                    VampTot[bin].append(Vamp[datapoint])
                    magErrTot[bin].append(magErr[datapoint])


        ## perform linear regression for each amplitude bins
        for bin in range(binNum):
            x = VampTot[bin]
            y = magErrTot[bin]

            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(np.array(x),np.array(y))
            line = slope*np.array(x) + intercept
            medAbsDev = stats.median_absolute_deviation(y)
            stdev = 1.4826*medAbsDev
            lineUpper = line + stdev
            lineLower = line - stdev


            ###### PLOTS ######

            fig,ax = plt.subplots()
            equation = "y = " + str(slope) + "x + " + str(intercept)
            plt.text(.5, .9, equation, horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, bbox=dict(facecolor='gray', alpha=0.5))
            plt.legend(['data', 'linear', 'cubic'], loc='best')
            plt.plot(np.array(x),np.array(y),'.', color = 'orange', markeredgecolor = 'darkorange')
            plt.plot(np.array(x), line, '-', color = 'black')
            plt.plot(np.array(x), lineUpper, color = 'black', linestyle='dashed')
            plt.plot(np.array(x), lineLower, color = 'black', linestyle='dashed')
            plt.title(name + ": " + variable)
            plt.ylabel('Magnitude Error')
            plt.xlabel('V amp')
            ax = plt.gca()
            fig = plt.gcf()
            variable = variable.replace('/','and')
            filename = "/Users/touatokuchi/Desktop/SouthStars/LinearRegressionSingle/" + variable + "_" + name + "bin#" + str(bin)
            plt.savefig(filename, bbox_inches = 'tight')
            plt.close(fig)    # close the figure

            mean = statistics.mean(y)

            ## each row in LinStats corresponds to an amplitude bin. There are four rows in total max
            LinStats.append([variable, mean, stdev, lowerBounds[bin], upperBounds[bin]])

        return LinStats


### gets Pvalues from Zscores of each value in sample relative to given mean and stdev ####
def getPvalue(magErrorVals, ampVals, variableType):
    variableType = variableType.replace('/','and') ##/'s not allowed in file name
    pValues = []
    for datapoint in range(len(magErrorVals)):
        Vamp = ampVals[datapoint]
        with open("/Users/touatokuchi/Desktop/SouthStars/South_LinReg.csv") as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            for row in plots:
                try:
                    type = row[0]
                    lowAmp = float(row[3])
                    highAmp = float(row[4])
                    if type == variableType and Vamp > lowAmp and Vamp <= highAmp:
                        stdev = float(row[1])
                        mean = float(row[2])
                        zScore= (magErrorVals[datapoint]-mean)/stdev
                        pValues.append(scipy.stats.norm.sf(abs(zScore))*2)

                except ValueError:
                    continue
    return pValues



def recordData(Ra, Dec, magErr, Vamp, pVals, variableName):
    ## check arrays are all equal size
    if len(Ra) == len(magErr) and len(Vamp) == len(pVals):

        ## loop through all data points
        variableName = variableName.replace('/','and') ##/'s not allowed in file name
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

    else:
        print "Error: Check that South_LinReg is clean. Check optical variable names are clear of /'s. '"
        print "Variable:" + variableName
        print len(Vamp)
        print len(magErr)
        print len(pVals)





#######################################################################
#################### HelperFunctions for Image Output##################
#######################################################################

def combineImages(pdfFileName, listPages, dir = ''):
    if (dir):
        dir += "/"

    cover = Image.open(dir + str(listPages[0]))
    width, height = cover.size

    pdf = FPDF(unit = "pt", format = [width, height])

    for page in listPages:
        pdf.add_page()
        pdf.image(dir + str(page), 0, 0)

    pdf.output("/Users/touatokuchi/Desktop/" + pdfFileName + ".pdf", "F")
    print pdfFileName + ".pdf has been saved to: /Users/touatokuchi/Desktop/"


def makePdf(newname, directory):
	listPages = []
	for filename in os.listdir(directory):
		if filename.endswith("png"):
			listPages.append(filename)
	combineImages(newname, listPages, directory)


#######################################################################
######################### Main Method #################################
#######################################################################

def main():

     plotStarsSouth("/Users/touatokuchi/Desktop/MSU_REU_2019/OpticalVariables/SouthStars.csv") #EW, EA, #CepII, #RRab, #RRc, #RRd, #Blazkho
     makePdf("IndvLinReg", "/Users/touatokuchi/Desktop/SouthStars/LinearRegressionSingle")
     #makePdf("NoAmpBins", "/Users/touatokuchi/Desktop/SouthStars/NoAmpBins")

if __name__== "__main__":
  main()
