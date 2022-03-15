# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\define_geometry.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DefineGeometry(object):
    def setupUi(self, DefineGeometry):
        DefineGeometry.setObjectName("DefineGeometry")
        DefineGeometry.resize(619, 313)
        self.geometrySettings = QtWidgets.QTableWidget(DefineGeometry)
        self.geometrySettings.setGeometry(QtCore.QRect(250, 30, 361, 271))
        self.geometrySettings.setObjectName("geometrySettings")
        self.geometrySettings.setColumnCount(0)
        self.geometrySettings.setRowCount(0)
        self.close_window = QtWidgets.QPushButton(DefineGeometry)
        self.close_window.setGeometry(QtCore.QRect(20, 30, 211, 46))
        self.close_window.setObjectName("close_window")

        self.retranslateUi(DefineGeometry)
        QtCore.QMetaObject.connectSlotsByName(DefineGeometry)

    def retranslateUi(self, DefineGeometry):
        _translate = QtCore.QCoreApplication.translate
        DefineGeometry.setWindowTitle(_translate("DefineGeometry", "Form"))
        self.close_window.setText(_translate("DefineGeometry", "Write && Close"))

