import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/runs/runs_autoddt_thermalreact/run1/tDDT_sample.dat')

# Extract time and enuc columns
time = data[:, 0]  
enuc = data[:, 31]
print('enuc',enuc)
dt = []

# Calculate dt for each timestep
for i in range(1, len(time)):
    dt.append(time[i] - time[i-1])  

dt = np.array(dt)
print('dt',dt)

#Calculate the integral
integral = np.cumsum(enuc[1:]*dt)

print('max_integral',np.max(integral))
print('integral',integral)

# Plotting
plt.figure(figsize=(8, 6))
#print(dt)
#print(dt)
plt.plot(time[1:], integral[:])
plt.yscale('log')
plt.xlabel('Time')
plt.ylabel('cumulative enuc')
plt.title('The cumulative energy release vs time')
plt.grid(True)
plt.savefig('enuc_integral_vs_time.png')
#plt.savefig('a.png')
