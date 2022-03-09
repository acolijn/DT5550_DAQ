from DT5550 import *

import numpy as np
import pandas as pd

N_DETECTOR = 8


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

    def process_data(self, **kwargs):
        """
        Process the data for use in the Co60 analysis

        Input: max_files = maximum number of files to process (set to low number for debugging)
               data = 'raw' -> raw data (re-)processing
                    = 'hd5' -> summary hhd5 data read directly (if existent, otherwise raw processing)
        """

        nfmax = kwargs.pop('max_files', 99999)  # maximum number of files to process (handy for debugging)
        data = kwargs.pop('data', 'raw')

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

    def process_event(self, **kwargs):
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
        if (nh >= 3) and (self.Q.sum() > 2150) and (self.Q.sum() < 2400):
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

                if abs(self.Q[idet] - 1274) < 100 and (self.valid[idet]) and (abs(rr - rmean) < 3 * rsig):
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
                if (self.valid[idet]) and (idet != i0) and (abs(rr - rmean) < 3 * rsig):
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
