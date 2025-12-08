import yt
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from mpi4py import MPI
import math
import gc

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Define the path to your data files; adjust the file pattern as needed
data_files = glob.glob("./../*plt*_0000*")

# Distribute files among MPI ranks
# Divide files evenly among ranks
data_files_split = np.array_split(data_files, size)

# Each rank processes its assigned files
local_files = data_files_split[rank]

@yt.derived_field(name="lrat_new", units="dimensionless", sampling_type="cell")
def _lrat_new(field, data):
    cond = (data["flam"] > 1e-3) & (data["flam"] < 1e-2)
    return data["lrat"] * cond
@yt.derived_field(name="enuc_floor", units="dimensionless", sampling_type="cell")
def _enuc_floor(field, data):
    return np.maximum(data["enuc"], 1e12)
# Define a derived field for (phaq - phqn)
def _phaq_minus_phqn(field, data):
    return data["phaq"] - data["phqn"]
yt.add_field(
    ("gas", "phaq_minus_phqn"),
    function=_phaq_minus_phqn,
    sampling_type="cell",
    units="dimensionless"
)

# Define the fields you want to plot
fields = ["temp", "dens", "pres", "lrat", "flam", "enuc_floor"]
#fields = ["temp", "pres", ("gas", "temperature_gradient_magnitude"), "dens"]
#fields = ["lrat_new","flam"]

# Loop over each data file assigned to this rank
for data_file in local_files:
    # Load the dataset
    ds = yt.load(data_file)

    # Extract time 't' from the filename
    #t = int(os.path.basename(data_file).split('_')[-1].split('.')[0]) / 1000.0
    t = ds.current_time

    # Define center and width
    center = np.array([0.0, 0.0, 0.0])
    width = ds.domain_width * 0.0165
    widthLrat = ds.domain_width * 0.00375

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
        #plot = yt.SlicePlot(ds, "x", field, center=center, width=width)
        # Set field-specific width
        if field == "lrat":
            plot = yt.SlicePlot(ds, "x", field, center=center, width=widthLrat)
        elif field == "flam":
            plot = yt.SlicePlot(ds, "x", field, center=center, width=widthLrat)
        elif field == "phfa":
            plot = yt.SlicePlot(ds, "x", field, center=center, width=widthLrat)
        elif field == "enuc_floor":
            plot = yt.SlicePlot(ds, "x", field, center=center, width=widthLrat)
        else:
            plot = yt.SlicePlot(ds, "x", field, center=center, width=width)


        plot.annotate_grids()
        plot.set_axes_unit("cm")
        plot.set_font({"size": 24})
        # Apply field-specific customizations
        if field == "temp":
            plot.set_cmap("temp", "inferno")
            plot.set_zlim("temp", zmin=3e7, zmax=1e10)
            plot.set_unit("temp", "K")
            plot.annotate_title("Temperature (K)")
            
        elif field == "dens":
            plot.set_cmap("dens", "viridis")
            plot.set_zlim("dens", zmin=1e0, zmax=2e9)
            plot.set_unit("dens", "g/cm**3")
            plot.annotate_title("Density (g/cm$^3$)")
            
        elif field == "lrat":
            plot.set_cmap("lrat", "plasma")
            plot.set_zlim("lrat", zmin=1e-3, zmax=1e2)
            plot.set_unit("lrat", "dimensionless")
            plot.set_log("lrat", True)
            plot.annotate_title("L-Ratio (L/L$_CJ$)")
            
        elif field == "flam":
            plot.set_cmap("flam", "hot")
            plot.set_zlim("flam", zmin=5e-7, zmax=1)
            plot.set_unit("flam", "dimensionless")
            plot.set_log("flam", True)
            plot.annotate_title("Flame Progress Variable")
            
        elif field == "pres":
            plot.set_cmap("pres", "jet")
            plot.set_zlim("pres", zmin=3e17, zmax=1.5e27)
            plot.set_unit("pres", "dyne/cm**2")
            plot.annotate_title("Pressure (dyne/cm$^2$)")
            
        elif field == "velocity_magnitude":
            plot.set_cmap("velocity_magnitude", "Rainbow + white")
            plot.set_zlim("velocity_magnitude", zmin=1e5, zmax=30000e5)
            plot.set_unit("velocity_magnitude", "cm/s")
            plot.set_log("velocity_magnitude", False)
            plot.annotate_title("Velocity Magnitude (cm/s)")
            
        elif field == ("gas", "temperature_gradient_magnitude"):
            plot.set_cmap(("gas", "temperature_gradient_magnitude"), "magma")
            plot.set_unit(("gas", "temperature_gradient_magnitude"), "K/cm")
            plot.annotate_title("Temperature Gradient Magnitude (K/cm)")
            
        elif field == "phfa":
            plot.set_cmap("phfa", "viridis")
            plot.set_zlim("phfa", zmin=0, zmax=1)
            plot.set_unit("phfa", "dimensionless")
            plot.set_log("phfa", False)
            plot.annotate_title("PHFA (0 = Fuel, 1 = Ash)")
            
        elif field == "enuc_floor":
            plot.set_cmap("enuc_floor", "magma")
            plot.set_zlim("enuc_floor", zmin=5e15, zmax=1e21)
            plot.annotate_title("Specific Nuclear Energy Generation (erg/g/s)")
            
        elif field == "phaq_minus_phqn":
            plot.set_cmap("phaq_minus_phqn", "viridis")
            plot.set_log("phaq_minus_phqn", True)
            plot.set_unit("phaq_minus_phqn", "dimensionless")
            plot.set_zlim("phaq_minus_phqn", zmin=1e-5, zmax=1e0)
            plot.annotate_title("QSE Progress Variable (PHAQ - PHQN)")
        # Annotate timestamp
        plot.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)

        # Save the individual plot as a temporary image
        temp_filename = f"temp_plot_{field}_{rank}.png"
        plot.save(temp_filename, mpl_kwargs={"bbox_inches": "tight", "pad_inches": 0})
        #plot.save(temp_filename)

        # Load the saved image into matplotlib and display in the subplot
        img = plt.imread(temp_filename)
        axes[i].imshow(img)
        axes[i].axis('off')  # Hide axes for a cleaner look
        #axes[i].set_title(field)

        # Explicit memory cleanup for plot
        del plot
        gc.collect()

    # Adjust layout and save the combined plot as a single file with higher resolution
    #plt.tight_layout()
    #plt.subplots_adjust(wspace=0.002, hspace=0.002, left=0.001, right=0.999, bottom=0.001, top=0.999)
    plt.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)
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

    # Final cleanup per file
    del ds
    del fig
    del axes
    gc.collect()

