import pandas as pd
import numpy as np
import glob
import h5py
import argparse

def get_data(file):
    f = h5py.File(file ,"r")
    dset = list(f.keys())
    r_s = f['real scalars']
    i_r_p = f['particle names']
    df = pd.DataFrame(data = i_r_p, dtype = str)
    t_p = f['tracer particles']
    data = pd.DataFrame(data = t_p)
    data.sort_values(by = [11], ascending = True, inplace = True)
    return data, df, r_s[1][1] # returns the dataframe of particle fields and time of the particle file.

file = "./data/tDDT_hdf5_part_001516"
print_data=get_data(file)
print(get_data(file))
print(print_data[0].to_string())



