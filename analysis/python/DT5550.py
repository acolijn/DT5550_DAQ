import numpy as np
import matplotlib.pyplot as plt
import numpy.polynomial.chebyshev as cheb
import glob
import os
import json

import numba as nb
import pandas as pd
#
# variable needed for data decoding
#
CHUNK_SIZE = 72  # bytes
CHANNEL_SIZE = 8  # bytes per channel
N_DETECTOR = 8  # number of detectors

@nb.jit
def word_unpack(word, ioff):

    #  decode valid bits
    i0 = 15 + ioff
    #i1 = 16 + ioff
    #ival0 = (int.from_bytes(word[i0:i1], byteorder='little') & 0x80) >> 7
    #ival1 = (int.from_bytes(word[i0:i1], byteorder='little') & 0x40) >> 6

    value = np.frombuffer(word, dtype=np.uint8, offset=i0)[0]

    ival0 = ( value & 0x80) >> 7
    ival1 = ( value & 0x40) >> 6

    #print('val0', ival0, ival_tmp0)
    #print('val1', ival1, ival_tmp1)


    return ival0, ival1


class DT5550:
    """
    DT5550 class to handle binary data
    """
    def __init__(self, **kwargs):
        """
        Initialize.....

        :param kwargs:
        """

        self.indir = kwargs.pop('indir', 'None')
        self.filename = kwargs.pop('file', 'None')
        self.config_file = kwargs.pop('config', 'None')


        if (self.indir == 'None') and (self.filename == 'None'):
            print('DT5550:: no data files specified.... re-initialize before use')
            return
        #
        # if no filename is given we analyze all files in the directory indir
        #
        self.filenames = []
        self.fin = ''

        if self.filename == 'None':
            self.filenames = sorted(glob.glob(self.indir+'/data_*.raw'), key=os.path.getmtime)
        else:
            self.filenames = glob.glob(self.filename)
            self.indir = os.path.dirname(self.filenames[0])

        if self.config_file == 'None':
            self.config_file = glob.glob(self.indir + '/config*.json')[0]

        # summary data file
        self.hd5_file = 'None'
        hd5_list = glob.glob(self.indir + '/*.hd5')
        if len(hd5_list) == 1:
            self.hd5_file = hd5_list[0]

        print('DT5550:: Data recorded with config: ', self.config_file)
        f = open(self.config_file,'r')
        self.config = json.load(f)
        f.close()

        self.found_gain_correction = False
        if 'GCOR' in self.config['detector_settings'][0].keys():
            self.found_gain_correction = True

        self.charges = [dict() for _ in range(N_DETECTOR)]
        self.Q_binwidth = 10
        
        self.times = [dict() for _ in range(N_DETECTOR)]
        self.t_binwidth = 0.1

        # event structure
        
        # time
        self.t = np.zeros(N_DETECTOR)
        # corrected time
        self.tc = np.zeros(N_DETECTOR)
        #
        self.Q = np.zeros(N_DETECTOR)
        self.ph = np.zeros(N_DETECTOR)
        self.R = np.zeros(N_DETECTOR)
        self.Qraw = np.zeros(N_DETECTOR)

        self.valid = np.zeros(N_DETECTOR)
        self.valid0 = np.zeros(N_DETECTOR)
        self.valid1 = np.zeros(N_DETECTOR)

        self.n_event = 0
        
        self.cheb_param = self.config['timewalk']['chebyshev_parameters']
        self.area_to_peak = self.config['timewalk']['area_to_peak']
        
        self.clock_speed = 12.5
        self.fine_time_bins = 16
        
        self.toff = np.zeros([N_DETECTOR])
        for i in range(N_DETECTOR):
            self.toff[i] = self.config['detector_settings'][i]['TOFF']

        return
    
    def timewalk_correct(self, idet):
        """
        Timewalk correction: base on 8th order Chebyshev fit of the pulse shape.
        """
        alpha = 0
        peak = self.ph[idet]
        if peak != 0:
            alpha = self.config['detector_settings'][idet]['THRS'] / peak
        # else:
        #    print('timewalk_correction:: WARNING peak = ',peak,' Q= ',Q,' conv = ',self.area_to_peak)
            
        if alpha > 1:
            alpha = 1
        elif alpha < 0:
            alpha = 0
            
        dt = cheb.chebval(alpha, self.cheb_param)*self.clock_speed

        return dt

    def open_data(self, filename):
        print('DT5550:: Open data file:', filename)
        self.fin = open(filename, "rb")

    def close_data(self):
        self.fin.close()

    def read_event(self):
        """
        Read and decode a single event
        """
        err = 0

        #
        # this is the actual read from the data
        #
        event = self.fin.read(CHUNK_SIZE)
        if not event:
            err = -1
            return err

        self.n_event = self.n_event+1

        #
        # process the data
        #
        for idet in range(N_DETECTOR):
            #  offset to data
            ioff = idet * CHANNEL_SIZE

            #  decode valid bits
            i0 = 15 + ioff
            i1 = 16 + ioff
            ival0 = (int.from_bytes(event[i0:i1], byteorder='little') & 0x80) >> 7
            ival1 = (int.from_bytes(event[i0:i1], byteorder='little') & 0x40) >> 6

            #print('A: I0 =',ival0, ival1)
            #ival0, ival1 = word_unpack(event, ioff)
            #print('B: I0 =',ival0, ival1)

            self.valid0[idet] = ival0  # valid charge measurement
            self.valid1[idet] = ival1  # valid time measurement
            ival = (ival0 & ival1)
            self.valid[idet] = ival

            i0 = 12 + ioff
            i1 = 14 + ioff
            gcor = 1.0
            if self.found_gain_correction:
                gcor = self.config['detector_settings'][idet]['GCOR']
            self.Qraw[idet] = int.from_bytes(event[i0:i1], byteorder='little')
            self.Qraw[idet] = self.Qraw[idet] * gcor

            # reset the measured values
            self.Q[idet] = 0
            self.ph[idet] = 0
            self.t[idet] = 0
            self.tc[idet] = 0
            self.R[idet] = 0
            # only fill if there is valid data on this detector
            if ival:
                # decode time
                i0 = 8 + ioff
                i1 = 12 + ioff
                self.t[idet] = int.from_bytes(event[i0:i1], byteorder='little')*self.clock_speed/self.fine_time_bins
                self.t[idet] = self.t[idet]*ival
                # decode pulse height
                i0 = 14 + ioff
                i1 = 16 + ioff
                self.ph[idet] = (int.from_bytes(event[i0:i1], byteorder='little') & 0x3FFF)
                # decode charge
                i0 = 12 + ioff
                i1 = 14 + ioff

                gain = self.config['detector_settings'][idet]['GAIN']
                gcor = 1.0
                if self.found_gain_correction:
                    gcor = self.config['detector_settings'][idet]['GCOR']
                self.Q[idet] = int.from_bytes(event[i0:i1], byteorder='little')
                if self.Q[idet] > 0.:
                    self.R[idet] = self.ph[idet] * gain / self.Q[idet]

                self.Q[idet] = self.Q[idet]*gcor

                #  make the timewalk correction
                self.t[idet] = self.t[idet]-self.toff[idet]
                dt = self.timewalk_correct(idet)
                self.tc[idet] = self.t[idet] - dt

                #  dictonary with charge
                binname = int(np.floor(self.Q[idet] / self.Q_binwidth) * self.Q_binwidth)
                if binname not in self.charges[idet]:
                    self.charges[idet][binname] = 0
                self.charges[idet][binname] += 1
                # histogramming time
                binname = int(np.floor(self.tc[idet] / self.t_binwidth) * self.t_binwidth)
                if binname not in self.times[idet]:
                    self.times[idet][binname] = 0
                self.times[idet][binname] += 1


        return err
    
    def plot_time(self, idet, bins, plot_range, logy):
        """
        Plot the charge
        
        :param idet: detector number
        :param bins: number of bins
        :param plot_range: range of the plot
        :param logy: logarithmic plot or not
        """
        
        mylist = [key for key, val in self.times[idet].items() for _ in range(val)]

        if plot_range[0] == -1:
            plot_range = (0, max(mylist))
        
        plt.hist(mylist, bins=bins, range=plot_range, histtype='step', color='blue')
        plt.title("id ="+str(idet), x=0.9, y=0.85)
        if logy:
            plt.yscale('log')
        else:
            plt.yscale('linear') 

        plt.xlabel('time (CLK)')

        return
    
    def plot_charge(self, idet, bins, plot_range, logy):
        """
        Plot the charge

        :param idet: detector number
        :param bins: number of bins
        :param plot_range: range of the plot
        :param logy: logarithmic plot or not
        """

        mylist = [key for key, val in self.charges[idet].items() for _ in range(val)]
        
        if plot_range[0] == -1:
            plot_range = (0, max(mylist))

        plt.hist(mylist, bins=bins, range=plot_range, histtype='step', color='blue')
        plt.title("id ="+str(idet), x=0.9, y=0.85)
        if logy:
            plt.yscale('log')
        else:
            plt.yscale('linear')    
        plt.xlabel('Q (a.u.)')
        
        # you can also directly plot from teh dict, but that does not always gives a visible histogram
        # command for example: plt.bar(list(io.charges[idet].keys()),io.charges[idet].values(),width=1.)
        
        return
    
    def plot_all(self, **kwargs):
        """
        Plot for all detectors
        
        :param **kwargs: type ("charge", "time")
        :param **kwargs: bins (default 100)
        :param **kwargs: range (min,max)
        :param **kwargs: logy (default = False)
        """        
        plot_type = kwargs.pop('type', 'charge')
        plot_range = kwargs.pop('range', (-1, -1))
        bins = kwargs.pop('bins', 100)
        logy = kwargs.pop('logy', False)

        plt.figure(figsize=(10, 15))

        for idet in range(N_DETECTOR):
            plt.subplot(4, 2, 1+idet)
            if plot_type == "charge":
                self.plot_charge(idet, bins=bins, plot_range=plot_range, logy=logy)
            elif plot_type == "time":
                self.plot_time(idet, bins=bins, plot_range=plot_range, logy=logy)
   
        plt.show()

        return

    def write_config_file(self):
        """
        Overwrite the configuration file with the current values of the settings
        """
        fout = open(self.config_file, "w")
        json.dump(self.config, fout, indent=4)
        fout.close()
