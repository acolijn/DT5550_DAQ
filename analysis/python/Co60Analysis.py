from DT5550 import *

import numpy as np
from lmfit import Model
from scipy.special import legendre

from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import heapq

import pandas as pd

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
        self.untagged_runs = kwargs.pop('untagged_runs', 'None')
        self.ee1173_range = kwargs.pop('e1173_range', (1100, 1250))
        self.ee1332_range = kwargs.pop('e1332_range', (1250, 1500))
        self.dt_max = kwargs.pop('dt_max', 10)

        self.rate_correction = np.ones(N_DETECTOR)

        self.data_sel = []
        self.df = pd.DataFrame()

        self.cost = []
        self.ntag = []
        self.dntag = []
        self.ntag_label = []

    def add_background(self, **kwargs):
        """
        Add the untagged data runs
        """
        self.untagged_runs = kwargs.pop('bg', 'None')

    def process_data(self, **kwargs):
        """
        Process the data for use in the Co60 analysis

        Input: type = 'correlation' for gamma angular correlation data
                    = 'untagged' for untagged data analysis
               max_files = maximum number of files to process (set to low number for debugging)
        """

        run_type = kwargs.pop('type', 'correlation')
        nfmax = kwargs.pop('max_files', 99999)  # maximum number of files to process (handy for debugging)

        print("Co60Analysis:: Begin processing data....")

        nf = 0

        data_dirs = []
        if run_type == 'correlation':
            data_dirs = self.runs
        elif run_type == 'untagged':
            data_dirs = self.untagged_runs

        for run_dir in data_dirs:
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
                    self.process_event(type=run_type)

        #
        # generate a pandas dataframe from the selected data
        #
        self.df = pd.DataFrame(self.data_sel)

        print("Co60Analysis:: Processing data - Done....")

    def process_event(self, **kwargs):
        """
        Process a single event
        """
        run_type = kwargs.pop('type', 'correlation')

        nh = self.valid.sum()

        if nh == 2:
            id_sel = np.where(self.valid == 1)[0]
            id0 = id_sel[0]
            id1 = id_sel[1]
            # calculate the time difference between hits
            delta_t = self.tc[id1] - self.tc[id0]
            record = {'id0': id0, 'id1': id1, 'E0': self.Q[id0], 'E1': self.Q[id1], 'R0': self.R[id0], 'R1': self.R[id1], 'dt': delta_t}
            self.data_sel.append(record)

    def tag_and_count(self, **kwargs):
        """
        Tag and count events.....
        """

        tagged_peak = kwargs.pop('tagged_peak', '1173keV')  # or 1332keV
        id_tag = kwargs.pop('idet_tag', -1)
        id_sel = kwargs.pop('idet_sel', -1)
        bin_width = kwargs.pop('bin_width', 10)

        if (id_tag == -1) or (id_sel == -1):
            print('Co60Analysis::tag_and_count_events ERROR idet_tag =',id_tag,' idet_sel =',id_sel)
            print('Co60Analysis::tag_and_count_events       should both be [0..7])')
            return

        fit_range = (0, 0)
        tag_range = (0, 0)
        p0 = np.zeros(3)

        fit = np.zeros(3)
        err = np.zeros(3)

        if tagged_peak == '1173keV':
            tag_range = self.ee1173_range
            fit_range = self.ee1332_range
            p0 = [100, 1173, 20]
        elif tagged_peak == '1332keV':
            tag_range = self.ee1332_range
            fit_range = self.ee1173_range
            p0 = [100, 1330, 20]

        #
        # get the processed data.....
        #
        df = self.df
        #
        # selection criteria
        #
        select0 = (df['id0'] == id_tag) & (df['E0'] > tag_range[0]) & (df['E0'] < tag_range[1]) & (abs(df['dt']) < self.dt_max)
        select1 = (df['id1'] == id_tag) & (df['E1'] > tag_range[0]) & (df['E1'] < tag_range[1]) & (abs(df['dt']) < self.dt_max)

        #
        # get the data from the selected detector with a tag in id_tag
        #
        if id_sel == id_tag:
            data = np.array(df['E0'][select0])
            data = np.append(data, df['E1'][select1])
        else:
            # events tagged by detector id1 and seen in id0=idet
            data = np.array(df['E0'][select1 & (df['id0'] == id_sel)])
            # events tagged by detector id0 and seen in id1=idet
            data = np.append(data, np.array(df['E1'][select0 & (df['id1'] == id_sel)]))
            #
            # fit a Gaussian to the data from the selected detector
            #
            fit, err = gauss_fit(data, range=fit_range, bins=int((fit_range[1] - fit_range[0]) / bin_width), p0=p0)
            ##data_sel = data[data>1250]
            ##data_sel = data_sel[data_sel<1450]
            ##fit[0] = len(data_sel)
            ##fit[1] = 1
            ##fit[2] = 1
        return data, fit, err

    def correlation_analysis(self, **kwargs):
        """
        analyze the gamma-gamma correlations for all detector combinations
        """

        tagged_peak = kwargs.pop('tagged_peak', '1173keV')
        plot_range = kwargs.pop('range', (0, 2000))
        bins = kwargs.pop('bins', 100)

        # define x-variable for plotting the fittted functions
        bin_width = (plot_range[1] - plot_range[0]) / bins
        xx = np.linspace(plot_range[0], plot_range[1], 1000)

        plt.figure(figsize=(18, 18))

        self.cost = []
        self.ntag = []
        self.dntag = []
        self.ntag_label = []

        for id_tag in range(N_DETECTOR-1):
            for idet in range(N_DETECTOR-1):
                plt.subplot(7, 7, 1 + idet + id_tag*7)
                #
                # measure the correlation between id_tag and idet
                #
                data, fit, err = self.tag_and_count(tagged_peak=tagged_peak, bin_width=bin_width, idet_tag=id_tag, idet_sel=idet)

                if idet == id_tag: # just for display the tagged events....
                    txt = 'CH{:1d}'.format(idet)
                    y, _, _ = plt.hist(data, bins=bins, range=plot_range, histtype='step', color='blue', label=txt)
                else:
                    fwhm = 2.35 * fit[2] / fit[1] * 100
                    txt = 'CH{:1d}-{:1d}\nN={:5.0f} $\pm$ {:2.0f} \n$\mu$={:5.1f} $\pm$ {:3.1f} keV \n$\sigma$={:5.1f} $\pm$ {:3.1f} keV\nFWHM/E = {:3.1f}%'.format(
                        idet, id_tag, fit[0], err[0], fit[1], err[1], fit[2], err[2], fwhm)
                    y, _, _ = plt.hist(data, bins=bins, range=plot_range, histtype='step', color='blue', label=txt)
                    plt.plot(xx, bin_width * gauss(xx, fit[0], fit[1], fit[2]), color='red')

                    ##print(idet, ' N=', fit[0], ' D=', np.sqrt(fit[0]), ' N count =', len(data))
                    theta0 = self.config['detector_settings'][id_tag]['THETA']
                    theta1 = self.config['detector_settings'][idet]['THETA']
                    #print(idet,id_tag)
                    #print('            fit parameters =', fit)
                    self.cost.append(np.cos(theta0 - theta1))
                    self.ntag.append(abs(fit[0]) / self.rate_correction[idet] / self.rate_correction[id_tag])
                    self.dntag.append(np.sqrt(abs(fit[0])) / self.rate_correction[idet] / self.rate_correction[id_tag] )
                    txt = '{:1d}-{:1d}'.format(id_tag, idet)
                    self.ntag_label.append(txt)

                plt.legend(loc='upper right')
                plt.xlabel('E (keV)')
                plt.yscale('linear')
                plt.ylim([0.6, 1.1 * max(y)])
        # for i in self.cost:
        #     print("hoeken", i / np.pi * 180)
        # print("detectoren",self.ntag_label)

        plt.show()

    def calculate_corrections(self, **kwargs):
        """
        Calculate rate corrections from the untagged data....
        """

        tagged_peak = kwargs.pop('tagged_peak', '1173keV')  # or 1332keV
        id_tag = kwargs.pop('idet_tag', 7)  # default tagging detector
        bins = kwargs.pop('bins', 100)
        plot_range = kwargs.pop('range', (0,2000))

        # define x-variable for plotting the fittted functions
        bin_width = (plot_range[1] - plot_range[0]) / bins
        xx = np.linspace(plot_range[0], plot_range[1], 1000)

        plt.figure(figsize=(20, 10))
        for idet in range(N_DETECTOR):
            plt.subplot(2, 4, 1 + idet)
            data, fit, err = self.tag_and_count(tagged_peak=tagged_peak, bin_width=bin_width, idet_tag=id_tag,
                                                idet_sel=idet)
            if idet == id_tag:
                txt = 'CH{:1d}'.format(idet)
                y, _, _ = plt.hist(data, bins=bins, range=plot_range, histtype='step', color='blue', label=txt)
            else:
                fwhm = 2.35 * fit[2] / fit[1] * 100
                txt = 'CH{:1d}-{:1d}\nN={:5.0f} $\pm$ {:2.0f} \n$\mu$={:5.1f} $\pm$ {:3.1f} keV \n$\sigma$={:5.1f} $\pm$ {:3.1f} keV\nFWHM/E = {:3.1f}%'.format(
                    idet, id_tag, fit[0], err[0], fit[1], err[1], fit[2], err[2], fwhm)
                y, _, _ = plt.hist(data, bins=bins, range=plot_range, histtype='step', color='blue', label=txt)
                plt.plot(xx, bin_width * gauss(xx, fit[0], fit[1], fit[2]), color='red')

                self.rate_correction[idet] = fit[0]

            plt.legend(loc='upper right')
            plt.xlabel('E (keV)')
            plt.yscale('linear')
            plt.ylim([0.6, 1.1 * max(y)])

        #cmax = max(self.rate_correction)
        #self.rate_correction = self.rate_correction/cmax

    def correlation_fit(self):
        """
        Do the correlation analysis... and plot
        """
        cost = np.array(self.cost)
        data = np.array(self.ntag)
        yerr = np.array(self.dntag)
        labels = np.array(self.ntag_label)

        for i in range(len(cost)):
            if cost[i] < 0:
                cost[i] = cost[i] * -1

        #
        # fit the data
        #
        fit, err = legendre_fit(cost, data, yerr=yerr)
        #
        # plot the data
        #
        txt = '$c_2$ = {:4.3f} $\pm$ {:4.3f} \n$c_4$ = {:4.3f} $\pm$ {:4.3f}'.format(fit[1], err[1], fit[2], err[2])
        plt.figure(figsize=(10, 12))
        plt.subplot(2, 1, 1)
        h = plt.errorbar(cost, data, yerr=yerr, fmt='o', color='blue', label=txt)

        for i in range(len(data)):
            plt.text(cost[i], data[i], labels[i])
        #
        # plot the fit to the data
        #
        xx = np.linspace(0, 1, 500)
        plt.plot(xx, legendre_polynomial(xx, fit[0], fit[1], fit[2]), '-', color='red', label='fit')
        plt.plot(xx, legendre_polynomial(xx, fit[0], 0.1005, 0.0094), '--', color='green', label='theory')
        plt.xlabel('$\cos \\theta$')
        plt.legend()
        plt.title("$\gamma$ correlation in $^{60}$Co decay")

        average_data = []
        check = []
        yerr_list = []
        for i in range(len(cost)):
            sum = data[i]
            count = 1
            positive_check = 0

            for k in check:
                if abs(cost[i]) > (k - 0.001) and abs(cost[i]) < (k + 0.001):
                    positive_check = positive_check + 1
            if positive_check == 0:
                for j in range(len(cost)):
                    if i != j:
                        if abs(cost[i]) > (abs(cost[j]) - 0.001) and abs(cost[i]) < (abs(cost[j]) + 0.001) :
                            sum = sum + data[j]
                            count = count + 1
                            if abs(cost[i]) not in check:
                                check.append(abs(cost[i]))
                average_data.append(sum/count)
                yerr_list.append(np.sqrt(sum)/count)

        print(yerr)
        print(yerr_list)

        plt.subplot(2, 1, 2)
        h = plt.errorbar(check, average_data, yerr = yerr_list, fmt='o', color='blue', label=txt)

        #
        # plot the fit to the data
        #
        xx = np.linspace(0, 1, 500)
        plt.plot(xx, legendre_polynomial(xx, fit[0], fit[1], fit[2]), '-', color='red', label='fit')
        plt.plot(xx, legendre_polynomial(xx, fit[0], 0.1005, 0.0094), '--', color='green', label='theory')
        plt.xlabel('$\cos \\theta$')
        plt.legend()
        plt.title("$\gamma$ correlation in $^{60}$Co decay with average measurements")

        plt.show()
