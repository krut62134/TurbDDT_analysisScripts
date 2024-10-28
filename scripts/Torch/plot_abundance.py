## This is a modified version of Abdullah Alshaffi's script abundance_distribution.py !kbhargava
## This script can be used for models that have lost particles 

import numpy as np
import matplotlib.pyplot as plt
import h5py
import glob
import pandas
import re
import colorsys

plt.style.use('dark_background')
plt.rcParams["figure.figsize"] = (12,20)

#reading the last particle file used in TORCH to get particle data
file = h5py.File("/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/kpatel29/runs/runs_autoddt_thermalreact/run_Torchex/tDDT_hdf5_part_000695",'r')
file.keys()

#loading data of tracer particle
particle_properties = file["particle names"][:]
particle_values = file["tracer particles"][:]

particle_tag = particle_values[:, 11]
posx = particle_values[:, 6] # col 13 is posx in the tracer particle data
posy = particle_values[:, 7] # col 14 is posy in the tracer particle data

posx = np.array( [x for _,x in sorted(zip(particle_tag,posx))] )
posy = np.array( [x for _,x in sorted(zip(particle_tag,posy))] )

white_list = []
green_list = []
blue_list = []
red_list = []

for i in sorted(particle_tag.astype(int)):
    f = 'out_' + str(i) + '_final.dat'
    file = open(f,'r')
    abundances = file.readlines()

    # To append the atom. baryon, and mass fraction to empty lists
    atom_number=[] # to append the atomic number from the abundance files
    baryon_number=[] # to append the baryon number from the abundance files
    mass_fraction=[] # to append the mass fraction from the abundance files

    ni56 = 0
    low = 0
    ime = 0
    ige = 0

    for w in abundances:
        line = w.split()
        atom_number.append(int(line[0]))
        baryon_number.append(int(line[1]))
        mass_fraction.append(float(line[2]))

    for j in range(np.size(atom_number)):
        if(baryon_number[j] <= 16):
            low = low + mass_fraction[j]
        elif (baryon_number[j] > 16 and baryon_number[j] <= 40):
            ime = ime + mass_fraction[j]
        elif (baryon_number[j] > 40 and (atom_number[j] != 28 or baryon_number[j] != 56)):
            ige = ige + mass_fraction[j]
        else:
            ni56 = ni56 + mass_fraction[j]

    ni56 = ni56 / (ni56 + low + ime + ige)
    low = low / (ni56 + low + ime + ige)
    ige = ige / (ni56 + low + ime + ige)
    ime = ime / (ni56 + low + ime + ige)
    
    white_list.append(ni56)
    green_list.append(low)
    blue_list.append(ime)
    red_list.append(ige)

#To get gradient in colour shading
color = np.transpose([white_list, green_list, blue_list, red_list])

plt.scatter(posx, posy, s = [5], c = color, alpha = 0.5)
plt.xticks(fontsize = 30)
plt.yticks(fontsize = 30)
plt.xlabel(r"r", fontsize = 35)
plt.ylabel(r"z", fontsize = 35)
plt.text(1.8, 1.9, 'Ni56', fontsize=35,  color='white')
plt.text(1.8, 1.7, 'A <= 16', fontsize=35,  color='green')
plt.text(1.8, 1.5, 'IME', fontsize=35,  color='blue')
plt.text(1.8, 1.3, 'IGE', fontsize=35,  color='red')
plt.tight_layout()
plt.savefig("abundance_ratios_ddt.jpg")
    
