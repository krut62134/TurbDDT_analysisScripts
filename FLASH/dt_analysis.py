import re
import matplotlib.pyplot as plt

# Read the log file
with open('tDDT_hd_o12r32_HLLC_Roe2.log', 'r') as f:
    lines = f.readlines()

# Extract n and dt values
n_values = []
dt_values = []

for line in lines:
    if 'step: n=' in line and 'dt=' in line:
        # Extract n
        n_match = re.search(r'n=(\d+)', line)
        # Extract dt
        dt_match = re.search(r'dt=([\d.E+-]+)', line)
        
        if n_match and dt_match:
            n_values.append(int(n_match.group(1)))
            dt_values.append(float(dt_match.group(1)))

# Calculate average dt
avg_dt = sum(dt_values) / len(dt_values)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(n_values, dt_values, marker='o', markersize=3, linestyle='-')
plt.xlabel('n')
plt.ylabel('dt')
plt.title(f'dt vs n (Average dt = {avg_dt:.6e})')
plt.grid(True)
plt.savefig('dt_plot.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"Average dt: {avg_dt:.6e}")
print(f"Total data points: {len(dt_values)}")
