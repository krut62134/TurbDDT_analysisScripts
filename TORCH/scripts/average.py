##################################################################################
# A simple script to compute average mass fraction for all isotopes.
# Just make sure to change the hardcoded input path
# The solar mass is just a good estimate as we are assuming the mass of the WD to be 1.4 Msun
#  ~krut patel 111824
##################################################################################
import glob
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # Hardcoded input path
    input_path = "/scratch/09430/kpatel5/PRODUCTION/highDensity/o12r32/TORCH/src"
    files = sorted(glob.glob(f"{input_path}/*final.dat"))
    
    # Hardcoded output filename
    output_filename = "meanAbundance.dat"
    
    with open(files[0], 'r') as f:
        isotopes = [line.strip().split()[3] for line in f]
    data = (files, isotopes, output_filename)
else:
    data = None

# Broadcast data to all ranks
files, isotopes, output_filename = comm.bcast(data, root=0)

# Each rank processes its own slice of files
my_files = files[rank::size]
local_sum = np.zeros(len(isotopes))

for f in my_files:
    with open(f, 'r') as handle:
        lines = [line.strip().split() for line in handle]
        local_sum += [float(line[2]) for line in lines]

# Sum all results at rank 0
global_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

# Rank 0 calculates final average and writes file
if rank == 0:
    avg_mass_fractions = global_sum / len(files)
    avg_mass_solar = avg_mass_fractions * 1.4
    isotope_avg = sorted(zip(isotopes, avg_mass_fractions, avg_mass_solar), key=lambda x: -x[1])

    with open(output_filename, 'w') as out_f:
        # Write header lines with #
        out_f.write(f"# Using {len(files)} files.\n")
        out_f.write(f"#{'Isotope':10s} {'Fraction':>12s} {'Solar Mass':>12s}\n")
        
        for iso, avg, solar in isotope_avg:
            out_f.write(f"{iso:10s} {avg:12.4e} {solar:12.4e}\n")

