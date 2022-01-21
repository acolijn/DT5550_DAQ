from DT5550 import *

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import heapq

N_DETECTOR = 8


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
        self.pulse_ratio = [[] for _ in range(N_DETECTOR)]
        self.delta_time = [[] for _ in range(N_DETECTOR)]
        self.delta_time_all = []
        self.delta_time_all_nocorr = []

        self.energy_min = 0
        self.delta_time_max = 100
        self.peak_select = -1
        self.gain_fit = np.zeros([N_DETECTOR, 3])
        self.gain_binwidth = 5

        self.ratio_fit = np.zeros([N_DETECTOR, 3])
        self.ratio_binwidth = 10

        # calibration result
        self.time_offset = np.zeros(N_DETECTOR)
        self.gain_correction = np.ones(N_DETECTOR)
        self.pulse_ratio_mean = np.zeros(N_DETECTOR)
        self.pulse_ratio_sigma = np.zeros(N_DETECTOR)


    def set_energy_min(self, emin):
        self.energy_min = emin

    def process_calibration_data(self):
        """
        Process the data for use either in calibration
        """

        print("Calibration:: Begin processing data....")
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
                        R = self.R[idet]

                        rmean = 0
                        rsig = 10000
                        if 'RMEAN' in self.config['detector_settings'][idet].keys():
                            rmean = self.config['detector_settings'][idet]['RMEAN']
                            rsig = self.config['detector_settings'][idet]['RSIGMA']

                        if abs(R-rmean) < 3*rsig:
                            self.raw_energy[idet].append(self.Q[idet])

                        self.pulse_ratio[idet].append(self.R[idet])

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
        self.pulse_ratio = np.array([np.array(x) for x in self.pulse_ratio], dtype=object)
        self.delta_time_all = np.array(self.delta_time_all)
        self.delta_time_all_nocorr = np.array(self.delta_time_all_nocorr)
        print("Calibration::calculate_time_offsets:: Done....")

    def calculate_pulse_ratio(self, **kwargs):
        """
        Calculate average peak / area ratio for all channels
        """
        self.ratio_binwidth = kwargs.pop('binwidth', self.ratio_binwidth)

        write_config = kwargs.pop('write_config', False)
        plot_it = kwargs.pop('plot', False)

        print('calculate_pulse_ratio:: Calculate the mean pk/charge ratio' )
        for idet in range(N_DETECTOR):
            vals = self.pulse_ratio[idet]
            mean = vals.mean()
            fit = self.gauss_fit(vals, p0=(mean, 70000, 10),  range=(mean - 100, mean + 100),
                                 bins=int(200/self.ratio_binwidth))
            print(idet, ' <R> = ', fit[0], ' A = ', fit[1], ' sig = ', fit[2])
            self.ratio_fit[idet] = fit
            self.pulse_ratio_mean[idet] = fit[0]
            self.pulse_ratio_sigma[idet] = abs(fit[2])


        if write_config:
            self.write_calibration(calibration_type='ratio')

        if plot_it:
            self.plot_ratio_calibration()

    def calculate_time_offsets(self, **kwargs):
        """
        Calculate time offsets (as can be seen above this is dnoe wrt channel0)
        """

        self.delta_time_max = kwargs.pop('delta_time_max', 100)
        write_config = kwargs.pop('write_config', False)
        plot_it = kwargs.pop('plot', False)

        self.delta_time = np.array(self.delta_time, dtype=object)

        print('calculate_time_offsets:: 0  dt =', 0, 'ns')
        for idet in range(1, N_DETECTOR):
            dt = self.delta_time[idet][abs(self.delta_time[idet]) < self.delta_time_max]
            self.time_offset[idet] = dt.mean()
            print('calculate_time_offsets::', idet, ' dt =', self.time_offset[idet], 'ns')

        if write_config:
            self.write_calibration(calibration_type='time_offset')

        if plot_it:
            self.plot_time_calibration()

    # Function to be fitted
    def gauss(self, x, x0, y0, sigma):
        p = [x0, y0, sigma]
        return p[1] * np.exp(-((x - p[0]) / p[2]) ** 2 / 2)

    def gauss_fit(self, data, **kwargs):
        """
        Fit a Gaussian to a distribution
        """
        p0 = kwargs.pop('p0', (1, 1, 1))
        fit_range = kwargs.pop('range', (0, 3000))
        bins = kwargs.pop('bins', 100)

        data = data[data>fit_range[0]]
        data = data[data<fit_range[1]]

        # fit a Gaussian to the delta_t distribution
        y, xe = np.histogram(data, bins=bins, range=fit_range)
        x = .5 * (xe[:-1] + xe[1:])

        # Fit the data with the function
        fit_par, _ = curve_fit(self.gauss, x, y, p0=p0)

        return fit_par

    def plot_ratio_calibration(self, **kwargs):
        """
        Plot the peak/area calibration histograms
        """
        plt.figure(figsize=(10, 15))

        plot_range = kwargs.pop('range', (1000, 2000))
        yscale = kwargs.pop('yscale', 'linear')
        bins = int((plot_range[1] - plot_range[0]) / self.ratio_binwidth)

        for idet in range(N_DETECTOR):
            plt.subplot(4, 2, 1+idet)
            txt = 'CH{:1d} \n$<R>$ = {:3.1f} \n$\sigma$ = {:3.1f}'.format(idet,
                                                                          self.pulse_ratio_mean[idet],
                                                                          self.pulse_ratio_sigma[idet])
            y,_,_= plt.hist(self.pulse_ratio[idet], bins=bins, range=plot_range, label=txt, histtype='step', color='blue')
            x_fine = np.linspace(plot_range[0], plot_range[1], 500)
            f = self.ratio_fit[idet]
            plt.plot(x_fine, self.gauss(x_fine, f[0], f[1], f[2]), color='red', linewidth=1)
            plt.yscale(yscale)
            if yscale == 'log':
                plt.ylim([0.1, 2*max(y)])
            txt = 'R_{:1d}'.format(idet)
            plt.xlabel(txt)
            plt.legend(loc='upper left')

    def plot_time_calibration(self):
        """
        Plot the delta histograms
        """
        plt.figure(figsize=(10, 15))

        for idet in range(N_DETECTOR):
            plt.subplot(4, 2, 1+idet)
            if idet != 0:
                txt = 'CH{:1d} $\mu$ = {:3.1f} ns'.format(idet, self.time_offset[idet])
                plt.hist(self.delta_time[idet][abs(self.delta_time[idet]) < self.delta_time_max],
                         bins=100, range=(-self.delta_time_max, +self.delta_time_max), label=txt)
                txt = '$t_{:1d}-t_0$ (ns)'.format(idet)
                plt.xlabel(txt)
                plt.legend(loc='upper left')

            else:
                self.plot_all_dt()

    def plot_all_dt(self, **kwargs):
        """
        Fit a Gauss to the dt distribution of all measured time differences
        """
        bins = kwargs.pop('bins',200)

        dt_all = self.delta_time_all[abs(self.delta_time_all) < self.delta_time_max]
        dt_all_nocorr = self.delta_time_all_nocorr[abs(self.delta_time_all_nocorr) < self.delta_time_max]

        fit = self.gauss_fit(dt_all, range=(-self.delta_time_max, +self.delta_time_max), bins=bins)

        # Plot the results
        plt.title('$\mu$=%.2e $\sigma$=%.2e' % (fit[0], fit[2]))
        # Fitted function
        x_fine = np.linspace(-self.delta_time_max, +self.delta_time_max, 100)

        plt.xlabel('$\Delta t$ (ns)', fontsize=12)

        txt = 'dt no timewalk correction'
        plt.hist(dt_all_nocorr, bins=bins, range=(-self.delta_time_max, +self.delta_time_max), histtype='step',
                 label=txt, color='grey')

        txt = 'dt'
        y, _, _ = plt.hist(dt_all, bins=bins, range=(-self.delta_time_max, +self.delta_time_max),
                           histtype='step', label=txt, linewidth=2, color='blue')
        plt.plot(x_fine, self.gauss(x_fine, fit[0], fit[1], fit[2]), 'r-', linewidth=1)

        plt.ylim([0, 1.5*max(y)])

        plt.legend(loc='upper left')

    def write_calibration(self, **kwargs):
        """
        Write calibrated configuration file
        """

        calibration_type = kwargs.pop('calibration_type', None)

        print('write_calibration:: type =',calibration_type)
        for idet in range(N_DETECTOR):
            if calibration_type == 'time_offset':
                # time offsets
                toff = self.config['detector_settings'][idet]['TOFF']
                self.config['detector_settings'][idet]['TOFF'] = toff + self.time_offset[idet]

            if calibration_type == 'gain':
                # energy calibration
                gcor = 1.0
                if "GCOR" in self.config['detector_settings'][idet].keys():
                    gcor = self.config['detector_settings'][idet]['GCOR']
                self.config['detector_settings'][idet]['GCOR'] = self.gain_correction[idet]*gcor

            if calibration_type == 'ratio':
                # average pulse ratio
                self.config['detector_settings'][idet]['RMEAN'] = self.pulse_ratio_mean[idet]
                self.config['detector_settings'][idet]['RSIGMA'] = self.pulse_ratio_sigma[idet]


        print('write_calibration:: calibration constants to ', self.config_file)
        # here the actual write is done.... (from baseclass DT5550)
        self.write_config_file()

    def calculate_gains(self, **kwargs):
        """
        Calculate gains
        """

        # bin width for the histogramming
        self.gain_binwidth = kwargs.pop('binwidth', self.gain_binwidth)
        write_config = kwargs.pop('write_config', False)
        plot_it = kwargs.pop('plot', False)

        source = self.config['source']
        self.energy_calibration_point = -1
        if source == "Co60":
            self.energy_calibration_point = 1332.5  # choose the highest energy gamma for gain calibration
            self.peak_select = 2                    # select teh 2nd highest peak in the spectrum
        elif source == "Na22":
            self.energy_calibration_point = 511.0
            self.peak_select = 1
        elif source == "Cs137":
            self.energy_calibration_point = 661.6
            self.peak_select = 1
        else:
            print('calulate_gains:: ERROR wrong source selected: ', source)

        print('calculate_gains:: Calibrate energy scale on ', source,
              ' peak energy =', self.energy_calibration_point, ' keV')

        de = 100  # guess what the fit range should be.... could be improved
        for idet in range(N_DETECTOR):
            fit_est = self.estimate_peak_position(idet)
            nbin = int(2*de/self.gain_binwidth)
            self.gain_fit[idet] = self.gauss_fit(self.raw_energy[idet], p0=fit_est, bins=nbin,
                                                 range=(fit_est[0]-de, fit_est[0]+de))
            if self.gain_fit[idet][0] != 0:
                self.gain_correction[idet] = self.energy_calibration_point / self.gain_fit[idet][0]
            else:
                self.gain_correction[idet] = 1.

        if write_config:
            self.write_calibration(calibration_type='gain')

        if plot_it:
            self.plot_gain_calibration()

    def estimate_peak_position(self, idet, **kwargs):
        """
        Estimate the peak position... rough estimate->then the Gauss fit will get you accurate parameters
        """
        bins = kwargs.pop('bins', 100)
        search_range = kwargs.pop('range', (0, 3000))

        # from scipy.signal.... find the peak locations
        y, x = np.histogram(self.raw_energy[idet], bins=bins, range=search_range)
        peaks, _ = find_peaks(y, prominence=100)#, width=10)
        print("estimate_peak_positon:: channel ",idet,"found ", len(peaks),' peaks')
        if len(peaks) < self.peak_select:
            print("estimate_peak_position:: failed to find the appropriate number of peaks")
            print("estimate_peak_position:: stop")
            return [0, 0, 0]
        # select the right peak (here the index in the histogram is returned)
        index_sel = peaks[heapq.nlargest(self.peak_select, range(len(y[peaks])), key=y[peaks].__getitem__)[-1]]

        # if Co60 is used for calibration we need to check whether we use the right peak
        if self.config['source'] == "Co60":
            idx_1st = peaks[heapq.nlargest(1, range(len(y[peaks])), key=y[peaks].__getitem__)[-1]]
            idx_2nd = peaks[heapq.nlargest(2, range(len(y[peaks])), key=y[peaks].__getitem__)[-1]]
            if idx_2nd<idx_1st:
                print("estimate_peak_position:: Co60:: swapped 1173keV and 1332keV peak... fix it")
                index_sel = idx_1st

        mean = x[index_sel]
        amplitude = y[index_sel]
        sigma = 5.  # dunno

        return [mean, amplitude, sigma]

    def plot_gain_calibration(self, **kwargs):
        """
        Plot the energy distribution
        """
        plot_range = kwargs.pop('range', (1000, 1500))

        plt.figure(figsize=(10, 15))

        bins = int((plot_range[1]-plot_range[0])/self.gain_binwidth)

        for idet in range(N_DETECTOR):
            plt.subplot(4, 2, 1+idet)
            txt = 'CH{:1d}\n$\mu$={:5.1f} keV \nFWHM/E={:3.1f}% \nC={:4.2f}'.format(idet,
                                                                           self.gain_fit[idet][0],
                                                                           self.gain_fit[idet][2]*2.35/self.gain_fit[idet][0]*100,
                                                                           self.gain_correction[idet])
            y, _, _ = plt.hist(self.raw_energy[idet], bins=bins, range=plot_range,
                               histtype='step', label=txt, linewidth=2, color='blue')

            x_fine = np.linspace(plot_range[0], plot_range[1], 500)
            plt.plot(x_fine, self.gauss(x_fine, self.gain_fit[idet][0], self.gain_fit[idet][1], self.gain_fit[idet][2]),
                     'r-', linewidth=1)

            plt.ylim([0, 1.2*max(y)])
            txt = '$E_{:1d}$ (keV)'.format(idet)
            plt.xlabel(txt)
            plt.legend(loc='upper left')



