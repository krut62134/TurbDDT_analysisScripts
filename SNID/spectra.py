###############################################################
# To use this script you will have to get the spectra from SNID first
# For example 1a.dat can be your model and 1b.dat can be the best match from SNID
#  ~krut patel 100725
#
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

files = [('1a.dat', '1b.dat', 'red'),
         ('2a.dat', '2b.dat', 'blue'),
         ('4a.dat', '4b.dat', 'orange')]
legends = ['1: model epoch = -4.98, sn1991T epoch = -5.30, rlap = 3.58',
           '2: model epoch = 0, sn1991T epoch = -0.20, rlap = 6.78',
           '3: model epoch = +10.89, sn1991T epoch = +10.90, rlap = 6.05']

plt.figure(figsize=(8, 10))

# Plot spectra first
for i, (file_a, file_b, color) in enumerate(files):
    wave_a, flux_a = np.loadtxt(file_a, unpack=True)
    wave_b, flux_b = np.loadtxt(file_b, unpack=True)
    # Normalize
    flux_a = flux_a / np.median(flux_a)
    flux_b = flux_b / np.median(flux_b)
    # Use multiplicative offset for log scale
    scale_factor = 10 ** ((2 - i) * 1.4)
    plt.plot(wave_a, flux_a * scale_factor, 'k', linewidth=2)
    plt.plot(wave_b, flux_b * scale_factor, color, linewidth=2, alpha=0.6, label=legends[i])

# Set limits and scale
plt.xlim(2500, 7500)
plt.ylim(0.005, 50000)
plt.yscale('log')
plt.yticks([])

# Add grey vertical rectangles for specified wavelength ranges
plt.axvspan(4100, 4370, color='grey', alpha=0.3, zorder=0)
plt.axvspan(4700, 5100, color='grey', alpha=0.3, zorder=0)
plt.axvspan(5990, 6210, color='grey', alpha=0.3, zorder=0)
plt.axvspan(7500, 7800, color='grey', alpha=0.3, zorder=0)

# Add minor ticks on x-axis
ax = plt.gca()
ax.xaxis.set_minor_locator(MultipleLocator(200))
ax.tick_params(which='minor', length=3)
ax.tick_params(which='major', length=5)

plt.xlabel('Rest Wavelength (Å)', fontsize=14)
plt.ylabel(r'log($F_\lambda$) + constant', fontsize=14)
plt.legend(loc='upper center', fontsize=12, ncol=1, frameon=True, 
           handlelength=4, handletextpad=1, borderpad=2, labelspacing=1)

# Add labels at the BOTTOM near the x-axis
plt.text(4235, 0.006, 'Mg II', ha='center', va='bottom', fontsize=10, weight='bold')
plt.text(4900, 0.006, 'Fe II', ha='center', va='bottom', fontsize=10, weight='bold')
plt.text(6115, 0.006, 'Si II', ha='center', va='bottom', fontsize=10, weight='bold')

plt.tight_layout()
plt.savefig('spectra_plot.png', dpi=300, bbox_inches='tight')
plt.show()
