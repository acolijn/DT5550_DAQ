from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, QtCore

from analysis.python.DT5550_Waveform import DT5550_Waveform
import sys
import glob
import wave_gui
import numpy as np
from matplotlib.pyplot import cm

N_DETECTOR = 8
N_DIGITAL_OUT = 4

# nice dark style for GUI
import qdarkstyle

fontsize_axis = 10

# Handle high resolution displays:
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class WavePlotter(QMainWindow, wave_gui.Ui_MainWindow, DT5550_Waveform):
    """
    GUI for waveform plotting - data from DT5550 in Oscilloscope mode
    """
    def __init__(self, parent=None):
        super(WavePlotter, self).__init__(parent)
        # setup the GUI
        self.setupUi(self)
        # initialize the widget functionality
        self.plotIt.clicked.connect(self.read_and_draw)
        self.saveBaseline.clicked.connect(self.save_the_baseline)
        # check boxes to select the channels
        self.checkers = [self.channel_0, self.channel_1, self.channel_2, self.channel_3,
                         self.channel_4, self.channel_5, self.channel_6, self.channel_7]
        for i in range(len(self.checkers)):
            self.checkers[i].setChecked(True)
            self.checkers[i].stateChanged.connect(self.selectChannel)
        self.trigger_sel.stateChanged.connect(self.selectChannel)
        self.baselineSubtract.stateChanged.connect(self.selectChannel)

        self.selectALL.stateChanged.connect(self.selectAllChannels)

        # disable all buttons... enable after a file is opened
        self.enableButtons(False)
        # baseline saving button only visible if the baseline tab is selected
        self.saveBaseline.setVisible(False)

        self.folderpath = ''
        self.draw_hold = False

        self.actionExit.triggered.connect(self.exit_action)
        self.actionOpenDir.triggered.connect(self.select_data_dir)
        self.actionOpenFile.triggered.connect(self.select_data_file)

        self.tabWidget.currentChanged.connect(self.tab_plot)

    def save_the_baseline(self):
        """
        Overwrite the configurations and write to file
        """

        print("save_the_baseline:: overwrite config and values to config file")
        self.baseline_to_config()
        self.write_config_file()

    def tab_plot(self):
        """
        plot: tab=waveform tab2=baseline
        """
        if self.tab.isVisible():
            self.saveBaseline.setVisible(False)
            self.drawPlot()
        elif self.tab_2.isVisible():
            self.saveBaseline.setEnabled(False)
            self.drawBaseline()
            self.saveBaseline.setVisible(True)
            self.saveBaseline.setEnabled(True)

    def exit_action(self):
        sys.exit(0)

    def select_data_file(self):
        """
        Select the datafile and initialize the DT5550_Waveform class
        """
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Select input waveform', r'C:\\data')[0]
        if self.filename == '':
            return

        DT5550_Waveform.__init__(self, file=self.filename)

        self.read_and_draw()

        self.enableButtons(True)  # now all buttons can be anabled

    def select_data_dir(self):
        """
        Select the data directory and initialize the DT5550_Waveform class
        """
        self.folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select input folder', r'C:\\data')
        fnames = glob.glob(self.folderpath + r'\wave*.raw')
        if len(fnames) == 0:
            return

        DT5550_Waveform.__init__(self, indir=self.folderpath)
        self.read_and_draw()

        self.enableButtons(True)  # now all buttons can be anabled

    def enableButtons(self, status):
        # only after selecting data we should be able to do something....
        self.plotIt.setEnabled(status)
        self.selectALL.setEnabled(status)
        [ch.setEnabled(status) for ch in self.checkers]
        self.trigger_sel.setEnabled(status)
        self.baselineSubtract.setEnabled(status)

    def selectAllChannels(self):
        #
        # we will change the individual check boxes and I dont want to re-draw the picture 8x
        #
        self.draw_hold = True

        value = self.selectALL.isChecked()
        [ch.setChecked(value) for ch in self.checkers]
        self.trigger_sel.setChecked(value)

        if self.tab.isVisible():
            self.drawPlot()
        elif self.tab_2.isVisible():
            self.drawBaseline()

        self.draw_hold = False


    def selectChannel(self):
        #
        # draw if needed
        #
        if not self.draw_hold:
            if self.tab.isVisible():
                self.drawPlot()
            elif self.tab_2.isVisible():
                self.drawBaseline()

    def read_and_draw(self):
        # read the next event
        if self.read_event() == -1:
            self.plotIt.setEnabled(False)

        # and draw either the waveform or the baseline graphs, depending on which tab is selected in the GUI
        if self.tab.isVisible():
            self.drawPlot()
        elif self.tab_2.isVisible():
            self.drawBaseline()


    def drawBaseline(self):
        """
        1. Draw the baseline histograms.
        2. Calculate the mean and the error on the mean
        3. Calculate the baseline spread
        """

        axs = self.plotBaselineWidget.canvas.ax
        nrow, ncol = np.shape(axs)

        for irow in range(nrow):
            for icol in range(ncol):
                self.plotBaselineWidget.canvas.ax[irow, icol].clear()

        for irow in range(nrow):
            for icol in range(ncol):
                idet = irow*2+icol
                # calculate the baseline from the first 100bins of the waveform
                self.calculateBaseline(idet)
                # and now plot the baseline
                txt = 'CH {:1d} \n$\mu$ = {:>5.1f} $\pm$ {:>3.1f}\n$\sigma$ = {:>5.1f}'.format(idet,
                                                                                               self.baseline[idet],
                                                                                               self.baseline_err[idet],
                                                                                               self.baseline_sigma[idet])

                vals = self.analog[idet][0:100] * self.digital[2, idet][0:100]
                vals = vals[vals > 0]

                n, bins, patches = axs[irow, icol].hist(vals, bins=500, range=(0, 1000), label=txt)
                elem = np.argmax(n)
                #print('max = ', elem, bins[elem])
                axs[irow, icol].set_xlim(bins[elem]-50, bins[elem]+50)
                axs[irow, icol].set_xlabel('baseline (ADC)', fontsize=fontsize_axis)
                axs[irow, icol].legend(loc='upper left', fontsize=8, frameon=False)


        self.plotBaselineWidget.canvas.draw()


    def drawPlot(self):
        """
        Draw the analog and digital waveforms
        """
        for i in range(5):
            self.plotWidget.canvas.ax[i].clear()

        axs = self.plotWidget.canvas.ax

        # set the bin limits... bin 1023 always behave weirrd, so I do not plot it.
        imin = 0
        imax = 1022

        Q = np.zeros([N_DETECTOR])
        Pk = np.zeros([N_DETECTOR])

        plot_range = [0, 1022]
        nplot = 0
        colors = iter(cm.rainbow(np.linspace(0, 1, N_DETECTOR)))


        #
        # loop over all the detectors
        #
        for idet in range(N_DETECTOR):
            col = next(colors)
            #
            # integrate waveform
            #
            Q[idet] = self.integrate_waveform(idet)
            Pk[idet] = self.get_peak(idet)

            #
            # calculate the peak to charge ratio
            #
            Ratio = 0
            if Q[idet] != 0:
                Ratio = Pk[idet] * (self.config['detector_settings'][idet]['GAIN']/Q[idet])

            txt = 'CH {:1d} Q = {:>5.1f} Pk = {:>5.1f} Ratio = {:>5.2f}'.format(idet, Q[idet], Pk[idet], Ratio)
            # only plot the selected channels
            if self.checkers[idet].isChecked() == True:
                # subtract the baseline (as set from the config file) from the analog signal.
                # this should be just used as an indicator, since the DT5550 DAQ dynamically adjusts the baseline
                if self.baselineSubtract.isChecked():
                    axs[0].plot(self.analog[idet][imin:imax] -
                                self.config["detector_settings"][idet]["BASE"],
                                label=txt, drawstyle='steps', c=col)
                else:
                    axs[0].plot(self.analog[idet][imin:imax], label=txt, drawstyle='steps', c=col)

                axs[0].set_xlim(plot_range)

                # plot the digital signal D0-D3
                nplot = nplot + 1
                for idig in range(N_DIGITAL_OUT):
                    axs[1 + idig].plot(self.digital[idig][idet][imin:imax], drawstyle='steps', c=col)
                    axs[1 + idig].set_xlim(plot_range)

        # plot channel #8 with trigger info as well
        if self.trigger_sel.isChecked():
            for idig in range(N_DIGITAL_OUT):
                axs[1 + idig].plot(self.digital[idig][8][imin:imax], ':', drawstyle='steps', c='black')
                axs[1 + idig].set_xlim(plot_range)

        # only draw the axis label if there are plots
        if nplot >0:
            axs[0].legend(loc='upper right', fontsize=8)

        # dual y-axis for the analog output signal. left: ADC counts right: V
        axs[0].set_ylabel('Analog (ADC)', fontsize=fontsize_axis)
        secax = axs[0].secondary_yaxis('right', functions=(self.adc2v, self.v2adc))
        secax.set_color('green')
        secax.set_ylabel('Analog (V)', fontsize=fontsize_axis)

        # set the y-limits for the digital signals and the axes labels
        for i in range(1, 5):
            axs[i].set_ylim([-0.1, 1.1])
            txt = 'D' + str(i - 1)
            axs[i].set_ylabel(txt, fontsize=fontsize_axis)

        axs[4].set_xlabel('time (CLK)', fontsize=fontsize_axis)

        #
        # Don't forget to draw the canvas
        #
        self.plotWidget.canvas.draw()

def main():
    app = QApplication(sys.argv)



    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)

    form = WavePlotter()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
