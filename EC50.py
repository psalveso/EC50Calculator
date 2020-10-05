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
parser.add_argument("--fit_hill", action='store_true', help="turns on fitting of hill coefficient", dest="hill")
parser.add_argument("--no_fit_hill", action='store_false', help="turns off fitting of hill coefficient (default behavior)", dest="hill")
parser.add_argument("-m", "--mode", help="$4 experiments with 3 replicates (True), or 2 experiments with 4 replicates (False)", default=True, dest="mode", type=bool)
parser.set_defaults(hill=False)
args = parser.parse_args()

# Calculated based on user input
low = args.high / args.base ** (args.numSamples - 1)

# Define the Parameters:
params = Parameters()
params.add('max', value=1.5, min=1.0)
params.add('n', value=1.0, vary=args.hill)
params.add('EC50', value=0.004, min=0.0000001)

# This function removes the annoying non UTF-* character in the raw data file
def simplifyInputFile(fileLocation):

    foutput = os.path.join(__location__, 'workdir/data_editted.txt')
    with open(fileLocation, 'rb') as f:
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
    # saves to a 2 x numSample array that is (avg, stddev)

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

    # This loop splits the 8x12 matrix (i.e. the 96-well plate) into the numReplciates x numSamples matrix
    # it then calcualtes their averages and stdved
    # then spits out a 3xnumSample matrix continin vectors of [x, avg, stdev]

    if args.mode == True:
        for row in readFile:
            replicate1 = np.array([row[0], row[1], row[2]]) #column 1, 2, 3
            replicate2 = np.array([row[3], row[4], row[5]]) #column 4, 5, 6
            replicate3 = np.array([row[6], row[7], row[8]]) #column 7, 8, 9
            replicate4 = np.array([row[9], row[10], row[11]]) #column 10, 11, 12

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
    else:
        for row in np.transpose(readFile):
            replicate1 = np.array([row[0], row[1], row[2], row[3]]) #column 1, 2, 3, 5
            replicate2 = np.array([row[4], row[5], row[6], row[7]]) #column 5, 6, 7, 8

            av1 = np.average(replicate1)
            av2 = np.average(replicate2)

            sd1 = np.std(replicate1)
            sd2 = np.std(replicate2)

            dataSet1[index] = [x[index], av1, sd1]
            dataSet2[index] = [x[index], av2, sd2]

            index += 1
            if index > args.numSamples - 1:
                break

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

def plotFits(filename, graphTitle, ds1Name, ds2Name, ds3Name, ds4Name, results1, results2, results3, results4, xdata, ydata1, yerr1, ydata2, ydata3, ydata4, yerr2, yerr3, yerr4):

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
        # These make editing the text labels in Illustrator much easier
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['ps.fonttype'] = 42
        plt.rcParams["font.family"] = "arial"

        # sets up the first sub plot with normal axis
        plt.figure(1)
        plt.subplot(211)

        # data set 1
        plt.errorbar(xdata, normalizedData(optParams1, ydata1), yerr1, fmt='b.')
        plt.plot(xdataOpt, plotFunc(optParams1, xdataOpt), 'b--')


        # data set 2
        plt.errorbar(xdata, normalizedData(optParams2, ydata2), yerr2, fmt='g.',)
        plt.plot(xdataOpt, plotFunc(optParams2, xdataOpt), 'g--')


        # data set 3
        plt.errorbar(xdata, normalizedData(optParams3, ydata3), yerr3, fmt='r.')
        plt.plot(xdataOpt, plotFunc(optParams3, xdataOpt), 'r--')


        # data set 4
        plt.errorbar(xdata, normalizedData(optParams4, ydata4), yerr4, fmt='k.')
        plt.plot(xdataOpt, plotFunc(optParams4, xdataOpt), 'k--')


        plt.ylabel("normalized absorbance")
        #plt.legend()
        plt.title(f"{graphTitle}\nnormalized fits")

        # sets up the second sub plot with log axis
        plt.figure(1)
        plt.subplot(212)

        # Normalized data with error bars
        # data set 1
        plt.errorbar(xdata, normalizedData(optParams1, ydata1), yerr1, fmt='b.')
        # data set 2
        plt.errorbar(xdata, normalizedData(optParams2, ydata2), yerr2, fmt='g.')
        # data set 3
        plt.errorbar(xdata, normalizedData(optParams3, ydata3), yerr3, fmt='r.')
        # data set 4
        plt.errorbar(xdata, normalizedData(optParams4, ydata4), yerr4, fmt='k.')

        # Fitted curves
        # data set 1
        plt.plot(xdataOpt, plotFunc(optParams1, xdataOpt), 'b--', label=f'{ds1Name}\nEC50: {round(optParams1["EC50"],4)} {args.axis}')
        # data set 2
        plt.plot(xdataOpt, plotFunc(optParams2, xdataOpt), 'g--', label=f'{ds2Name}\nEC50: {round(optParams2["EC50"],4)} {args.axis}')
        # data set 3
        plt.plot(xdataOpt, plotFunc(optParams3, xdataOpt), 'r--', label=f'{ds3Name}\nEC50: {round(optParams3["EC50"],4)} {args.axis}')
        # data set 4
        plt.plot(xdataOpt, plotFunc(optParams4, xdataOpt), 'k--', label=f'{ds4Name}\nEC50: {round(optParams4["EC50"], 4)} {args.axis}')

        plt.xscale('log')
        plt.xlabel(args.axis)
        plt.ylabel("normalized absorbance")

        # Put a legend below current axis
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.25), ncol=2)

        f = f'results/results_{filename[:-4]}.pdf'

        plt.savefig(os.path.join(__location__, f), bbox_inches="tight", transparent=True)

        # This command causes the plot to load in a different window
        plt.show()
        plt.close()

    except ImportError:
        print('Missing package matplotlib, please install to see graph')
        pass

def plotFits2(filename, graphTitle, ds1Name, ds2Name, results1, results2, xdata, ydata1, yerr1, ydata2, yerr2):

    #gets the optimized paramters, which it needs to normalize data
    optParams1 = results1.params.valuesdict()
    optParams2 = results2.params.valuesdict()

    # generates more x data points for soother fit line
    xdataOpt = np.logspace(np.log(args.high)/np.log(args.base), np.log(low)/np.log(args.base), num=50, base=args.base)

    # For ploting the raw data and the fit
    try:
        import matplotlib.pyplot as plt
        # These make editing the text labels in Illustrator much easier
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['ps.fonttype'] = 42
        plt.rcParams["font.family"] = "arial"

        # sets up the first sub plot with normal axis
        plt.figure(1)
        plt.subplot(211)

        # data set 1
        plt.errorbar(xdata, normalizedData(optParams1, ydata1), yerr1, fmt='b.')
        plt.plot(xdataOpt, plotFunc(optParams1, xdataOpt), 'b--')


        # data set 2
        plt.errorbar(xdata, normalizedData(optParams2, ydata2), yerr2, fmt='g.',)
        plt.plot(xdataOpt, plotFunc(optParams2, xdataOpt), 'g--')

        plt.ylabel("normalized absorbance")
        #plt.legend()
        plt.title(f"{graphTitle}\nnormalized fits")

        # sets up the second sub plot with log axis
        plt.figure(1)
        plt.subplot(212)

        # Normalized data with error bars
        # data set 1
        plt.errorbar(xdata, normalizedData(optParams1, ydata1), yerr1, fmt='b.')
        # data set 2
        plt.errorbar(xdata, normalizedData(optParams2, ydata2), yerr2, fmt='g.')

        # Fitted curves
        # data set 1
        plt.plot(xdataOpt, plotFunc(optParams1, xdataOpt), 'b--', label=f'{ds1Name}\nEC50: {round(optParams1["EC50"],4)} {args.axis}')
        # data set 2
        plt.plot(xdataOpt, plotFunc(optParams2, xdataOpt), 'g--', label=f'{ds2Name}\nEC50: {round(optParams2["EC50"],4)} {args.axis}')

        plt.xscale('log')
        plt.xlabel(args.axis)
        plt.ylabel("normalized absorbance")

        # Put a legend below current axis
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.25), ncol=2)

        f = f'results/results_{filename[:-4]}.pdf'

        plt.savefig(os.path.join(__location__, f), bbox_inches="tight", transparent=True)

        # This command causes the plot to load in a different window
        plt.show()
        plt.close()

    except ImportError:
        print('Missing package matplotlib, please install to see graph')
        pass


# This writes tab deleinated textfiles with the (x, avg, stdev) and optimazed paramters from fit
def outputFile(plateNumber, dataname, data, resultOfFit):
    f =f'results/{dataname}_results_{plateNumber}.txt'
    filename = os.path.join(__location__, f)
    paramDict = resultOfFit.params.valuesdict()
    myFooterString = f"\nResults from nonlinear regression\nEC50\t{paramDict['EC50']}\nA\t{paramDict['max']}\nHill coefficient\t{paramDict['n']}"
    np.savetxt(filename, data, delimiter='\t', fmt="%s", comments="", header=f"{dataname}\n{args.axis}\taverage abs\tstandard deviation", footer=myFooterString)
    return


# This writes the sample name, and EC50 to a tab deleniated textfile.
def outputEC50Table(dictionaryOfEC50s, experimentalInfo):
    f = f'results/EC50Table.txt'
    filename = os.path.join(__location__, f)
    i = 0
    for key, value in dictionaryOfEC50s.items():
        with open(filename, 'a') as myfile:
            if i > 0:
                myfile.write(f'\t{key}\t{value}\n')
            else:
                myfile.write(f'{experimentalInfo}\t{key}\t{value}\n')
        i += 1



# The Fitting script runs in these commands
if __name__ == '__main__':

    # Loops through all files in input/
    directory = os.path.join(__location__, "input/")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        # checks if the file ends with .txt, if so runs the script on it
        if filename.endswith(".txt"):
            if args.mode == True:

                # need to make array from file name
                fileInfo = filename[:-4].split("_")

                # fileInfo[0] is the plate Number
                # fileInfo[1] is the experiment information
                # fileInfo[2] through fileInfo[5] are the experiment names

                # now run through the rest of the parsing and fitting script:
                simplifyInputFile(os.path.join(directory, filename))
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
                outputFile(fileInfo[0], fileInfo[2], ds1, result1)
                outputFile(fileInfo[0], fileInfo[3], ds2, result2)
                outputFile(fileInfo[0], fileInfo[4], ds3, result3)
                outputFile(fileInfo[0], fileInfo[5], ds4, result4)

                # this calls the funtion that writes the tab delimnated file
                EC50s = {fileInfo[2] : result1.params.valuesdict()['EC50'], fileInfo[3] : result2.params.valuesdict()['EC50'], fileInfo[4] : result3.params.valuesdict()['EC50'], fileInfo[5] : result4.params.valuesdict()['EC50']}
                outputEC50Table(EC50s, fileInfo[1])

                # generates plot and saves pdf version of plot
                plotFits(filename, fileInfo[1], fileInfo[2], fileInfo[3], fileInfo[4], fileInfo[5], result1, result2, result3, result4, ds1[:,0], ds1[:,1], ((ds1[:,2]/ds1[:,1])*(ds1[:,1]/result1.params.valuesdict()['max'])), ds2[:,1], ds3[:,1], ds4[:,1], ((ds2[:,2]/ds2[:,1])*(ds2[:,1]/result2.params.valuesdict()['max'])), ((ds3[:,2]/ds3[:,1])*(ds3[:,1]/result3.params.valuesdict()['max'])), ((ds4[:,2]/ds4[:,1])*(ds4[:,1]/result4.params.valuesdict()['max'])))

                continue
            else:
                # need to make array from file name
                fileInfo = filename[:-4].split("_")

                # fileInfo[0] is the plate Number
                # fileInfo[1] is the experiment information
                # fileInfo[2] through fileInfo[5] are the experiment names

                # now run through the rest of the parsing and fitting script:
                simplifyInputFile(os.path.join(directory, filename))
                ds1, ds2, ds3, ds4 = getData(os.path.join(__location__, 'workdir/data_editted.txt'))

                # does the minimization here:
                # data set 1
                mini1 = Minimizer(func, params, fcn_args=(ds1[:,0], ds1[:,1]))
                result1 = mini1.minimize()

                # data set 2
                mini2 = Minimizer(func, params, fcn_args=(ds2[:,0], ds2[:,1]))
                result2 = mini2.minimize()

                # generates output files
                outputFile(fileInfo[0], fileInfo[2], ds1, result1)
                outputFile(fileInfo[0], fileInfo[3], ds2, result2)

                # this calls the funtion that writes the tab delimnated file
                EC50s = {fileInfo[2] : result1.params.valuesdict()['EC50'], fileInfo[3] : result2.params.valuesdict()['EC50']}
                outputEC50Table(EC50s, fileInfo[1])

                plotFits2(filename, fileInfo[1], fileInfo[2], fileInfo[3],  result1, result2, ds1[:,0], ds1[:,1], ((ds1[:,2]/ds1[:,1])*(ds1[:,1]/result1.params.valuesdict()['max'])), ds2[:,1], ((ds2[:,2]/ds2[:,1])*(ds2[:,1]/result2.params.valuesdict()['max'])))
        else:
            continue
