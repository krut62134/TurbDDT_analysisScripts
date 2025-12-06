import matplotlib.pyplot as plt
import numpy as np


time, temp , dens = np.loadtxt('./../../../history/tempdens78399.dat', usecols=(0,1,2), unpack = True)


plt.figure(figsize=(12, 4), facecolor="#FFFFFF")
plt.subplot(1,2,1)
plt.plot(time, temp)
plt.xlim(0.0, 0.6)
plt.ylim(1.0e8,2.0e10)
plt.yscale('log')
plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.subplot(1,2,2)
plt.plot(time, dens)
plt.xlim(0.0, 0.6)
plt.yscale('log')
plt.xlabel('Time (s)')
plt.ylabel('Density (gm/cm^3)')
plt.savefig("tempVsTime.png")
