import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import json

N_DETECTOR = 8
N_BINS = 1024
N_DIGITAL_OUT = 4
CH_SIZE = 4  # 4 - bytes per channel
MAX14BIT = 16383
MAX16BIT = 65535

NCHANNEL_OSC = 9


class DT5550_Waveform:
    """
    DT5550 class to handle waveform data
    """
    def __init__(self, **kwargs):
        """
        Initialize

        param kwargs:
        """
        print('DT5550_Waveform:: Initialize......')
        self.indir = kwargs.pop('indir', 'None')
        self.filename = kwargs.pop('file', 'None')

        #
        # if no filename is given we analyze all files in the directory indir
        #
        self.filenames = []
        #self.fin = ''
        self.config_file = 'None'

        if self.filename == 'None':
            self.filenames = glob.glob(self.indir + '/waveform_*.raw')
        else:
            self.filenames = glob.glob(self.filename)
            self.indir = os.path.dirname(self.filenames[0])

        self.config_file = glob.glob(self.indir+r'\config*.json')[0]
        
        # read the configuration file for this run
        f = open(self.config_file, 'r')
        self.config = json.load(f)
        f.close()

        self.n_event = 0
        
        self.analog  = np.zeros([NCHANNEL_OSC, N_BINS])
        self.digital = np.zeros([N_DIGITAL_OUT, NCHANNEL_OSC, N_BINS])

        self.current_file = 0
        self.open_data(self.filenames[0])

        self.end_of_data = False

        self.baseline = np.zeros(N_DETECTOR)
        self.baseline_err = np.zeros(N_DETECTOR)
        self.baseline_sigma = np.zeros(N_DETECTOR)

        return

    def open_data(self, filename):
        print('DT5550_Waveform:: Open data file:', filename)
        self.fin = open(filename, "rb")

    def close_data(self):
        self.fin.close()

    def read_event(self):
        """
        Read and decode a single event
        """

        err = 0
        if not self.end_of_data:
            wave = self.fin.read(N_BINS*NCHANNEL_OSC*CH_SIZE)
        else:
            wave = 0
        #
        # red an event. if we are at the end of a file then open the next one
        #
        if not wave:
            self.close_data()
            # see if there exist more files
            self.current_file = self.current_file+1
            if self.current_file < len(self.filenames):
                self.open_data(self.filenames[self.current_file])
                wave = self.fin.read(N_BINS * NCHANNEL_OSC * CH_SIZE)
            else:
                print("DT5550_Waveform::INFO end of data")
                self.end_of_data = True
                return -1

        self.n_event = self.n_event+1

        for idet in range(NCHANNEL_OSC):
            max_ch = 0
            min_ch = 9999999
            for i in range(N_BINS-2):
                i0 = i*CH_SIZE + idet*N_BINS*CH_SIZE
                i1 = i0+CH_SIZE
                self.analog[idet][i] = (int.from_bytes(wave[i0:i1], byteorder='little') & 0x00003fff )
                if self.analog[idet][i] > max_ch:
                    max_ch = self.analog[idet][i]
                if self.analog[idet][i] < min_ch:
                    min_ch = self.analog[idet][i]
                for idig in range(N_DIGITAL_OUT):
                    self.digital[idig][idet][i] = \
                        (int.from_bytes(wave[i0:i1], byteorder='little') >> 16+idig) & 0x00000001
            # print(idet,'min =',min_ch,' max =',max_ch,' delta =',max_ch-min_ch)
        return err

    def adc2v(self, adc):
        return adc/MAX14BIT*1.8

    def v2adc(self, v):
        return v*MAX14BIT/1.8
    
    def integrate_waveform(self, idet):
        """
        Integrate the waveform
        """
        baseline = self.config["detector_settings"][idet]["BASE"]
        gain = self.config["detector_settings"][idet]["GAIN"]
        corr = 1.0
        if "GCOR" in self.config["detector_settings"][idet].keys():
            corr = self.config["detector_settings"][idet]["GCOR"]
        inttime = self.config["registers"]["INTTIME"]
        
        idx = 0
        for i in range(1023):
            if self.digital[0, idet, i] == 1:
                idx = i+10
                break
        
        wave = (self.analog[idet, idx:idx+inttime]-baseline)  # *self.digital[3,idet,:]
        Q = (wave.sum()) / MAX16BIT * gain * corr
        
        return Q
    
    def get_peak(self, idet):
        """
        Get the peak value
        """
        baseline = self.config["detector_settings"][idet]["BASE"]
        wave = (self.analog[idet, :]-baseline)*self.digital[3, idet, :]
        peak = wave.max()
        
        return peak

    def calculateBaseline(self, idet):
        """
        Calculate the baseline from the waveform data
        """

        vals = self.analog[idet][0:100] * self.digital[2, idet][0:100]
        vals = vals[vals > 0]
        self.baseline[idet] = vals.mean()
        self.baseline_sigma[idet] = np.sqrt(vals.var())
        self.baseline_err[idet] = self.baseline_sigma[idet] / np.sqrt(len(vals))
        print('calculateBaseline:: idet =', idet,' baseline =', self.baseline[idet])
    
    def plot_waveform(self, plot_range):
        """
        Plot the waveform
        """
        # plot single event
        imin = 0
        imax = 1022
        fig, axs = plt.subplots(5, 1, sharex=True, gridspec_kw={'height_ratios': [5, 1.5, 1.5, 1.5, 1.5]}, figsize=(15, 10))
        
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
            
            # txt = 'CH '+str(idet)+' Q='+str(Q[idet])+' Pk='+str(Pk[idet])+' Ratio = '+str((Ratio))
            txt = 'CH {:1d} Q = {:>5.1f} Pk = {:>5.1f} Ratio = {:>5.2f}'.format(idet, Q[idet], Pk[idet], Ratio)
            axs[0].plot(self.analog[idet][imin:imax] -
                        self.config["detector_settings"][idet]["BASE"], label=txt, drawstyle='steps')
            axs[0].set_xlim(plot_range)
            for idig in range(N_DIGITAL_OUT):
                axs[1+idig].plot(self.digital[idig][idet][imin:imax], drawstyle='steps')
                axs[1+idig].set_xlim(plot_range)

        # plot channel #8 with trigger info as well
        for idig in range(N_DIGITAL_OUT):
            #print(self.digital[idig][8][imin:imax])
            axs[1 + idig].plot(self.digital[idig][8][imin:imax], drawstyle='steps')
            axs[1 + idig].set_xlim(plot_range)

        axs[0].legend(loc='upper right')
        # if N_DETECTOR == 8:
        #    for idig in range(N_DIGITAL_OUT):
        #        axs[1+idig].plot(self.digital[idig][7][imin:imax])    
    
        axs[0].set_ylabel('Analog (ADC)')
        # axs[0].set_ylim([-20,20])
        secax = axs[0].secondary_yaxis('right', functions=(self.adc2v, self.v2adc))
        secax.set_color('green')
        secax.set_ylabel('Analog (V)')
        
        for i in range(1, 5):
            axs[i].set_ylim([-0.1, 1.1])
            txt = 'D'+str(i-1)
            axs[i].set_ylabel(txt)

        plt.xlabel('time (CLK)')
        plt.show()

        return fig

    def baseline_to_config(self):
        """
        Modify the configuration dictionary with the new baseline values
        """

        for idet in range(N_DETECTOR):
            self.config['detector_settings'][idet]['BASE'] = self.baseline[idet]

    def write_config_file(self):
        """
        Overwrite the configuration file with the current values of the settings
        """
        print("write_config_file:: write config to ", self.config_file)
        fout = open(self.config_file, "w")
        json.dump(self.config, fout, indent=4)
        fout.close()
