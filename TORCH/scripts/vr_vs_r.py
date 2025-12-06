###################################################################################
# This script will plot radial velocity vs radius. Used to check if               #
#  the ejecta is in free expansion                                                #     
# The script calculates Δ = σ / median(vr/r), where σ is the standard             #
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
part_file = "/scratch/09430/kpatel5/PRODUCTION/highDensity/o12r32/tDDT_hd_o12r32_HLLC_Roe_hdf5_part_004885"

# === Load data ===
with h5py.File(part_file, "r") as f:
    arr = f["tracer particles"][:]  # to numpy

# positions: 6,7,8 ; velocities: 15,16,17
x, y, z = arr[:, 6], arr[:, 7], arr[:, 8]
vx, vy, vz = arr[:, 15], arr[:, 16], arr[:, 17]

# === Compute r and v_r ===
r = np.sqrt(x * x + y * y + z * z)
mask = r > 0    # just a fail safe
r = r[mask]
x, y, z = x[mask], y[mask], z[mask]
vx, vy, vz = vx[mask], vy[mask], vz[mask]

vr = (vx * x + vy * y + vz * z) / r

# === Homologous expansion diagnostic ===
vr_over_r = vr / r  # s^-1
vr_over_r_mean = np.mean(vr_over_r)
vr_over_r_std = np.std(vr_over_r)
vr_over_r_median = np.median(vr_over_r)
delta = vr_over_r_std / vr_over_r_median  # Δ = σ / median(vr/r)

print(f"vr/r mean: {vr_over_r_mean:.7e} s^-1")
print(f"vr/r std:  {vr_over_r_std:.7e} s^-1")
print(f"vr/r median: {vr_over_r_median:.7e} s^-1")
print(f"Δ = σ / median(vr/r) = {delta:.3e}")

# === Plot ===
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(r, vr, s=0.2, color="blue", rasterized=True)

# Add a text-only legend entry for Δ
label = rf"$\Delta = \sigma / \tilde{{(v_r/r)}} = {delta:.2e}$"
ax.plot([], [], ' ', label=label)

# Axes labels and title
ax.set_xlabel(r"$r\ \mathrm{(cm)}$", fontsize=12)
ax.set_ylabel(r"$v_r\ \mathrm{(cm\ s^{-1})}$", fontsize=12)
#ax.set_title(r"$v_r\ \mathrm{vs.}\ r\ \text{at yield-calculation epoch}$", fontsize=13)

# Legend styling
ax.legend(loc="upper left", frameon=False, fontsize=10)

# Layout & save
fig.tight_layout()
fig.savefig("vr_vs_r.png", dpi=200, bbox_inches="tight")
plt.close(fig)

