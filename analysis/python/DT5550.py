import numpy as np
import matplotlib.pyplot as plt
import numba

#
# variable needed for data decoding
#
CHUNK_SIZE = 72 # bytes
CHANNEL_SIZE = 8 # bytes per channel
N_DETECTOR = 8# number of detectors

class DT5550:
    """
    DT5550 class to handle binary data
    """
    def __init__(self, **kwargs):
        """
        Initialize.....

        :param kwargs:
        """

        self.filename = kwargs.pop('file', 'None')
        self.fin = open(self.filename,"rb")

        self.charges = [dict() for x in range(N_DETECTOR)]
        self.Q_binwidth = 20
        
        self.times = [dict() for x in range(N_DETECTOR)]
        self.t_binwidth = 1

        # event structure
        self.t = np.zeros(N_DETECTOR)
        self.Q = np.zeros(N_DETECTOR)
        self.valid = np.zeros(N_DETECTOR)

        self.n_event = 0

        return

    def read_event(self):
        """
        Read and decode a single event
        """

        err = 0
        event = self.fin.read(CHUNK_SIZE)
        if not event:
            self.fin.close()
            err = -1
            return err

        self.n_event = self.n_event+1

        for idet in range(N_DETECTOR):
            ioff = idet * CHANNEL_SIZE
            
            # decode valid bit
            i0 = 15 + ioff
            i1 = 16 + ioff
            ival0 = (int.from_bytes(event[i0:i1],byteorder='little') & 0x80)>>7
            ival1 = (int.from_bytes(event[i0:i1],byteorder='little') & 0x40)>>6
            # print(idet,'v0',ival0,'v1',ival1)
            #ival = (ival0 & ival1)
            ival = ival0
            
            self.valid[idet] = ival

            # decode time
            i0 = 8 + ioff
            i1 = 12 + ioff

            self.t[idet] = int.from_bytes(event[i0:i1], byteorder='little')

            # histogramming time
            if ival:
                binname = int(np.floor(self.t[idet] / self.t_binwidth) * self.t_binwidth)
                if binname not in self.times[idet]:
                    self.times[idet][binname] = 0
                self.times[idet][binname] += 1

            # decode charge
            i0 = 12 + ioff
            i1 = 14 + ioff
            self.Q[idet] = int.from_bytes(event[i0:i1], byteorder='little')

            # dictonary with charge
            if ival:
                binname = int(np.floor(self.Q[idet] / self.Q_binwidth) * self.Q_binwidth)
                if binname not in self.charges[idet]:
                    self.charges[idet][binname] = 0
                self.charges[idet][binname] += 1



        return err
    
    def plot_time(self, idet, bins, plot_range, logy):
        """
        Plot the charge
        
        :param idet: detector number
        """
        
        mylist = [key for key, val in self.times[idet].items() for _ in range(val)]

        plt.hist(mylist,bins=bins, range=plot_range)
        plt.title("id ="+str(idet),x=0.9,y=0.85)
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
        """
        
        mylist = [key for key, val in self.charges[idet].items() for _ in range(val)]

        plt.hist(mylist,bins=bins, range=plot_range)
        plt.title("id ="+str(idet),x=0.9,y=0.85)
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
        plot_type = kwargs.pop('type','charge')
        plot_range = kwargs.pop('range',(0,10000))
        bins = kwargs.pop('bins',100)
        logy = kwargs.pop('logy',False)


        fig = plt.figure(figsize=(10,15))

        for idet in range(N_DETECTOR):
            plt.subplot(4, 2, 1+idet)
            if plot_type == "charge":
                self.plot_charge(idet,bins=bins,plot_range=plot_range, logy=logy)
            elif plot_type == "time":
                self.plot_time(idet,bins=bins,plot_range=plot_range, logy=logy)
   
        plt.show()

        return