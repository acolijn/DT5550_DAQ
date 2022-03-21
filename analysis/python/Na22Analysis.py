from DT5550 import *

import numpy as np
import pandas as pd

from scipy import special
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib import gridspec



N_DETECTOR = 8
ETOT_THEORY = 2296.5
E1274 = 1274.5


def dt_model(x, *pars):
    """
    Fit to the dt distribution

    1. Gauss around zero with width sigma to account for zero-lifetime component
    2. Exp(tau0) (x) Gauss(sigma)
    3. Exp(tau1) (x) Gauss(sigma)

    pars[0] = amplitude of the zero lifetime Gaussian
    pars[1] = timing resolution sigma
    pars[2] = amplitude of short lifetime exponential
    pars[3] = short lifetime
    pars[4] = amplitude of long lifetime exponential
    pars[5] = long lifetime
    pars[6] = constant background due to pile-up

    A.P. Colijn / 13-03-2022

    """
    A0 = pars[0]
    sigma = pars[1]

    A1 = pars[2]
    tau1 = pars[3]
    A2 = pars[4]
    tau2 = pars[5]
    C = pars[6]

    mu = pars[7]

    x = x - mu

    # zero-lifetime Gaussian
    arg = -x ** 2 / sigma ** 2 / 2
    fval = A0 * np.exp(arg) / sigma / np.sqrt(2 * np.pi)

    # short lifetime exponential convoluted with Gaussian. Gaussian has same sigma as zero-lfetime component
    lam = 1. / tau1
    arg0 = -lam * (x - sigma ** 2 * lam / 2.)
    arg1 = (x - sigma ** 2 * lam) / np.sqrt(2.) / sigma
    fval = fval + A1 * np.exp(arg0) * (1 + special.erf(arg1)) / 2

    # long lifetime exponential convoluted with Gaussian. Gaussian has same sigma as zero-lfetime component
    lam = 1. / tau2
    arg0 = -lam * (x - sigma ** 2 * lam / 2.)
    arg1 = (x - sigma ** 2 * lam) / np.sqrt(2.) / sigma
    fval = fval + A2 * np.exp(arg0) * (1 + special.erf(arg1)) / 2

    # constant factor to take into account pile-up
    fval = fval + C

    return fval


class Na22Analysis(DT5550):
    """
    Class for Co60 analysis
    """
    def __init__(self, **kwargs):
        """
        Initialize the calibration class
        """
        super(Na22Analysis, self).__init__(**kwargs)
        self.runs = kwargs.pop('runs', 'None')

        self.data_sel = []
        self.df = pd.DataFrame()

        self.detot_max = 100.
        self.dr_max = 3.

    def process_data(self, **kwargs):
        """
        Process the data for use in the Co60 analysis

        Input: max_files = maximum number of files to process (set to low number for debugging)
               data = 'raw' -> raw data (re-)processing
                    = 'hd5' -> summary hhd5 data read directly (if existent, otherwise raw processing)
        """

        nfmax = kwargs.pop('max_files', 99999)  # maximum number of files to process (handy for debugging)
        data = kwargs.pop('data', 'raw')

        # raw data selection......
        self.detot_max = kwargs.pop('detot_max', 100)  # cut on |E(1274)+E(gg/ggg) - 2296.5keV| < detot_max
        self.dr_max = kwargs.pop('dr_max', 3.)  # cut on | R - RMEAN | < dr_max*RSIGMA

        print("Na22Analysis:: Begin processing data....")

        nf = 0

        data_dirs = self.runs

        for run_dir in data_dirs:
            #
            # initialie the DT5550 data structure
            #
            DT5550.__init__(self, indir=run_dir)

            do_raw = True

            if data == 'hd5':
                # check if the hd5 file exists.....
                if self.hd5_file == 'None':
                    #  it does not exist, so we have to process teh raw data......
                    do_raw = True
                else:
                    do_raw = False

            if do_raw:
                print('Na22Analysis:: process raw data....')
                self.data_sel = []

                #
                #  loop over all events
                #
                for file in self.filenames:
                    nf += 1
                    if nf > nfmax:
                        print('reached maximum number of files.... stop processing ', nf)
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
                    # generate a pandas dataframe from the selected data
                    #
                    df = pd.DataFrame(self.data_sel)
                    #
                    # and dump the dataframe to an hd5 summary file
                    #
                    hd5_filename = self.indir + '/selected_data.hd5'
                    df.to_hdf(hd5_filename, key='df', mode='w')

        #
        # construct the sumamry dataframe......
        #
        print('Na22Analysis:: create pandas dataframe for analysis.....')
        self.df = pd.DataFrame()
        for run_dir in data_dirs:
            DT5550.__init__(self, indir=run_dir)
            hd5_filename = self.hd5_file
            print(hd5_filename)
            if hd5_filename != 'None':
                df_new = pd.read_hdf(hd5_filename, key='df')
                self.df = pd.concat([self.df, df_new], ignore_index='True')

        print("Na22Analysis:: Processing data - Done....")

    def process_event(self):
        """
        Process a single event and make an event selection
        """

        #
        # count the number of valida hits in this event
        #
        nh = self.valid.sum()

        #
        # select events where
        # 1. the total energy of a Na22 decay is observed
        # 2. there are 3 or more detectors that registers an energy deposit
        #
        if (nh >= 3) and (abs(self.Q.sum() - ETOT_THEORY) < self.detot_max):
            #
            # 1274 gamma ray from Ne22
            #
            i0 = -1  # index of detector that registers the 1274keV event
            t0 = -1  # this will be the time a 1274keV hit is recorded
            for idet in range(N_DETECTOR):
                #
                # if the energy is within 100keV of the 1274keV gamma ray line, we found it (check if this is OK)
                #
                rr = self.R[idet]
                rmean = self.config['detector_settings'][idet]['RMEAN']
                rsig = self.config['detector_settings'][idet]['RSIGMA']

                if abs(self.Q[idet] - E1274) < 100 and (self.valid[idet]) and (abs(rr - rmean) < self.dr_max * rsig):
                    # print('1274keV ', idet,'t =',io.tc[idet],'E =',io.Q[idet])
                    t0 = self.tc[idet]
                    i0 = idet

            #
            # look at the other energy deposits in the event
            #
            nn = 0
            esum = 0
            dt = []
            for idet in range(N_DETECTOR):
                # if the hits is valid AND the detector is not the one that saw the 1274keV gamma ray
                rr = self.R[idet]
                rmean = self.config['detector_settings'][idet]['RMEAN']
                rsig = self.config['detector_settings'][idet]['RSIGMA']
                if (self.valid[idet]) and (idet != i0) and (abs(rr - rmean) < self.dr_max * rsig):
                    nn = nn + 1
                    esum = esum + self.Q[idet]
                    dt.append(self.tc[idet] - t0)  # time difference wrt to 1274keV gamma ray
            dt = np.array(dt)

            #
            # continue with this event if:
            # 1. there are two or more hits beside the 1274keV gamma ray (should be most, due to earlier selection)
            # 2. a 1274keV gamma ray is actually found
            #
            if (nn >= 2) and (i0 != -1):
                record = {'etot': self.Q.sum(), 'etag': self.Q[i0], 'epos': esum, 'npos': nn, 'dt': dt.mean(),
                          'sdt': np.sqrt(dt.var())}
                self.data_sel.append(record)  # we select this event......

    def fit_dt_model(self, **kwargs):
        """
        Fit delta time model to the observed distribution

        Input:

        bin_width = bin width of delta_t histogram in ns
        plot_range = plot range (not the fit range, which is currently fixed to dt=(-500ns, 1000ns)
        sdt_max = maximum spread of the time measurement of the 2/3 gammas
        de_max = maximum energy difference in keV to 2*me for the 2/3 gammas
        toffset = additional time offset correction in ns to let peak coincide with zero (probably due to imperfect
                  timewalk calculations)

        A.P. Colijn / 18-03-2022
        """

        bin_width = kwargs.pop('bin_width', 1)
        plot_range = kwargs.pop('range', (-50, 250))
        sdt_max = kwargs.pop('sigma_max', 5)
        de_max = kwargs.pop('de_max', 100)
        toffset = kwargs.pop('t_offset', 0)

        #
        # make an array with the time differences
        #
        cut = (self.df['sdt'] < sdt_max) & (abs(self.df['epos'] - 1022) < de_max)
        tt = self.df['dt'][cut] - toffset

        #
        # fit range..... (the range argument is only used for plotting)
        #
        xr = (-500, 1000)
        bins = int((xr[1]-xr[0])/bin_width)
        #
        # make a histogram with the time differences and unpack it
        #
        y, xe = np.histogram(tt, bins=bins, range=xr)
        x = .5 * (xe[:-1] + xe[1:])

        #
        # fit the model to the dt distribution
        #

        # initial fit values
        s0 = 1.5
        a0 = max(y)*np.sqrt(2*np.pi)*s0
        popt = np.array([a0, s0, a0/10, 2.3, 1000, 100, y[-1], 2.5])
        popt, pcov = curve_fit(dt_model, x, y, sigma=np.sqrt(y),
                               p0=popt,
                               bounds=((-np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf),
                                       (np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf)))
        print(popt)
        txt = '\n'.join([r'$A_G$ = {:5.1f} $\pm$ {:5.1f}'.format(popt[0], np.sqrt(pcov[0][0])),
                         r'$\sigma$ = {:5.2f} $\pm$ {:5.2f} ns'.format(popt[1], np.sqrt(pcov[1][1])),
                         r'$A_0$ = {:5.1f} $\pm$ {:5.1f}'.format(popt[2], np.sqrt(pcov[2][2])),
                         r'$\tau_0$ = {:5.2f} $\pm$ {:5.2f} ns'.format(popt[3], np.sqrt(pcov[3][3])),
                         r'$A_1$ = {:5.1f} $\pm$ {:5.1f}'.format(popt[4], np.sqrt(pcov[4][4])),
                         r'$\tau_1$ = {:5.2f} $\pm$ {:5.2f} ns'.format(popt[5], np.sqrt(pcov[5][5])),
                         r'C = {:5.1f} $\pm$ {:5.2f}'.format(popt[6], np.sqrt(pcov[6][6]))
                         ])
        #
        # start the plot
        #
        #plt.figure(figsize=(10, 5))
        #plt.subplot(2, 1, 1)
        #fig = plt.figure(figsize=(10, 8))
        spec = gridspec.GridSpec(ncols=1, nrows=2,
                                 wspace=0.5,
                                 hspace=0.0, height_ratios=[3, 1])

        fig, (ax0, ax1) = plt.subplots(nrows=2, sharex='all', gridspec_kw={'height_ratios': [5, 2]})
        fig.set_size_inches(10,5)
        fig.subplots_adjust(hspace=0.05)
        #fig.set_height(10)
        #ax0 = fig.add_subplot(spec[0])
        #ax1 = fig.add_subplot(spec[1], sharex=ax0)

        ax0.hist(tt, bins=bins, range=xr, histtype='step', linewidth=1)
        ax0.text(plot_range[0]+(plot_range[1]-plot_range[0])*0.7, max(y)*0.9, txt, va='top',
                 bbox=dict(facecolor='white', edgecolor='blue', pad=5.0))
        xx = np.linspace(xr[0], xr[1], 10000)
        ax0.grid()
        ax0.plot(xx, dt_model(xx, *popt), color='green')
        ax0.plot([xr[0], xr[1]], [popt[6], popt[6]], '--', color='green')
        ax0.set_yscale('log')
        ax0.set_xlim(plot_range)

        # calculate the residuals and plot them
        res = y - dt_model(x, *popt)
        pull = res / np.sqrt(y)
        ax1.axhline(0, linewidth=1, color='grey')
        for y in range(-10,10,1):
            ax1.axhline(y, linewidth=0.5, color='grey')
        ax1.plot(x, pull)

        ax1.set_ylim([-5, 5])
        ax1.set_xlabel('$\Delta t$ (ns)', fontsize=14)
        ax1.set_ylabel('$\Delta / \sigma$', fontsize=14)



        #plt.show()
