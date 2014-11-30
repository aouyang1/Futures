__author__ = 'aouyang1'

class Backtest:

    def __init__(self, table_name, RANGE, start_stamp_utc, final_stamp_utc):
        self.table_name = table_name
        self.RANGE = RANGE
        self.start_stamp_utc = start_stamp_utc
        self.final_stamp_utc = final_stamp_utc
        self.futures_db = None
        self.range_bar = None
        self.daily_tick = None
        self.order = None
        self.indicators = {}
        self.strategies = {}



