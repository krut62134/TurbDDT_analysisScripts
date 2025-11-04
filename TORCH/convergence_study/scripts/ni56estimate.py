import glob

# Directory containing the .dat files
data_directory = './../../../src/'

# Variable to store the sum of mass fractions for ni56
total_mass_fraction = 0.0

# Use glob to find all files matching the pattern out_*_final.dat
file_pattern = data_directory + "out_*_final.dat"
files = glob.glob(file_pattern)

# Loop through all matching files
for file_path in files:
    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            columns = line.strip().split()
            
            # Extract species and mass fraction
            species_name = columns[-1]
            mass_fraction = float(columns[-2])
            
            # Add mass fraction to the total if the species is ni56
            if species_name == 'ni56':
                total_mass_fraction += mass_fraction

# Divide the total sum of ni56 mass fractions by 9990
final_value = total_mass_fraction / 97431.0

print("Final result:", final_value)

