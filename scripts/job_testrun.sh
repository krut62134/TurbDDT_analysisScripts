#!/bin/bash
#SBATCH -n 128
#SBATCH --partition=umd-cscdr-cpu  # Partition
#SBATCH --mem=250G # 250 GB
#SBATCH -t 200  # Job time limit
#SBATCH -o %j.o  # %j = job ID # Name of stdout output file
#SBATCH -e %j.e           # Name of stderr error file
#SBATCH --mail-user=kpatel29@umassd.edu
#SBATCH --mail-type=all    # Send email at begin and end of job


module list
pwd
date

# Launch MPI code..
srun -n 120 python3 ./slice_plot_mpi.py
# ---------------------------------------------------


