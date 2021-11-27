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

        self.t = np.zeros(N_DETECTOR)
        self.Q = np.zeros(N_DETECTOR)
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

            i0 = 8 + ioff
            i1 = 12 + ioff
            self.t[idet] = int.from_bytes(event[i0:i1], byteorder='little')

            #
            # histogramming of charge
            #
            binname = int(np.floor(self.t[idet] / self.t_binwidth) * self.t_binwidth)
            if binname not in self.times[idet]:
                self.times[idet][binname] = 0
            self.times[idet][binname] += 1

            i0 = 12 + ioff
            i1 = 14 + ioff
            # print('idet', idet,' ',event[i0:i1])
            self.Q[idet] = int.from_bytes(event[i0:i1], byteorder='little')

            binname = int(np.floor(self.Q[idet] / self.Q_binwidth) * self.Q_binwidth)
            if binname not in self.charges[idet]:
                self.charges[idet][binname] = 0
            self.charges[idet][binname] += 1

        return err
    
    def plot_time(self, idet):
        """
        Plot the charge
        
        :param idet: detector number
        """
        
        mylist = [key for key, val in self.times[idet].items() for _ in range(val)]

        plt.hist(mylist,bins=100)
        plt.xlabel('time (CLK)')

        return
    
    def plot_charge(self, idet):
        """
        Plot the charge
        
        :param idet: detector number
        """
        
        mylist = [key for key, val in self.charges[idet].items() for _ in range(val)]

        plt.hist(mylist,bins=100)
        plt.xlabel('Q (a.u.)')
        
        # you can also directly plot from teh dict, but that does not always gives a visible histogram
        # command for example: plt.bar(list(io.charges[idet].keys()),io.charges[idet].values(),width=1.)
        
        return
