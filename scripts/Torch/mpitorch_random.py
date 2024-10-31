import numpy as np
import os
import sys
from mpi4py import MPI

comm = MPI.COMM_WORLD

# Rank of the processor
my_rank = comm.Get_rank()

# Number of processors to use
nprocs = comm.Get_size()

# Number of trajectories (files) to process
nfiles = int(sys.argv[1])

# Fixed random seed for reproducibility
seed = 42
np.random.seed(seed)

# Generate a list of trajectory indices from 1 to nfiles and shuffle them
indices = np.arange(1, nfiles + 1)
np.random.shuffle(indices)

# Distribute files among processors
remainder = nfiles % nprocs
quotient = (nfiles - remainder) // nprocs

# Array indicating the number of files for each processor
files_array = quotient * np.ones(nprocs, dtype=int)

# Distribute remainder files to some processors
for j in range(remainder):
    files_array[j] += 1

# Get the starting and ending index for the current processor
start_index = sum(files_array[:my_rank])
end_index = start_index + files_array[my_rank]

# Each processor processes its portion of the shuffled indices
for i in range(start_index, end_index):
    file_number = indices[i]
    command = f"./torch -i {file_number} -f {file_number}"
    print(command)
    os.system(command)

MPI.Finalize()

