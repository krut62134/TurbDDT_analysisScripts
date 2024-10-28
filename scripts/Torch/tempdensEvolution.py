import numpy as np
import matplotlib.pyplot as plt

# Load the .dat file
data = np.loadtxt('./data/tempdens99807.dat')

# Extracting the first, second, and third arrays (columns)
x = data[:, 0]  # First array (1st column)
y1 = data[:, 1] # Second array (2nd column)
y2 = data[:, 2] # Third array (3rd column)

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

# Plot 1: First array vs Second array
ax1.plot(x, y1)
ax1.set_xlabel('Time')
ax1.set_ylabel('Temp')
ax1.set_title('temp evolution')
ax1.set_yscale('log')

# Plot 2: First array vs Third array
ax2.plot(x, y2)
ax2.set_xlabel('Time')
ax2.set_ylabel('Dens')
ax2.set_title('Dens evolution')
ax2.set_yscale('log')

# Adjust layout and show the plot
fig.tight_layout()
fig.savefig("99807.png")

