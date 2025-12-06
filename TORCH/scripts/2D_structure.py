#####################################################################################
# To visualise the structure of the ejecta from turbulent DDT models in all         #
#  three 2D velocity space.                                                         #
# Plots IGEs, unburnt C/O, IMEs in RGB fashion and ni56 > 0.5 in strict white.      #
# So brown for example would mean the particle has mostly IGEs and some unburnt C/O #
#   ~krut patel 110425                                                              #
#####################################################################################

import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches # For the custom legend
from mpi4py import MPI
import os

# -------------------------------------------------------------------------
# PART 1: MPI SETUP & DATA LOADING (Unchanged)
# -------------------------------------------------------------------------
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

particle_file = './../../tDDT_hd_o12r32_HLLC_Roe_hdf5_part_004885'
final_dir = './../src/'

# Load particle data on rank 0
if rank == 0:
    print("Rank 0: Loading HDF5 particle data...")
    with h5py.File(particle_file, "r") as f:
        tracer_data = np.array(f['tracer particles'][:], dtype=float)
        df = pd.DataFrame(tracer_data, columns=np.arange(tracer_data.shape[1]))
        df.sort_values(by=11, ascending=True, inplace=True)
    
    velx = df[15].values / 1e8  # Convert to km/s
    vely = df[16].values / 1e8
    velz = df[17].values / 1e8
    tag = df[11].astype(int).values
    print(f"Rank 0: Loaded {len(tag)} particles.")
else:
    tag = None
    velx = None
    vely = None
    velz = None

# Broadcast data
tag = comm.bcast(tag, root=0)
velx = comm.bcast(velx, root=0)
vely = comm.bcast(vely, root=0)
velz = comm.bcast(velz, root=0)

# Split work among ranks
local_tags = np.array_split(tag, size)[rank]

# Define isotopes needed
isotopes = ['c12', 'o16',  # Fuel
            'si28', 's32', 'ca40', # IME
            'fe54', 'fe56', 'ni58', # Stable IGE
            'ni56'] # Radioactive IGE

abundance_dict_local = {iso: np.zeros(len(tag)) for iso in isotopes}
tag_to_index = {t: i for i, t in enumerate(tag)}

# Load abundances for local tags
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

# Gather all abundances to rank 0
abundance_dict = {iso: np.zeros(len(tag)) for iso in isotopes}
for iso in isotopes:
    comm.Reduce(abundance_dict_local[iso], abundance_dict[iso], op=MPI.SUM, root=0)

# -------------------------------------------------------------------------
# PART 2: RGB COLORING & PLOTTING (ON RANK 0)
# -------------------------------------------------------------------------
if rank == 0:
    print("Rank 0: Processing colors and generating 3 plots...")
    
    # --- RGB Coloring (Ni56 is now BLACK) ---
    X_fuel = abundance_dict['c12'] + abundance_dict['o16']
    X_ime = abundance_dict['si28'] + abundance_dict['s32'] + abundance_dict['ca40']
    X_ige_s = abundance_dict['fe54'] + abundance_dict['fe56'] + abundance_dict['ni58']
    X_ni56 = abundance_dict['ni56']

    X_total = X_fuel + X_ime + X_ige_s + X_ni56
    
    f_fuel = X_fuel / X_total
    f_ime = X_ime / X_total
    f_ige_s = X_ige_s / X_total
    f_ni56 = X_ni56 / X_total

    # Create RGB colors as 0-1 floats
    rgb_data = np.zeros((len(tag), 3))
    rgb_data[:, 0] = f_ige_s
    rgb_data[:, 1] = f_fuel
    rgb_data[:, 2] = f_ime

    # Set Ni-56 dominated particles to BLACK (0,0,0)
    ni_dom = f_ni56 > 0.5
    rgb_data[ni_dom, :] = 0.0 

    rgb_data = np.clip(rgb_data, 0, 1)
    
    # Matplotlib's scatter `c` argument can take the Nx3 array directly
    colors = rgb_data 
    
    # --- MATPLOTLIB PLOTTING SECTION ---

    # Set a global max velocity for consistent axes
    vmax = np.max(np.abs(np.concatenate([velx, vely, velz]))) * 1.05 # Add 5% padding
    vlims = [-vmax, vmax]
    
    # Define custom legend handles
    legend_handles = [
        mpatches.Patch(color='red', label='Stable IGE (Fe, Ni58)'),
        mpatches.Patch(color='green', label='C/O Fuel'),
        mpatches.Patch(color='blue', label='IME (Si, S, Ca)'),
        mpatches.Patch(color='black', label='Ni-56 Dominated')
    ]
    
    # Function to apply common styling
    def style_ax(ax, title, xlabel, ylabel):
        ax.set_facecolor('white')
        ax.set_title(title, color='black', fontsize=16)
        ax.set_xlabel(xlabel, color='black', fontsize=12)
        ax.set_ylabel(ylabel, color='black', fontsize=12)
        
        ax.spines['top'].set_color('black')
        ax.spines['bottom'].set_color('black')
        ax.spines['left'].set_color('black')
        ax.spines['right'].set_color('black')
        
        ax.tick_params(axis='x', colors='black')
        ax.tick_params(axis='y', colors='black')
        
        ax.grid(True, color='grey', linestyle='--', linewidth=0.5, alpha=0.5)
        ax.set_aspect('equal') # 1:1 aspect ratio
        ax.set_xlim(vlims)
        ax.set_ylim(vlims)
        
        leg = ax.legend(
            handles=legend_handles, 
            title="Color Legend:", 
            loc='upper right', 
            facecolor='white', 
            edgecolor='black',
            labelcolor='black',
            # Removed 'color' from this dictionary
            title_fontproperties={'weight':'bold'} 
        )
        # This is the correct way to set the title color
        if leg:
            leg.get_title().set_color('black')

    # --- PLOT 1: XY Plane ---
    fig1, ax1 = plt.subplots(figsize=(10, 9))
    fig1.set_facecolor('white')
    # Using rasterized=True speeds up rendering for many points
    ax1.scatter(velx, vely, s=5, c=colors, marker='.', rasterized=True) 
    style_ax(ax1, 
             'tDDT: high central density model ($6 \\times 10^9$ g cm$^{-3}$) - XY Plane',
             'v$_x$ (10$^3$ km/s)',
             'v$_y$ (10$^3$ km/s)')
    fig1.savefig('velocity_space_2d_xy.png', dpi=300, bbox_inches='tight')
    print("Saved velocity_space_2d_xy.png")
    plt.close(fig1)

    # --- PLOT 2: YZ Plane ---
    fig2, ax2 = plt.subplots(figsize=(10, 9))
    fig2.set_facecolor('white')
    ax2.scatter(vely, velz, s=5, c=colors, marker='.', rasterized=True)
    style_ax(ax2, 
             'tDDT: high central density model ($6 \\times 10^9$ g cm$^{-3}$) - YZ Plane',
             'v$_y$ (10$^3$ km/s)',
             'v$_z$ (10$^3$ km/s)')
    fig2.savefig('velocity_space_2d_yz.png', dpi=300, bbox_inches='tight')
    print("Saved velocity_space_2d_yz.png")
    plt.close(fig2)

    # --- PLOT 3: ZX Plane ---
    fig3, ax3 = plt.subplots(figsize=(10, 9))
    fig3.set_facecolor('white')
    ax3.scatter(velz, velx, s=5, c=colors, marker='.', rasterized=True)
    style_ax(ax3, 
             'tDDT: high central density model ($6 \\times 10^9$ g cm$^{-3}$) - ZX Plane',
             'v$_z$ (10$^3$ km/s)',
             'v$_x$ (10$^3$ km/s)')
    fig3.savefig('velocity_space_2d_zx.png', dpi=300, bbox_inches='tight')
    print("Saved velocity_space_2d_zx.png")
    plt.close(fig3)

    print("\nRank 0: All 3 plots saved as PNG files.")
