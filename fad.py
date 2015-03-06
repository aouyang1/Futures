from __future__ import with_statement
import numpy as np
import sys


# plotting import for candlestick
import matplotlib.finance as mplfin
import matplotlib.pyplot as plt

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

		self.text = open('util/setup_backtest.py', 'r').read()
		self.textEdit_setup_backtest.setText(self.text)

		self.tabWidget.setTabEnabled(1, False)

		QtCore.QObject.connect(self.pushButton_run_backtest,
							   QtCore.SIGNAL("clicked()"), self.run_backtest)
		QtCore.QObject.connect(self.horizontalScrollBar_range_bar,
							   QtCore.SIGNAL("valueChanged(int)"),
							   self.scroll_bars)
		QtCore.QObject.connect(self.horizontalSlider_bar_zoom,
							   QtCore.SIGNAL("valueChanged(int)"),
							   self.zoom_bars)
		QtCore.QObject.connect(self.pushButton_save_setup,
							   QtCore.SIGNAL("clicked()"), self.save_setup)
		QtCore.QObject.connect(self.textEdit_setup_backtest,
							   QtCore.SIGNAL("textChanged()"),
							   self.check_file_changed)
		QtCore.QObject.connect(self.pushButton_revert_setup,
							   QtCore.SIGNAL("clicked()"), self.revert_setup)

		self.bt = Backtest(self)
		self.min_bar_lookback = 50
		self.bar_len = 0
		self.zoom = 0
		self.bars_in_view = 50

	def revert_setup(self):
		curr_text = str(self.textEdit_setup_backtest.toPlainText())
		if curr_text != self.text:
			self.textEdit_setup_backtest.setText(self.text)
			self.label_setup_backtest.setText("setup_backtest.py")

	def save_setup(self):
		curr_text = str(self.textEdit_setup_backtest.toPlainText())
		if curr_text != self.text:
			open('util/setup_backtest.py', 'w').write(curr_text)
			self.label_setup_backtest.setText("setup_backtest.py")
			self.text = curr_text

	def check_file_changed(self):
		curr_text = str(self.textEdit_setup_backtest.toPlainText())
		if curr_text == self.text:
			self.label_setup_backtest.setText("setup_backtest.py")
		else:
			self.label_setup_backtest.setText("setup_backtest.py*")

	def zoom_bars(self):
		val = self.horizontalSlider_bar_zoom.value()

		self.zoom = val / 10.0

		bar_start = self.horizontalScrollBar_range_bar.maximum() - self.horizontalScrollBar_range_bar.value()

		self.bars_in_view = int(round(self.min_bar_lookback * 2 ** self.zoom))

		self.horizontalScrollBar_range_bar.setMaximum(
			self.bar_len - self.bars_in_view)
		self.horizontalScrollBar_range_bar.setPageStep(self.bars_in_view)
		self.horizontalScrollBar_range_bar.setValue(
			self.horizontalScrollBar_range_bar.maximum() - bar_start)

		self.scroll_bars()

	def scroll_bars(self):
		bar_start = self.horizontalScrollBar_range_bar.maximum() - self.horizontalScrollBar_range_bar.value()
		self.plot_bars(bar_start=bar_start)

	def plot_bars(self, bar_start=0):

		self.mpl.canvas.ax.clear()

		bar_end = min(bar_start + self.bars_in_view, self.bar_len)

		opens = self.bt.range_bar.Open[
				bar_start:bar_end]
		closes = self.bt.range_bar.Close[
				 bar_start:bar_end]
		highs = self.bt.range_bar.High[
				bar_start:bar_end]
		lows = self.bt.range_bar.Low[
			   bar_start:bar_end]
		dates = self.bt.range_bar.CloseTime[
				bar_start:bar_end]

		# TODO: select trades that are present in the current plot window
		strat_name = self.bt.strategies.keys()
		strat_name.sort()
		for s in strat_name:
			strat = self.bt.strategies[s]
			entry_bar = strat.trades.entry_bar
			exit_bar = strat.trades.exit_bar
			entry_price = strat.trades.entry_price
			exit_price = strat.trades.exit_price
			market_pos = strat.trades.market_pos

			# use binary search for first trade and last trade index
			trade_start = self.nearest_idx_gte(entry_bar,
											   self.bt.range_bar.cnt - bar_end - 1)
			trade_end = self.nearest_idx_gte(exit_bar,
											 self.bt.range_bar.cnt - bar_start - 1)

			if trade_start and not trade_end:
				trade_end = trade_start + 1

			for idx in range(trade_start, trade_end):
				bar_x = [entry_bar[idx] - (self.bt.range_bar.cnt - bar_start) + self.bars_in_view,
						 exit_bar[idx] - (self.bt.range_bar.cnt - bar_start) + self.bars_in_view]
				bar_y = [entry_price[idx], exit_price[idx]]
				if market_pos[idx] == "LONG":
					self.mpl.canvas.ax.plot(bar_x, bar_y, color='g',
											linestyle='--',
											linewidth=2.0)
				else:
					self.mpl.canvas.ax.plot(bar_x, bar_y, color='r',
											linestyle='--',
											linewidth=2.0)


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
		self.mpl.canvas.ax.get_yaxis().get_major_formatter().set_useOffset(
			False)

		increment = 10
		xidx = np.arange(0, self.bars_in_view, increment) + round(
			increment / 2) + bar_start % increment
		self.mpl.canvas.ax.set_xticks(xidx)

		time_list = [dates[int(idx)].time() for idx in xidx if
					 idx < self.bars_in_view]
		date_list = [dates[int(idx)].date() for idx in xidx if
					 idx < self.bars_in_view]

		self.label_view_date.setText(str(dates[-1].date()) + " " + str(dates[-1].time()) + "     ")
		self.mpl.canvas.ax.set_xticklabels(time_list)
		self.mpl.canvas.ax.get_xaxis().grid(True)
		self.mpl.canvas.ax.set_xlim(xmin=-1, xmax=self.bars_in_view)
		self.mpl.canvas.draw()

	def run_backtest(self):

		m = StateMachine()
		t = Transitions()  # next state functions for state machine

		m.add_state("initialize", t.initialize_transitions)
		m.add_state("load_daily_data", t.load_daily_data_transitions)
		m.add_state("check_orders", t.check_orders_transitions)
		m.add_state("update_range_bar", t.update_range_bar_transitions)
		m.add_state("compute_indicators", t.compute_indicators_transitions)
		m.add_state("check_strategy", t.check_strategy_transitions)
		m.add_state("check_range_bar_finished",
					t.check_range_bar_finished_transitions)
		m.add_state("show_results", t.write_results_transitions)
		m.add_state("finished", None, end_state=1)

		m.set_start("initialize")

		self.bt.instr_name = str(self.comboBox_instrument.currentText())
		self.bt.RANGE = int(self.spinBox_range.value())

		self.bt.init_day = str(self.dateEdit_start_date.date().toString(
			"yyyy-MM-dd")) + " 17:00:00"
		self.bt.final_day = str(
			self.dateEdit_end_date.date().toString("yyyy-MM-dd")) + " 16:59:59"

		self.bt.log_intrabar_data = self.checkBox_log_intrabar_data.isChecked()  # setting true can significantly slowdown backtesting
		self.bt.write_trade_data = self.checkBox_write_trade_data.isChecked()
		self.bt.trade_data_root = '/home/aouyang1/Dropbox/Futures Trading/FT_QUICKY_v3/BASE (copy)'

		self.bt.write_bar_data = self.checkBox_write_bar_data.isChecked()
		self.bt.bar_data_root = '/home/aouyang1/Dropbox/Futures Trading/Backtester/FT_QUICKY_GC_BASE'

		cProfile.runctx('m.run(self.bt)', globals(), locals(),
						'backtest_profile')
		self.bar_len = self.bt.range_bar.cnt
		self.tabWidget.setTabEnabled(1, True)

		print " "

		p = pstats.Stats('backtest_profile')
		p.strip_dirs().sort_stats('cumulative').print_stats('transitions')

		self.horizontalScrollBar_range_bar.setMaximum(
			self.bar_len - self.bars_in_view)
		self.horizontalScrollBar_range_bar.setPageStep(self.bars_in_view)
		self.horizontalScrollBar_range_bar.setValue(
			self.bar_len - self.bars_in_view)

		self.plot_bars()


	def nearest_idx_gte(self, a, val):
		"""
		:param a: list of sorted floats
		:param val: value to find in a
		:return: index in 'a' where the value is greater than or equal
		to val
		"""
		if not a:
			return

		start = 0
		end = len(a)-1

		while end - start > 1:
			midpoint = (end-start)/2 + start
			if a[midpoint] == val:
				return midpoint
			elif a[midpoint] < val:
				start = midpoint
			else:
				end = midpoint

		if a[end] < val:
			return
		else:
			return end


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	dmw = DesignerMainWindow()
	dmw.show()
	sys.exit(app.exec_())