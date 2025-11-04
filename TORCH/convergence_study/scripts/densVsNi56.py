import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import pandas as pd

# Load the position data (replace with actual path)
pos_data = np.loadtxt('./../../../example/dens_pos.dat')

# Assuming the columns in 'pos.dat' are structured like:
# column 1: x position, column 2: y position, column 3: z position, column 4: tag (particle identifier), column 5: density
x = pos_data[:, 1]  # x positions (2nd column)
y = pos_data[:, 2]  # y positions (3rd column)
z = pos_data[:, 3]  # z positions (4th column)
dens = pos_data[:, 5]  # density (5th column)
tags = pos_data[:, 4].astype(int)  # tag numbers (5th column, converted to integers)

# Path to the final files (replace with actual path)
final_files_path = './../../../src/'

# Get all final files in the directory
final_files = glob.glob(os.path.join(final_files_path, 'out_*_final.dat'))

# Initialize lists for storing density and mass fractions
dens_plot = []  # density values for the plot
mass_fraction_plot = []  # ni56 mass fraction values for the plot

# Function to extract the ni56 mass fraction from a final file
def extract_mass_fraction(file_path):
    try:
        df = pd.read_csv(file_path, sep='\s+', header=None)  # Updated to use sep='\s+' instead of delim_whitespace=True
        # Find the row with 'ni56' in the last column
        ni56_row = df[df[3] == 'ni56']
        if not ni56_row.empty:
            return float(ni56_row.iloc[0, 2])  # 3rd column (index 2) has the mass fraction
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return None

# Loop over each final file
for final_file in final_files:
    # Extract the tag number from the filename (e.g., 'out_9991_final.dat')
    tag_number = int(os.path.basename(final_file).split('_')[1])

    # Check if this tag exists in the position data
    if tag_number in tags:
        # Get the index of the matching tag in pos_data
        tag_index = np.where(tags == tag_number)[0][0]

        # Extract the corresponding density for this tag
        dens_tag = dens[tag_index]

        # Extract the mass fraction for ni56
        mass_fraction = extract_mass_fraction(final_file)

        # If the mass fraction was found, add it to the plot data
        if mass_fraction is not None:
            dens_plot.append(dens_tag)
            mass_fraction_plot.append(mass_fraction)

# Create a scatter plot for density vs mass fraction (ni56) with logarithmic x-axis
plt.figure(figsize=(8, 6))
scatter = plt.scatter(dens_plot, mass_fraction_plot, c=mass_fraction_plot, cmap='viridis', s=1)
plt.colorbar(scatter, label='Mass Fraction (ni56)')
plt.xscale('log')  # Set x-axis (density) to log scale
plt.xlabel('Density (log scale)')
plt.ylabel('Mass Fraction (ni56)')
plt.title('Density (log scale) vs Mass Fraction (ni56)')
plt.savefig('density_vs_mass_fraction_log.png')
plt.close()

