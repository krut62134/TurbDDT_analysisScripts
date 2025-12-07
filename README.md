# SNIa_turbDDT_analysis

This repository contains the scripts for analysis and post-processing of the SNIa_turbDDT project. Refer to the documentation below for the post-processing workflow.

## FLASH run analysis


## TORCH

### Post-processing workflow

After the supernova ejecta has reached homologous expansion, follow the workflow below to calculate the nucleosynthetic yields and the synthetic spectra.

A thorough documentation for the initial modifications in the torch source code from [Pranav Dave](https://www.linkedin.com/in/pdave07/) and [Khanak Bhargava](https://www.linkedin.com/in/khanakb/) can be found here:

[TORCH: Initial Changes](https://novastella.org/wiki/index.php?title=Light_Curves_and_Spectra_of_Type_Ia_Supernovae_using_SuperNu#Loop_Torch_over_multiple_trajectories)

This repository contains some additional modifications in the torch source code as below:

- line 251: `tol = 1.0d-5`
- line 23412: `temp = max(5.0d8,min(temp,2.0d10))`

The first change was made after doing a convergence study on the TORCH yields. The study can be found in `TORCH/convergence` in this repo. The second change is specifically for the single degenerate model, where temperatures can reach higher than 1 x 10^9 K. At such high temperatures, the TORCH calculations become invalid. Temperatures near 1 x 10^9 K are enough to reach nuclear statistical equilibrium (NSE) before the ejecta cools down, even for our highest central density progenitor. This change adds a ceiling to the temperature. This change adds a ceiling to the temperature values.

File structure:

```
TORCH/
├── convergence/
├── scripts/
└── src/
```

### 1. Trajectory Generation

First, create a new folder in the TORCH directory named `history`. Copy the `create_traj.py` script into this history directory.

Before running the script, you must update it to match your simulation data:

- Change the path of the particle file to point to your FLASH simulation's final particle file.
- Update the column indices for temperature, density, and particle tag to match your particle file structure.

**Tip:** You can use the `test.py` script to check the structure of your particle file.

Once configured, run the script:

```bash
python3 create_traj.py
```

This is a serial code that reads all particle files and writes the temperature and density trajectories. The process should not take longer than 2 hours.

**Note:** If you encounter memory issues, use the `create_traj_mpi_restartable.py` script instead. You will need to update the column indices and file paths in this script as well. Execute it using the number of processes available to you. You can also increase the number of nodes to increase memory. 

### 2. Compilation

Navigate to the `src` directory. Open `torch.f` and go to line 17460. Change the path for the trajectory files to point to your history directory.

Ensure the compiler in the Makefile matches your system's configuration. Based on your machine, you might need to choose between the compilers `ifort` and `gfortran`. Compile the code:

```bash
make
```

This will generate the `torch` executable.

### 3. Execution

Copy the `runTORCHmpi.py` script to the src directory. Update the following before running the script:
 - total number of particles

**Note:** This number might vary slightly between runs even with the same progenitor. You can find the total count in the log file or by checking the particle files with `test.py`. Make sure you update the column for tag based on your data structure.

Run the script using MPI:

```bash
mpirun -n <number of processes> python3 runTORCHmpi.py
```

**Scalability and Restartability:** TORCH is inherently a serial code. The `runTORCHmpi.py` script processes one trajectory per MPI thread, making the execution embarrassingly parallel and almost 100% scalable. This script uses mpi4py for parallalization. You can try OpenMP with a C code to create an exicutable for running TORCH in parallel. It's a better option then MPI

If all particles are not processed in a single job submission, simply resubmit the job without changes. The script checks the output files and automatically compiles a list of unprocessed trajectories to handle in the subsequent run.

After all the trajectories are processed, you will have `out_<tag>_final.dat` files for each trajectory associated with its particle tag. The shape of each file should be the same, containing 489 rows representing 489 isotopes, and 4 columns representing baryon number, atomic number, mass fraction, and the name of the isotope. These are your final nucleosynthetic yields. The sum of all mass fractions for each final file should be equal to 1.

### 4. Analysing the yields

Use the `average.py` script to calculate the total final yields, which simply calculates the average yields from all the trajectories and outputs the data in the `meanAbundances.dat` file. Change the path for the final TORCH output to your TORCH run, and change the total mass of your ejecta to get accurate calculations in solar mass. Run the script with the following command:

```bash
mpirun -n <total processes> python3 average.py
```

There are multiple ways you can visualize the ejecta structure. The most common method is to plot a 1D structure. You can use the `structure.py` script for that. It converts the ejecta from 3D Cartesian space into 1D Spherical space, and then maps it into a velocity mesh. Before using this script, make sure you have provided the correct paths for your final particle file from FLASH simulation, and your TORCH run for that simulation. Also adjust the column indices for position x, y, z; velocity vx, vy, vz and the particle tag. Choose the isotopes you want to plot by adding them in the isotopes array. This is also an MPI script, so make sure you use mpirun to execute it.

![Alt text](./misc/tDDT_1D_structure.png)
*Figure 1: The plot above is for a standard central density progenitor. This is the simplest and most compact way to visualise the ejecta structure. Since the ejecta has reached free expansion, we can analyse the position of the products of the explosion from its radial velocity. As seen in the plot, we can clearly see a Ni56 hole within the core, dominated by the stable iron group elements (IGEs). These are the products of high neutronization inside the core of the White Dwarf due to high density burning. We see most of the ejecta beyond that is heavily dominated by Ni56, the most abundant products of NSE. This particular isotope is responsible for the bright nature of the SNe Ia. The final layer of the ejecta are the products of Quasi-Statistical Equilibrium (QSE) and unburnt C/O. We can also see a faint layer of Ca40 between the Ni56 and Si28.*

Another way to visualize the structure is to plot it in 3D. You can use the `interactive_structure.py` script for that. This script outputs an HTML file containing an interactive plot of all the particles in a 3D velocity space. The plot contains IGEs, unburnt C/O, and IMEs in RGB fashion, and ni56 > 0.5 in strict white. So brown, for example, would mean the particle has mostly IGEs and some unburnt C/O. Again, before running the script, make sure your paths for the final particle file from the FLASH simulation and the corresponding TORCH run are correct. Also, change the column index for velocities and tag according to your data. This script is also executed with mpirun.

<a plot showing sample 3D structure plot with description.>

## SuperNu

This next stage of the pipeline is calculating the synthetic light curve using SuperNu. Before moving forward, go through the documentation in the link provided below to setup SuperNu for both serial and parallel mode. There are also sample data available for the classic W7 model for Type Ia supernovae originally developed by Nomoto, Thielemann, and Yokoi in 1984. You can use that to test your SuperNu installation.

[SuperNu: Code Setup Instructions](https://novastella.org/wiki/index.php?title=Light_Curves_and_Spectra_of_Type_Ia_Supernovae_using_SuperNu#Code_Setup_Instructions)

Once everything is set up, you will have to convert the TORCH output yields into a SuperNu input string. This is a two-stage process. SuperNu accepts elemental abundances rather than isotopic abundances.

### 1. Isotopic to Elemental Conversion

The first stage is to convert the isotopic abundances into elemental abundances. Provide the path to your TORCH run in the `isotopicToElemental_mpi.py` script, and run it with the following command:

```bash
mpirun -n <number of processes> python3 isotopicToElemental_mpi.py
```

This will create a directory named `elemental` where you execute the script, and save the converted elemental abundances for all the trajectories from your TORCH run in it.

### 2. Generating Input String

Once this stage is complete, open the `Torch_to_Supernu.py` script, and change the following:

- Path to your final particle file from the FLASH simulation
- Path to your elemental abundance data
- Path to your TORCH run
- Final mass of your ejecta, which can be found in the global data of your FLASH run
- Total number of particles in your FLASH simulation
- Column index for position x, y, z; velocity vx, vy, vz and tag based on your particle file data structure

You can adjust the number of bins for the input string for SuperNu according to your needs. The default 128 bins provide sufficient resolution without making the SuperNu runs unnecessarily expensive. Run the script with the following command:

```bash
mpirun -n <number of processes> python3 Torch_to_Supernu.py
```

Once the script is done, you will get `input.str` as an output. This file will have 51 columns. The first two columns are the velocity of the right edge of the bins and mass, followed by the elemental abundances from hydrogen (h) to technetium (tc). The last 6 columns are Ni56, Co56, Fe52, Mn52, Cr48, and V48. SuperNu only includes the unstable alpha-chain isotopes Ni56, Fe52, and Cr48, and the products of their decay chain. Thus, only these isotopes are included in the input string.

### 3. Calculating Spectra

You can now use the `input.str` to calculate the synthetic spectra. There is a sample `input.par` parameter file provided in the `SuperNu/sample` directory. This sample file is configured for 1D spherical geometry with 128 bins, which you have. When you run SuperNu, it will calculate the total mass of the ejecta and the Ni56 mass. If everything went well, these masses will match your FLASH simulation and the TORCH output.

## SNID

The Supernova Identification Code, short for SNID, is made by Stephane Blondin for classification of the spectra. It is the same tool used by observers. We will use it to classify our synthetic spectra to observed events.

From the SuperNu run you will get multiple files as an output. The ones you need for this stage of the pipelines are `output.flx_grid` and `output.flx_luminos`. The `flx_luminos` file contains the spectral flux for each timestep of the SuperNu run. The `flx_grid` file contains the wavelength grid for the flux and the epoch or timestep that corresponds to the rows of the luminos file. These timesteps can be considered as fractional epochs of the synthetic spectra.

### 1. Preparing Spectra

We will use the script `SuperNu_to_SNID_v2.0.py` written by [Mckenzie Ferrari](https://www.linkedin.com/in/mckenzie-ferrari/). Execute the script with this command:

```bash
python3 SuperNu_to_SNID_v2.0.py
```

Upon execution, you will be prompted with these two questions:

```
Enter file name for WAVELENGTHS (i.e. __grid):
Enter file name for FLUX/LUMINOSITY (i.e. __luminos):
```

To which you will provide the location of the `flx_grid` and `flx_luminos` file of your SuperNu run. The script will then calculate the epoch for peak brightness and prompt you with the following:

```
Peak brightness found at LINE xx out of yy
Would you like to use this line at peak brightness? (Y/n):
```

Answer with 'Y' if you want the spectra for the epoch with peak brightness, and 'n' if you want the spectra for some other epoch. Read the `flx_grid` file to see which line corresponds to which fractional epoch. Once done, it will ask you to provide a name of your output file, to which you can input the name according to your epoch choice.

### 2. Building SNID

Now that you have the spectra you want to classify, you will have to build SNID first. Dr. Robert Fisher has made a very easy to use docker version of the SNID code. The link to that repository is provided below.

[https://github.com/rtfisher/snid_docker](https://github.com/rtfisher/snid_docker)

Follow the instructions there to build SNID on your device. Once done, you can run SNID in a local directory containing your spectra. Once you're in SNID, edit the `snidmore.f` code in the source directory to change the path of the template directory to yours. It will have the path for Dr. Blondin's device by default. Then follow the commands below to remake SNID.

```bash
make clean
make
make install
```

### 3. Running SNID

That's it! You can now classify your synthetic spectra using SNID. You can use the base command below to run SNID.

```bash
./snid forcez=0.0 wmin=2500 wmax=10000 ./localdir/your_spectra.dat
```

`forcez=0.0` is an important flag used to force the redshift of the synthetic spectra to 0. SNID will prompt you with a question `Do you want to enter a new redshift ? ( y / n ) [ n ]:` if you don't add the flag beforehand. You can enter 'y' and set the redshift to 0.0 later.

`wmin` and `wmax` flags are used to set bounds of the wavelength of the spectra. Almost all the observed spectra are in the range of 2500 to 10000 Angstrom, so this is a safe choice.

If your synthetic spectra matches any observed events with `rlap > 5`, it will open a pgplot window where you can see the respective matches of your model with the observed events in the template. If not, you will be prompted with:

```
Enter a new (1) redshift; (2) zfilter; (3) rlapmin; (4) lapmin; or (q)uit:
```

You should choose number 3, and set rlap to a lower value, e.g., 3.0.

To extract any matches, you can either click the PS button which will save the image as a .ps file, or click the ASCII button that will save the matching event as a data file. You can later use these data files to make combined plots of multiple spectra. By default, when you run snid for any synthetic spectra, it will generate a data file containing the information on all the events in the template directory and how it compares against your synthetic spectra. You can use it to check the rlap score for any observed event. A match is a good match if `|z - zuser| < zfilter`, where z is the redshift of the observed event and zuser is the redshift of your synthetic spectra (0.0). zfilter is set to 0.02 by default.

### Troubleshooting

If you come across any errors while saving the ps file, considering these drivers in your driver list in the source code, and rebuild it using the make commands given above.

```
AQDRIV 0 /AQT       AquaTerm.app under Mac OS X             C        <=== ONLY FOR MAC OSX!
GIDRIV 1 /GIF       GIF-format file, landscape
GIDRIV 2 /VGIF      GIF-format file, portrait
LXDRIV 0 /LATEX     LaTeX picture environment
PSDRIV 1 /PS        PostScript printers, monochrome, landscape  Std F77
PSDRIV 2 /VPS       Postscript printers, monochrome, portrait   Std F77
PSDRIV 3 /CPS       PostScript printers, color, landscape   Std F77
PSDRIV 4 /VCPS      PostScript printers, color, portrait    Std F77
TTDRIV 4 /GTERM     GTERM Tektronix terminal emulator       Std F77
TTDRIV 5 /XTERM     XTERM Tektronix terminal emulator       Std F77
WDDRIV 1 /WD        X Window dump file, landscape
WDDRIV 2 /VWD       X Window dump file, portrait
XWDRIV 1 /XWINDOW   Workstations running X Window System    C
XWDRIV 2 /XSERVE    Persistent window on X Window System    C
```

You can check out the complete documentation of SNID from the link below:

[SNID documentation](https://people.lam.fr/blondin.stephane/software/snid/howto.html)
