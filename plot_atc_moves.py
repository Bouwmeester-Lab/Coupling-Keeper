import numpy as np
import matplotlib.pyplot as plt

_, t_atc, x, z = np.loadtxt('data_cooldown_4/atc_moves.csv', unpack=True, delimiter=',',  skiprows=1)
#_, t_spectra_old, min_old, avg_old, max_old = np.loadtxt('data_second_cooldown/spectrum_metrics_old.csv', unpack=True, delimiter=',', skiprows=1)
_, t_spectra, min, avg, max, norm_factor = np.loadtxt('data_cooldown_4/spectrum_metrics.csv', unpack=True, delimiter=',', skiprows=1)

#t_spectra = np.hstack( (t_spectra_old, t_spectra) )
#min = np.hstack( (min_old, min) )
#avg = np.hstack( (avg_old, avg) )
#max = np.hstack( (max_old, max) )
#norm_factor = np.hstack( (np.full(len(t_spectra_old), np.mean(norm_factor)), norm_factor) )

start_iteration = 0#55 # index = 3 * the number of iterations, every iteration 3 moves are saved: sample down, fiber +/- x, sample up
dark_voltage = 119.5e-3

t_atc_minutes = t_atc[3*start_iteration:]/60
pos_x = np.cumsum(x)[3*start_iteration:]
pos_z = np.cumsum(z)[3*start_iteration:]

print(np.mean(np.diff(t_spectra)))

t_spectra = t_spectra[start_iteration:]/60 - t_spectra[start_iteration]/60
min = (min[start_iteration:] - dark_voltage)# / norm_factor[start_iteration:]
avg = (avg[start_iteration:] - dark_voltage)# / norm_factor[start_iteration:]
max = (max[start_iteration:] - dark_voltage)# / norm_factor[start_iteration:]

t_atc_minutes -= t_atc_minutes[0]
pos_x -= pos_x[0]
pos_z -= pos_z[0]

fit_range = (20, 150) #minutes
i_start = np.argmin(np.abs(t_atc_minutes-fit_range[0]))
i_end = np.argmin(np.abs(t_atc_minutes-fit_range[1]))

coeffs = np.polyfit(t_atc_minutes[i_start:i_end], pos_z[i_start:i_end], 1)
eval = np.polyval(coeffs, t_atc_minutes)

fig, axs = plt.subplots(1, 4, figsize=(25, 10))

axs[0].plot(t_atc_minutes, pos_x, c='k')
axs[0].set_xlabel('time [minutes]')
axs[0].set_ylabel('x [steps]')

axs[1].plot(t_atc_minutes, pos_z, c='k')
axs[1].plot(t_atc_minutes, pos_z-eval, c='r')
axs[1].plot(t_atc_minutes, eval, linestyle='--', c='r')
axs[1].set_xlabel('time [minutes]')
axs[1].set_ylabel('z [steps]')

axs[2].plot(pos_x, pos_z, alpha=.6, c='k')
axs[2].scatter(pos_x[0], pos_z[0], label='starting_position', color='r')
axs[2].scatter(pos_x[-1], pos_z[-1], label='final position', color='k')
axs[2].set_ylabel('z [steps]')
axs[2].set_xlabel('x [steps]')
axs[2].legend()

axs[3].plot(t_spectra, min, label='min')
axs[3].plot(t_spectra, avg, label='avg')
axs[3].plot(t_spectra, max, label='max')
axs[3].set_xlabel('time [minutes]')
axs[3].set_ylabel('normalized voltage')
axs[3].legend()

for ax in axs:
    ax.grid(True)

plt.show()

plt.plot(t_spectra, norm_factor[start_iteration:])
plt.show()