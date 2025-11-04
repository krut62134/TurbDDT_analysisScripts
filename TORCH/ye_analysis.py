#####################################################################################################
# This scrip can be used to compare the y_e from your particle files with the Torch output files    #
# It is only useful if you are saving y_e as a lagrangian quentity                                  #
# Change the particle file name and location to the last particle file of your run                  #
# Make sure the columns for position, velocities, tags and y_e is correct                           #
# Provide the correct path to the source directry of Torch run that you want to compare against     #
#  ~krut patel 110225                                                                               #
#####################################################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import h5py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

particle_file = "./../../tDDT_hd_o12r32_HLLC_Roe_hdf5_part_004885"

# Load particle file on rank 0
if rank == 0:
    with h5py.File(particle_file, "r") as f:
        tracer_data = np.array(f['tracer particles'][:], dtype=float)
        df = pd.DataFrame(tracer_data, columns=np.arange(tracer_data.shape[1]))
        df.sort_values(by=11, ascending=True, inplace=True)
    
    # Filter tags between 1 and 100000
    df = df[(df[11] >= 1) & (df[11] <= 100000)]
    
    x = df[6].values
    y = df[7].values
    z = df[8].values
    velx = df[15].values
    vely = df[16].values
    velz = df[17].values
    tags = df[11].astype(int).values
    ye_initial = df[18].values
    
    # Calculate radial velocity
    v_r = (velx*x + vely*y + velz*z) / (np.sqrt(x**2 + y**2 + z**2) * 1e5)  # km/s
else:
    tags = None
    ye_initial = None
    v_r = None

# Broadcast to all ranks
tags = comm.bcast(tags, root=0)
ye_initial = comm.bcast(ye_initial, root=0)
v_r = comm.bcast(v_r, root=0)

# Divide work among ranks
n_particles = len(tags)
particles_per_rank = n_particles // size
start_idx = rank * particles_per_rank
end_idx = start_idx + particles_per_rank if rank < size - 1 else n_particles

# Process local particles
local_results = []
for i in range(start_idx, end_idx):
    tag = int(tags[i])
    ye_init = ye_initial[i]
    vr = v_r[i]
    
    data = np.loadtxt(f'./../src/out_{tag}_0000_z1.dat', skiprows=1)
    ye_final = data[-1, 8]
    
    local_results.append({
        'tag': tag,
        'ye_initial': ye_init,
        'ye_final': ye_final,
        'delta_ye': ye_final - ye_init,
        'v_r': vr
    })

# Gather all results to rank 0
all_results = comm.gather(local_results, root=0)

# Rank 0 processes and saves
if rank == 0:
    results = [item for sublist in all_results for item in sublist]
    results_df = pd.DataFrame(results)
    
    # Sort by radial velocity
    results_df.sort_values(by='v_r', ascending=True, inplace=True)
    
    # Save to file
    results_df.to_csv('ye_comparison.dat', sep='\t', index=False)
    
    # Plot delta_ye vs v_r
    plt.figure(figsize=(10, 6))
    plt.scatter(results_df['v_r'], results_df['delta_ye'], s=5)
    plt.xlabel('Radial Velocity (km/s)')
    plt.ylabel('ΔY_e (torchData - particleData)')
    plt.title('Y_e Change vs Radial Velocity')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('ye_vs_vr.png', dpi=150)
    
    print(f"Results saved to ye_comparison.dat")
    print(f"Plot saved to ye_vs_vr.png")
