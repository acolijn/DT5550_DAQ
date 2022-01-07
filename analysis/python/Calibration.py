from DT5550 import *

import numpy as np
from scipy.optimize import curve_fit

N_DETECTOR = 8

# Function to be fitted
def gauss(x, x0, y0, sigma):
    p = [x0, y0, sigma]
    return p[1] * np.exp(-((x - p[0]) / p[2]) ** 2)

class Calibration(DT5550):
    """
    Class for energy and timing calibrations
    """
    def __init__(self, **kwargs):
        """
        Initialize the calibration class
        """
        super(Calibration, self).__init__(**kwargs)

        self.raw_energy = [[] for _ in range(N_DETECTOR)]
        self.delta_time = [[] for _ in range(N_DETECTOR)]
        self.delta_time_all = []
        self.delta_time_all_nocorr = []


        self.energy_min = 0
        self.delta_time_max = 100

        # calibration result
        self.time_offset = np.zeros(N_DETECTOR)
        self.gain_correction = np.ones(N_DETECTOR)

    def set_energy_min(self, emin):
        self.energy_min = emin

    def process_calibration_data(self):
        """
        Process the data for use either in calibration
        """

        print("Calibration::calculate_time_offsets:: Begin....")
        # reinitialize the delta_time array
        self.raw_energy = [[] for _ in range(N_DETECTOR)]
        self.delta_time = [[] for _ in range(N_DETECTOR)]

        #
        #  loop over all events
        #
        for file in self.filenames:
            #
            # open the data file
            #
            self.open_data(file)
            #
            # read an event as long as you have not reached the end of the data
            #
            while self.read_event() == 0:
                #
                #  For gain calibration:: select valid event (selection can be extended)
                #
                for idet in range(N_DETECTOR):
                    if self.valid[idet]:
                        self.raw_energy[idet].append(self.Q[idet])

                #
                #  For time offset calibrations:: select events with two valid hits
                #
                if self.valid.sum() == 2:
                    # get the detector IDs
                    idet_sel = []
                    energy_total = self.Q.sum()

                    if energy_total > self.energy_min:
                        #
                        # get the indices of the two hits
                        #
                        for idet in range(N_DETECTOR):
                            if self.valid[idet]:
                                idet_sel.append(idet)

                        id0 = idet_sel[0]
                        id1 = idet_sel[1]
                        # all delta t: used to estimate the timing resolution
                        self.delta_time_all.append(self.tc[id1]-self.tc[id0])
                        self.delta_time_all_nocorr.append(self.t[id1]-self.t[id0])
                        # delta with respect to channel0: used for calibration
                        if id0 == 0:  # we will calculaet the time difference with respect to idet=0
                            self.delta_time[id1].append(self.tc[id1] - self.tc[id0])

        #
        # convert the lists to numpy arrays
        #
        self.delta_time = np.array([np.array(x) for x in self.delta_time], dtype=object)
        self.raw_energy = np.array([np.array(x) for x in self.raw_energy], dtype=object)
        self.delta_time_all = np.array(self.delta_time_all)
        self.delta_time_all_nocorr = np.array(self.delta_time_all_nocorr)
        print("Calibration::calculate_time_offsets:: Done....")


    def calculate_time_offsets(self, **kwargs):
        """
        Calculate time offsets (as can be seen above this is dnoe wrt channel0)
        """

        self.delta_time_max = kwargs.pop('delta_time_max', 100)
        write_config = kwargs.pop('write_config', False)
        plot_it = kwargs.pop('plot', False)

        self.delta_time = np.array(self.delta_time, dtype=object)

        print('calculate_time_ooffsets:: 0  dt =', 0)
        for idet in range(1, N_DETECTOR):
            dt = self.delta_time[idet][abs(self.delta_time[idet]) < self.delta_time_max]
            self.time_offset[idet] = dt.mean()
            print('calculate_time_offsets::', idet, ' dt =', self.time_offset[idet])

        if write_config:
            self.write_calibration()

        if plot_it:
            self.plot_time_calibration()



    def plot_time_calibration(self):
        """
        Plot the delta histograms
        """
        plt.figure(figsize=(10, 15))

        for idet in range(N_DETECTOR):
            plt.subplot(4, 2, 1+idet)
            if idet != 0:
                txt = 'CH{:1d} $\mu$ = {:3.1f} ns'.format(idet,self.time_offset[idet])
                plt.hist(self.delta_time[idet][abs(self.delta_time[idet]) < self.delta_time_max],
                         bins=100, range=(-self.delta_time_max, +self.delta_time_max), label=txt)
            else:
                #
                # fit a Gauss to the dt distribution
                #
                bins = 200
                dt_all = self.delta_time_all[abs(self.delta_time_all) < self.delta_time_max]
                dt_all_nocorr = self.delta_time_all_nocorr[abs(self.delta_time_all_nocorr) < self.delta_time_max]

                y, xe = np.histogram(dt_all, bins=bins)
                x = .5 * (xe[:-1] + xe[1:])
                # Initialization parameters
                p0 = [1., 1., 1.]
                # Fit the data with the function
                fit, tmp = curve_fit(gauss, x, y, p0=p0)

                # Plot the results
                plt.title('$\mu$=%.2e $\sigma$=%.2e' % (fit[0], fit[2]))
                # Fitted function
                x_fine = np.linspace(xe[0], xe[-1], 100)

                plt.xlabel('$\Delta t$ (ns)', fontsize=12)

                txt = 'dt no timewalk correction'
                plt.hist(dt_all_nocorr, bins=bins, range=(-self.delta_time_max, +self.delta_time_max), histtype='step',
                         label=txt, color='grey')

                txt = 'dt'
                y, _, _ = plt.hist(dt_all, bins=bins, range=(-self.delta_time_max, +self.delta_time_max),
                                   histtype='step', label=txt, linewidth=2, color='blue')
                plt.plot(x_fine, gauss(x_fine, fit[0], fit[1], fit[2]), 'r-', linewidth=1)

                plt.ylim([0, 1.5*max(y)])

            plt.legend(loc='upper left')

    def write_calibration(self):
        """
        ver-write configuration file
        """

        for idet in range(N_DETECTOR):
            # time offsets
            toff = self.config['detector_settings'][idet]['TOFF']
            self.config['detector_settings'][idet]['TOFF'] = toff + self.time_offset[idet]
            # energy calibration
            gain = self.config['detector_settings'][idet]['GAIN']
            self.config['detector_settings'][idet]['GAIN'] = gain*self.gain_correction[idet]

        print('write_calibration:: write time offsets to ', self.config_file)
        fout = open(self.config_file, "w")
        json.dump(self.config, fout, indent=4)
        fout.close()

    def calculate_gains(self):
        """
        Calculate gains
        """