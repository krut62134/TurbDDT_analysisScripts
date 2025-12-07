import numpy as np
import matplotlib.pyplot as plt
import h5py
import pandas as pd
import os
from mpi4py import MPI
from matplotlib.lines import Line2D

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Configuration
particle_file = './../../tDDT_hd_o12r32_HLLC_Roe_hdf5_part_001372'
final_dir = './../src/'
iso_fuel = ['c12', 'o16']
iso_ime = ['si28', 's32', 'ca40']
iso_ige = ['fe54', 'fe56', 'ni58'] 
iso_ni56 = 'ni56'

# Rank 0 reads kinematics
if rank == 0:
    with h5py.File(particle_file, "r") as f:
        data = np.array(f['tracer particles'][:], dtype=float)
        df = pd.DataFrame(data, columns=np.arange(data.shape[1])).sort_values(by=11)
    tag_glob = df[7].astype(int).values
    v_cyl_glob = np.sqrt(df[9]**2 + df[10]**2).values / 1e5
    v_z_glob = df[11].values / 1e5
else:
    tag_glob = None
    v_cyl_glob = None
    v_z_glob = None

# Broadcast
tag_glob = comm.bcast(tag_glob, root=0)
v_cyl_glob = comm.bcast(v_cyl_glob, root=0)
v_z_glob = comm.bcast(v_z_glob, root=0)

# Split work
tag_local = np.array_split(tag_glob, size)[rank]
abunds_local = np.zeros((len(tag_local), 4)) # Fuel, IME, StableIGE, Ni56

for i, t in enumerate(tag_local):
    fpath = os.path.join(final_dir, f"out_{t}_final.dat")
    if os.path.isfile(fpath):
        with open(fpath) as f:
            for line in f:
                p = line.split()
                iso, mass = p[3].lower(), float(p[2])
                if iso in iso_fuel: abunds_local[i, 0] += mass
                elif iso in iso_ime: abunds_local[i, 1] += mass
                elif iso in iso_ige: abunds_local[i, 2] += mass
                elif iso == iso_ni56: abunds_local[i, 3] = mass

# Gather
abunds_gathered = comm.gather(abunds_local, root=0)

if rank == 0:
    abunds = np.concatenate(abunds_gathered)
    
    # RGB Calculation
    # abunds columns: 0=Fuel, 1=IME, 2=StableIGE, 3=Ni56
    total = np.sum(abunds, axis=1)
    total[total == 0] = 1e-30 
    
    f_fuel = abunds[:, 0] / total
    f_ime  = abunds[:, 1] / total
    f_ige  = abunds[:, 2] / total
    f_ni56 = abunds[:, 3] / total

    # Map to RGB: R=IGE, G=Fuel, B=IME
    rgb_data = np.zeros((len(tag_glob), 3))
    rgb_data[:, 0] = f_ige
    rgb_data[:, 1] = f_fuel
    rgb_data[:, 2] = f_ime
    
    # Ni56 Override (White)
    rgb_data[f_ni56 > 0.5] = 1.0
    
    # Plotting
    plt.style.use('dark_background')
    
    fig, ax = plt.subplots(figsize=(10, 10)) 
    
    ax.scatter(v_cyl_glob, v_z_glob, c=rgb_data, s=1, alpha=0.6)
    ax.set_box_aspect(2)

    ax.set_xlabel('Radial Velocity $v_{r}$ (km/s)')
    ax.set_ylabel('Velocity in z direction $v_z$ (km/s)')
    ax.set_title('tDDT Ejecta Structure')
    plt.grid(True, alpha=0.3)

    # Custom Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Fuel',
               markerfacecolor='green', markersize=8, markeredgewidth=0),
        Line2D([0], [0], marker='o', color='w', label='IMEs',
               markerfacecolor='blue', markersize=8, markeredgewidth=0),
        Line2D([0], [0], marker='o', color='w', label='Stable IGEs',
               markerfacecolor='red', markersize=8, markeredgewidth=0),
        Line2D([0], [0], marker='o', color='w', label=r'$^{56}$Ni > 0.5',
               markerfacecolor='white', markersize=8, markeredgewidth=0)
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=True, facecolor='black', edgecolor='gray')
    
    plt.savefig('tDDT_2D_structure_cyl_rgb.png', dpi=1000, bbox_inches='tight')
