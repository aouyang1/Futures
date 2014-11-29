__author__ = 'aouyang1'


class Tick:

    def __init__(self, df, tick_cnt):
        self.tick_df = df
        self.tick_cnt = tick_cnt


class Backtest(Tick):

    def __init__(self, table_name, RANGE, start_stamp_utc, final_stamp_utc):
        Tick.__init__(self, None, 0)
        self.table_name = table_name
        self.RANGE = RANGE
        self.start_stamp_utc = start_stamp_utc
        self.final_stamp_utc = final_stamp_utc
        self.fdb = None
        self.rb = None



