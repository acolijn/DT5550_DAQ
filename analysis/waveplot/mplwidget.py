from PyQt5 import QtWidgets

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')


class MplCanvas(Canvas):
    """
    Matplotlib class to enable plotting
    """
    def __init__(self):
        self.fig = Figure()
        self.fig.subplots_adjust(
            top=0.989,
            bottom=0.048,
            left=0.068,
            right=0.936,
            hspace=0.08,
            wspace=0.05
        )
        self.ax = self.fig.subplots(5, 1, sharex='all', gridspec_kw={'height_ratios': [5, 1.2, 1.2, 1.2, 1.2]})

        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


class MplWidget(QtWidgets.QWidget):
    """
    Matplotlib widget -> upgrades a standard QWidget to MplWidget -> allows plotting
    """
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.vbl.addWidget(self.toolbar)
