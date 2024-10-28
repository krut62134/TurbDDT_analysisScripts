import yt
import glob
import numpy as np
import os
import matplotlib.pyplot as plt

# Load the HDF5 file using yt
for file in glob.glob("/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/runs/runs_autoddt_thermalreact/run1/tDDT_*_plt_cnt_000500"):
    ds = yt.load(file)

    # Print the list of fields
    print(ds.field_list)
    
    t = int(file.split('_')[-1].split('.')[0]) / 1000.0

    # Define the center and width of the region you want to zoom in on
    center = np.array([0.0, 0.0, 0.0])
    width = ds.domain_width * 0.04578  # 

    # Create a slice plot for temperature
    plot_temp = yt.SlicePlot(ds, "x", "temp", center=center, width=width)
    plot_dens = yt.SlicePlot(ds, "x", "dens", center=center, width=width)
    plot_flam = yt.SlicePlot(ds, "x", "flam", center=center, width=width)
    plot_pres = yt.SlicePlot(ds, "x", "pres", center=center, width=width)
    plot_lchj = yt.SlicePlot(ds, "x", "lchj", center=center, width=width)

    # Apply colorbar settings for temperature plot
    plot_temp.set_cmap("temp", "hot")
    plot_dens.set_cmap("dens", "viridis")
    plot_flam.set_cmap("flam", "hot")
    plot_pres.set_cmap("pres", "jet")
    plot_lchj.set_cmap("lchj", "viridis")

    plot_temp.set_zlim("temp", zmin=(0.625e8, "K"), zmax=(1e10, "K"))
    plot_dens.set_zlim("dens", zmin=(0.01, "g/cm**3"), zmax=(2e9, "g/cm**3"))
    plot_flam.set_zlim("flam", zmin=(1e8, ""), zmax=(1e10, ""))
    plot_pres.set_zlim("pres", zmin=(1e15, "dyne/cm**2"), zmax=(1.5e27, "dyne/cm**2"))
    plot_lchj.set_zlim("lchj", zmin=(0), zmax=(1))

    plot_temp.set_unit("temp", "K")
    plot_dens.set_unit("dens", "g/cm**3")
    plot_flam.set_unit("flam", "")
    plot_pres.set_unit("pres", "dyne/cm**2")   
    plot_lchj.set_unit("lchj", "")

    plot_temp.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
    plot_dens.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
    plot_flam.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
    plot_pres.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
    plot_lchj.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)

    # Set the axis labels for all plots
    for plot in [plot_temp, plot_dens, plot_flam, plot_pres]:
        plot.set_xlabel("y (cm)")
        plot.set_ylabel("z (cm)")
      

    ### matplotlib sttuff for subplot  
    # Create a figure and four subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 12))

    # Assign each slice plot to a subplot
    plot_temp.plots['temp'].figure = fig
    plot_temp.plots['temp'].axes = axs[0, 0]
    plot_temp._setup_plots()

    plot_dens.plots['dens'].figure = fig
    plot_dens.plots['dens'].axes = axs[0, 1]
    plot_dens._setup_plots()

    plot_flam.plots['flam'].figure = fig
    plot_flam.plots['flam'].axes = axs[1, 0]
    plot_flam._setup_plots()

    plot_lchj.plots['lchj'].figure = fig
    plot_lchj.plots['lchj'].axes = axs[1, 1]
    plot_lchj._setup_plots()

    # Adjust the spacing between subplots
    plt.tight_layout()

    # Save or show the figure
    plt.savefig('merged_plots.png')

    # Save each plot
#    plot_temp.save()
#    plot_dens.save()
#    plot_flam.save()
#    plot_pres.save()
#    plot_lchj.save()
