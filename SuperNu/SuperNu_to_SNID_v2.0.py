# Converts SuperNu outputs (wavelength & spectral flux) into SNID format
# VERSION 2.0
# author: Mckenzie Ferrari
# last updated: June 22, 2021

import numpy as np

sourceFileWV = input("Enter file name for WAVELENGTHS (i.e. __grid): ")
sourceFileFLX = input("Enter file name for FLUX/LUMINOSITY (i.e. __luminos): ")

# # # CREATING ARRAYS FOR DATASETS # # #
# wvData = np.array([])
flxData = np.array([])
wvDataMod = np.array([])

# # # LOADING FIRST NON-COMMENTED LINE FROM _GRID FILE # # #
wvData = np.loadtxt(sourceFileWV, max_rows=1)
# print("original values of wavelengths (cm): ", wvData)

# # # CALCULATING DLAMBDA FROM FIRST TWO VALUES OF WV (TO THEN CALCULATE PEAK BRIGHTNESS) # # #
dlambda = wvData[1] - wvData[0]
# print(dlambda)

# # # CONVERTING WAVELENGTH VALUES FROM CM TO ANGSTROMS # # #
for i in range(len(wvData)):
    wvData[i] = (wvData[i]) * (10**8)
wvData = wvData[:-1]  # REMOVES LAST WAVELENGTH VALUE TO MATCH # OF FLUX VALUES
# print("converted values of wavelengths (Angstrom): ", wvData)

# # # FINDING NUMBER OF USABLE LINES IN LUMINOSITY FILE (TO THEN FIND PEAK BRIGHT.) # # #
inFileFLX = open(sourceFileFLX, "r")
nonempty_lines = [line.strip("\n") for line in inFileFLX if line != "\n"]
line_count = len(nonempty_lines)
inFileFLX.close()
# print(line_count)

# # # FINDING PEAK BRIGHTNESS LINE AND TOTAL MAX FLUX # # #
totalFLX = []
flxData = np.loadtxt(sourceFileFLX)
# print(flxData)

for i in range(0, line_count):
    sumNum = sum(flxData[i])
    totalFLX.append(sumNum)

# # # CHECKING IF CORRECT NUMBER OF LINES ARE READ # # #
if line_count == len(totalFLX):
    print("Correct number of lines read.")
else:
    print("INCORRECT number of lines read. Abort!")

# # # FINDING PEAK BRIGHTNESS (ctd.) # # #
maxElement = np.amax(totalFLX)
# print('Max total value of flux : ', maxElement)
result = np.where(totalFLX == np.amax(totalFLX))              # locating max total flux value in array
# print('Returned tuple of arrays :', result)     # returning array value (array starts at 0 so below adds 1)
peakDay = result[0]+1
print('Peak brightness found at LINE %.1d out of %.1d' % (peakDay, line_count))
# print("Max Total Values of flux for file: ", totalFLX)
# print("Number of Lines read: ", len(totalFLX))

# # # NORMALIZING FLUX VALUES TO AVOID OVERFLOW IN SNID # # #
meanPeak = maxElement / 500  # normalization using peak brightness and BIN SIZE

# # # ASKING TO USE PEAK BRIGHTNESS, CORRECTING IF NOT; PREPARING FOR PRINTING OUTPUT FILE # # #
day = 0
question = input("Would you like to use this line at peak brightness? (Y/n): ")
if question == 'Y':
    day = peakDay
elif question != 'Y':
    day = input("Which line would you like to use instead?: ")

day = int(day)
flxData = flxData[day, :]
flxDataList = []
flxDataNew = np.array([])
for i in range(len(flxData)):
    # print((flxData[i] / meanPeak))
    flxDataList.append((flxData[i] / meanPeak))
    np.append(flxDataNew, [flxData[i]])
# print(flxDataList)
# print(len(flxDataList))
# np.reshape(flxData, (1, 500))
# print("wavelengths length:", len(wvData))
# print("flx length: ", len(flxData))

# # # PRINTING VALUES TO SNID-FORMATTED FILE # # #
newfile = input("Enter file name for OUTPUT (without .dat): ") + '.dat'
with open(newfile, 'w') as f:
    f.writelines("# wavelength (angstrom)  .    spectral flux ( ) \n")
    for y in range(len(wvData)):                                 # using length of values of WVs (wvDataMod)
        write_buffer = str(wvData[y]) + "  " + str(flxDataList[y])   # printing the conv. values of wvData (wvDataMod)
        f.writelines(write_buffer)
        f.writelines("\n")
        # print(write_buffer)                                      # printing values to new file

print("Generated", newfile, "for line %.1d of %.1d" % (day, line_count))

''' IGNORE
chosen_epoch_values = np.array([])
for i in range(len(wvData)):
    np.append(chosen_epoch_values, [wvData, flxData], axis=0)
# chosen_epoch_values = np.array([wvData, flxData[day]], dtype=object)
print(chosen_epoch_values)


output_name = newfile + '.dat'
np.savetxt(output_name, chosen_epoch_values, delimiter="  ", header="WV  FLX", comments="#")'''
