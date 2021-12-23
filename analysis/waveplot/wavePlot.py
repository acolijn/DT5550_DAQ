from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets

from analysis.python.DT5550_Waveform import DT5550_Waveform
import sys
import wave_gui
import numpy as np
from matplotlib.pyplot import cm


N_DETECTOR = 8
N_DIGITAL_OUT = 4

class WavePlotter(QMainWindow, wave_gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(WavePlotter, self).__init__(parent)
        self.setupUi(self)
        self.plotIt.clicked.connect(self.readAndDraw)
        # check boxes
        #        self.findChild()
        self.checkers = [self.channel_0, self.channel_1, self.channel_2, self.channel_3, self.channel_4, self.channel_5, self.channel_6, self.channel_7]
        for i in range(len(self.checkers)):
            self.checkers[i].setChecked(True)
            self.checkers[i].stateChanged.connect(self.selectChannel)

        self.selectALL.stateChanged.connect(self.selectAllChannels)

        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select input folder', r'C:\\Users\aukep\surfdrive\FineStructure\data')
        self.waves = DT5550_Waveform(indir=folderpath)
        # read first event and plot
        self.readAndDraw()

        self.draw_hold = False

    def selectAllChannels(self):
        # we will change the individual check boxes and I dont want to re-draw the picture 8x
        self.draw_hold = True

        value = self.selectALL.isChecked()
        [ch.setChecked(value) for ch in self.checkers]

        self.drawPlot()

        self.draw_hold = False

    def selectChannel(self):
        if not self.draw_hold:
            self.drawPlot()

    def readAndDraw(self):
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

        plot_range = [0, 1022]
        nplot = 0
        colors = iter(cm.rainbow(np.linspace(0, 1, N_DETECTOR)))

        for idet in range(N_DETECTOR):
            col = next(colors)
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
            if self.checkers[idet].isChecked() == True:
                axs[0].plot(self.waves.analog[idet][imin:imax] -
                            self.waves.config["detector_settings"][idet]["BASE"], label=txt, drawstyle='steps', c=col)
                axs[0].set_xlim(plot_range)
                nplot = nplot + 1
                for idig in range(N_DIGITAL_OUT):
                    axs[1 + idig].plot(self.waves.digital[idig][idet][imin:imax], drawstyle='steps', c=col)
                    axs[1 + idig].set_xlim(plot_range)

        # plot channel #8 with trigger info as well
        for idig in range(N_DIGITAL_OUT):
            axs[1 + idig].plot(self.waves.digital[idig][8][imin:imax], ':', drawstyle='steps', c='black')
            axs[1 + idig].set_xlim(plot_range)

        if nplot >0:
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

        axs[4].set_xlabel('time (CLK)')
        self.plotWidget.canvas.draw()

def main():
    app = QApplication(sys.argv)
    form = WavePlotter()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()