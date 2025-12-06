import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # Added for square root calculation

# File paths for the data files
files = {
    "e-1": "./1/out_78399_final.dat",
    "e-2": "./2/out_78399_final.dat",
    "e-3": "./3/out_78399_final.dat",
    "e-4": "./4/out_78399_final.dat",
    "e-5": "./5/out_78399_final.dat",
    "e-6": "./6/out_78399_final.dat",
    "e-7": "./7/out_78399_final.dat",
    "e-8": "./8/out_78399_final.dat"
}
# Row indices for species of interest (rows are zero-indexed in numpy)
row_indices = [12, 211, 213, 227, 243, 245, 272, 278]

# Read the reference data (e-8 tolerance level)
ref_data = pd.read_csv(files["e-8"], sep='\s+', header=None)

# Extract the mass fractions for all species of interest
ref_mass_fractions = [
    ref_data.iloc[12, 2],  # C12
    ref_data.iloc[211, 2],  # Cr52
    ref_data.iloc[213, 2],  # Cr54
    ref_data.iloc[227, 2],  # Mn55
    ref_data.iloc[243, 2],  # Fe56
    ref_data.iloc[245, 2],  # Fe58
    ref_data.iloc[272, 2],  # Ni56
    ref_data.iloc[278, 2]   # Ni62
]

# Initialize lists to store L1 and L2 errors for each tolerance level
l1_errors = []
l2_errors = []

# Iterate through tolerance files e-1 to e-7
for tol in ["e-1", "e-2", "e-3", "e-4", "e-5", "e-6", "e-7"]:
    # Read the data for the current tolerance using pandas
    data = pd.read_csv(files[tol], sep='\s+', header=None)

    # Extract the mass fractions for all species of interest for the current tolerance
    mass_fractions = [
        data.iloc[12, 2],  # C12
        data.iloc[211, 2],  # Cr52
        data.iloc[213, 2],  # Cr54
        data.iloc[227, 2],  # Mn55
        data.iloc[243, 2],  # Fe56
        data.iloc[245, 2],  # Fe58
        data.iloc[272, 2],  # Ni56
        data.iloc[278, 2]   # Ni62
    ]

    # Calculate the L1 and L2 errors for the current tolerance
    l1_error = sum(abs(ref - mf) for ref, mf in zip(ref_mass_fractions, mass_fractions)) / len(mass_fractions)
    l2_error = np.sqrt(sum((ref - mf) ** 2 for ref, mf in zip(ref_mass_fractions, mass_fractions)) / len(mass_fractions))

    # Store the errors
    l1_errors.append(l1_error)
    l2_errors.append(l2_error)

    # Print the L1 and L2 errors for the current tolerance level
    print(f"L1 Error for {tol}: {l1_error}")
    print(f"L2 Error for {tol}: {l2_error}")

# Plot the L1 and L2 errors for each tolerance level
tolerances = ["e-1", "e-2", "e-3", "e-4", "e-5", "e-6", "e-7"]

plt.plot(tolerances, l1_errors, label="L1 Error", marker='o')
plt.plot(tolerances, l2_errors, label="L2 Error", marker='x')

# Add labels and title
plt.xlabel("Tolerance Level")
plt.ylabel("Error")
plt.title("L1 and L2 Errors for Mass Fraction at Different Tolerances")
plt.yscale('log')  # Set y-axis to logarithmic scale
plt.legend()
plt.grid(True)

# Save the plot instead of showing it
plt.savefig("l1_l2_error_67040.png", dpi=300)  # Save with high resolution


