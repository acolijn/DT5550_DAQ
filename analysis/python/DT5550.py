import numpy as np
import matplotlib.pyplot as plt
import numpy.polynomial.chebyshev as cheb
import glob
import os
import json

#
# variable needed for data decoding
#
CHUNK_SIZE = 72  # bytes
CHANNEL_SIZE = 8  # bytes per channel
N_DETECTOR = 8  # number of detectors


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
        
        #
        # if no filename is given we analyze all files in the directory indir
        #
        self.filenames = []
        self.fin = ''
        self.config_file = 'None'

        if self.filename == 'None':
            self.filenames = glob.glob(self.indir+'/data_*.raw')

        else:
            self.filenames = glob.glob(self.filename)
            self.indir = os.path.dirname(self.filenames[0])

        self.config_file = glob.glob(self.indir + '/config*.json')[0]
        print('DT5550:: Data recorded with config: ', self.config_file)
        f = open(self.config_file,'r')
        self.config = json.load(f)
        f.close()
        
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
        self.Qold = np.zeros(N_DETECTOR)

        self.valid = np.zeros(N_DETECTOR)
        self.valid_old = np.zeros(N_DETECTOR)


        self.n_event = 0
        
        self.cheb_param = self.config['timewalk']['chebyshev_parameters']
        self.area_to_peak = self.config['timewalk']['area_to_peak']
        
        self.clock_speed = 12.5
        self.fine_time_bins = 16
        
        self.toff = np.zeros([N_DETECTOR])
        for i in range(N_DETECTOR):
            self.toff[i] = self.config['detector_settings'][i]['TOFF']
            #print(i,'TOFF = ',self.toff[i])

        return
    
    def timewalk_correct(self, idet):
        
        Q = self.Q[idet]
        peak = Q*self.area_to_peak  # always the same conversion factor
        alpha = 0
        if peak != 0:
            alpha = self.config['detector_settings'][idet]['THRS'] / peak
        # else:
        #    print('timewalk_correction:: WARNING peak = ',peak,' Q= ',Q,' conv = ',self.area_to_peak)
            
        if alpha > 1:
            alpha = 1
        elif alpha < 0:
            alpha = 0
            
        dt = cheb.chebval(alpha, self.cheb_param)*self.clock_speed
        # print('peak = ',peak,' Q =',Q,' THRS =',self.config['detector_settings'][idet]['THRS'],
        # ' alpha = ',alpha,' dt = ',dt)

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
        for i in range(N_DETECTOR):
            self.Qold[i] = self.Q[i]
            self.valid_old[i] = self.valid[i]
        
        err = 0
        event = self.fin.read(CHUNK_SIZE)
        if not event:
            err = -1
            return err

        self.n_event = self.n_event+1

        for idet in range(N_DETECTOR):
            ioff = idet * CHANNEL_SIZE
            
            # decode valid bit
            i0 = 15 + ioff
            i1 = 16 + ioff
            ival0 = (int.from_bytes(event[i0:i1], byteorder='little') & 0x80) >> 7
            # ival1 = (int.from_bytes(event[i0:i1], byteorder='little') & 0x40) >> 6
            # print(idet,'v0',ival0,'v1',ival1)
            # ival = (ival0 & ival1)
            ival = ival0
            
            self.valid[idet] = ival

            # decode time
            i0 = 8 + ioff
            i1 = 12 + ioff
            self.t[idet] = int.from_bytes(event[i0:i1],                                   byteorder='little')*self.clock_speed/self.fine_time_bins
            # decode charge
            i0 = 12 + ioff
            i1 = 14 + ioff
            self.Q[idet] = int.from_bytes(event[i0:i1], byteorder='little')

            #if ival == 1 and self.Q[idet] ==0:
            #    print('asjemenou.....')

            # make the timewalk correction
            self.t[idet] = self.t[idet]-self.toff[idet]
            if ival == 1:
                dt = self.timewalk_correct(idet)
                self.tc[idet] = self.t[idet] - dt
            
            
            # dictonary with charge
            if ival:
                binname = int(np.floor(self.Q[idet] / self.Q_binwidth) * self.Q_binwidth)
                if binname not in self.charges[idet]:
                    self.charges[idet][binname] = 0
                self.charges[idet][binname] += 1
            # histogramming time
            if ival:
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
        
        plt.hist(mylist, bins=bins, range=plot_range)
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

        plt.hist(mylist, bins=bins, range=plot_range)
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
