from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, QtCore, Qt

import sys
import glob
import daq_interface
import numpy as np

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
        # initialize the widget functionality
        self.initTable()

    def initTable(self):
        self.detectorSettings.setRowCount(N_DETECTOR)
        self.detectorSettings.setColumnCount(5)
        hlabels = ("Gain", "Threshold", "Invert", "Baseline", "HV")
        self.detectorSettings.setHorizontalHeaderLabels(hlabels)
        vlabels = []
        for i in range(N_DETECTOR):
            name = "CH "+str(i)
            vlabels.append(name)
        self.detectorSettings.setVerticalHeaderLabels(vlabels)


def main():
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)

    form = DAQgui()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
