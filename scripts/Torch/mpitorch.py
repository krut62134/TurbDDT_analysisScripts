###This script can be used to process multiple trajectories in Torch using multiple cores. 
### This will give one trajectory to every core and the remainder will be given to cores as they free up. 
### By: Sudarshan Neopane

import numpy as np
import os
import sys
from mpi4py import MPI

comm = MPI.COMM_WORLD

# Rank of the processor
my_rank = comm.Get_rank()

# No. of processors to use
nprocs = comm.Get_size()

#No. of particles to process

nfiles = int(sys.argv[1])  ##Added this to get the number of files to be processed through the command line -K

# Determine the no of files to be provided to each processor
remainder = nfiles % nprocs
#print(remainder)
quotient = (nfiles - remainder) / nprocs
#print(quotient)

# Array of number of files for rach processor
files_array = quotient * np.ones(nprocs)
#print(files_array)

# No of files to be read by each processor
for j in range(remainder):
    files_array[j] = files_array[j] + 1
#print(files_array)

for i in range(int(files_array[my_rank])):
        command = "./torch -i " + str(my_rank + 1) + \
                  " -f " + str(my_rank + 1) #This will ensure every run of Torch processes a single trajectory such that the core frees up to take in another trajectory -K
        print(command)
        os.system(command)
        my_rank = my_rank + nprocs

MPI.Finalize
