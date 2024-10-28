import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt('/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/runs/runs_autoddt_thermalreact/run1/tDDT_sample.dat')

time = data[:, 0]
mass = data[:, 1]
x_momentum = data[:, 2]
y_momentum = data[:, 3]
z_momentum = data[:, 4]
IE_plus_KE = data[:, 5]
Kinetic_energy = data[:, 6]
Internal_energy = data[:, 7]
E_grav = data[:, 8]
E_restmass = data[:, 9]
E_nuc = data[:, 31]
E_neutloss = data[:, 10]
mass_burned = data[:, 11]
mass_burned_NSQE = data[:, 12]
mass_burned_NSE = data[:, 13]
mass_bunred_by_flame = data[:, 14]
estimated_Ni56 = data[:, 15]
bn_vol = data[:, 26]
max_den = data[:, 27]
min_flame_dens = data[:, 28]
T_max = data[:, 29]
P_tmax = data[:, 30]
x = data[:, 32]

plt.figure(figsize=(24, 40), facecolor="#FFFFFF")
plt.suptitle('Global Quantities tDDT OFFSET 100 km with bubble radius 16 km', fontsize=40, fontweight="bold")

# Mass
ax1 = plt.subplot(8, 3, 1)
ax1.plot(time, mass)
ax1.set_title('Mass')
ax1.set_yscale('log')

# X_momentum
ax2 = plt.subplot(8, 3, 2)
ax2.plot(time, x_momentum)
ax2.set_title('X-Momentum')
#ax2.set_yscale('log')

# Y_Momentum
ax3 = plt.subplot(8, 3, 3)
ax3.plot(time, y_momentum)
ax3.set_title('Y-Momentum')
#ax3.set_yscale('log')

# Z_Momentum
ax4 = plt.subplot(8, 3, 4)
ax4.plot(time, z_momentum)
ax4.set_title('Z-Momentum')
#ax4.set_yscale('log')

# Total_energy
ax5 = plt.subplot(8, 3, 5)
ax5.plot(time, IE_plus_KE)
ax5.set_title('Internal + Kinetic Energy')
ax5.set_yscale('log')

# Internal_energy
ax6 = plt.subplot(8, 3, 6)
ax6.plot(time, Internal_energy)
ax6.set_title('Internal Energy')
ax6.set_yscale('log')

# Kinetic_energy with log scale
ax7 = plt.subplot(8, 3, 7)
ax7.plot(time, Kinetic_energy)
ax7.set_yscale('log')
ax7.set_title('Kinetic Energy')

# Gravitational_Energy
ax8 = plt.subplot(8, 3, 8)
ax8.plot(time, E_grav)
ax8.set_title('Gravitational Energy')
#ax8.set_yscale('log')

# Restmass_energy
ax9 = plt.subplot(8, 3, 9)
ax9.plot(time, E_restmass)
ax9.set_title('Restmass Energy')
#ax9.set_yscale('log')

# Nuclear_energy
ax10 = plt.subplot(8, 3, 10)
ax10.plot(time, E_nuc)
ax10.set_yscale('log')
ax10.set_title('Specific Nuclear Energy Rate')

# Energy_Nutrino
ax11 = plt.subplot(8, 3, 11)
ax11.plot(time, E_neutloss)
ax11.set_title('Nutrino Energy')
ax11.set_yscale('log')

# Mass_burned
ax12 = plt.subplot(8, 3, 14)
ax12.plot(time, mass_burned)
ax12.set_title('Mass Burned')
ax12.set_yscale('log')

# Mass_burned_NSQE
ax13 = plt.subplot(8, 3, 15)
ax13.plot(time, mass_burned_NSQE)
ax13.set_title('Mass Burned (NSQE)')
ax13.set_yscale('log')

# Mass_burned_NSE
ax14 = plt.subplot(8, 3, 16)
ax14.plot(time, mass_burned_NSE)
ax14.set_title('Mass Burned (NSE)')
ax14.set_yscale('log')

# Mass_burned_by_flame
ax15 = plt.subplot(8, 3, 17)
ax15.plot(time, mass_bunred_by_flame)
ax15.set_title('Mass Burned by Flame')
ax15.set_yscale('log')

# Estimated mass of Ni56
ax16 = plt.subplot(8, 3, 18)
ax16.plot(time, estimated_Ni56)
ax16.set_title('Estimated Mass of Ni56')
ax16.set_yscale('log')

# Burned_volume
ax17 = plt.subplot(8, 3, 12)
ax17.plot(time, bn_vol)
ax17.set_title('Burned Volume')
ax17.set_yscale('log')

# Maximum_density
ax18 = plt.subplot(8, 3, 19)
ax18.plot(time, max_den)
ax18.set_title('Maximum Density')
ax18.set_yscale('log')

# Minimum Flame density
ax19 = plt.subplot(8, 3, 20)
ax19.plot(time, min_flame_dens)
ax19.set_title('Minimum Flame Density')
ax19.set_yscale('log')

# Maximum_temperature
ax20 = plt.subplot(8, 3, 21)
ax20.plot(time, T_max)
ax20.set_title('Max Temperature')
ax20.set_yscale('log')

# Maximum_pressure
ax21 = plt.subplot(8, 3, 22)
ax21.plot(time, P_tmax)
ax21.set_title('Max. Pressure at T_max')
ax21.set_yscale('log')

# KE + Internal E + GravBind (Internal E - Enuc) per m
ax22 = plt.subplot(8, 3, 13)
ax22.plot(time, x)
ax22.set_title('KE + IE + GravBind (Internal E - Enuc) per m')
#ax22.set_yscale('log')

plt.savefig("Global_Quantities_2.png")

