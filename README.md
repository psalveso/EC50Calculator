# EC50 Calculator

This python script calculates EC50 values for the affinity of antibody sera towards an antigen. The script reads multiple `.txt` files produced by Varioskan Lux and performs a nonlinear least squares fit of the data sets within. The script outputs the results of the fits as text files and saves graphs of the results to a pdf file.

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

The script should handle `.txt` files output by Varioskan Lux, wherein data is places in a tab-separated text file mimicking the layout of a 96-well plate. The script will work with data outputted from Skanit Software 5.0, using the default export options. Prior to outputting the data from the instrument, it is critical that **your 96-well plate be laid out in a particular way for the script to work.**


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

**Your data file also needs to be named in a specific way for the script to work.** Your naming scheme should look like this: `PLATENUMBER_EXPERIMENTALINFO_EXPERIMENT1_EXPERIMENT2_EXPERIMENT3_EXPERIMENT4.txt`. When the script runs, it uses these values to label the output files. For example, whatever you have placed in the `EXPERIMENT1` position in the file name, will be used to label the graph containing that data set, etc...

You can name these whatever you like; however, you **cannot** include underscores: `_` anywhere else in the name. For example:

`Plate1_AGK-IV-200-6E10_2AT_1AT_2A_1A.txt` is a valid name.
`Plate1_AGK_IV_200_6E10_2AT_1AT_2A_1A.txt` is not a valid name.

### Running the script from the terminal

After cloning/forking/downloading the repository, you first need to place your data files output by the Varioskan Lux into the `input/` directory. The script can processes multiple files at once.

Navigate to the directory that contains the script using a terminal. The script is run by entering `python3 EC50.py`.

You have the option of specifying several parameters for the script using flags when you run it. These flags are:

- `-d` This specifies the dilution factor. It needs to be a number.
- `-c` This specifies the highest concentration used in the concentration gradient. It needs to be a number.
- `-s` This specifies the number of samples that the concentration gradient spans. It needs to be a number.
- `-a` This specifies the units that the script should label the x-axis It needs to be a string.
- `--fit_hill` This turns on fitting of the hill coefficient.
- `--no_fit_hill` This turns off fitting of the hill coefficient. Script defaults to this.
- `-m` This specifies the layout of the plate. Options are `True` (4 experiments, each with 3 replicate samples) or `False` (2 experiments, each with 4 replicate samples).

For example: `python3 EC50.py -d 2 -c 1 -s 8 -a mg/mL --no_fit_hill` or `python3 EC50.py -d 2 -c 1 -s 8 -a mg/mL` fit with hill = 1.0. `python3 EC50.py -d 2 -c 1 -s 8 -a mg/mL --fit_hill` will fit the hill coefficient

This tells the script that there are 8 samples that span from 1 mg/mL to 0.0078125 mg/mL. The fit will treat n fixed to 1. It will then label the x-axis of the output graphs with `mg/mL`,

If you have 10 plates that were set up using the same concentration gradient, then they can be run together. However, if those 10 plates contain 10 different concentration gradients, then you should process them one at a time: **you cannot currently specify individual flags for specific input files, if you are processing more than one at a time**.

You can view what these flags are in the terminal by entering `python3 EC50.py -h`.

These flags do not need to be used every time that the script is run. If they are not specified, they will take a default value. The default values set the max concentration to 3 mg/mL and the dilution factor to 3-fold.

| flag | default value |
| --- | --- |
| `-d` | 3 |
| `-c` | 3 |
| `-s` | 8 |
| `-a` | mg/mL |
| `-m` | True |

For example: `python3 EC50.py -d 10 -c 1` will set the concentration gradient to be 8 samples which span 1 mg/mL to 0.00000001 mg/mL. The unspecified flags will take on their default values listed in the above table.

You can run less than 8 samples if you would like. In this situation, you need to place your highest concentration samples in row A. Your lowest concentration will be placed into the corresponding row, depending on how many samples you have. You will then need to include the `-s` flag when you run the script. If you use this flag, every experiment on the plate needs to use the same number of samples. You cannot have one experiment with 8 samples, and three with only 4 samples, for example

As the script does the fit for each input data file in `input/`, a new window will appear showing you the graphed data. You need to close this window for the script to proceed to the next input file.

**A note on `-m`**: This switches the plate layout 2 experiments, with 4 replicates. The two experiments should be in rows (A, B, C, D) for experiment 1, and rows (E, F, G, H). The replicates for those experiments should be in the column. I.e. A1, B1, C1, D1 are the four replicates of the highest concentration sample in experiment 1... If you are using more than 8 samples in your experiments you **need** to use the `-s` flag when you execute the script, otherwise it will default to 8 sample. Your file naming scheme for you input data should look like this: `PLATENUMBER_EXPERIMENTALINFO_EXPERIMENT1_EXPERIMENT2.txt`.


### Output of the script

For each input data file you placed in `input/`, the script will place four tab-separated `.txt` files and a `results.pdf` into the `results/` directory. The tab-separated text files can be directly opened in excel. They contain the concentrations, the average absorbance of the three replicates, and the standard deviation of the three replicates for the given experiment. These `.txt` files also contain the optimized values for the EC50, A, and n parameters. The `results.pdf` file contains two graphs of the normalized data and the normalized fits: one with a log scale x-axis and one without. Both graphs include the normalized error, which is propagated from the standard deviation of the three replicate measurements. The legend for these graphs contains the fitted EC50 values, rounded to 4 significant figures. The legends are labeled according to the `EXPERIMENT#` strings in the input file names. The `results.pdf` can be loaded into illustrator so that you can change the names or colors of the curves, if you would like.

The script will also make a tab-separated `EC50table.txt` file. This will contain the EC50s for every sample from every input file you placed in `input/`. For example, if you place one input file into `input/`, the `EC50Table.txt` will contain only 4 samples and their respective EC50s. If you place 10 input files into `input/`, then the `EC50Table.txt` will contain 40 samples and their respective EC50s. The samples in this file will be labeled based on the name of the input files.

The script will not overwrite the `EC50Table.txt` file, instead it will just continue to add values to it. Therefore if you have multiple plates that you cannot process together because they require different flags, you can process them one-at-a-time and their EC50s will get aggregated in `EC50Table.txt`.

Once you have finished analyzing your data, you should move all the files out of  the `results` directory and save them else where on your computer. If not, subsequent runs of the script may overwrite all of the output files.
