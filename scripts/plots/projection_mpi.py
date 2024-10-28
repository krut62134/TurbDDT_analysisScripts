import yt
from yt.units import kpc
import glob
import numpy as np
import os
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Get the list of files to process
files = sorted(glob.glob("/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/runs/runs_autoddt_thermalreact/run1/*_plt_cnt*"))

# Distribute files among processors
files_per_rank = np.array_split(files, size)

# Each processor works on its subset of files
for file in files_per_rank[rank]:
    ds = yt.load(file)

    # simulation time
    t = int(file.split('_')[-1].split('.')[0]) / 1000.0

    # Define the center and width of the region you want to zoom in on
    center = np.array([0.0, 0.0, 0.0])
    width = ds.domain_width * 0.01526

    prj = yt.ProjectionPlot(ds, "x", "lchj", center=center, width=width, weight_field='dens')
    prj.set_cmap("lchj", "Rainbow + white")
    prj.set_zlim("lchj", zmin=0, zmax=1)
    prj.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
    prj.set_log("lchj", False)
    prj.save()

# Finalize MPI
comm.Barrier()
MPI.Finalize()

