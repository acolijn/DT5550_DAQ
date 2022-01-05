from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtWidgets, QtCore, Qt

import sys
import json
import daq_interface

N_DETECTOR = 8
N_DIGITAL_OUT = 4

import qdarkstyle

fontsize_axis = 10

# Handle high resolution displays:
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class DAQgui(QMainWindow, daq_interface.Ui_MainWindow):
    """
    GUI for DAQ
    """
    def __init__(self, parent=None):
        super(DAQgui, self).__init__(parent)
        # setup the GUI
        self.setupUi(self)

        self.default_config_file = '../ReadoutClient/config.json'
        self.config_file = 'None'
        self.config = ''
        self.config_new = ''
        self.hlabels = []
        self.g_hlabels = []
        self.vlabels = []

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

    def selectTheSource(self):
        """
        Select the source... written to the header of the config file
        """
        print('select',self.sourceSelect.currentText())

    def writeConfiguration(self):
        """
        Write a new configuration file, based on the values in the table
        """

        readConfigurationFromTable()

        f = open('test.json')
        json.dump(self.config_new, f, indent=4)
        f.close()

    def readConfigurationFromTable(self):
        """
        Read the values from the configuration tables to make.....
        """
        self.config_new = self.config

        # global settings
        for label in self.g_hlabels:
            icol = self.g_hlabels(label).index()
            value = self.detectorSettings.item(0, icol)
            self.config_new['registers'][label] = value

        # individual detector settings
        for idet in range(N_DETECTOR):
            for label in self.hlabels:
                icol = self.hlabels(label).index()
                value = self.detectorSettings.item(idet,icol)
                self.config_new['detector_settings'][idet][label] = value


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
        print('readConfiguration:: read config from: ', self.config_file)

        f = open(self.config_file, 'r')
        self.config = json.load(f)
        f.close()

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
        self.hlabels = ("GAIN", "THRS", "INVERT", "BASE", "TOFF", "HV")

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

    def fillDetectorSettingsTable(self):
        """
        Fill the table with settings from the current config file
        """
        table = self.detectorSettings
        for idet in range(N_DETECTOR):
            for label in self.hlabels:
                icol = self.hlabels.index(label)
                val = self.config['detector_settings'][idet][label]
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
