# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'daq_interface.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1181, 747)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.detectorSettings = QtWidgets.QTableWidget(self.centralwidget)
        self.detectorSettings.setGeometry(QtCore.QRect(300, 190, 671, 281))
        self.detectorSettings.setObjectName("detectorSettings")
        self.detectorSettings.setColumnCount(0)
        self.detectorSettings.setRowCount(0)
        self.globalSettings = QtWidgets.QTableWidget(self.centralwidget)
        self.globalSettings.setGeometry(QtCore.QRect(300, 110, 851, 61))
        self.globalSettings.setObjectName("globalSettings")
        self.globalSettings.setColumnCount(0)
        self.globalSettings.setRowCount(0)
        self.run_stop = QtWidgets.QPushButton(self.centralwidget)
        self.run_stop.setGeometry(QtCore.QRect(20, 590, 211, 46))
        self.run_stop.setObjectName("run_stop")
        self.run_start = QtWidgets.QPushButton(self.centralwidget)
        self.run_start.setGeometry(QtCore.QRect(20, 530, 211, 46))
        self.run_start.setObjectName("run_start")
        self.loadConfig = QtWidgets.QPushButton(self.centralwidget)
        self.loadConfig.setGeometry(QtCore.QRect(20, 50, 211, 46))
        self.loadConfig.setObjectName("loadConfig")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(250, 30, 20, 631))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.logWindow = QtWidgets.QTextBrowser(self.centralwidget)
        self.logWindow.setGeometry(QtCore.QRect(300, 520, 851, 141))
        self.logWindow.setObjectName("logWindow")
        self.sourceSelect = QtWidgets.QComboBox(self.centralwidget)
        self.sourceSelect.setGeometry(QtCore.QRect(680, 50, 114, 31))
        self.sourceSelect.setObjectName("sourceSelect")
        self.numberOfEvents = QtWidgets.QLineEdit(self.centralwidget)
        self.numberOfEvents.setGeometry(QtCore.QRect(478, 50, 101, 31))
        self.numberOfEvents.setObjectName("numberOfEvents")
        self.storeWaveforms = QtWidgets.QCheckBox(self.centralwidget)
        self.storeWaveforms.setGeometry(QtCore.QRect(830, 50, 143, 29))
        self.storeWaveforms.setChecked(True)
        self.storeWaveforms.setObjectName("storeWaveforms")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(300, 50, 168, 25))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(600, 50, 64, 25))
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1181, 38))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DT5550 DAQ"))
        self.run_stop.setText(_translate("MainWindow", "Stop"))
        self.run_start.setText(_translate("MainWindow", "Run"))
        self.loadConfig.setText(_translate("MainWindow", "Load Configuration"))
        self.numberOfEvents.setText(_translate("MainWindow", "100000"))
        self.storeWaveforms.setText(_translate("MainWindow", "waveforms"))
        self.label.setText(_translate("MainWindow", "Number of Events"))
        self.label_2.setText(_translate("MainWindow", "Source"))

