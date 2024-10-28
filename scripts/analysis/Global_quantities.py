import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt('/project/pi_rfisher1_umassd_edu/SNIa_turbDDT/runs/run_1a_mxb250_autoddt_thermalreact/tDDT_1a.dat')

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
print(E_nuc)
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


plt.figure(figsize=(24,40),facecolor="#FFFFFF")
plt.suptitle('Global Quantities tDDT OFFSET 100 km with bubble radius 16 km',fontsize = 40, fontweight="bold")

#Mass
plt.subplot(8, 3, 1)
plt.plot(time, mass)
plt.title('Mass')
#X_momentum
plt.subplot(8, 3, 2)
plt.plot(time, x_momentum)
plt.title('X-Momentum')
#Y_Momentum
plt.subplot(8, 3, 3)
plt.plot(time, y_momentum)
plt.title('Y-Momentum')
#Z_Momentum
plt.subplot(8, 3, 4)
plt.plot(time, z_momentum)
plt.title('Z-Momentum')
#Total_energy
plt.subplot(8, 3, 5)
plt.plot(time, IE_plus_KE)
plt.title('Internal + Kinetic Energy')
#Internal_energy
plt.subplot(8, 3, 6)
plt.plot(time, Internal_energy)
plt.title('Internal_energy')
#Kinetic_energy
plt.subplot(8, 3, 7)
plt.plot(time, Kinetic_energy)
plt.title('Kinetic_energy')
#Gravitational_Energy
plt.subplot(8, 3, 8)
plt.plot(time, E_grav)
plt.title('Gravitational Energy')
#Restmass_energy
plt.subplot(8, 3, 9)
plt.plot(time, E_restmass)
plt.title('Restmass Energy')
#Nuclear_energy
plt.subplot(8, 3, 10)
plt.plot(time, E_nuc)
plt.title('Specific Nuclear Energy rate')
#Energy_Nutrino
plt.subplot(8, 3, 11)
plt.plot(time, E_neutloss)
plt.title('Nutrino Energy')
#Mass_burned
plt.subplot(8, 3, 12)
plt.plot(time, mass_burned)
plt.title('Mass Burned')
#Mass_burned_NSQE
plt.subplot(8, 3, 13)
plt.plot(time, mass_burned_NSQE)
plt.title('Mass Burned (NSQE)')
#Mass_burned_NSE
plt.subplot(8, 3, 14)
plt.plot(time,mass_burned_NSE )
plt.title('Mass Burned (NSE)')
#Mass_burned_by_flame
plt.subplot(8, 3, 15)
plt.plot(time, mass_bunred_by_flame)
plt.title('Mass Burned by flame')
#Estimated mass of Ni56
plt.subplot(8, 3, 16)
plt.plot(time, estimated_Ni56)
plt.title('Estimated Mass of Ni56')
#Burned_volume
plt.subplot(8, 3, 17)
plt.plot(time, bn_vol)
plt.title('Burned Volume')
#Maximum_density
plt.subplot(8, 3, 18)
plt.plot(time, max_den)
plt.title('Maximum Density')
#Mimimum Flame density
plt.subplot(8, 3, 19)
plt.plot(time, min_flame_dens)
plt.title('Minimum Flame density')
#Maximum_temperature
plt.subplot(8, 3, 20)
plt.plot(time, T_max)
plt.title('Max Temperature')
#Maximum_pressure
plt.subplot(8, 3, 21)
plt.plot(time, P_tmax)
plt.title('Max. Pressure at T_max')
#KE + Internal E+ GravBind (Internal E - Enuc) per m
plt.subplot(8, 3, 22)
plt.plot(time, x)
plt.title('KE + IE+ GravBind (Internal E - Enuc) per m')

#plt.xlim(0,83.0)
plt.yscale('log')
plt.savefig("Global_Quantities.png")
