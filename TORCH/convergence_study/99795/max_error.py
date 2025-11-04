import pandas as pd
import numpy as np

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

# Extract the species names from the fourth column of the reference file
species_names = ref_data.iloc[:, 3].tolist()

# Loop through the tolerance levels e-1 to e-7
for tol in ["e-1", "e-2", "e-3", "e-4", "e-5", "e-6", "e-7"]:
    # Read the data for the current tolerance
    data = pd.read_csv(files[tol], sep='\s+', header=None)

    # Extract the mass fractions from all rows (assumed to be in column 2)
    mass_fractions = data.iloc[:, 2]

    # Calculate the L1 error for all rows (species)
    l1_errors = [abs(ref - mf) for ref, mf in zip(ref_mass_fractions, mass_fractions)]

    # Combine the L1 errors with species names
    output_data = list(zip(l1_errors, species_names))

    # Sort the data by L1 error in descending order
    output_data_sorted = sorted(output_data, key=lambda x: x[0], reverse=True)

    # Generate the output filename based on the tolerance level
    output_file = f"errors_{tol}_sorted_67040.dat"

    # Write the sorted results to the .dat file
    with open(output_file, "w") as f:
        f.write(f"# L1 Error for {tol} with reference to e-8 for each species (sorted by error)\n")
        f.write("# L1_Error    Species\n")
        for error, species in output_data_sorted:
            f.write(f"{error:.8e}    {species}\n")  # Using scientific notation for the error

    print(f"Sorted L1 errors for {tol} compared to e-8 saved to {output_file}")

print("L1 error files for all tolerance levels generated successfully!")

