import h5py
import numpy as np
with h5py.File('tDDT_hd_o12r32_HLLC_Roe_hdf5_plt_cnt_000100', 'r') as f:
    dens = f['dens'][:]
    pres = f['pres'][:]
    gamc = f['gamc'][:]
    velx = f['velx'][:]
    vely = f['vely'][:]
    velz = f['velz'][:]
    
    cs = np.sqrt(gamc * pres / dens)
    # Compute directional wave speeds (as done in FLASH)
    wave_x = np.abs(velx) + cs
    wave_y = np.abs(vely) + cs
    wave_z = np.abs(velz) + cs
    wave_max_dir = np.maximum(np.maximum(wave_x, wave_y), wave_z)
    # Find location of max wave speed
    max_idx = np.unravel_index(np.argmax(wave_max_dir), wave_max_dir.shape)
    max_wave = wave_max_dir[max_idx]
    max_cs = cs[max_idx]
    max_velx = velx[max_idx]
    max_vely = vely[max_idx]
    max_velz = velz[max_idx]
    max_dens = dens[max_idx]
    max_pres = pres[max_idx]
    max_gamc = gamc[max_idx]
    vel_mag = np.sqrt(max_velx**2 + max_vely**2 + max_velz**2)
    dt_cfl = 0.48 * 8e5 / max_wave
    print(f"Cell with maximum wave speed:")
    print(f"Wave speed = c_s + |velocity|")
    print(f"Max wave speed = {max_wave/1e5:.2f} km/s")
    print(f"  c_s = {max_cs/1e5:.2f} km/s")
    print(f"  velocity = ({max_velx/1e5:.2f}, {max_vely/1e5:.2f}, {max_velz/1e5:.2f}) km/s")
    print(f"  |velocity| = {vel_mag/1e5:.2f} km/s")
    print(f"  dens = {max_dens:.3e} g/cm³")
    print(f"  pres = {max_pres:.3e} dyne/cm²")
    print(f"  gamc = {max_gamc:.4f}")
    print(f"CFL timestep (CFL=0.48, dx=8km) = {dt_cfl:.3e} s")
    print(f"Location(block, i, j, k): {max_idx}")
