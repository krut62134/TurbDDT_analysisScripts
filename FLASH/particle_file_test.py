import pandas as pd
import numpy as np
import glob
import h5py
import argparse

def get_data(file):
    """
    Loads HDF5 file, returns particle data, particle names, and time.
    (Using the function provided by you)
    """
    f = h5py.File(file ,"r")
    dset = list(f.keys())
    r_s = f['real scalars']
    i_r_p = f['particle names']
    df = pd.DataFrame(data = i_r_p, dtype = str)
    t_p = f['tracer particles']
    data = pd.DataFrame(data = t_p)
    data.sort_values(by = [11], ascending = True, inplace = True)
    time = r_s[1][1]
    f.close() # Added to prevent file handle leaks
    # returns the dataframe of particle fields and time of the particle file.
    return data, df, time

# --- Main Script Logic ---

# 1. Find and sort all particle files
# Using the path from your example script
file_pattern = "/scratch/09430/kpatel5/PRODUCTION/stdDensity/tDDT_sd_o12r32_hdf5_part*"
files = glob.glob(file_pattern)
files.sort()

if not files:
    print(f"No files found matching pattern: {file_pattern}")
    exit()

print(f"Found {len(files)} files. Checking time continuity...")

# 2. Initialize with the time from the very first file
first_file = files[0]
# Get time (which is the 3rd item, index 2)
last_time = get_data(first_file)[2] 
last_file = first_file

print(f"Starting at {first_file} with time {last_time}")

continuity_broken = False

# 3. Loop through the rest of the files
for file_path in files[1:]: # Start from the second file
    current_time = get_data(file_path)[2]
    
    # Check if the current time is less than the last time
    if current_time < last_time:
        print("\n--- TIME CONTINUITY BROKEN! ---")
        print(f"Previous File: {last_file}")
        print(f"Previous Time: {last_time}")
        print(f"Current File:  {file_path}")
        print(f"Current Time:  {current_time} (This is smaller!)\n")
        continuity_broken = True
    
    last_time = current_time
    last_file = file_path

if not continuity_broken:
    print("Check complete. All file times are in ascending order.")
else:
    print("Check complete. Time continuity breaks were found.")
