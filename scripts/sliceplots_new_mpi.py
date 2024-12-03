import yt
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from mpi4py import MPI
import math

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Define the path to your data files; adjust the file pattern as needed
data_files = glob.glob("/scratch/09430/kpatel5/runs/run_16km_HD_unsplit/*plt_cnt*")

# Distribute files among MPI ranks
# Divide files evenly among ranks
data_files_split = np.array_split(data_files, size)

# Each rank processes its assigned files
local_files = data_files_split[rank]

# Define the fields you want to plot
#fields = ["temp", "dens", "phfa", "flam", "pres", "velocity_magnitude"]
fields = ["temp", "pres", "phfa", "dens"]
#fields = ["temp"]

# Loop over each data file assigned to this rank
for data_file in local_files:
    # Load the dataset
    ds = yt.load(data_file)

    # Extract time 't' from the filename
    t = int(os.path.basename(data_file).split('_')[-1].split('.')[0]) / 1000.0

    # Define center and width
    center = np.array([0.0, 0.0, 0.0])
    width = ds.domain_width * 0.1

    # Dynamically determine the number of rows and columns to keep the plot layout close to square
    num_fields = len(fields)
    cols = math.ceil(math.sqrt(num_fields))  # Number of columns
    rows = math.ceil(num_fields / cols)      # Number of rows needed

    # Set up the figure with the calculated rows and columns
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows))

    # Flatten axes if there's more than one row and column
    if rows * cols > 1:
        axes = axes.flatten()

    # If there's only one field, make `axes` a list to simplify indexing
    if num_fields == 1:
        axes = [axes]

    # Loop over fields to create slice plots and add them to subplots
    for i, field in enumerate(fields):
        # Create the slice plot for the current field
        plot = yt.SlicePlot(ds, "x", field, center=center, width=width)
        plot.annotate_grids()

        # Apply field-specific customizations
        if field == "temp":
            plot.set_cmap("temp", "hot")
            plot.set_zlim("temp", zmin=6.25e7, zmax=1e10)
            plot.set_unit("temp", "K")
        elif field == "dens":
            plot.set_cmap("dens", "viridis")
            plot.set_zlim("dens", zmin=1e-2, zmax=2e9)
            plot.set_unit("dens", "g/cm**3")
        elif field == "lchj":
            plot.set_cmap("lchj", "Rainbow + white")
            plot.set_zlim("lchj", zmin=0, zmax=1)
            plot.set_unit("lchj", "dimensionless")
            plot.set_log("lchj", False)
        elif field == "flam":
            plot.set_cmap("flam", "hot")
            plot.set_zlim("flam", zmin=0, zmax=1)
            plot.set_unit("flam", "dimensionless")
            plot.set_log("flam", False)
        elif field == "pres":
            plot.set_cmap("pres", "jet")
            plot.set_zlim("pres", zmin=1e15, zmax=1.5e27)
            plot.set_unit("pres", "dyne/cm**2")
        elif field == "velocity_magnitude":
            plot.set_cmap("velocity_magnitude", "Rainbow + white")
            plot.set_zlim("velocity_magnitude", zmin=5e7, zmax=1e10)
            plot.set_unit("velocity_magnitude", "cm/s")

        # Annotate timestamp
        plot.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)

        # Save the individual plot as a temporary image
        temp_filename = f"temp_plot_{field}_{rank}.png"
        plot.save(temp_filename)

        # Load the saved image into matplotlib and display in the subplot
        img = plt.imread(temp_filename)
        axes[i].imshow(img)
        axes[i].axis('off')  # Hide axes for a cleaner look
        axes[i].set_title(field)

    # Adjust layout and save the combined plot as a single file with higher resolution
    plt.tight_layout()
    
    # Check if there's only one field and adjust the filename accordingly
    if len(fields) == 1:
        filename = f"{os.path.basename(data_file)}_{fields[0]}_slice.png"
    else:
        filename = f"{os.path.basename(data_file)}_combined_slice.png"
    
    plt.savefig(filename, dpi=400)
    plt.close(fig)

    # Optionally, remove the temporary files
    for field in fields:
        os.remove(f"temp_plot_{field}_{rank}.png")

