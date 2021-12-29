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
        MainWindow.resize(1703, 1632)
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.plotIt = QtWidgets.QPushButton(self.centralwidget)
        self.plotIt.setGeometry(QtCore.QRect(30, 1435, 231, 81))
        self.plotIt.setObjectName("plotIt")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(280, 40, 20, 1501))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(320, 70, 1351, 1461))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.plotWidget = MplWidget(self.tab)
        self.plotWidget.setEnabled(True)
        self.plotWidget.setGeometry(QtCore.QRect(0, 0, 1341, 1421))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy)
        self.plotWidget.setObjectName("plotWidget")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.plotBaselineWidget = MplWidget_Baseline(self.tab_2)
        self.plotBaselineWidget.setEnabled(True)
        self.plotBaselineWidget.setGeometry(QtCore.QRect(0, 0, 1341, 1421))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotBaselineWidget.sizePolicy().hasHeightForWidth())
        self.plotBaselineWidget.setSizePolicy(sizePolicy)
        self.plotBaselineWidget.setObjectName("plotBaselineWidget")
        self.tabWidget.addTab(self.tab_2, "")
        self.baselineSubtract = QtWidgets.QCheckBox(self.centralwidget)
        self.baselineSubtract.setGeometry(QtCore.QRect(20, 730, 261, 29))
        self.baselineSubtract.setChecked(True)
        self.baselineSubtract.setObjectName("baselineSubtract")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 80, 246, 600))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.selectALL = QtWidgets.QCheckBox(self.layoutWidget)
        self.selectALL.setEnabled(True)
        self.selectALL.setChecked(True)
        self.selectALL.setObjectName("selectALL")
        self.verticalLayout.addWidget(self.selectALL)
        self.channel_0 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_0.setObjectName("channel_0")
        self.verticalLayout.addWidget(self.channel_0)
        self.channel_1 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_1.setObjectName("channel_1")
        self.verticalLayout.addWidget(self.channel_1)
        self.channel_2 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_2.setObjectName("channel_2")
        self.verticalLayout.addWidget(self.channel_2)
        self.channel_3 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_3.setObjectName("channel_3")
        self.verticalLayout.addWidget(self.channel_3)
        self.channel_4 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_4.setObjectName("channel_4")
        self.verticalLayout.addWidget(self.channel_4)
        self.channel_5 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_5.setObjectName("channel_5")
        self.verticalLayout.addWidget(self.channel_5)
        self.channel_6 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_6.setObjectName("channel_6")
        self.verticalLayout.addWidget(self.channel_6)
        self.channel_7 = QtWidgets.QCheckBox(self.layoutWidget)
        self.channel_7.setObjectName("channel_7")
        self.verticalLayout.addWidget(self.channel_7)
        self.trigger_sel = QtWidgets.QCheckBox(self.layoutWidget)
        self.trigger_sel.setChecked(True)
        self.trigger_sel.setObjectName("trigger_sel")
        self.verticalLayout.addWidget(self.trigger_sel)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1703, 43))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpenDir = QtWidgets.QAction(MainWindow)
        self.actionOpenDir.setObjectName("actionOpenDir")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionOpenFile = QtWidgets.QAction(MainWindow)
        self.actionOpenFile.setObjectName("actionOpenFile")
        self.menuFile.addAction(self.actionOpenFile)
        self.menuFile.addAction(self.actionOpenDir)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.plotIt, self.tabWidget)
        MainWindow.setTabOrder(self.tabWidget, self.selectALL)
        MainWindow.setTabOrder(self.selectALL, self.channel_0)
        MainWindow.setTabOrder(self.channel_0, self.channel_1)
        MainWindow.setTabOrder(self.channel_1, self.channel_2)
        MainWindow.setTabOrder(self.channel_2, self.channel_3)
        MainWindow.setTabOrder(self.channel_3, self.channel_4)
        MainWindow.setTabOrder(self.channel_4, self.channel_5)
        MainWindow.setTabOrder(self.channel_5, self.channel_6)
        MainWindow.setTabOrder(self.channel_6, self.channel_7)
        MainWindow.setTabOrder(self.channel_7, self.trigger_sel)
        MainWindow.setTabOrder(self.trigger_sel, self.baselineSubtract)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Waveform Display"))
        self.plotIt.setText(_translate("MainWindow", "Next Event"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Waveform"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Baseline"))
        self.baselineSubtract.setText(_translate("MainWindow", "subtract baseline"))
        self.selectALL.setText(_translate("MainWindow", "ALL"))
        self.channel_0.setText(_translate("MainWindow", "channel 0"))
        self.channel_1.setText(_translate("MainWindow", "channel 1"))
        self.channel_2.setText(_translate("MainWindow", "channel 2"))
        self.channel_3.setText(_translate("MainWindow", "channel 3"))
        self.channel_4.setText(_translate("MainWindow", "channel 4"))
        self.channel_5.setText(_translate("MainWindow", "channel 5"))
        self.channel_6.setText(_translate("MainWindow", "channel 6"))
        self.channel_7.setText(_translate("MainWindow", "channel 7"))
        self.trigger_sel.setText(_translate("MainWindow", "show trigger"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpenDir.setText(_translate("MainWindow", "Open directory...."))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionOpenFile.setText(_translate("MainWindow", "Open file...."))

from mplwidget import MplWidget
from mplwidget_baseline import MplWidget_Baseline
