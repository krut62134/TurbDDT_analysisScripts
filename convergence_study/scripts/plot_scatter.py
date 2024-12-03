import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import pandas as pd

# Load the position data (replace with actual path)
pos_data = np.loadtxt('./../../../example/pos.dat')

# Assuming the columns in 'pos.dat' are structured like:
# column 1: x position, column 2: y position, column 3: z position, column 4: tag (particle identifier)
x = pos_data[:, 1]  # x positions (2nd column)
y = pos_data[:, 2]  # y positions (3rd column)
z = pos_data[:, 3]  # z positions (4th column)
tags = pos_data[:, 4].astype(int)  # tag numbers (5th column, converted to integers)

# Path to the final files (replace with actual path)
final_files_path = './../../../src/'

# Get all final files in the directory
final_files = glob.glob(os.path.join(final_files_path, 'out_*_final.dat'))

# Initialize lists for storing positions and mass fractions
x_plot = []
y_plot = []
z_plot = []
mass_fraction_plot = []

# Function to extract the ni56 mass fraction from a final file
def extract_mass_fraction(file_path):
    try:
        # Replaced delim_whitespace=True with sep='\s+'
        df = pd.read_csv(file_path, sep='\s+', header=None)
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

        # Extract the corresponding x, y, z positions for this tag
        x_tag = x[tag_index]
        y_tag = y[tag_index]
        z_tag = z[tag_index]

        # Extract the mass fraction for ni56
        mass_fraction = extract_mass_fraction(final_file)

        # If the mass fraction was found, add it to the plot data
        if mass_fraction is not None:
            x_plot.append(x_tag)
            y_plot.append(y_tag)
            z_plot.append(z_tag)
            mass_fraction_plot.append(mass_fraction)

# Create a function to make scatter plots
def create_scatter_plot(x_data, y_data, mass_data, xlabel, ylabel, plot_name):
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(x_data, y_data, c=mass_data, cmap='viridis', s=1)  # Adjust marker size with 's'

    # Add a colorbar to show the mass fraction values
    plt.colorbar(scatter, label='Mass Fraction (ni56)')

    # Set x and y axis limits symmetrically around 0
    plt.xlim(min(min(x_data), -max(x_data)), max(max(x_data), -min(x_data)))
    plt.ylim(min(min(y_data), -max(y_data)), max(max(y_data), -min(y_data)))

    # Add labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f'Mass Fraction Scatter Plot for {xlabel} vs {ylabel}')

    # Save the plot instead of displaying it
    plt.savefig(plot_name)
    plt.close()

# Create 3 scatter plots:
# 1. x vs y
create_scatter_plot(x_plot, y_plot, mass_fraction_plot, "X Position", "Y Position", "mass_fraction_scatter_plot_xy.png")

# 2. y vs z
create_scatter_plot(y_plot, z_plot, mass_fraction_plot, "Y Position", "Z Position", "mass_fraction_scatter_plot_yz.png")

# 3. z vs x
create_scatter_plot(z_plot, x_plot, mass_fraction_plot, "Z Position", "X Position", "mass_fraction_scatter_plot_zx.png")

