#########################################################################
# This script is made by Krut Patel (110425) with initial skeleton from #
#  Dr. Fisher to visualise the structure of the ejecta from turbulent   #
#  DDT models in an interactive 3D velocity space.                      #
# Plots IGEs, unburnt C/O, IMEs in RGB fashion and ni56 > 0.5 in strict #
#  white. So brown for example would mean the particle has mostly IGEs  #
#  and some unburnt C/O                                                 #
#########################################################################
import h5py
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from mpi4py import MPI
import os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

particle_file = '/scratch/09430/kpatel5/PRODUCTION/stdDensity/tDDT_sd_o12r32_hdf5_part_006692'
final_dir = '/scratch/09430/kpatel5/PRODUCTION/stdDensity/Torch-SuperNu/TORCH/src/'

# Load particle data on rank 0
if rank == 0:
    with h5py.File(particle_file, "r") as f:
        tracer_data = np.array(f['tracer particles'][:], dtype=float)
        df = pd.DataFrame(tracer_data, columns=np.arange(tracer_data.shape[1]))
        df.sort_values(by=11, ascending=True, inplace=True)
    
    velx = df[15].values / 1e8  # Convert to km/s
    vely = df[16].values / 1e8
    velz = df[17].values / 1e8
    tag = df[11].astype(int).values
else:
    tag = None
    velx = None
    vely = None
    velz = None

# Broadcast data
tag = comm.bcast(tag, root=0)
velx = comm.bcast(velx, root=0)
vely = comm.bcast(vely, root=0)
velz = comm.bcast(velz, root=0)

# Split work among ranks
local_tags = np.array_split(tag, size)[rank]

# Define isotopes needed for Fuel, IME, and IGE groups
isotopes = ['c12', 'o16',  # Fuel
            'si28', 's32', 'ca40', # IME
            'fe54', 'fe56', 'ni58', # Stable IGE
            'ni56'] # Radioactive IGE

abundance_dict_local = {iso: np.zeros(len(tag)) for iso in isotopes}
tag_to_index = {t: i for i, t in enumerate(tag)}

# Load abundances for local tags
for t in local_tags:
    fpath = os.path.join(final_dir, f"out_{t}_final.dat")
    if not os.path.isfile(fpath):
        continue
    with open(fpath) as f:
        for line in f:
            parts = line.strip().split()
            iso = parts[3].lower()
            if iso in abundance_dict_local:
                i = tag_to_index[t]
                abundance_dict_local[iso][i] = float(parts[2])

# Gather all abundances to rank 0
abundance_dict = {iso: np.zeros(len(tag)) for iso in isotopes}
for iso in isotopes:
    comm.Reduce(abundance_dict_local[iso], abundance_dict[iso], op=MPI.SUM, root=0)

if rank == 0:
    
    # -------------------------------------------------------------------------
    # PART 2: RGB COLORING (Unchanged)
    # -------------------------------------------------------------------------
    X_fuel = abundance_dict['c12'] + abundance_dict['o16']
    X_ime = abundance_dict['si28'] + abundance_dict['s32'] + abundance_dict['ca40']
    X_ige_s = abundance_dict['fe54'] + abundance_dict['fe56'] + abundance_dict['ni58']
    X_ni56 = abundance_dict['ni56']

    X_total = X_fuel + X_ime + X_ige_s + X_ni56
    X_total[X_total == 0] = 1e-30
    
    f_fuel = X_fuel / X_total
    f_ime = X_ime / X_total
    f_ige_s = X_ige_s / X_total
    f_ni56 = X_ni56 / X_total

    rgb_data = np.zeros((len(tag), 3))
    rgb_data[:, 0] = f_ige_s
    rgb_data[:, 1] = f_fuel
    rgb_data[:, 2] = f_ime

    ni_dom = f_ni56 > 0.5
    rgb_data[ni_dom, :] = 1.0

    rgb_data = np.clip(rgb_data, 0, 1)
    colors = [f'rgb({int(r*255)},{int(g*255)},{int(b*255)})' 
              for r, g, b in rgb_data]
    
    n_total = len(velx)
    hover_text = [f'Fuel: {f_fuel[i]:.3f}<br>IME: {f_ime[i]:.3f}<br>Stable IGE: {f_ige_s[i]:.3f}<br>Ni56: {f_ni56[i]:.3f}' 
                  for i in range(n_total)]

    # -------------------------------------------------------------------------
    # PART 3: NEW RADIUS-BASED OPACITY PLOTTING
    # -------------------------------------------------------------------------
    
    # 1. Calculate radius for all particles (assuming center is 0,0,0)
    r = np.sqrt(velx**2 + vely**2 + velz**2)
    r_max = np.max(r)
    
    # 2. Define slider steps and shell opacity
    # 9 steps from 1.0 down to 0.2 (1.0, 0.9, 0.8, ..., 0.2)
    slider_values = np.linspace(1.0, 0.1, 5) 
    shell_opacity = 0.1 # Opacity for particles in the outer "shell"

    fig = go.Figure()

    # 3. Create all traces (2 per slider step)
    for i, s in enumerate(slider_values):
        r_cutoff = s * r_max
        indices_core = np.where(r <= r_cutoff)[0]
        indices_shell = np.where(r > r_cutoff)[0]
        
        # Make the first step (1.0) visible by default
        is_visible = (i == 0) 
        
        # Add CORE trace (opacity 1.0)
        fig.add_trace(go.Scatter3d(
            x=velx[indices_core], y=vely[indices_core], z=velz[indices_core],
            mode='markers',
            marker=dict(size=2, color=[colors[j] for j in indices_core], opacity=1.0),
            text=[hover_text[j] for j in indices_core],
            hoverinfo='text',
            name=f'Core (r <= {s:.1f}*r_max)',
            visible=is_visible
        ))
        
        # Add SHELL trace (low opacity)
        fig.add_trace(go.Scatter3d(
            x=velx[indices_shell], y=vely[indices_shell], z=velz[indices_shell],
            mode='markers',
            marker=dict(size=2, color=[colors[j] for j in indices_shell], opacity=shell_opacity),
            text=[hover_text[j] for j in indices_shell],
            hoverinfo='text',
            name=f'Shell (r > {s:.1f}*r_max)',
            visible=is_visible
        ))

# 4. Create slider steps to control visibility
    steps = []
    num_traces_per_step = 2
    for i, s in enumerate(slider_values):
        # Calculate the actual cutoff velocity for the label
        r_cutoff = s * r_max
        
        # Create a visibility mask for all traces
        visibility_mask = [False] * (len(slider_values) * num_traces_per_step)
        
        # Set the two traces for this step to True
        visibility_mask[i * num_traces_per_step] = True
        visibility_mask[i * num_traces_per_step + 1] = True
        
        step = dict(
            method="update",
            args=[{"visible": visibility_mask}],
            # ADD THIS LINE: Set the label to the actual velocity value
            label=f"{r_cutoff:.1f}" 
        )
        steps.append(step)
    sliders = [dict(
        active=0,  # Start at the first step (1.0)
        # UPDATE THIS LINE: Change prefix and add suffix for units
        currentvalue={"prefix": "Core Velocity Cutoff: ", "suffix": " (10<sup>3</sup> km/s)"},
        pad={"t": 50},
        steps=steps
    )]
    # 5. Update layout
    fig.update_layout(
        title='tDDT: low central density model (1x10<sup>9</sup> g/cm<sup>3</sup>)',
        showlegend=False,  # <-- ADD THIS LINE
        scene=dict(
            xaxis=dict(
                title=dict(text='v<sub>x</sub> (10<sup>3</sup> km/s)', font=dict(color='white')),
                backgroundcolor='rgb(0, 0, 0)',
                gridcolor='rgb(70, 70, 70)',
                zerolinecolor='rgb(150, 150, 150)',
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                title=dict(text='v<sub>y</sub> (10<sup>3</sup> km/s)', font=dict(color='white')),
                backgroundcolor='rgb(0, 0, 0)',
                gridcolor='rgb(70, 70, 70)',
                zerolinecolor='rgb(150, 150, 150)',
                tickfont=dict(color='white')
            ),
            zaxis=dict(
                title=dict(text='v<sub>z</sub> (10<sup>3</sup> km/s)', font=dict(color='white')),
                backgroundcolor='rgb(0, 0, 0)',
                gridcolor='rgb(70, 70, 70)',
                zerolinecolor='rgb(150, 150, 150)',
                tickfont=dict(color='white')
            ),
            bgcolor='black'
        ),
        sliders=sliders,
        width=1000,
        height=900,
        annotations=[  # This is your custom "Color Legend", it will stay
            dict(
                text="<b>Color Legend:</b><br>" +
                     "<span style='color:rgb(255,0,0)'>■</span> Stable IGE (Fe, Ni58)<br>" +
                     "<span style='color:rgb(0,255,0)'>■</span> C/O Fuel<br>" +
                     "<span style='color:rgb(0,0,255)'>■</span> IME (Si, S, Ca)<br>" +
                     "<span style='color:rgb(255,255,255)'>■</span> Ni-56 Dominated",
                xref="paper", yref="paper",
                x=0.92, y=0.92,
                showarrow=False,
                bgcolor="rgba(0, 0, 0, 0.8)",
                bordercolor="white",
                font=dict(color="white"),
                borderwidth=1
            )
        ]
    )

    fig.write_html('structure_3d_LCD_opacity.html')
    print("3D plot saved to velocity_space_3d_radius_opacity.html")
