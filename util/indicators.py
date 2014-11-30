__author__ = 'aouyang1'

from math import log
import numpy as np

class FisherTransform:

    def __init__(self, backtest, dataseries, period):
        self.bt = backtest
        self.dataseries = dataseries
        self.period = period
        self.val = []           # 0 index is newest
        self.tmp_series = []    # 0 index is newest

    def on_bar_update(self):

        if self.bt.range_bar.cnt == 1:
            fish_prev = 0
            tmp_value_prev = 0
        else:
            fish_prev = self.val[0]
            tmp_value_prev = self.tmp_series[0]

        data = self.dataseries[0:self.period]
        min_lo = min(data)
        max_hi = max(data)

        num1 = max_hi - min_lo

        if num1 < self.bt.range_bar.instr.TICK_SIZE / 10:
            num1 = self.bt.range_bar.instr.TICK_SIZE / 10

        tmp_value = 0.66 * ((data[0] - min_lo) / num1 - 0.5) + 0.67 * tmp_value_prev

        if tmp_value > 0.99:
            tmp_value = 0.999

        if tmp_value < -0.99:
            tmp_value = -0.999

        self.tmp_series.insert(0, tmp_value)

        fish_value = 0.5 * log((1 + tmp_value) / (1 - tmp_value)) + 0.5 * fish_prev
        self.val.insert(0, fish_value)


class LinRegSlope:

    def __init__(self, backtest, dataseries, period):
        self.bt = backtest
        self.dataseries = dataseries
        self.period = period
        self.val = []

    def on_bar_update(self):

        if self.bt.range_bar.cnt >= self.period:
            data = self.dataseries[0:self.period]
            x = np.arange(self.period, 0, -1)
            coeff = np.polyfit(x, data, 1)
            self.val.insert(0, coeff[0])

        else:
            self.val.insert(0, 0)







