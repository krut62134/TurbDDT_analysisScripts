#########################################################################
# Produces structure plot (isotopes mass fraction vs velocity) from     # 
#  the Torch output and last particle file                              #
# The velocity range with a small buffer is devided by the number       #
#  of bins and the isotope mass fraction is averaged for all the        #
#  particles that lie in each bin. The bin velocity is the central      #
#  mean velocity of the bin edges                                       #
# You may change the isotopes based on your needs                       #
# You should change the final particle file path and name, as well      #
#  as the source directory path from Torch                              #
# Before running the script, make sure the columns for position,        #
#  velocities and tag are correct based on your data                    #
#   ~krut patel 051325                                                  #
#########################################################################
import numpy as np
import matplotlib.pyplot as plt
import h5py
import pandas as pd
import os
from mpi4py import MPI
from scipy.stats import binned_statistic

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Path to the last particle file from FLASH
particle_file = './../../tDDT_hd_o12r32_HLLC_Roe_hdf5_part_004885'
# Path to the source directory from Torch where your final abundances are saved
final_dir = './../src/'
# Select isotopes for the structure plot
isotopes = ['ni56', 'ni58', 'fe54','si28', "s32", "ca40", "mn55"]

if rank == 0:
    with h5py.File(particle_file, "r") as f:
        tracer_data = np.array(f['tracer particles'][:], dtype=float)
        df = pd.DataFrame(tracer_data, columns=np.arange(tracer_data.shape[1]))
        df.sort_values(by=11, ascending=True, inplace=True)
    x = df[6]
    y = df[7]
    z = df[8]
    velx = df[15]
    vely = df[16]
    velz = df[17]
    tag = df[11].astype(int)
    v_r = (velx*x + vely*y + velz*z) / (np.sqrt(x**2 + y**2 + z**2) * 1e5)  # Convert cm/s to km/s
else:
    tag = None
    v_r = None

# Broadcast data to all ranks
tag = comm.bcast(tag, root=0)
v_r = comm.bcast(v_r, root=0)

local_tags = np.array_split(tag, size)[rank]
abundance_dict_local = {iso: np.zeros(len(tag)) for iso in isotopes}
tag_to_index = {t: i for i, t in enumerate(tag)}

for t in local_tags:
    fpath = os.path.join(final_dir, f"out_{t}_final.dat")
    if not os.path.isfile(fpath):
        continue
    with open(fpath) as f:
        for line in f:
            parts = line.strip().split()
            iso = parts[3].lower()
            if iso in abundance_dict_local:
                i = tag_to_index[t]
                abundance_dict_local[iso][i] = float(parts[2])

abundance_dict = {iso: np.zeros(len(tag)) for iso in isotopes}
for iso in isotopes:
    comm.Reduce(abundance_dict_local[iso], abundance_dict[iso], op=MPI.SUM, root=0)

if rank == 0:
    plt.figure(figsize=(8, 6))

    # Use actual data range with a small buffer
    v_min = max(0, v_r.min() - 10)
    v_max = v_r.max() + 10

    bins = np.linspace(v_min, v_max, 50)        #change the number for total bins
    bin_centers = 0.5 * (bins[1:] + bins[:-1])

    for iso, abundance in abundance_dict.items():
        mean_abundance, _, _ = binned_statistic(v_r, abundance, statistic='mean', bins=bins)
        plt.semilogy(bin_centers, mean_abundance, label=rf'${iso}$')

    plt.xlabel('Radial Velocity (km/s)')
    plt.ylabel('Isotope Mass Fraction')
    plt.title(r'tDDT - high central density (6 x 10**9 g/cm**3) ejecta structure')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('tDDT_hcd_structure', dpi=1000)
