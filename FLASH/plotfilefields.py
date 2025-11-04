import yt
import glob
import numpy as np
import os

# Load the HDF5 file using yt
ds = yt.load("/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/runs/run_1a_mxb250_autoddt_thermalreact/tDDT_1a_hdf5_plt_cnt_000555")

    # Print the list of fields
print(ds.field_list)

