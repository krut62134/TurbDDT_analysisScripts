#########################################################################################
# This script converts final isotopic abundances from TORCH to elemental abundances     #
# Provide the correct path to source of Torch and a directory where you want to         #
#  save the elemental mass fractions                                                    #
#   ~krut patel 091525                                                                  #
#########################################################################################
from pathlib import Path
import pandas as pd, re
from mpi4py import MPI

# --- setup ---
indir  = Path("./../src/")     # change this
outdir = Path("./elemental/")    # change this
outdir.mkdir(exist_ok=True)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# --- distribute files ---
files = sorted(indir.glob("out_*_final.dat"))
for i, f in enumerate(files):
    if i % size != rank:
        continue

    df = pd.read_csv(f, sep=r"\s+", header=None, names=["Z","A","frac","iso"])
    df = df[df["Z"] != 0]  # drop neut (Z=0)

    out = df.groupby("Z", as_index=False).agg(frac=("frac","sum"), iso=("iso","first"))
    out["iso"] = out["iso"].str.replace(r"\d+$","", regex=True)  # strip trailing digits
    out = out[["iso","frac"]]

    outname = f.name.replace("_final.dat", "_elemental.dat")
    out.to_csv(outdir / outname, sep="\t", index=False, header=False, float_format="%.7E")

