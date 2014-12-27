from __future__ import with_statement
import numpy as np
import sys


# plotting import for candlestick
import matplotlib.finance as mplfin

# backtesting imports
from util.statemachine import StateMachine
from util.transitions import Transitions
from util.backtest import Backtest
from util.setup_backtest import *
import cProfile
import pstats

from PyQt4 import QtCore
from PyQt4 import QtGui

from futures_algo_dev import Ui_MainWindow

class DesignerMainWindow(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(DesignerMainWindow, self).__init__(parent)
		self.setupUi(self)

		QtCore.QObject.connect(self.pushButton_run_backtest, QtCore.SIGNAL("clicked()"), self.run_backtest)
		QtCore.QObject.connect(self.horizontalScrollBar_range_bar, QtCore.SIGNAL("valueChanged(int)"), self.scroll_bars)
		QtCore.QObject.connect(self.horizontalSlider_bar_zoom, QtCore.SIGNAL("valueChanged(int)"), self.zoom_bars)

		self.tabWidget.setTabEnabled(1, False)

		self.bt = Backtest(self)
		self.min_bar_lookback = 50
		self.bar_len = 0
		self.zoom = 0
		self.bars_in_view = 50

	def zoom_bars(self):
		val = self.horizontalSlider_bar_zoom.value()

		self.zoom = val/10.0

		bar_start = self.horizontalScrollBar_range_bar.maximum() - self.horizontalScrollBar_range_bar.value()

		self.bars_in_view = int(round(self.min_bar_lookback*2**self.zoom))		

		self.horizontalScrollBar_range_bar.setMaximum(self.bar_len - self.bars_in_view)		
		self.horizontalScrollBar_range_bar.setPageStep(self.bars_in_view)	
		self.horizontalScrollBar_range_bar.setValue(self.horizontalScrollBar_range_bar.maximum() - bar_start)

		self.scroll_bars()

	def scroll_bars(self):		
		bar_start = self.horizontalScrollBar_range_bar.maximum() - self.horizontalScrollBar_range_bar.value()
		self.plot_bars(bar_start=bar_start)

	def plot_bars(self, bar_start=0):				

		self.mpl.canvas.ax.clear()

		opens = self.bt.range_bar.Open[bar_start:min(bar_start + self.bars_in_view, self.bar_len)]
		closes = self.bt.range_bar.Close[bar_start:min(bar_start + self.bars_in_view, self.bar_len)]
		highs = self.bt.range_bar.High[bar_start:min(bar_start + self.bars_in_view, self.bar_len)]
		lows = self.bt.range_bar.Low[bar_start:min(bar_start + self.bars_in_view, self.bar_len)]
		dates = self.bt.range_bar.CloseTime[bar_start:min(bar_start + self.bars_in_view, self.bar_len)]
		
		opens.reverse()
		closes.reverse()
		highs.reverse()
		lows.reverse()
		dates.reverse()
		
		mplfin.candlestick2(self.mpl.canvas.ax, opens=opens,
												closes=closes,
												highs=highs,
												lows=lows,
												width=0.75,
												colorup=u'g')
		
		self.mpl.canvas.ax.get_yaxis().grid(True)
		self.mpl.canvas.ax.get_yaxis().get_major_formatter().set_useOffset(False)
		
		increment = 10
		xidx = np.arange(0, self.bars_in_view, increment) + round(increment/2) + bar_start%increment		
		self.mpl.canvas.ax.set_xticks(xidx)

		time_list = [dates[int(idx)].time() for idx in xidx if idx < self.bars_in_view]
		date_list = [dates[int(idx)].date() for idx in xidx if idx < self.bars_in_view]
		
		self.label_view_date.setText(str(dates[-1].date()) + "     ")
		self.mpl.canvas.ax.set_xticklabels(time_list)
		self.mpl.canvas.ax.get_xaxis().grid(True)				
		self.mpl.canvas.ax.set_xlim(xmin=-1, xmax=self.bars_in_view)
		self.mpl.canvas.draw()

	def run_backtest(self):
		
		m = StateMachine()
		t = Transitions()       # next state functions for state machine

		m.add_state("initialize", t.initialize_transitions)
		m.add_state("load_daily_data", t.load_daily_data_transitions)
		m.add_state("check_orders", t.check_orders_transitions)
		m.add_state("update_range_bar", t.update_range_bar_transitions)
		m.add_state("compute_indicators", t.compute_indicators_transitions)
		m.add_state("check_strategy", t.check_strategy_transitions)
		m.add_state("check_range_bar_finished", t.check_range_bar_finished_transitions)
		m.add_state("show_results", t.write_results_transitions)
		m.add_state("finished", None, end_state=1)

		m.set_start("initialize")

		
		self.bt.instr_name = str(self.comboBox_instrument.currentText())
		self.bt.RANGE = int(self.spinBox_range.value())

		self.bt.init_day = str(self.dateEdit_start_date.date().toString("yyyy-MM-dd")) + " 17:00:00"
		self.bt.final_day = str(self.dateEdit_end_date.date().toString("yyyy-MM-dd")) + " 16:59:59"

		self.bt.optimization = self.checkBox_optimize.isChecked()          # if indicators are the same across all strategies, set True
		self.bt.log_intrabar_data = self.checkBox_log_intrabar_data.isChecked()    # setting true can significantly slowdown backtesting

		self.bt.write_trade_data = self.checkBox_write_trade_data.isChecked()
		self.bt.trade_data_root = '/home/aouyang1/Dropbox/Futures Trading/FT_QUICKY_v3/BASE (copy)'

		self.bt.write_bar_data = self.checkBox_write_bar_data.isChecked()
		self.bt.bar_data_root = '/home/aouyang1/Dropbox/Futures Trading/Backtester/FT_QUICKY_GC_BASE'

		cProfile.runctx('m.run(self.bt)', globals(), locals(), 'backtest_profile')
		self.bar_len = self.bt.range_bar.cnt
		self.tabWidget.setTabEnabled(1, True)

		print " "

		p = pstats.Stats('backtest_profile')
		p.strip_dirs().sort_stats('cumulative').print_stats('transitions')
						
		self.horizontalScrollBar_range_bar.setMaximum(self.bar_len - self.bars_in_view)		
		self.horizontalScrollBar_range_bar.setPageStep(self.bars_in_view)
		self.horizontalScrollBar_range_bar.setValue(self.bar_len - self.bars_in_view)

		self.plot_bars()


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	dmw = DesignerMainWindow()
	dmw.show()
	sys.exit(app.exec_())