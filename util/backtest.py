__author__ = 'aouyang1'


class Backtest:

    def __init__(self, gui=None):
        self.gui = gui

        self.table_name = None
        self.RANGE = None
        self.init_day = None
        self.final_day = None

        self.start_stamp_utc = None
        self.final_stamp_utc = None

        self.futures_db = None
        self.range_bar = None
        self.daily_tick = None

        self.tick = None
        self.prev_tick = None

        self.strategies = {}

        self.optimization = False
        self.log_intrabar_data = False
        self.write_trade_data = False
        self.trade_data_root = ''
        self.write_bar_data = False
        self.bar_data_root = ''



