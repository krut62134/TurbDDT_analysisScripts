import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# File paths for the data files
files = {
    "e-1": "./1/out_33216_final.dat",
    "e-2": "./2/out_33216_final.dat",
    "e-3": "./3/out_33216_final.dat",
    "e-4": "./4/out_33216_final.dat",
    "e-5": "./5/out_33216_final.dat",
    "e-6": "./6/out_33216_final.dat",
    "e-7": "./7/out_33216_final.dat",
    "e-8": "./8/out_33216_final.dat"
}
# Row indices for species of interest (rows are zero-indexed in numpy)
row_indices = [12, 211, 213, 227, 243, 245,  272, 278]  # Corresponds to rows 13 and 273 in the data files

# Read the reference data (e-8 tolerance level)
ref_data = pd.read_csv(files["e-8"], sep='\s+', header=None)

# Extract the mass fraction from the relevant rows and columns (assuming mass fraction is in column 2)
ref_mass_fraction_c12 = ref_data.iloc[12, 2]  # Row 13, 3rd column (mass fraction)
ref_mass_fraction_cr52 = ref_data.iloc[211, 2]  # Row 273, 3rd column (mass fraction)
ref_mass_fraction_cr54 = ref_data.iloc[213, 2]  # Row 13, 3rd column (mass fraction)
ref_mass_fraction_mn55 = ref_data.iloc[227, 2]  # Row 273, 3rd column (mass fraction)
ref_mass_fraction_fe56 = ref_data.iloc[243, 2]  # Row 13, 3rd column (mass fraction)
ref_mass_fraction_fe58 = ref_data.iloc[245, 2]  # Row 273, 3rd column (mass fraction)
ref_mass_fraction_ni56 = ref_data.iloc[272, 2]  # Row 13, 3rd column (mass fraction)
ref_mass_fraction_ni62 = ref_data.iloc[278, 2]  # Row 273, 3rd column (mass fraction)

# Initialize lists to store L1 errors for each tolerance level
errors_c12 = []
errors_cr52 = []
errors_cr54 = []
errors_mn55 = []
errors_fe56 = []
errors_fe58 = []
errors_ni56 = []
errors_ni62 = []

# Iterate through tolerance files e-1 to e-7
for tol in ["e-1", "e-2", "e-3", "e-4", "e-5", "e-6", "e-7"]:
    # Read the data for the current tolerance using pandas
    data = pd.read_csv(files[tol], sep='\s+', header=None)
    
    # Extract mass fractions for row 13 and row 273
    mass_fraction_c12 = data.iloc[12, 2]  # 13th row (3rd column for mass fraction)
    mass_fraction_cr52 = data.iloc[211, 2]  # 273rd row (3rd column for mass fraction)
    mass_fraction_cr54 = data.iloc[213, 2]  # 13th row (3rd column for mass fraction)
    mass_fraction_mn55 = data.iloc[227, 2]  # 273rd row (3rd column for mass fraction)
    mass_fraction_fe56 = data.iloc[243, 2]  # 13th row (3rd column for mass fraction)
    mass_fraction_fe58 = data.iloc[245, 2]  # 273rd row (3rd column for mass fraction)
    mass_fraction_ni56 = data.iloc[272, 2]  # 13th row (3rd column for mass fraction)
    mass_fraction_ni62 = data.iloc[278, 2]  # 273rd row (3rd column for mass fraction)

    # Calculate the L1 error compared to the reference (e-8)
    c12 = abs(ref_mass_fraction_c12 - mass_fraction_c12)
    cr52 = abs(ref_mass_fraction_cr52 - mass_fraction_cr52)
    cr54 = abs(ref_mass_fraction_cr54 - mass_fraction_cr54)
    mn55 = abs(ref_mass_fraction_mn55 - mass_fraction_mn55)
    fe56 = abs(ref_mass_fraction_fe56 - mass_fraction_fe56)
    fe58 = abs(ref_mass_fraction_fe58 - mass_fraction_fe58)
    ni56 = abs(ref_mass_fraction_ni56 - mass_fraction_ni56)
    ni62 = abs(ref_mass_fraction_ni62 - mass_fraction_ni62)

    # Store the errors
    errors_c12.append(c12)
    errors_cr52.append(cr52)
    errors_cr54.append(cr54)
    errors_mn55.append(mn55)
    errors_fe56.append(fe56)
    errors_fe58.append(fe58)
    errors_ni56.append(ni56)
    errors_ni62.append(ni62)

# Plot the L1 errors for both rows
tolerances = ["e-1", "e-2", "e-3", "e-4", "e-5", "e-6", "e-7"]

ec12 = np.array(errors_c12)

l1_error_c12 = np.sum(np.abs(ec12)) / len(ec12)
print(l1_error_c12)

plt.plot(tolerances, errors_c12, label="C12")
plt.plot(tolerances, errors_cr52, label="cr52")
plt.plot(tolerances, errors_cr54, label="cr54")
plt.plot(tolerances, errors_mn55, label="mn55")
plt.plot(tolerances, errors_fe56, label="fe56")
plt.plot(tolerances, errors_fe58, label="fe58")
plt.plot(tolerances, errors_ni56, label="ni56")
plt.plot(tolerances, errors_ni62, label="ni62")

# Add labels and title
plt.xlabel("Tolerance Level")
plt.ylabel("L1 Error (Mass Fraction)")
plt.title("L1 Error for Mass Fraction at Different Tolerances")
plt.yscale('log')  # Set y-axis to logarithmic scale
plt.legend()
plt.grid(True)

# Save the plot instead of showing it
plt.savefig("convergence_study_67040.png")  # You can specify the file type (e.g., .png, .pdf)

# Optionally, you can also specify the resolution by adding 'dpi' 
# plt.savefig("l1_error_plot.png", dpi=300)

