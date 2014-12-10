__author__ = 'aouyang1'

from pandas import DataFrame


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


class CurrentTrade:

    def __init__(self):
        self.market_pos = None
        self.entry_price = None
        self.exit_price = None
        self.entry_time = None
        self.exit_time = None
        self.exit_name = None
        self.profit = None

