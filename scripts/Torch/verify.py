## This script was wiritten by sneopane to convert isotopic abundances to chemical abundances
## We can also use it to calculate IGE ratios and total abundance of a given isotope

import numpy as np

nfiles = 9992 #Total number of particles
nelements = 92 #Total number of elements output by Torch

Mn = 0
Ni = 0
Cr = 0
Fe = 0

## USe glob in case particles were lost !kbhargava
for f in range(nfiles):
    fname = 'out_' + str(f+1) + '_decayed.dat'
    file = open(fname,'r') #Open the file
    file_length = file.readlines() #Lines in the files

    atomic_number = [] # Array stores the atomic numbers
    baryon_number = []  # Array to store baryon number
    mass_fraction = []  # Array to store mass fraction
    isotope_array = [] # 2D array with indices of isotopes grouped together
    atomic_number_array = []
    baryon_number_array = [] # 2D array with baryon number grouped together
    mass_fraction_array = [] # 2D array with mass fraction grouped together
    all_mass_fraction = np.zeros(int(nelements))

    for line in file_length: #Loop over the lines in files
        lst = line.split() # Split each line into a list
        atomic_number.append(int(lst[0])) # Reading atomic number
        baryon_number.append(int(lst[1])) # Reading baryon number
        mass_fraction.append(float(lst[2])) #Reading abundances

    file.close()

    atomic_number = np.array(atomic_number) 

    for i in range(nelements):
        array = np.where(atomic_number == i+1) # Find the elements with specific atomic number
        isotope_array.append(array[0])  # Genertaing a 2D list

    isotope_array = np.array(isotope_array, dtype = object)

    for a in range(nelements): # Specifies the atomic number of element
        empty_atomic = [] 
        empty_baryon = [] # List to store Baryon number array for paticular element
        empty_fraction = []  # List yo store mass fraction array for paticular element

        for b in isotope_array[a]:
            empty_atomic.append(atomic_number[b])
            empty_baryon.append(baryon_number[b]) 
            empty_fraction.append(mass_fraction[b])

        atomic_number_array.append(np.array(empty_atomic))    
        baryon_number_array.append(np.array(empty_baryon)) # 2D list being created
        mass_fraction_array.append(np.array(empty_fraction)) # 2D list being created

    atomic_number_array = np.array(atomic_number_array, dtype = object)
    baryon_number_array = np.array(baryon_number_array, dtype = object) # Convert to numpy array
    mass_fraction_array = np.array(mass_fraction_array, dtype = object)

    for j in range(nelements):   # Storing all the  elements
        all_mass_fraction[j] = sum(mass_fraction_array[j])

    Mn = Mn + all_mass_fraction[24] #Summing over Mn abundance for all particles
    Ni = Ni + all_mass_fraction[27] #Summing over Ni abundance for all particles
    Cr = Cr + all_mass_fraction[23] #Summing over Cr abundance for all particles
    Fe = Fe + all_mass_fraction[25] #Summing over Fe abundance for all particles
   
r1 = Mn/Fe
r2 = Ni/Fe
r3 = Cr/Fe

print(r1,r2,r3)

