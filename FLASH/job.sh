#!/bin/bash
#----------------------------------------------------
# Sample Slurm job script
#   for TACC Stampede3 SKX nodes
#
#   *** MPI Job in SKX Queue ***
# 
# Last revised: 23 April 2024
#
# Notes:
#
#   -- Launch this script by executing
#      "sbatch skx.mpi.slurm" on Stampede3 login node.
#
#   -- Use ibrun to launch MPI codes on TACC systems.
#      Do not use mpirun or mpiexec.
#
#   -- Max recommended MPI ranks per SKX node: 48
#      (start small, increase gradually).
#
#   -- If you're running out of memory, try running
#      fewer tasks per node to give each task more memory.
#
#----------------------------------------------------

#SBATCH -o %j.o       # Name of stdout output file
#SBATCH -e %j.e       # Name of stderr error file
#SBATCH -p skx-dev             # Queue (partition) name
#SBATCH -N 8               # Total # of nodes 
#SBATCH --ntasks-per-node=48              # Total # of mpi tasks
#SBATCH -t 02:00:00        # Run time (hh:mm:ss)

# Other commands must follow all #SBATCH directives...

module list
pwd
date

# Launch MPI code... 
scontrol show hostnames $HOSTLIST > hosts.txt
mpiexec -f hosts.txt -n 768 -ppn 48 ./flash4
#ibrun ./flash4 
