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

    def get_num_trades(self):
        return self.trade_log.shape[0]

    def calc_win_perc(self):
        profit = self.trade_log['profit']
        num_trades = self.get_num_trades()
        total_wins = np.sum(profit > 0.0)
        if num_trades == 0:
            return 0, 0.0
        else:
            return total_wins/float(num_trades), stats.binom_test(total_wins, n=num_trades, p=0.5)

    def calc_var(self, perc, period):
        # TODO: calculate daily value at risk given percentage
        # period can be 'daily', 'weekly', 'monthly'
        pass

    def calc_distribution(self, period):
        # TODO: calculate distribution
        # period can be 'hourly', 'daily', 'weekly', 'monthly'
        pass

    def calc_cumulative_profit(self):
        # TODO: calculate cumulative profit and insert into trade_log
        pass





class CurrentTrade:

    def __init__(self):
        self.market_pos = None
        self.entry_price = None
        self.exit_price = None
        self.entry_time = None
        self.exit_time = None
        self.exit_name = None
        self.profit = None

