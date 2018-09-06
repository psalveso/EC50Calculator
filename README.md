# EC50 Calculator

This python script calculates EC50 values for the affinity of antibody sera towards an antigen. The script reads a `.txt` file produced by Varioskan Lux and performs a nonlinear least squares fit of the data sets within. The script outputs the results of the fits as text files and saves a graph of the results to a pdf file.

## Dependencies

The following must be installed on your system to run the script properly

- Python3
- Numpy
- Scipy
- lmfit
- matplotlib
- kiwisolver

## Running the script

### Formatting input data

The script should handle `.txt` files output by Varioskan Lux, wherein data is places in a tab-seperated text file mimicking the layout of a 96-well plate. The script will work with data outputted from Skanit Software 5.0, using the default export options. Prior to outputting the data from the instrument, it is critical that **your 96-well plate be laid out in a particular way for the script to work.**


| - | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A** |  |  |  |  |  |  |  |  |  |  |  |  |
| **B** | | | | | | | | | | | | |
| **C** | | | | | | | | | | | | |
| **D** | | | | | | | | | | | | |
| **E** | | | | | | | | | | | | |
| **F** | | | | | | | | | | | | |
| **G** | | | | | | | | | | | | |
| **H** | | | | | | | | | | | | | |

- You need to have four experiments on each plate, the samples for these experiments need to be run in triplicate.
- Experiment 1 needs to be placed in columns 1, 2, and 3. Experiment 2 needs to be placed in columns 4, 5, and 6. Experiment 3 needs to be placed in columns 7, 8, 9. Experiment 4 needs to be placed in columns 10, 11, and 12.
- If you have less than 4 experiments on the plate, you should instead process the data with Solver in Excel, as this script will not run.
- Your highest concentration samples for the experiments need to be in row A of the 96-well plate. Your lowest concentration needs to be in row H.
- Your concentration gradient needs to spaced uniformly (i.e., 1, 0.5, 0.25, 0.125 ...).

### Running the script from the terminal

After cloning/forking/downloading the repository, you first need to place your data file output by the Varioskan Lux into the same directory as the script. Then navigate to the directory that contains the script using a terminal.

The script is run by entering `python3 EC50.py`.

You have the option of specifying several parameters for the script using flags when you run it. These flags are:

- `-i` This specifies the input data file name.
- `-d` This specifies the dilution factor. It needs to be a number.
- `-c` This specifies the highest concentration used in the concentration gradient. It needs to be a number.
- `-s` This specifies the number of samples that the concentration gradient spans. It needs to be a number.
- `-a` This specifies the units that the script should label the x-axis It needs to be a string.
- `-n` This specifies whether the parameter n should be fit, or fixed. Options are `True` or `False`
- `-1` This specifies the name of the first experiment. It needs to be a string.
- `-2` This specifies the name of the second experiment. It needs to be a string.
- `-3` This specifies the name of the third experiment. It needs to be a string.
- `-4` This specifies the name of the fourth experiment. It needs to be a string.

For example: `python3 EC50.py -i CL2A_CL1A_BSA.txt -d 2 -c 1 -s 8 -a mg/mL -n False -1 CL2A -2 CL1A -3 CL2A_BSA -4 CL1A_BSA`

This tells the script that there are 8 samples that span from 1 mg/mL to 0.0078125 mg/mL. The fit will treat n fixed to 1. It will then label the figure and output files according to the names CL2A, CL1A, CL2A_BSA, and CL1A_BSA. The data is located in `CL2A_CL1A_BSA.txt`, which was output by Varioskan Lux.

You can view what these flags are in the terminal by entering `python3 EC50.py -h`.

These flags do not need to be used every time that the script is run. If they are not specified, they will take a default value. The default values set the max concentration to 3 mg/mL and the dilution factor to 3-fold.

| flag | default value |
| --- | --- |
| `-i` | `data.txt` |
| `-d` | 3 |
| `-c` | 3 |
| `-s` | 8 |
| `-a` | mg/mL |
| `-n` | False |
| `-1` | data set 1 |
| `-2` | data set 2 |
| `-3` | data set 3 |
| `-4` | data set 4 |

For example: `python3 EC50.py -d 10 -c 1` will set the concentration gradient to be 8 samples which span 1 mg/mL to 0.00000001 mg/mL. The unspecified flags will take on their default values listed in the above table.

You can run less than 8 samples if you would like. In this situation, you need to place your highest concentration samples in row A. Your lowest concentration will be placed into the corresponding row, depending on how many samples you have. You will then need to include the `-s` flag when you run the script.


### Output of the script

The script will place five tab-seperated `.txt` files and a `results.pdf` into the `results` directory. The tab-seperated text files can be directly opened in excel. Four of the five `.txt` files contain the concentrations, the average absorbance of the three replicates, and the standard deviation of the three replicates for the given experiment. These `.txt` files also contain the optimized values for the EC50, A, and n parameters. the fifth `.txt` file contains a table of the four fitted EC50 values. The `results.pdf` file contains two graphs of the normalized data and the normalized fits: one with a log scale x-axis and one without. Both graphs include the normalized error, which is propagated from the standard deviation of the three replicate measurements. The legend for these graphs contains the fitted EC50 values, rounded to 4 significant figures. The legends are labeled according to the `-1`, `-2`, `-3`, and `-4`  flags. The `results.pdf` can be loaded into illustrator so that you can change the names or colors of the curves, if you would like.

Once you have finished analyzing your data, you should move all the files out of  the `results` directory and save them else where on your computer. If not, subsequent runs of the script will overwrite all of the output files.
