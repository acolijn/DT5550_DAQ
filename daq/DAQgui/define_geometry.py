# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\define_geometry.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(706, 330)
        self.geometrySettings = QtWidgets.QTableWidget(Form)
        self.geometrySettings.setGeometry(QtCore.QRect(250, 30, 441, 291))
        self.geometrySettings.setObjectName("geometrySettings")
        self.geometrySettings.setColumnCount(0)
        self.geometrySettings.setRowCount(0)
        self.close_window = QtWidgets.QPushButton(Form)
        self.close_window.setGeometry(QtCore.QRect(20, 30, 211, 46))
        self.close_window.setObjectName("close_window")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.close_window.setText(_translate("Form", "Write && Close"))

