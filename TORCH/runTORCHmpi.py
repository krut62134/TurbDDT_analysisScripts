##################################################################
# This script can be used to process multiple trajectories in Torch using multiple cores. 
# This will give one trajectory to every core and the remainder will be given to cores as they free up. 
#  By: Sudarshan Neopane
#---
# Added randomization in trajectory selection, allows us to do small sample tests
# This same script can also be used to restart the runs
# Make sure to change the total number of particles in your model. Run the script in the src folder
#  ~krut patel 111824
##################################################################
import numpy as np
import os
import sys
import re
import glob
from mpi4py import MPI

# Get the processed particles final files
files = glob.glob("./*final.dat")
files.sort()

proc_files = []  # To store the processed particle tags
proc_tag = []

for f in files:
    head_tail = os.path.split(f)
    proc_files.append(head_tail[1])
    s = re.findall(r"\d+", head_tail[1])
    proc_tag.append(s[0])

left_tag = []  # To store unprocessed particle tags

# Open in write mode if you want to overwrite any previous data
with open('left_tags.dat', 'w') as f:
    for i in range(1, 100024):      #edit here for total particles
        if str(i) in proc_tag:
            continue
        else:
            left_tag.append(i)
            f.write(str(i) + "\n")

# Initialize MPI variables
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nprocs = comm.Get_size()

# --- Shuffle left_tag randomly --- #
if rank == 0:
    np.random.shuffle(left_tag)
# Broadcast the same shuffled list to all processes
left_tag = comm.bcast(left_tag, root=0)

# Distribute the tasks among the processors
nfiles = len(left_tag)
remainder = nfiles % nprocs
quotient = (nfiles - remainder) // nprocs  # use integer division

# Create an array holding the number of files each process should handle
files_array = quotient * np.ones(nprocs, dtype=int)
for j in range(remainder):
    files_array[j] += 1

# Instead of modifying rank, use an index variable starting at the rank offset
index = rank
for _ in range(files_array[rank]):
    tag = left_tag[index]
    command = "./torch -i " + str(tag) + " -f " + str(tag)
    os.system(command)
    index += nprocs
