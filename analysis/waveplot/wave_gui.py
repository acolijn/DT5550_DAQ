# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\wave_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1242, 1328)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.plotWidget = MplWidget(self.centralwidget)
        self.plotWidget.setEnabled(True)
        self.plotWidget.setGeometry(QtCore.QRect(280, 90, 921, 1171))
        self.plotWidget.setObjectName("plotWidget")
        self.plotIt = QtWidgets.QPushButton(self.centralwidget)
        self.plotIt.setGeometry(QtCore.QRect(60, 40, 150, 46))
        self.plotIt.setObjectName("plotIt")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(250, 40, 20, 1221))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(60, 170, 133, 481))
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.selectALL = QtWidgets.QCheckBox(self.splitter)
        self.selectALL.setEnabled(True)
        self.selectALL.setChecked(True)
        self.selectALL.setObjectName("selectALL")
        self.channel_0 = QtWidgets.QCheckBox(self.splitter)
        self.channel_0.setObjectName("channel_0")
        self.channel_1 = QtWidgets.QCheckBox(self.splitter)
        self.channel_1.setObjectName("channel_1")
        self.channel_2 = QtWidgets.QCheckBox(self.splitter)
        self.channel_2.setObjectName("channel_2")
        self.channel_3 = QtWidgets.QCheckBox(self.splitter_2)
        self.channel_3.setObjectName("channel_3")
        self.channel_4 = QtWidgets.QCheckBox(self.splitter_2)
        self.channel_4.setObjectName("channel_4")
        self.channel_5 = QtWidgets.QCheckBox(self.splitter_2)
        self.channel_5.setObjectName("channel_5")
        self.channel_6 = QtWidgets.QCheckBox(self.splitter_2)
        self.channel_6.setObjectName("channel_6")
        self.channel_7 = QtWidgets.QCheckBox(self.splitter_2)
        self.channel_7.setObjectName("channel_7")
        self.selectDataDir = QtWidgets.QComboBox(self.centralwidget)
        self.selectDataDir.setGeometry(QtCore.QRect(280, 40, 261, 31))
        self.selectDataDir.setObjectName("selectDataDir")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1242, 38))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Waveform Display"))
        self.plotIt.setText(_translate("MainWindow", "Next"))
        self.selectALL.setText(_translate("MainWindow", "ALL"))
        self.channel_0.setText(_translate("MainWindow", "channel 0"))
        self.channel_1.setText(_translate("MainWindow", "channel 1"))
        self.channel_2.setText(_translate("MainWindow", "channel 2"))
        self.channel_3.setText(_translate("MainWindow", "channel 3"))
        self.channel_4.setText(_translate("MainWindow", "channel 4"))
        self.channel_5.setText(_translate("MainWindow", "channel 5"))
        self.channel_6.setText(_translate("MainWindow", "channel 6"))
        self.channel_7.setText(_translate("MainWindow", "channel 7"))

from mplwidget import MplWidget
