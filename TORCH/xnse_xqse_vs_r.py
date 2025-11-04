#####################################################################
# This plots NSE and QSE estimate vs radius in the Eulerial grid    #
# Only useful for the DDT or tDDT models                            #
# Change the path to your plt file before using                     #
#  ~krut patel 110125                                               #
#####################################################################

import yt
import numpy as np

# Load the dataset
ds = yt.load("./../tDDT_hd_o12r32_HLLC_Roe_hdf5_plt_cnt_001707")

# Define derived field for X_QSE (phaq - phqn)
def _xqse(field, data):
    return data["phaq"] - data["phqn"]

ds.add_field(
    ("gas", "xqse"),
    function=_xqse,
    sampling_type="cell",
    units="dimensionless"
)

# Create a sphere encompassing the full domain centered at domain center
center = "c"
radius = ds.domain_width.max()  # Use maximum domain width as radius
my_sphere = ds.sphere(center, radius)

# Create radial profile plot with both X_NSE (phqn) and X_QSE (xqse)
# Volume-weighted average vs radius
plot = yt.ProfilePlot(
    my_sphere,
    ("index", "radius"),
    [("gas", "phqn"), ("gas", "xqse")],
    weight_field=("index", "cell_volume"),  # Volume-weighted
)

# Customize the plot
plot.set_log(("index", "radius"), False)  # Linear radius axis
plot.set_log(("gas", "phqn"), False)      # Linear for X_NSE
plot.set_log(("gas", "xqse"), False)      # Linear for X_QSE

# Set axis labels
plot.set_xlabel("Radius (cm)")
plot.set_ylabel("Volume-weighted Average")

# Add units
plot.set_unit(("index", "radius"), "km")

# Save the plot
plot.save("radial_profile_nse_qse.png")

print("Plot saved as radial_profile_nse_qse.png")
