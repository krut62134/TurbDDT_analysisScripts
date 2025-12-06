#read and print the data from particle files
# ~vmehta
import pandas as pd
import h5py

def get_data(file):
    f = h5py.File(file ,"r")
    dset = list(f.keys())
    r_s = f['real scalars']
    i_r_p = f['particle names']
    df = pd.DataFrame(data = i_r_p, dtype = str)
    t_p = f['tracer particles']
    data = pd.DataFrame(data = t_p)
    data.sort_values(by = [11], ascending = True, inplace = True)
    return data, df, r_s[1][1]

# Load and print data from the specific file
file = "./../../tDDT_hd_o12r32_HLLC_Roe_hdf5_part_004500"
print(get_data(file))
#data, time, data1, data2 = get_data(filename)
#print(data1)
#print("Time:", time)
#print(data2)
#print(data)

