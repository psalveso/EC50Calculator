import numpy as np
import os
import argparse
from lmfit import Minimizer, Parameters, report_fit

# To handle file locations
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# set up the parser for the command line
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dilution", help="Dilution factor i.e., 2-fold, 3-fold, etc...", default=3, dest="base", type=float)
parser.add_argument("-c", "--concentation", help="Highest concentration used", default=3, dest="high", type=float)
parser.add_argument("-s", "--samples", help="Number of samples used", default=8, dest="numSamples", type=int)
parser.add_argument("-a", "--axis", help="Units of x-axis for graphing", default="mg/mL", dest="axis")
parser.add_argument("-1", "--dataset1", help="Name of samples in columns 1, 2, and 3", default="data set 1", dest="dataSet1Name")
parser.add_argument("-2", "--dataset2", help="Name of samples in columns 4, 5, and 6", default="data set 2", dest="dataSet2Name")
parser.add_argument("-3", "--dataset3", help="Name of samples in columns 7, 8, and 9", default="data set 3", dest="dataSet3Name")
parser.add_argument("-4", "--dataset4", help="Name of samples in columns 10, 11, and 12", default="data set 4", dest="dataSet4Name")
parser.add_argument("-n", "--hill", help="Fit Hill coefficient? True or False", default=False, dest="hill")
parser.add_argument("-i", "--input", help="Input data file name", default="data.txt", dest="datafile")
args = parser.parse_args()

# Calculated based on user input
low = args.high / args.base ** (args.numSamples - 1)

# Define the Parameters:
params = Parameters()
params.add('max', value=1.5, min=1.0)
params.add('n', value=1.0, vary=args.hill)
params.add('EC50', value=0.004, min=0.0000001)

# This function removes the annoying non UTF-* character in the raw data file
def simplifyInputFile():

    finput = os.path.join(__location__, args.datafile)
    foutput = os.path.join(__location__, 'workdir/data_editted.txt')
    with open(finput, 'rb') as f:
        with open(foutput, 'w') as x:
            try:
                for line in f:
                    x.write(line.decode('utf8'))
            except UnicodeDecodeError:
                pass


def getData(inputfile):

    # This makes the x values
    start = np.log(args.high)/np.log(args.base)
    stop = np.log(low)/np.log(args.base)
    x = np.logspace(start, stop, num=args.numSamples, base=args.base)

    # opens the optimized textfile
    # saves to a 2 x 8 array that is (avg, stddev)
    # wants this to evenaully read from within workdir
    with open(inputfile, 'r') as f:
        numLines = 0
        for line in f:
            numLines += 1
        footer  = numLines - 18
        f.seek(0)
        readFile = np.genfromtxt(f, delimiter="\t", skip_header=10, skip_footer=footer, usecols=(1,2,3,4,5,6,7,8,9,10,11,12))

    dataSet1 = np.empty(shape=(args.numSamples,3))
    dataSet2 = np.empty(shape=(args.numSamples,3))
    dataSet3 = np.empty(shape=(args.numSamples,3))
    dataSet4 = np.empty(shape=(args.numSamples,3))

    index = 0
    for row in readFile:
        replicate1 = np.array([row[0], row[1], row[2]])
        replicate2 = np.array([row[3], row[4], row[5]])
        replicate3 = np.array([row[6], row[7], row[8]])
        replicate4 = np.array([row[9], row[10], row[11]])

        av1 = np.average(replicate1)
        av2 = np.average(replicate2)
        av3 = np.average(replicate3)
        av4 = np.average(replicate4)

        sd1 = np.std(replicate1)
        sd2 = np.std(replicate2)
        sd3 = np.std(replicate3)
        sd4 = np.std(replicate4)

        dataSet1[index] = [x[index], av1, sd1]
        dataSet2[index] = [x[index], av2, sd2]
        dataSet3[index] = [x[index], av3, sd3]
        dataSet4[index] = [x[index], av4, sd4]

        index += 1

    return dataSet1, dataSet2, dataSet3, dataSet4

# the function that should explain the data
def func(params, conc, data):
    A = params['max']
    n = params['n']
    EC50 = params['EC50']
    model = A * ((conc ** n)/(conc ** n + EC50 ** n))
    return model - data

# The funciton plotted with best-fit parameters
def plotFunc(params, conc):
    A = params['max']
    n = params['n']
    EC50 = params['EC50']
    graph = ((conc ** n)/(conc ** n + EC50 ** n))
    return graph

# The raw data normalized to the best-fit max value
def normalizedData(params, data):
    A = params['max']
    graph = data / A
    return graph

def plotFits(results1, results2, results3, results4, xdata, ydata1, yerr1, ydata2, ydata3, ydata4):

    #gets the optimized paramters, which it needs to normalize data
    optParams1 = results1.params.valuesdict()
    optParams2 = results2.params.valuesdict()
    optParams3 = results3.params.valuesdict()
    optParams4 = results4.params.valuesdict()

    # generates more x data points for soother fit line
    xdataOpt = np.logspace(np.log(args.high)/np.log(args.base), np.log(low)/np.log(args.base), num=50, base=args.base)

    # For ploting the raw data and the fit
    try:
        import matplotlib.pyplot as plt
        # Normalzied data and normalized fitted curve
        # These make the fitted curve much smoother

        # data set 1
        plt.plot(xdata, normalizedData(optParams1, ydata1), 'b.', label=f'{args.dataSet1Name}')
        plt.plot(xdataOpt, plotFunc(optParams1, xdataOpt), 'b--', label='fit')


        # data set 2
        plt.plot(xdata, normalizedData(optParams2, ydata2), 'g.', label=f'{args.dataSet2Name}')
        plt.plot(xdataOpt, plotFunc(optParams2, xdataOpt), 'g--', label='fit')


        # data set 3
        plt.plot(xdata, normalizedData(optParams3, ydata3), 'r.', label=f'{args.dataSet3Name}')
        plt.plot(xdataOpt, plotFunc(optParams3, xdataOpt), 'r--', label='fit')


        # data set 4
        plt.plot(xdata, normalizedData(optParams4, ydata4), 'k.', label=f'{args.dataSet4Name}')
        plt.plot(xdataOpt, plotFunc(optParams4, xdataOpt), 'k--', label='fit')


        plt.xlabel(args.axis)
        plt.ylabel("normalized absorbance")
        plt.legend()
        plt.title("normalized fits")



        plt.savefig(os.path.join(__location__, 'results/results.pdf'))

        # This command causes the plot to load in a different window
        plt.show()
        plt.close()

    except ImportError:
        print('Missing package matplotlib, please install to see graph')
        pass


# This writes tab deleinated textfiles with the (x, avg, stdev) and optimazed paramters from fit
def outputFile(dataname, data, resultOfFit):
    f =f'results/{dataname}_results.txt'
    filename = os.path.join(__location__, f)
    paramDict = resultOfFit.params.valuesdict()
    myFooterString = f"\nResults from nonlinear regression\nEC50\t{paramDict['EC50']}\nA\t{paramDict['max']}\nHill coefficient\t{paramDict['n']}"
    np.savetxt(filename, data, delimiter='\t', fmt="%s", comments="", header=f"{dataname}\n{args.axis}\taverage abs\tstandard deviation", footer=myFooterString)
    return



# The Fitting script runs in these commands
if __name__ == '__main__':

    # parses the data file, loads the data arrays to four numpy arrays
    simplifyInputFile()
    ds1, ds2, ds3, ds4 = getData(os.path.join(__location__, 'workdir/data_editted.txt'))

    # does the minimization here:
    # data set 1
    mini1 = Minimizer(func, params, fcn_args=(ds1[:,0], ds1[:,1]))
    result1 = mini1.minimize()

    # data set 2
    mini2 = Minimizer(func, params, fcn_args=(ds2[:,0], ds2[:,1]))
    result2 = mini2.minimize()

    # data set 3
    mini3 = Minimizer(func, params, fcn_args=(ds3[:,0], ds3[:,1]))
    result3 = mini3.minimize()

    # data set 4
    mini4 = Minimizer(func, params, fcn_args=(ds4[:,0], ds4[:,1]))
    result4 = mini4.minimize()

    # generates output files
    outputFile(args.dataSet1Name, ds1, result1)
    outputFile(args.dataSet2Name, ds2, result2)
    outputFile(args.dataSet3Name, ds3, result3)
    outputFile(args.dataSet4Name, ds4, result4)

    # generates plot and saves pdf version of plot
    plotFits(result1, result2, result3, result4, ds1[:,0], ds1[:,1], ds1[:,2], ds2[:,1], ds3[:,1], ds4[:,1])
