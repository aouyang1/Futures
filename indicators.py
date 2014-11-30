__author__ = 'aouyang1'

from math import log
import numpy as np

class FisherTransform:

    def __init__(self, backtest, period):
        self.range_bar = backtest.range_bar
        self.period = period
        self.val = []           # 0 index is newest
        self.tmp_series = []    # 0 index is newest

    def on_bar_update(self):

        if self.range_bar.cnt == 1:
            fish_prev = 0
            tmp_value_prev = 0
        else:
            fish_prev = self.val[0]
            tmp_value_prev = self.tmp_series[0]

        period_close = self.range_bar.Close[0:self.period-1]
        min_lo = min(period_close)
        max_hi = max(period_close)

        num1 = max_hi - min_lo

        if num1 < self.range_bar.instr.TICK_SIZE / 10:
            num1 = self.range_bar.instr.TICK_SIZE / 10

        tmp_value = 0.66 * ((period_close[0] - min_lo) / num1 - 0.5) + 0.67 * tmp_value_prev

        if tmp_value > 0.99:
            tmp_value = 0.999

        if tmp_value < -0.99:
            tmp_value = -0.999

        self.tmp_series.insert(0, tmp_value)

        fish_value = 0.5 * log((1 + tmp_value) / (1 - tmp_value)) + 0.5 * fish_prev
        self.val.insert(0, fish_value)


class FTD:

    def __init__(self, backtest, N, period):
        self.range_bar = backtest.range_bar
        self.N = N
        self.period = period
        self.val = []

    def on_bar_update(self):
        # TODO Implement Fisher transform derivative
        pass





