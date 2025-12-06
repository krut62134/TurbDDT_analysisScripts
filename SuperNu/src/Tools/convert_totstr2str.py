#!/usr/bin/env python

#-- importing libraries
from scipy import stats
import numpy as np
import argparse
import matplotlib.pyplot as plt

#-- constructing parse field
parser = argparse.ArgumentParser(description = 'Map general ejecta structure to SuperNu input.str.')
parser.add_argument('f', type=str, help='General input structure.')
parser.add_argument('--gen_instr', action="store_true", help='Generate input structure.')

#-- parsing arguments
args = parser.parse_args()

#-- load general input structure
gen_str = np.loadtxt(args.f, skiprows=3)

num_round = 4

#-- get spatial grids and velocities
nrow = np.size(gen_str, 0)
print()
print('nrow = ', nrow)
xleft, xlindx = np.unique(gen_str[:,0].round(num_round), return_index=True)
xrigh, xrindx = np.unique(gen_str[:,1].round(num_round), return_index=True)
yleft, ylindx = np.unique(gen_str[:,2].round(num_round), return_index=True)
yrigh, yrindx = np.unique(gen_str[:,3].round(num_round), return_index=True)
zleft, zlindx = np.unique(gen_str[:,4].round(num_round), return_index=True)
zrigh, zrindx = np.unique(gen_str[:,5].round(num_round), return_index=True)
#-- get number of cells along each dimension
nx = np.size(xleft)
ny = np.size(yleft)
nz = np.size(zleft)
print()
print('nx = ', nx)
print('ny = ', ny)
print('nz = ', nz)
if(np.size(xrigh) != nx): print('np.size(xrigh) != nx')
if(np.size(yrigh) != ny): print('np.size(yrigh) != ny')
if(np.size(zrigh) != nz): print('np.size(zrigh) != nz')

#-- get radial component of each velocity
xcoors = 0.5 * (gen_str[:,0] + gen_str[:,1])
ycoors = 0.5 * (gen_str[:,2] + gen_str[:,3])
zcoors = 0.5 * (gen_str[:,4] + gen_str[:,5])
vxcoors = 0.5 * (gen_str[:,6] + gen_str[:,7])
vycoors = 0.5 * (gen_str[:,8] + gen_str[:,9])
vzcoors = 0.5 * (gen_str[:,10] + gen_str[:,11])
rcoor = np.array(nrow * [0.0])
vrcoor = np.array(nrow * [0.0])
vperpr = np.array(nrow * [0.0])
for irow in range(nrow):
    rcoor[irow] = np.sqrt(xcoors[irow] * xcoors[irow] + \
                          ycoors[irow] * ycoors[irow] + \
                          zcoors[irow] * zcoors[irow])
    vrcoor[irow] = xcoors[irow] * vxcoors[irow] + \
                   ycoors[irow] * vycoors[irow] + \
                   zcoors[irow] * vzcoors[irow]
    vrcoor[irow] /= rcoor[irow]
    vperpr[irow] = np.sqrt(vxcoors[irow] * vxcoors[irow] +
                           vycoors[irow] * vycoors[irow] +
                           vzcoors[irow] * vzcoors[irow] -
                           vrcoor[irow] * vrcoor[irow])

#-- plot radial velocity vs radious
plt.figure()
plt.plot(rcoor, vrcoor, '*', label='Radial Projection')
plt.plot(rcoor, vperpr, '*', label='Perpendicular Magnitude')
plt.legend()
plt.xlabel('Radius [cm]')
plt.ylabel('Velocity [cm/s]')
plt.show(block=False)

#-- choose radius at which to truncate linear regression
r_cutoff = float(input('Select radial cutoff for linear regression of velocity: '))
# r_cutoff = 3.5e10
slope, intercept, r_value, p_value, std_err = stats.linregress(rcoor[rcoor < r_cutoff],vrcoor[rcoor < r_cutoff])
print('slope, intercept, r_value, p_value, std_err = ', slope, intercept, r_value, p_value, std_err)

#-- plot linear regression
plt.figure()
plt.plot(rcoor, vrcoor, '*', label='Radial Projection')
plt.plot(rcoor, slope * rcoor, '--', label='Homologous')
plt.legend()
plt.xlabel('Radius [cm]')
plt.ylabel('Velocity [cm/s]')
plt.xlim([0.0, 5.0e10])
plt.ylim([-3.0e8, 3.0e9])
plt.show()

if(args.gen_instr):
    #-- generate a reduced input structure for supernu (-6 for true velocities, -1 for density)
    ncol = np.size(gen_str, 1)
    ncol_spn = ncol - 6
    spn_str = []
    for irow in range(nrow):
        #-- z-bound condition
        l_inz = abs(zcoors[irow]) <= r_cutoff
        #-- y-bound condition
        l_iny = abs(ycoors[irow]) <= r_cutoff
        #-- x-bound condition
        l_inx = abs(xcoors[irow]) <= r_cutoff
        if (l_inx and l_iny and l_inz):
            spn_row = np.array(ncol_spn * [0.0])
            #-- convert coordinates to velocity
            spn_row[:6] = slope * gen_str[irow, :6]
            #-- simply copy over remainder of data, excluding velocity, density
            spn_row[6:8] = gen_str[irow, 12:14]
            spn_row[8:ncol_spn-1] = gen_str[irow, 15:]
            spn_row[ncol_spn-1] = gen_str[irow, ncol-1]
            #-- increment the row
            spn_str.append(spn_row)

    #-- convert supernu structure to numpy array
    spn_str = np.array(spn_str)
    nrow_spn = np.size(spn_str, 0)

    #-- find new dimensions
    vxleft = np.unique(spn_str[:,0].round(num_round))
    vxrigh = np.unique(spn_str[:,1].round(num_round))
    vyleft = np.unique(spn_str[:,2].round(num_round))
    vyrigh = np.unique(spn_str[:,3].round(num_round))
    vzleft = np.unique(spn_str[:,4].round(num_round))
    vzrigh = np.unique(spn_str[:,5].round(num_round))
    #-- get number of cells along each dimension
    nx_spn = np.size(vxleft)
    ny_spn = np.size(vyleft)
    nz_spn = np.size(vzleft)
    print()
    print('nrow_spn = ', nrow_spn)
    print('nx_spn, ny_spn, nz_spn = ', nx_spn, ny_spn, nz_spn)
    print('nx_spn * ny_spn * nz_spn = ', nx_spn * ny_spn * nz_spn)
    if(np.size(vxrigh) != nx_spn): print('np.size(vxrigh) != nx_spn')
    if(np.size(vyrigh) != ny_spn): print('np.size(vyrigh) != ny_spn')
    if(np.size(vzrigh) != nz_spn): print('np.size(vzrigh) != nz_spn')

    #-- sort the cells
    spn_str_new = spn_str.copy();
    for irow in range(nrow_spn):
        ix = np.argmin(abs(vxleft - spn_str[irow, 0]))
        iy = np.argmin(abs(vyleft - spn_str[irow, 2]))
        iz = np.argmin(abs(vzleft - spn_str[irow, 4]))
        irow_sort = ix + nx_spn * iy + ny_spn * nx_spn * iz
        spn_str_new[irow_sort, :] = spn_str[irow, :]

    #-- convert to numpy
    spn_str_new = np.array(spn_str_new)
    if(np.array_equal(spn_str, spn_str_new)): print('Sort did not change anything.')

    #-- save the supernu structure
    np.savetxt('input.str_flash_x'+str(nx_spn)+'y'+str(ny_spn)+'z'+str(nz_spn),
               spn_str_new, fmt='% .4e',delimiter=' ')
