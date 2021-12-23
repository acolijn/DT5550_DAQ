from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
sys.path.insert(0,'../python/')
from DT5550_Waveform import *
import wave_gui

N_DETECTOR = 8

class WavePlotter(QMainWindow, wave_gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(WavePlotter, self).__init__(parent)
        self.setupUi(self)
        self.plotIt.clicked.connect(self.buttonClicked)

        filename = "../../../data/20211217_171057/20211217_171057/waveform_20211217_171057_0.raw"
        self.waves = DT5550_Waveform(file=filename)
        # read first event and plot
        self.waves.read_event()
        self.drawPlot()

    def buttonClicked(self):
        self.waves.read_event()
        self.drawPlot()

    def drawPlot(self):
        for i in range(5):
            self.plotWidget.canvas.ax[i].clear()

        axs = self.plotWidget.canvas.ax

        # plot single event
        imin = 0
        imax = 1022

        Q = np.zeros([N_DETECTOR])
        Pk = np.zeros([N_DETECTOR])

        plot_range=[0,1022]
        for idet in range(N_DETECTOR):
            #
            # integrate waveform
            #
            Q[idet] = self.waves.integrate_waveform(idet)
            Pk[idet] = self.waves.get_peak(idet)

            Ratio = 0
            if Q[idet] != 0:
                Ratio = Pk[idet] / Q[idet]

            # txt = 'CH '+str(idet)+' Q='+str(Q[idet])+' Pk='+str(Pk[idet])+' Ratio = '+str((Ratio))
            txt = 'CH {:1d} Q = {:>5.1f} Pk = {:>5.1f} Ratio = {:>5.2f}'.format(idet, Q[idet], Pk[idet], Ratio)
            print(txt)
            axs[0].plot(self.waves.analog[idet][imin:imax] -
                        self.waves.config["detector_settings"][idet]["BASE"], label=txt, drawstyle='steps')
            axs[0].set_xlim(plot_range)
            for idig in range(N_DIGITAL_OUT):
                axs[1 + idig].plot(self.waves.digital[idig][idet][imin:imax], drawstyle='steps')
                axs[1 + idig].set_xlim(plot_range)

        # plot channel #8 with trigger info as well
        for idig in range(N_DIGITAL_OUT):
            axs[1 + idig].plot(self.waves.digital[idig][8][imin:imax], drawstyle='steps')
            axs[1 + idig].set_xlim(plot_range)

        axs[0].legend(loc='upper right')
        # if N_DETECTOR == 8:
        #    for idig in range(N_DIGITAL_OUT):
        #        axs[1+idig].plot(self.digital[idig][7][imin:imax])
        axs[0].set_ylabel('Analog (ADC)')
        # axs[0].set_ylim([-20,20])
        secax = axs[0].secondary_yaxis('right', functions=(self.waves.adc2v, self.waves.v2adc))
        secax.set_color('green')
        secax.set_ylabel('Analog (V)')

        for i in range(1, 5):
            axs[i].set_ylim([-0.1, 1.1])
            txt = 'D' + str(i - 1)
            axs[i].set_ylabel(txt)

        self.plotWidget.canvas.draw()

def main():
    app = QApplication(sys.argv)
    form = WavePlotter()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()