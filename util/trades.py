__author__ = 'aouyang1'

from pandas import DataFrame
import numpy as np
from scipy import stats


class Trades:

    def __init__(self):
        self.trade_log = None
        self.market_pos = []
        self.entry_price = []
        self.exit_price = []
        self.entry_time = []
        self.exit_time = []
        self.exit_name = []
        self.profit = []
        self.curr = CurrentTrade()

    def add_trade(self):
        self.market_pos.append(self.curr.market_pos)
        self.entry_price.append(self.curr.entry_price)
        self.exit_price.append(self.curr.exit_price)
        self.entry_time.append(self.curr.entry_time)
        self.exit_time.append(self.curr.exit_time)
        self.exit_name.append(self.curr.exit_name)
        self.profit.append(self.curr.profit)

    def convert_to_dataframe(self):
        self.trade_log = DataFrame({'market_pos': self.market_pos,
                                    'entry_price': self.entry_price,
                                    'exit_price': self.exit_price,
                                    'entry_time': self.entry_time,
                                    'exit_time': self.exit_time,
                                    'exit_name': self.exit_name,
                                    'profit': self.profit})

    def calc_win_perc(self):
        profit = self.trade_log['profit']
        num_trades = len(profit)
        wins = np.sum(profit > 0.0)
        if num_trades == 0:
            return 0
        else:
            return wins/float(num_trades)

    def calc_pval(self):
        profit = self.trade_log['profit']
        num_trades = len(profit)
        wins = np.sum(profit > 0.0)
        return stats.binom_test(wins, n=num_trades, p=0.5)

class CurrentTrade:

    def __init__(self):
        self.market_pos = None
        self.entry_price = None
        self.exit_price = None
        self.entry_time = None
        self.exit_time = None
        self.exit_name = None
        self.profit = None

