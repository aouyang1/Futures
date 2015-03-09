
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MplCanvas(FigureCanvas):
	def __init__(self):
		self.fig = plt.figure(facecolor='w')
		self.ax = plt.subplot2grid((5,1), (0,0), rowspan=4)
		self.ax2 = plt.subplot2grid((5,1), (4,0), sharex=self.ax)
		plt.subplots_adjust(left=0.07, bottom=0.04, right=0.98, top=0.97,
							wspace=0.00, hspace=0.00)
		#self.ax2 = self.fig.add_axes([0.07,0.04,0.92,1])
		FigureCanvas.__init__(self, self.fig)
		FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)


class MplWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.canvas = MplCanvas()		
		self.vbl = QtGui.QVBoxLayout()
		self.vbl.addWidget(self.canvas)
		self.setLayout(self.vbl)