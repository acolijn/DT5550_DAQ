import pywt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QWidget
from PyQt5 import Qt, QtWidgets, QtCore
from PyQt5.QtCore import QThread, QProcess

from datetime import datetime
import sys
import json
import daq_interface
import define_geometry

N_DETECTOR = 8
N_DIGITAL_OUT = 4

import qdarkstyle

fontsize_axis = 10

PYTHON = "C:\ProgramData\Anaconda3\python"

# Handle high resolution displays:
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)



def deg2rad(deg):
    return deg*0.01745329


def rad2deg(rad):
    return rad*57.2957795


class GeometryWidget(QWidget, define_geometry.Ui_Form):
    def __init__(self, parent=None):
        super(GeometryWidget, self).__init__(parent)
        self.setupUi(self)
        self.config = []
        self.hlabels = []
        self.vlabels = []

    def initGeometrySettingsTable(self):
        """
        Initialize the table with individual detector settings
        """
        table = self.geometrySettings
        table.setRowCount(N_DETECTOR)

        self.hlabels = ("X", "Y", "Z")

        table.setColumnCount(len(self.hlabels))

        hlabels_display = ("X (mm)", "Y (mm)", "Z (mm)")
        table.setHorizontalHeaderLabels(hlabels_display)
        for i in range(N_DETECTOR):
            name = "CH "+str(i)
            self.vlabels.append(name)
        table.setVerticalHeaderLabels(self.vlabels)

        self.fillGeometrySettingsTable()

        self.setTableSize(self.geometrySettings)


    def fillGeometrySettingsTable(self):
        """
        Fill the table with settings from the current config file
        """
        table = self.geometrySettings
        for idet in range(N_DETECTOR):
            for label in self.hlabels:
                icol = self.hlabels.index(label)

                if label in self.config['detector_settings'][idet].keys():
                    val = self.config['detector_settings'][idet][label]
                else:
                    val = 0.0

                table.setItem(idet, icol, QTableWidgetItem(str(val)))

    def readGeometryFromTable(self):
        """
        Read the values from the geometry table to make a new configuration
        """
        #self.config_new = self.config

        # individual detector settings
        for idet in range(N_DETECTOR):
            for label in self.hlabels:
                icol = self.hlabels.index(label)
                value = self.geometrySettings.item(idet, icol).text()
                self.config['detector_settings'][idet][label] = float(value)

    def setTableSize(self, tab):

        # width
        width = tab.verticalHeader().width()
        width += tab.horizontalHeader().length()
        if tab.verticalScrollBar().isVisible():
            width += tab.verticalScrollBar().width()
        width += tab.frameWidth() * 2
        tab.setFixedWidth(width*1.05)
        tab.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # height
        #height = tab.verticalHeader().height()
        #height += tab.horizontalHeader().height()
        #if tab.horizontalScrollBar().isVisible():
        #    height += tab.horizontalScrollBar().height()
        #height += tab.rowHeight()*8
        #tab.setFixedHeight(height*1.01)

        tab.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)



class DAQgui(QMainWindow, daq_interface.Ui_MainWindow):
    """
    GUI for DAQ
    """
    def __init__(self, parent=None):
        super(DAQgui, self).__init__(parent)
        # setup the GUI
        self.setupUi(self)

        self.w = GeometryWidget()

        self.default_config_file = '../ReadoutClient/config.json'
        self.config_file = 'None'
        self.config = ''
        self.config_new = ''
        self.hlabels = []
        self.g_hlabels = []
        self.vlabels = []
        self.logcounter = 0
        self.doit = QProcess()
        self.doit.readyReadStandardOutput.connect(self.handle_stdout)
        self.doit.finished.connect(self.process_finished)  # Clean up once complete.

        self.open_geometry_button.clicked.connect(self.open_geometry_window)
        self.w.close_window.clicked.connect(self.close_geometry_window)

        #self.define_geometry = Second(self)

        # read the default configuration file....
        self.readConfiguration()
        # initialize the table with global detector settings
        self.initGlobalSettingsTable()
        # initialize the widget functionality
        self.initDetectorSettingsTable()
        #
        self.sourceSelect.addItem("None")
        self.sourceSelect.addItem("Co60")
        self.sourceSelect.addItem("Cs137")
        self.sourceSelect.addItem("Na22")
        self.sourceSelect.currentIndexChanged.connect(self.selectTheSource)
        #
        self.loadConfig.clicked.connect(self.loadConfiguration)
        # what to do if run is clicked
        self.run_start.clicked.connect(self.runStart)
        # what to do if stop is clicked
        self.run_stop.setDisabled(True)
        self.run_stop.clicked.connect(self.runStop)

    def close_geometry_window(self):
        """
        Overwrite the configuration on closing the geometry window
        """
        self.w.close()
        self.w.readGeometryFromTable()
        self.config = self.w.config

    def open_geometry_window(self):
        """
        Open the geometry definition window
        """
        self.w.show()
        self.w.config = self.config
        self.w.initGeometrySettingsTable()

    def runStart(self):
        """
        start a run
        """

        self.run_start.setDisabled(True)
        self.loadConfig.setDisabled(True)
        self.run_stop.setEnabled(True)


        # 1. write configuration
        self.writeConfiguration()
        # 2. compose the run command
        nevent = int(self.numberOfEvents.text())

        cmd = PYTHON+r' ../ReadoutClient/runDAQ.py -n '+str(nevent)+' -c config.json '
        if self.storeWaveforms.isChecked():
            cmd = cmd + ' -w'

        #self.doit.setProgram(PYTHON)
        #self.doit.setArguments(['test_process.py'])
        #self.doit.start('C:\ProgramData\Anaconda3\python test_process.py')
        self.doit.start(cmd)


    def process_finished(self):
        """
        Execute this on completion of datataking. Release a few buttons etc.
        """
        self.message('process_finished:: end of run')

        self.run_start.setEnabled(True)
        self.loadConfig.setEnabled(True)
        self.run_stop.setDisabled(True)

        #self.doit = None -> with this line the program crashes

    def handle_stdout(self):
        """
        redirect the standard output of teh QProcess
        """
        data = self.doit.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def message(self, s):
        """
        Message parsing to log window
        """
        prompt_base = datetime.now().strftime("%m/%d/%Y %H:%M:%S > ")
        lines = s.split('\n')

        for line in lines:
            line = line.strip()
            if line != '':
                prompt = '[' + str(self.logcounter) + '] ' + prompt_base
                self.logWindow.append(prompt + line)
                self.logcounter = self.logcounter + 1


    def runStop(self):
        """
        stop a run
        """
        self.message('runStop:: kill run')
        self.doit.kill()
        self.run_start.setEnabled(True)
        self.loadConfig.setEnabled(True)
        self.run_stop.setDisabled(True)

    def selectTheSource(self):
        """
        Select the source... written to the header of the config file
        """
        self.message('select ' + self.sourceSelect.currentText())

    def writeConfiguration(self):
        """
        Write a new configuration file, based on the values in the table
        """
        self.readConfigurationFromTable()

        filename = r'..\ReadoutClient\config.json'
        self.message("writeConfiguration:: write new config file:"+filename)

        f = open(filename, 'w')
        json.dump(self.config_new, f, indent=4)
        f.close()

        #print("writeConfiguration:: done")

    def readConfigurationFromTable(self):
        """
        Read the values from the configuration tables to make.....
        """
        self.config_new = self.config
        # source
        self.config_new['source'] = self.sourceSelect.currentText()
        # global settings

        for label in self.g_hlabels:
            icol = self.g_hlabels.index(label)
            value = self.globalSettings.item(0, icol).text()
            if label != 'V_offset':
                self.config_new['registers'][label] = int(value)
            else:
                self.config_new['registers'][label] = float(value)

        # individual detector settings
        for idet in range(N_DETECTOR):
            for label in self.hlabels:
                icol = self.hlabels.index(label)
                value = self.detectorSettings.item(idet, icol).text()
                if label == "THETA":
                    self.config_new['detector_settings'][idet][label] = deg2rad(float(value))
                else:
                    self.config_new['detector_settings'][idet][label] = int(float(value))


    def loadConfiguration(self):
        """
        Load a new configuration file: can be a config file of a previous run that has been fully processed, so Gains
        and time offsets are properly accounted for
        """
        self.config_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Select input waveform', r'C:\Users\aukep\surfdrive\FineStructure\data', '*.json')[0]
        if self.config_file == '':
            self.config_file = self.default_config_file

        self.readConfiguration(config_file=self.config_file)
        self.initGlobalSettingsTable()
        self.initDetectorSettingsTable()

    def readConfiguration(self, **kwargs):
        """
        Read the configuration file
        """
        self.config_file = kwargs.pop('config_file', 'None')
        if self.config_file == 'None':
            self.config_file = self.default_config_file
        self.message('readConfiguration:: read config from: '+self.config_file)

        f = open(self.config_file, 'r')
        self.config = json.load(f)
        f.close()

        # the gain corrections that were found from the calibration process will now be
        # incorporated into new gain values
        self.correct_gains()

    def correct_gains(self):
        """
        Correct the gains from the gain corrections found from a previous calibration
        1. correct gains, so that the correct gains will be used in the new run
        2. set the gain coorrections to one
        """

        self.message('correct_gains:: apply gain corrections to GAIN')

        for idet in range(N_DETECTOR):
            gain = self.config['detector_settings'][idet]['GAIN']
            corr = 1.0
            if 'GCOR' in self.config['detector_settings'][idet].keys():
                corr = self.config['detector_settings'][idet]['GCOR']
            self.message(str(idet)+" "+str(gain)+" "+str(corr))
            self.config['detector_settings'][idet]['GAIN'] = gain*corr
            self.config['detector_settings'][idet]['GCOR'] = 1.0

    def initGlobalSettingsTable(self):
        """
        Global settings for the fADC settings, integration settings, DT5550AFE settings
        """
        gtable = self.globalSettings
        gtable.setRowCount(1)
        self.g_hlabels = ("INTTIME", "PREINIT", "BLLEN", "BLHOLD", "WINDOW", "V_offset", "NMIN", "EMIN")
        gtable.setColumnCount(len(self.g_hlabels))
        gtable.setHorizontalHeaderLabels(self.g_hlabels)

        for label in self.g_hlabels:
            icol = self.g_hlabels.index(label)
            val = self.config['registers'][label]
            gtable.setItem(0, icol, QTableWidgetItem(str(val)))

        self.setTableWidth(self.globalSettings)

    def initDetectorSettingsTable(self):
        """
        Initialize the table with individual detector settings
        """
        table = self.detectorSettings
        table.setRowCount(N_DETECTOR)
        self.hlabels = ("GAIN", "THRS", "INVERT", "BASE", "TOFF", "HV", "THETA")

        table.setColumnCount(len(self.hlabels))

        table.setHorizontalHeaderLabels(self.hlabels)
        self.vlabels = []
        for i in range(N_DETECTOR):
            name = "CH "+str(i)
            self.vlabels.append(name)
        table.setVerticalHeaderLabels(self.vlabels)

        self.fillDetectorSettingsTable()

        self.setTableWidth(self.detectorSettings)

    def setTableWidth(self, tab):
        width = tab.verticalHeader().width()
        width += tab.horizontalHeader().length()
        if tab.verticalScrollBar().isVisible():
            width += tab.verticalScrollBar().width()
        width += tab.frameWidth() * 2
        tab.setFixedWidth(width*1.02)
        tab.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


    def fillDetectorSettingsTable(self):
        """
        Fill the table with settings from the current config file
        """
        table = self.detectorSettings
        for idet in range(N_DETECTOR):
            for label in self.hlabels:
                icol = self.hlabels.index(label)

                if label in self.config['detector_settings'][idet].keys():
                    val = self.config['detector_settings'][idet][label]
                else:
                    val = -1.0

                if label == 'THETA':
                    table.setItem(idet, icol, QTableWidgetItem(str(rad2deg(val))))
                else:
                    table.setItem(idet, icol, QTableWidgetItem(str(val)))




def main():
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)

    form = DAQgui()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
