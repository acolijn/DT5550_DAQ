import numpy as np
import matplotlib.pyplot as plt
import glob, os, json

N_DETECTOR = 8
N_BINS = 1024
N_DIGITAL_OUT = 4
CH_SIZE = 4 # 4 - bytes per channel

#
# variable needed for data decoding
#
class DT5550_Waveform:
    """
    DT5550 class to handle waveform data
    """
    def __init__(self, **kwargs):
        """
        Initialize.....

        :param kwargs:
        """

        self.filename = kwargs.pop('file', 'None')
        self.fin = open(self.filename,"rb")
        
        indir = os.path.dirname(self.filename)        
        config_file = glob.glob(indir+'\config*.json')[0]
        
        # read the configuration file for this run
        f = open(config_file,'r')
        self.config = json.load(f)
        f.close()

        self.n_event = 0
        
        self.analog  = np.zeros([N_DETECTOR,N_BINS])
        self.digital = np.zeros([N_DIGITAL_OUT,N_DETECTOR,N_BINS])

        return

    def read_event(self):
        """
        Read and decode a single event
        """

        err = 0
        wave = self.fin.read(N_BINS*N_DETECTOR*CH_SIZE)

        if not wave:
            self.fin.close()
            err = -1
            return err

        self.n_event = self.n_event+1

        for idet in range(N_DETECTOR):
            max_ch = 0
            min_ch = 9999999
            for i in range(N_BINS-2):
                i0 = i*CH_SIZE + idet*N_BINS*CH_SIZE
                i1 = i0+CH_SIZE
                self.analog[idet][i] = ( int.from_bytes(wave[i0:i1],byteorder='little') & 0x00003fff ) 
                if self.analog[idet][i] > max_ch:
                    max_ch = self.analog[idet][i]
                if self.analog[idet][i] < min_ch:
                    min_ch = self.analog[idet][i]
                for idig in range(N_DIGITAL_OUT):
                    self.digital[idig][idet][i] = (int.from_bytes(wave[i0:i1],byteorder='little') >> 16+idig) & 0x00000001
            #print(idet,'min =',min_ch,' max =',max_ch,' delta =',max_ch-min_ch)
        return err
    
    def adc2v(self,adc):
        return adc/2**14*1.8
    
    def v2adc(self,v):
        return v*2**14/1.8
    
    def integrate_waveform(self, idet):
        """
        Integrate the waveform
        """
        baseline = self.config["detector_settings"][idet]["BASE"]
        gain = self.config["detector_settings"][idet]["GAIN"]
        inttime = self.config["registers"]["INTTIME"]
        
        idx = 0
        for i in range(1023):
            if self.digital[0,idet,i] == 1:
                idx = i+10
                break
        
        wave = (self.analog[idet,idx:idx+inttime]-baseline)#*self.digital[3,idet,:]
        Q = (wave.sum()) / 2**16 * gain 
        
        return Q
    
    def get_peak(self,idet):
        """
        Get the peak value
        """
        baseline = self.config["detector_settings"][idet]["BASE"]
        wave = (self.analog[idet,:]-baseline)*self.digital[3,idet,:]
        peak = wave.max()
        
        return peak
    
    def plot_waveform(self, plot_range):
        """
        Plot the waveform
        
        :param idet: detector number
        """
        
        print(plot_range)
  
        # plot single event
        imin=0
        imax=1022
        fig, axs = plt.subplots(5,1, sharex=True, gridspec_kw={'height_ratios':[5,1,1,1,1]}, figsize=(15,10))
        
        Q = np.zeros([N_DETECTOR])
        Pk = np.zeros([N_DETECTOR])
        for idet in range(N_DETECTOR):
            #
            # integrate waveform
            #
            Q[idet] = self.integrate_waveform(idet)
            Pk[idet] = self.get_peak(idet)
            
            Ratio = 0
            if Q[idet] != 0:
                Ratio = Pk[idet]/Q[idet]
            
            txt = 'CH '+str(idet)+' Q='+str(Q[idet])+' Pk='+str(Pk[idet])+' Ratio = '+str((Ratio))
                                                                    
            axs[0].plot(self.analog[idet][imin:imax]-
                        self.config["detector_settings"][idet]["BASE"],label=txt,drawstyle='steps')
            axs[0].set_xlim(plot_range)
            for idig in range(N_DIGITAL_OUT):
                axs[1+idig].plot(self.digital[idig][idet][imin:imax],drawstyle='steps')
                axs[1+idig].set_xlim(plot_range)
        axs[0].legend(loc='upper right')
        #if N_DETECTOR == 8:
        #    for idig in range(N_DIGITAL_OUT):
        #        axs[1+idig].plot(self.digital[idig][7][imin:imax])    
    
        axs[0].set_ylabel('Analog (ADC)')
        #axs[0].set_ylim([-20,20])
        secax = axs[0].secondary_yaxis('right',functions=(self.adc2v,self.v2adc))
        secax.set_color('green')
        secax.set_ylabel('Analog (V)')
        
        
        for i in range(1,5):
            axs[i].set_ylim([0,1.3])
            txt = 'D'+str(i-1)
            axs[i].set_ylabel(txt)

        plt.xlabel('time (CLK)')
        plt.show()

        return fig
    