"""
Transition class containing the functions for the next state in the finite state machine:

- 'initialize_transitions', initialize Sudoku table and brute force class

"""

import pandas as pd
from pandas.tseries.offsets import *
from futuresdatabase import FuturesDatabase
from backtest import Backtest
from rangebar import RangeBar


class Transitions:

    @staticmethod
    def initialize_transitions((instr_name, RANGE, init_day, final_day)):
        table_name = instr_name + '_LAST'

        start_stamp = pd.Timestamp(init_day).tz_localize('US/Central')
        start_stamp_utc = start_stamp.tz_convert('utc')

        final_stamp = pd.Timestamp(final_day).tz_localize('US/Central')
        final_stamp_utc = final_stamp.tz_convert('utc')

        bt = Backtest(table_name, RANGE, start_stamp_utc, final_stamp_utc)
        bt.fdb = FuturesDatabase()
        bt.rb = RangeBar(instr_name, RANGE)
        new_state = "load_daily_data"

        return new_state, bt

    def load_daily_data_transitions(self, bt):

        if bt.start_stamp_utc < bt.final_stamp_utc:
            print bt.start_stamp_utc

            start_date = self.timestamp_to_SQLstring(bt.start_stamp_utc)

            # get end of day timestamp
            end_stamp_utc = bt.start_stamp_utc + Day() - 45*Minute()

            end_date = self.timestamp_to_SQLstring(end_stamp_utc)

            bt.tick_df = bt.fdb.fetch_between_dates(table_name=bt.table_name, start_date=start_date, end_date=end_date)

            new_state = "search_for_event"

        else:
            new_state = "finished"


        return new_state, bt

    @staticmethod
    def search_for_event_transitions(bt):

        if bt.tick_cnt < bt.tick_df.shape[0]:
            tick = bt.tick_df.ix[bt.tick_cnt]
            bt.rb.bar_tick_list.append(tick['Last'])
            # check for open orders and determine if they need to be filled
            # check_order()

            # compute range bar HLOC
            if bt.tick_cnt == 0:  # first tick of day session
                bt.rb.init_bar(tick)

            elif bt.tick_cnt == (bt.tick_df.shape[0]-1):  # last tick of day session
                bt.rb.update_range_bar(tick)
                bt.rb.close_bar()

            else:  # normal range bar check and update
                bt.rb.update_range_bar(tick)

            # next state logic
            if bt.rb.event_found:
                new_state = "compute_indicators"
                bt.rb.event_found = False
            else:
                new_state = "search_for_event"

            bt.tick_cnt += 1

        else:

            bt.tick_cnt = 0

            # increment to next day
            bt.start_stamp_utc += Day()

            # if start date is Thursday 5PM CST jump to Sunday 5PM CST
            if bt.start_stamp_utc.weekday() == 4:
                bt.start_stamp_utc += 2*Day()

            new_state = "load_daily_data"
            print "{} bars".format(len(bt.rb.Close))

        return new_state, bt

    @staticmethod
    def compute_indicators_transitions(bt):
        new_state = "check_strategy"
        return new_state, bt

    @staticmethod
    def check_strategy_transitions(bt):
        new_state = "search_for_event"
        return new_state, bt


    def timestamp_to_SQLstring(self, timestamp):
        return str(timestamp)[:-6]

