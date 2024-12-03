import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # Needed for square root calculation

# File paths for the data files
files = {
    "e-1": "./1/out_99795_final.dat",
    "e-2": "./2/out_99795_final.dat",
    "e-3": "./3/out_99795_final.dat",
    "e-4": "./4/out_99795_final.dat",
    "e-5": "./5/out_99795_final.dat",
    "e-6": "./6/out_99795_final.dat",
    "e-7": "./7/out_99795_final.dat",
    "e-8": "./8/out_99795_final.dat"
}
# Read the reference data (e-8 tolerance level)
ref_data = pd.read_csv(files["e-8"], sep='\s+', header=None)

# Extract the reference mass fractions from all rows (assumed to be in column 2)
ref_mass_fractions = ref_data.iloc[:, 2]

# Initialize lists to store L1 and L2 errors for each tolerance level
l1_errors = []
l2_errors = []

# Iterate through tolerance files e-1 to e-7
for tol in ["e-1", "e-2", "e-3", "e-4", "e-5", "e-6", "e-7"]:
    # Read the data for the current tolerance using pandas
    data = pd.read_csv(files[tol], sep='\s+', header=None)
    
    # Extract the mass fractions from all rows (assumed to be in column 2)
    mass_fractions = data.iloc[:, 2]

    # Calculate the L1 and L2 errors for all rows
    l1_error = sum(abs(ref - mf) for ref, mf in zip(ref_mass_fractions, mass_fractions)) / len(ref_mass_fractions)
    l2_error = np.sqrt(sum((ref - mf) ** 2 for ref, mf in zip(ref_mass_fractions, mass_fractions)) / len(ref_mass_fractions))

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
plt.title("L1 and L2 Errors for Mass Fraction at Different Tolerances (All Rows)")
plt.yscale('log')  # Set y-axis to logarithmic scale
plt.legend()
plt.grid(True)

# Save the plot instead of showing it
plt.savefig("l1_l2_error_all_species_67040.png", dpi=300)  # Save with high resolution

