### This script will find the particles that were not processed in the first job 
### Write the their particle tags in a file called 'left_tags.dat'
### Then process the remainind particles only, in parallel !kbhargava

import numpy as np
import os
import sys
import re
import glob
from mpi4py import MPI


##Get the processed particles final files
files = glob.glob("/scratch/07441/kbhargav/DEF2_STD_torch/*final.dat")
files.sort()

proc_files=[] # To store the processed particle tags
proc_tag = []

for i in range(len(files)):
        head_tail=os.path.split(files[i])
        proc_files.append(head_tail[1])
        string = proc_files[i]
        s = re.findall(r"\d+",string)
        #s.group(0)
        #print(s)
        proc_tag.append(s[0])

left_tag = [] # To store unprocessed particle tags

f = open('left_tags.dat','a')
for i in range(1,9992): # Change upper limit according to the total no. of particles
        if str(i) in proc_tag:
                continue
        else:
                left_tag.append(i)
                f.write(str(i))
                f.write("\n")
f.close()


## Now run torch to preocess unprocessed particle tags
comm = MPI.COMM_WORLD

# Rank of the processor
my_rank = comm.Get_rank()

# No. of processors to use
nprocs = comm.Get_size()

# No. of trajectory files to be procssed	
nfiles = len(left_tag)

remainder = nfiles % nprocs
quotient = (nfiles - remainder) / nprocs

files_array = quotient * np.ones(nprocs)

for j in range(remainder):
	files_array[j] = files_array[j] + 1

for i in range(int(files_array[my_rank])):
	command = "./torch -i " + str(left_tag[my_rank]) + " -f " + str(left_tag[my_rank])
	os.system(command)
	my_rank = my_rank + nprocs
