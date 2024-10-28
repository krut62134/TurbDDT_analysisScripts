from mpi4py import MPI
import yt
import glob
import numpy as np
import os

def process_file(file):
    # Load the HDF5 file using yt
    ds = yt.load(file)

    # Print the list of fields
    print(ds.field_list)

    t = int(file.split('_')[-1].split('.')[0]) / 1000.0

    # Define the center and width of the region you want to zoom in on
    center = np.array([0.0, 0.0, 0.0])
    width = ds.domain_width * 0.04526

    # Create a slice plot for temperature
#    plot_temp = yt.SlicePlot(ds, "x", "temp", center=center, width=width)
#    plot_dens = yt.SlicePlot(ds, "x", "dens", center=center, width=width)
    plot_flam = yt.SlicePlot(ds, "x", "flam", center=center, width=width)
#    plot_pres = yt.SlicePlot(ds, "x", "pres", center=center, width=width)
#    plot_lchj = yt.SlicePlot(ds, "x", "lchj", center=center, width=width)

#    plot_fspd = yt.SlicePlot(ds, "x", "fspd", center=center, width=width)
#    plot_gamc = yt.SlicePlot(ds, "x", "gamc", center=center, width=width)
#    plot_fldt = yt.SlicePlot(ds, "x", "fldt", center=center, width=width)
#    plot_phfa = yt.SlicePlot(ds, "x", "phfa", center=center, width=width)
#    plot_phaq = yt.SlicePlot(ds, "x", "phaq", center=center, width=width)
#    plot_phqn = yt.SlicePlot(ds, "x", "phqn", center=center, width=width)    

    # Apply colorbar settings for temperature plot
#    plot_temp.set_cmap("temp", "hot")
#    plot_dens.set_cmap("dens", "viridis")
    plot_flam.set_cmap("flam", "Rainbow + white")
#    plot_pres.set_cmap("pres", "jet")
#    plot_lchj.set_cmap("lchj", "Rainbow + white")

#    plot_fldt.set_cmap("fldt", "Rainbow18")

#    plot_temp.set_zlim("temp", zmin=(0.625e8, "K"), zmax=(1e10, "K"))
#    plot_dens.set_zlim("dens", zmin=(0.01, "g/cm**3"), zmax=(2e9, "g/cm**3"))
    plot_flam.set_zlim("flam", zmin=(0, ""), zmax=(1, ""))
#    plot_pres.set_zlim("pres", zmin=(1e15, "dyne/cm**2"), zmax=(1.5e27, "dyne/cm**2"))
#    plot_lchj.set_zlim("lchj", zmin=(0, ""), zmax=(1, ""))

#    plot_temp.set_unit("temp", "K")
#    plot_dens.set_unit("dens", "g/cm**3")
    plot_flam.set_unit("flam", "")
#    plot_pres.set_unit("pres", "dyne/cm**2")
#    plot_lchj.set_unit("lchj", "")

#    plot_lchj.set_log("lchj", False)
    plot_flam.set_log("flam", False)
#    plot_phfa.set_log("phfa", False)
#    plot_phaq.set_log("phaq", False)
#    plot_phqn.set_log("phqn", False)

 #   plot_temp.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
 #   plot_dens.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
    plot_flam.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
 #   plot_pres.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)
 #   plot_lchj.annotate_timestamp(corner='upper_right', redshift=True, draw_inset_box=True, time=t)

    # Set the axis labels for all plots
#    for plot in [plot_temp, plot_dens, plot_flam, plot_pres, plot_lchj]:
#        plot.set_xlabel("y (cm)")
#        plot.set_ylabel("z (cm)")

    # Save each plot
#    plot_temp.save()
#    plot_dens.save()
    plot_flam.save()
#    plot_pres.save()
#    plot_lchj.save()

#    plot_fspd.save()
#    plot_gamc.save()
#    plot_fldt.save()
#    plot_phfa.save()
#    plot_phaq.save()
#    plot_phqn.save()

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # List of files to process
    files = glob.glob("/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/kpatel29/runs/runs_autoddt_thermalreact/run_8km/tDDT_*_plt_cnt_000*")

    # Divide the work among processes
    for i in range(rank, len(files), size):
        process_file(files[i])

if __name__ == "__main__":
    main()

