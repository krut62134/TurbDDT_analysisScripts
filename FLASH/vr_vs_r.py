###################################################################################
# This script will plot radial velocity vs radius, and the distribution of        #
#  vr/r accross particles. Used to check if the ejecta is in free expansion       #     
# The script calculates Δ = σ(vr/r) / median(vr/r), where σ is the standard       #
#  devation of the v_r/r distribution. A small Δ value indicates a                #
#  tight linear relationship                                                      #
# Make sure to change the particle file path and name and if the position and     #
#  velocity columns match your dataset                                            #
#   ~krut patel 082525                                                            #
################################################################################### 
import h5py
import numpy as np
import matplotlib.pyplot as plt

# === Final particle file name and location ===
part_file = "./../../tDDT_hd_o12r32_HLLC_Roe_hdf5_part_001370"

# === Load data ===
with h5py.File(part_file, "r") as f:
    arr = f["tracer particles"][:]

x, y, z = arr[:, 2], arr[:, 3], arr[:, 4]
vx, vy, vz = arr[:, 9], arr[:, 10], arr[:, 11]

# === Compute r and v_r ===
r = np.sqrt(x * x + y * y + z * z)
mask = r > 0
r, x, y, z = r[mask], x[mask], y[mask], z[mask]
vx, vy, vz = vx[mask], vy[mask], vz[mask]

vr = (vx * x + vy * y + vz * z) / r
vr_over_r = vr / r

# === Statistics ===
med, mean, std = np.median(vr_over_r), np.mean(vr_over_r), np.std(vr_over_r)
delta = std / med
print(f"vr/r std:  {std:.7e} s^-1")
print(f"vr/r median: {med:.7e} s^-1")
print(f"Δ = σ / median(vr/r) = {delta:.7e}")
print(f"max vr = {max(vr):.7e}")
print(f"max r = {max(r):.7e}")

# === Plot ===
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Scatter vr vs r
axes[0].scatter(r, vr, s=0.2, color="blue", rasterized=True)
axes[0].plot([], [], ' ', label=rf"$\Delta = {delta:.2e}$")
axes[0].set_xlabel(r"$r\ \mathrm{(cm)}$")
axes[0].set_ylabel(r"$v_r\ \mathrm{(cm\ s^{-1})}$")
axes[0].legend(loc="upper left", frameon=False)

# Plot 2: Histogram of vr/r
axes[1].hist(vr_over_r, bins=100, color="green")
axes[1].set_xlabel(r"$v_r/r\ \mathrm{(s^{-1})}$")
axes[1].set_ylabel("Particle Count")

# Add mean line and text
axes[1].axvline(mean, color='k', linestyle='--', linewidth=1)
axes[1].text(mean, 0.5, f" Mean: {mean:.3e}", rotation=90, 
             transform=axes[1].get_xaxis_transform(), va='center')

fig.tight_layout()
fig.savefig("vr_vs_r_combined.png", dpi=200, bbox_inches="tight")
plt.close(fig)
