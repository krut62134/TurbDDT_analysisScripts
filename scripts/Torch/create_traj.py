### This script will read data from FLASH particle files and 
### create '.dat' trajectory files for Torch input
### Each file will have 3 columns - time, temp, and dens !kbhargava
### Note: This script will only work for models that do not lose particles

import h5py
import glob
import numpy as np

#Give path to particle files
#files = glob.glob("/work/07441/kbhargav/stampede2/puredet2/pure_det_hdf5_part_00[0-4][0-9][0-9][0-9]")
files =glob.glob("rot_flame_det_split_highdens_hdf5_part_*")
files.sort()

#Getting total number of particles from the first file
p_file = h5py.File(files[0],'r')
dset = p_file['tracer particles']
array1 = np.transpose(dset)
nparticles = array1.shape[1]

#Getting total number of files
nfiles = len(files)

#Creating arrays to store data
time = np.zeros([nparticles,nfiles], dtype = float)
temp = np.zeros([nparticles,nfiles], dtype = float)
dens = np.zeros([nparticles,nfiles], dtype = float)

#Reading data from particle files
for f,file in enumerate(files):
	p_file = h5py.File(file,'r')
	dset = p_file['tracer particles']
	array1 = np.transpose(dset)
	array2 = np.asarray(p_file['real scalars'])
	for i in range(nparticles):
        	ind = int(array1[11][i]) - 1
        	time[ind][f] = float(array2[1][1])
        	dens[ind][f] = float(array1[1][i])
        	temp[ind][f] = float(array1[12][i])
	p_file.close()

#Creating .dat trajectory files for Torch
for p in range(nparticles):
	history = "tempdens" + str(p+1) + ".dat"
	np.savetxt(history,np.c_[time[p],temp[p],dens[p]], fmt='%1.5e')
