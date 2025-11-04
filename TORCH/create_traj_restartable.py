###########################################################################################
# Parallel temperature, density trajectory extractor for Torch                            #
# The script will read all the particle files and write the time evolution of temperature #
#  and density profile for each particle and save it based on the particle tag            #
# This is a restartable script, as it loops through all the existing files at first       #
#  and only processing the remaining tags                                                 #
# To avoid OOM errors, rank 0 is kept free for only writing, and instead of deviding the  #
#  tags, we are deviding the particle files to other ranks.                               #        
# Make sure to change the path for FLASH _part_ files, and confirm that the assigned tag, #
#  temperature and density columns are correct based on your data                         #
#   ~krut patel 052325                                                                    #
###########################################################################################
import h5py
import glob
import numpy as np
from mpi4py import MPI
import os
from collections import Counter

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Step 1: Determine good output files
if rank == 0:
    file_rows = {}
    for fname in glob.glob("tempdens*.dat"):
        with open(fname, 'r') as f:
            file_rows[fname] = sum(1 for _ in f)
    row_counts = list(file_rows.values())
    dominant_count = Counter(row_counts).most_common(1)[0][0] if row_counts else None
    good_files = set(fname for fname, nrows in file_rows.items() if nrows == dominant_count)
else:
    good_files = None

good_files = comm.bcast(good_files, root=0)

# Step 2: Get list of FLASH _part_ files
if rank == 0:
    files = glob.glob("./../../*_part_*")
    files.sort()
else:
    files = None

files = comm.bcast(files, root=0)
nfiles = len(files)

# Step 3: Get number of particles
if rank == 0:
    with h5py.File(files[0], 'r') as p_file:
        array1 = np.transpose(p_file['tracer particles'])
        nparticles = array1.shape[1]
else:
    nparticles = None

nparticles = comm.bcast(nparticles, root=0)

# Step 4: Each worker loads its assigned _part_ files
if rank != 0:
    files_per_rank = [files[i] for i in range(rank - 1, nfiles, size - 1)]
    file_times = []
    file_data = []
    for file in files_per_rank:
        with h5py.File(file, 'r') as p_file:
            array1 = np.transpose(p_file['tracer particles'])
            array2 = np.asarray(p_file['real scalars'])
            particle_ids = array1[11].astype(int)       #tag column
            sort_indices = np.argsort(particle_ids)     
            array1 = array1[:, sort_indices]
            time = float(array2[1][1])
            file_times.append(time)
            file_data.append(array1)

# Step 5: Loop through each particle
for p in range(nparticles):
    tag = p + 1
    output_file = f"tempdens{tag}.dat"

    if rank == 0 and output_file in good_files:
        continue

    time_list = []
    temp_list = []
    dens_list = []

    if rank != 0:
        for fidx, data in enumerate(file_data):
            for i in range(data.shape[1]):
                if int(data[11][i]) == tag:             #tag column
                    time_list.append(file_times[fidx])
                    temp_list.append(data[12][i])       #temperature column
                    dens_list.append(data[1][i])        #density column
                    break

    time_array = comm.gather(time_list, root=0)
    temp_array = comm.gather(temp_list, root=0)
    dens_array = comm.gather(dens_list, root=0)

    if rank == 0 and output_file not in good_files:
        full_time = np.concatenate(time_array)
        full_temp = np.concatenate(temp_array)
        full_dens = np.concatenate(dens_array)

        sort_idx = np.argsort(full_time)
        full_time = full_time[sort_idx]
        full_temp = full_temp[sort_idx]
        full_dens = full_dens[sort_idx]

        np.savetxt(output_file, np.c_[full_time, full_temp, full_dens], fmt='%1.5e')
        print(f"{output_file} done!")

