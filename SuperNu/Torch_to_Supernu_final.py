#################################################################################################
# This script will create input string for SuperNu                                              #
# - Uses ALL elements found in out_<tag>_elemental.dat, preserving their on-disk order          #
# - Appends isotopes (ni56, co56, fe52, mn52, cr48, v48) at the end from out_<tag>_final.dat    #
# - Columns: vel_right  total_mass  <elements...>  ni56  co56  fe52  mn52  cr48  v48            #
# Make sure to provide correct paths for final particle file from the FLASH run,                #
#  the elemental data directory, and source of Torch run. Also double check your                #
#  mass of the ejecta and the totle number of particles                                         #
# You absolutly need to provide the ni56 column at the end, you can choose to keep the other    #
#  isotopes. SuperNu only has hardwired chains for these 6 isotopes, so that's a limitation.    #
#   ~krut patel 091525                                                                          #
#################################################################################################

from pathlib import Path
import numpy as np
import pandas as pd
import h5py
from mpi4py import MPI

# ---------- CONFIG ----------
particle_file = "./../../tDDT_sd_o12r32_hdf5_part_006692"

# Dir with per-particle elemental files (2 cols: iso frac), e.g. out_<tag>_elemental.dat
elem_dir  = Path("./elemental/")

# Dir with original isotopic files (4 cols: Z A frac iso), e.g. out_<tag>_final.dat
final_dir = Path("./../src/")

out_file  = "input.str"
nbins     = 256     #decide number of bins based on your needs, change it in input.par as well

M_total       = np.float64(2.744859152529676297E+33)    # your mass of the ejecta
N_particles   = np.int64(99872)     # total particles in your simulation
m_per_particle = M_total / np.float64(N_particles)   # float64 throughout

# extra isotopes to append (exact labels in _final.dat, lowercase)
EXTRA_ISOS = ["ni56", "co56", "fe52", "mn52", "cr48", "v48"]

# ---------- MPI ----------
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# ---------- ROOT loads particle arrays and broadcasts (float64 everywhere) ----------
if rank == 0:
    with h5py.File(particle_file, "r") as f:
        arr = f["tracer particles"][:]
    df = pd.DataFrame(arr, dtype=np.float64).sort_values(by=[11], ascending=True)
    velx = df.iloc[:,14].to_numpy(dtype=np.float64)
    vely = df.iloc[:,15].to_numpy(dtype=np.float64)
    velz = df.iloc[:,16].to_numpy(dtype=np.float64)
    tag  = df.iloc[:,11].to_numpy(dtype=np.int64)
    speed = np.sqrt(velx*velx + vely*vely + velz*velz, dtype=np.float64)
    vmin, vmax = float(speed.min()), float(speed.max())
else:
    speed = None
    tag   = None
    vmin = vmax = 0.0

speed = comm.bcast(speed, root=0)
tag   = comm.bcast(tag,   root=0)
vmin  = comm.bcast(vmin,  root=0)
vmax  = comm.bcast(vmax,  root=0)

# ---------- Build linear bins globally (float64) ----------
edges = np.linspace(np.float64(vmin), np.float64(vmax), nbins + 1, dtype=np.float64)
right_edges = edges[1:].astype(np.float64)
bin_idx = np.digitize(speed, edges, right=True) - 1
bin_idx[bin_idx < 0] = 0
bin_idx[bin_idx >= nbins] = nbins - 1

# ---------- Assign bins to ranks ----------
my_bins = [b for b in range(nbins) if b % size == rank]

# ---------- Per-rank bin computations ----------
# For each bin we’ll return:
# (bin_id, vel_right, total_mass, elem_means_ordered_dict, extra_iso_means_array(float64, len=6))
local_rows = []
local_elem_names_in_order = []  # preserve first-seen order on this rank

for b in my_bins:
    msk = (bin_idx == b)
    cnt = int(msk.sum())
    vel_right = np.float64(right_edges[b])

    if cnt == 0:
        # Empty bin
        local_rows.append((b, vel_right, np.float64(0.0), {}, np.zeros(len(EXTRA_ISOS), dtype=np.float64)))
        continue

    tags_b = tag[msk]
    total_mass = np.float64(cnt) * m_per_particle

    # Sum elements across particles in this bin (divide by cnt later). Preserve order as seen in files.
    elem_sums = {}  # insertion-ordered in Py>=3.7
    # Sum selected isotopes across particles
    extra_sums = {k: np.float64(0.0) for k in EXTRA_ISOS}

    for t in np.unique(tags_b):
        # Elemental file: two columns (iso, frac) already element symbols in desired order
        edf = pd.read_csv(
            elem_dir / f"out_{t}_elemental.dat",
            sep=r"\s+",
            header=None,
            names=["iso","frac"],
            dtype={"iso":"string","frac":np.float64}
        )
        # lower-case to be safe, but do NOT strip numbers (these files are already elemental)
        edf["iso"] = edf["iso"].str.lower()

        for iso, frac in zip(edf["iso"].to_numpy(dtype=str), edf["frac"].to_numpy(dtype=np.float64)):
            if iso not in elem_sums:
                elem_sums[iso] = np.float64(0.0)
                # track first-seen order across this rank
                if iso not in local_elem_names_in_order:
                    local_elem_names_in_order.append(iso)
            elem_sums[iso] += frac

        # Final isotopic file: four columns (Z A frac iso)
        fdf = pd.read_csv(
            final_dir / f"out_{t}_final.dat",
            sep=r"\s+",
            header=None,
            names=["Z","A","frac","iso"],
            dtype={"Z":np.int64,"A":np.int64,"frac":np.float64,"iso":"string"}
        )
        fdf["iso"] = fdf["iso"].str.lower()

        for lab in EXTRA_ISOS:
            row = fdf.loc[fdf["iso"] == lab, "frac"]
            if not row.empty:
                extra_sums[lab] += np.float64(row.iloc[0])

    # sums -> means
    inv_cnt = np.float64(1.0) / np.float64(cnt)
    elem_means = {k: (v * inv_cnt) for k, v in elem_sums.items()}
    extra_means = np.array([extra_sums[k] * inv_cnt for k in EXTRA_ISOS], dtype=np.float64)

    local_rows.append((b, vel_right, total_mass, elem_means, extra_means))

# ---------- Gather to root ----------
all_rows = comm.gather(local_rows, root=0)
all_name_orders = comm.gather(local_elem_names_in_order, root=0)

if rank == 0:
    # Build element column order by first-seen across ranks (rank order 0..size-1, then bin order)
    elem_cols = []
    for name_list in all_name_orders:
        for nm in name_list:
            if nm not in elem_cols:
                elem_cols.append(nm)

    # Float64 containers
    vel_col  = np.array(right_edges, dtype=np.float64)
    mass_col = np.zeros(nbins, dtype=np.float64)
    elem_mat = pd.DataFrame(np.zeros((nbins, len(elem_cols)), dtype=np.float64), columns=elem_cols)
    extra_mat = np.zeros((nbins, len(EXTRA_ISOS)), dtype=np.float64)

    # Fill from gathered rows
    for rows in all_rows:
        for b, vel_r, tmass, edict, extra_vec in rows:
            mass_col[b] = tmass
            if edict:
                for k, v in edict.items():
                    # only assign known columns (they should all be present)
                    if k in elem_mat.columns:
                        elem_mat.at[b, k] = v
            extra_mat[b, :] = extra_vec

    # Assemble DataFrame (float64 in memory)
    out_df = pd.DataFrame({"vel_right": vel_col, "total_mass": mass_col})
    out_df = pd.concat([out_df, elem_mat], axis=1)
    # Append extra isotopes strictly at the end
    extra_df = pd.DataFrame(extra_mat, columns=EXTRA_ISOS)
    out_df = pd.concat([out_df, extra_df], axis=1)

    # (Optional sanity) sum of elements per bin (excludes extra isotopes):
    # mf_sum = elem_mat.sum(axis=1).to_numpy()
    # for vr, s in zip(vel_col, mf_sum):
    #     print(f"vel_right={vr:.7E}\tmf_sum(elements)={s:.7E}")

    # ---- WRITE in float32 (single precision) ----
    out_df = out_df.astype(np.float32, copy=False)
    out_df.to_csv(out_file, sep="\t", index=False, header=True, float_format="%.7E")

