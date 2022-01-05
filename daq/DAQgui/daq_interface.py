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
        MainWindow.resize(1128, 771)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.detectorSettings = QtWidgets.QTableWidget(self.centralwidget)
        self.detectorSettings.setGeometry(QtCore.QRect(210, 190, 671, 281))
        self.detectorSettings.setObjectName("detectorSettings")
        self.detectorSettings.setColumnCount(0)
        self.detectorSettings.setRowCount(0)
        self.globalSettings = QtWidgets.QTableWidget(self.centralwidget)
        self.globalSettings.setGeometry(QtCore.QRect(210, 110, 851, 61))
        self.globalSettings.setObjectName("globalSettings")
        self.globalSettings.setColumnCount(0)
        self.globalSettings.setRowCount(0)
        self.run_stop = QtWidgets.QPushButton(self.centralwidget)
        self.run_stop.setGeometry(QtCore.QRect(20, 90, 150, 46))
        self.run_stop.setObjectName("run_stop")
        self.run_start = QtWidgets.QPushButton(self.centralwidget)
        self.run_start.setGeometry(QtCore.QRect(20, 30, 150, 46))
        self.run_start.setObjectName("run_start")
        self.loadConfig = QtWidgets.QPushButton(self.centralwidget)
        self.loadConfig.setGeometry(QtCore.QRect(210, 480, 211, 46))
        self.loadConfig.setObjectName("loadConfig")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(180, 30, 20, 491))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(20, 530, 1071, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(30, 550, 1071, 141))
        self.textBrowser.setObjectName("textBrowser")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(190, 90, 901, 21))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.sourceSelect = QtWidgets.QComboBox(self.centralwidget)
        self.sourceSelect.setGeometry(QtCore.QRect(400, 50, 114, 31))
        self.sourceSelect.setObjectName("sourceSelect")
        self.numberOfEvents = QtWidgets.QLineEdit(self.centralwidget)
        self.numberOfEvents.setGeometry(QtCore.QRect(210, 50, 113, 31))
        self.numberOfEvents.setObjectName("numberOfEvents")
        self.storeWaveforms = QtWidgets.QCheckBox(self.centralwidget)
        self.storeWaveforms.setGeometry(QtCore.QRect(540, 50, 151, 29))
        self.storeWaveforms.setChecked(True)
        self.storeWaveforms.setObjectName("storeWaveforms")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1128, 38))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.run_stop.setText(_translate("MainWindow", "Stop"))
        self.run_start.setText(_translate("MainWindow", "Run"))
        self.loadConfig.setText(_translate("MainWindow", "Load Configuration"))
        self.storeWaveforms.setText(_translate("MainWindow", "waveforms"))

