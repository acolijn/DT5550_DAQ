from DT5550 import *

import numpy as np
from lmfit import Model
from scipy.special import legendre

from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import heapq

N_DETECTOR = 8

def legendre_polynomial(x, A, c2, c4):
    p = [A, c2, c4]

    P0 = legendre(0)
    P2 = legendre(2)
    P4 = legendre(4)

    return p[0] * (P0(x) + p[1] * P2(x) + p[2] * P4(x))


def legendre_fit(x, y, yerr, **kwargs):
    """
    Fit Legendre polynomials
    """
    p0 = [12000, 0.1, 0.001]

    # fit_par, cov = curve_fit(legendre_polynomial, x, y, sigma=yerr, p0=p0)

    # lmfit it....
    gmodel = Model(legendre_polynomial)
    result = gmodel.fit(y, x=x, weights=1/yerr**2, A=p0[0], c2=p0[1], c4=p0[2])
    ### print(result.fit_report())

    fit_par = np.zeros(3)
    fit_err = np.zeros(3)

    fit_par[0] = result.params['A'].value
    fit_par[1] = result.params['c2'].value
    fit_par[2] = result.params['c4'].value

    fit_err[0] = result.params['A'].stderr
    fit_err[1] = result.params['c2'].stderr
    fit_err[2] = result.params['c4'].stderr

    return fit_par, fit_err


def gauss(x, A, mu, sigma):
    p = [A, mu, sigma]
    return p[0] / np.sqrt(2 * np.pi) / p[2] * (np.exp(-((x - p[1]) / p[2]) ** 2 / 2))


def gauss_fit(data, **kwargs):
    """
    Fit a Gaussian to a distribution
    """
    p0 = kwargs.pop('p0', (1, 1, 1))
    fit_range = kwargs.pop('range', (0, 3000))
    bins = kwargs.pop('bins', 100)

    data = data[data > fit_range[0]]
    data = data[data < fit_range[1]]

    bw = (fit_range[1] - fit_range[0]) / bins

    # fit a Gaussian to the delta_t distribution
    y, xe = np.histogram(data, bins=bins, range=fit_range)
    x = .5 * (xe[:-1] + xe[1:])
    # lmfit it....
    gmodel = Model(gauss)
    result = gmodel.fit(y, x=x, weights=1, A=p0[0], mu=p0[1], sigma=p0[2])

    fit_par = np.zeros(3)
    fit_err = np.zeros(3)

    fit_par[0] = result.params['A'].value / bw
    fit_par[1] = result.params['mu'].value
    fit_par[2] = result.params['sigma'].value

    fit_err[0] = result.params['A'].stderr / bw
    fit_err[1] = result.params['mu'].stderr
    fit_err[2] = result.params['sigma'].stderr

    return fit_par, fit_err


class Co60Analysis(DT5550):
    """
    Class for Co60 analysis
    """
    def __init__(self, **kwargs):
        """
        Initialize the calibration class
        """
        super(Co60Analysis, self).__init__(**kwargs)
        self.runs = kwargs.pop('runs', 'None')
        self.ee1173_range = kwargs.pop('e1173_range', (1100, 1250))
        self.ee1332_range = kwargs.pop('e1332_range', (1250, 1450))
        self.dt_max = kwargs.pop('dt_max', 10)

        self.ee1173 = []
        self.ee1332 = []

        for idet in range(N_DETECTOR):
            self.ee1173.append([])
            self.ee1332.append([])

        self.selected = None
        self.n_tag = np.zeros(N_DETECTOR)
        self.dn_tag = np.zeros(N_DETECTOR)

    def process_data(self, **kwargs):
        """
        Process the data for use in the Co60 analysis
        """
        nfmax = kwargs.pop('max_files', 99999)  # maximum number of files to process (handy for debugging)

        print("Co60Analysis:: Begin processing data....")

        nf = 0

        for run_dir in self.runs:
            #
            # initialie the DT5550 data structure
            #
            DT5550.__init__(self, indir=run_dir)
            #
            #  loop over all events
            #
            for file in self.filenames:

                nf += 1
                if nf > nfmax:
                    break

                #
                # open the data file
                #
                self.open_data(file)
                #
                # read an event as long as you have not reached the end of the data
                #
                while self.read_event() == 0:
                    #
                    #  Process a single event....
                    #
                    self.process_event()

        #
        # convert the lists to numpy arrays
        #
        self.ee1173 = np.array(self.ee1173, dtype=object)
        self.ee1332 = np.array(self.ee1332, dtype=object)

        print("Co60Analysis:: Processing data - Done....")

    def process_event(self):
        """
        Process a single event
        """
        nh = self.valid.sum()

        # events with two hits
        if nh == 2:
            id_sel = []
            for idet in range(8):
                if self.valid[idet]:
                    id_sel.append(idet)

            id0 = id_sel[0]
            id1 = id_sel[1]

            delta_t = self.tc[id1] - self.tc[id0]
            if id0 == 0:
                if abs(delta_t) < self.dt_max:
                    # select the 1173keV if detector0 detects the 1332keV
                    if self.ee1332_range[0] < self.Q[id0] < self.ee1332_range[1]:
                        self.ee1173[id1].append(self.Q[id1])
                        self.ee1173[id0].append(self.Q[id0])

                    # .... and the other way round
                    if self.ee1173_range[0] < self.Q[id0] < self.ee1173_range[1]:
                        self.ee1332[id1].append(self.Q[id1])
                        self.ee1332[id0].append(self.Q[id0])

    def tag_and_count_events(self, **kwargs):
        """

        """
        self.selected = kwargs.pop('select', None)
        bins = kwargs.pop('bins',100)
        if self.selected is None:
            print('Co600Analysis::tag_and_count_events no peak selected.... selected= <0->1173keV, 1->1332keV>')
            return

        plot_range = (1000, 1500)
        fit_range = (0, 0)
        ee_data = []

        if self.selected == 0:
            fit_range = (1100, 1250)
            p0 = [1000,1173, 20]
            ee_data = self.ee1173
        elif self.selected == 1:
            fit_range = (1250, 1500)
            p0 = [1000, 1330, 20]
            ee_data = self.ee1332

        # define x-variable for plotting teh fittted functions
        bin_width = (plot_range[1] - plot_range[0]) / bins
        xx = np.linspace(plot_range[0], plot_range[1], 1000)

        plt.figure(figsize=(12,18))
        for idet in range(N_DETECTOR):
            plt.subplot(4, 2, 1 + idet)
            data = np.array(ee_data[idet])

            if idet == 0:
                txt = 'CH{:1d}'.format(idet)
                y, _, _ = plt.hist(data, bins=bins, range=plot_range, histtype='step', color='blue', label=txt)
            else:
                fit, err = gauss_fit(data, range=fit_range, bins=int((fit_range[1] - fit_range[0]) / bin_width), p0=p0)
                fwhm = 2.35 * fit[2] / fit[1] * 100
                txt = 'CH{:1d}\nN={:5.0f} $\pm$ {:2.0f} \n$\mu$={:5.1f} $\pm$ {:3.1f} keV \n$\sigma$={:5.1f} $\pm$ {:3.1f} keV\nFWHM/E = {:3.1f}%'.format(
                    idet, fit[0], err[0], fit[1], err[1], fit[2], err[2], fwhm)
                y, _, _ = plt.hist(data, bins=bins, range=plot_range, histtype='step', color='blue', label=txt)
                plt.plot(xx, bin_width * gauss(xx, fit[0], fit[1], fit[2]), color='red')

                self.n_tag[idet] = fit[0]
                self.dn_tag[idet] = np.sqrt(self.n_tag[idet])
                data = data[data > fit_range[0]]
                data = data[data < fit_range[1]]
                print(idet, ' N=', self.n_tag[idet], ' D=', self.dn_tag[idet], ' N count =', len(data))
            if self.selected == 1:
                plt.legend(loc='upper left')
            else:
                plt.legend(loc='upper right')

            plt.xlabel('E (keV)')
            plt.yscale('linear')
            plt.ylim([0.6, 1.1 * max(y)])

        plt.show()

    def correlation_analysis(self):
        """
        Do the correlation analysis... and plot
        """

        # make an array with cos(theta) values
        # NOTE: the phi locations of teh detectors are hard coded... this could/should change in the future if we
        #       study different geometries.....

        x = np.arange(1, 8, 1)
        theta = (7 - x) * (np.pi / 12) + np.pi / 2
        cost = abs(np.cos(theta))

        data = self.n_tag[1:8]
        yerr = self.dn_tag[1:8]
        #
        # fit the data
        #
        fit, err = legendre_fit(cost, data, yerr=yerr)
        #
        # plot the data
        #
        txt = '$c_2$ = {:4.3f} $\pm$ {:4.3f} \n$c_4$ = {:4.3f} $\pm$ {:4.3f}'.format(fit[1], err[1], fit[2], err[2])
        plt.figure(figsize=(10, 6))
        h = plt.errorbar(cost, data, yerr=yerr, fmt='o', color='blue', label=txt)
        #
        # plot the fit to the data
        #
        xx = np.linspace(0, 1, 500)
        plt.plot(xx, legendre_polynomial(xx, fit[0], fit[1], fit[2]), '-', color='red', label='fit')
        plt.plot(xx, legendre_polynomial(xx, fit[0], 0.1005, 0.0094), '--', color='green', label='theory')
        plt.xlabel('$\cos \\theta$')
        plt.legend()
        plt.title("$\gamma$ correlation in $^{60}$Co decay")

        plt.show()
