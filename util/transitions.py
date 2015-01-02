"""
Transition class containing the functions for the next state in the finite state machine:

- 'initialize_transitions', initialize backtest class and subclasses futuresdatabase and rangebar
- 'load_daily_data_transitions', gets daily tick data from SQL database
- 'search_for_event_transitions', looks for a break in the range bar to compute indicator and strategy
- 'compute_indicators_transitions', compute indicators at close of bar
- 'check_strategy_transitions', check if strategy needs to enter/exit
"""

import pandas as pd
from pandas import DataFrame
from pandas.tseries.offsets import *
import re
import os
import ipdb
from util.futuresdatabase import FuturesDatabase
from util.rangebar import RangeBar
from util.dailytick import DailyTick
from util.setup_backtest import *
import time
import datetime
from sys import stdout


class Transitions:

    def __init__(self):
        self.num_bdays = 0
        self.day_cnt = 0
        self.backtest_start_time = 0

    def initialize_transitions(self, bt):

        self.backtest_start_time = time.time()

        bt.table_name = bt.instr_name + '_LAST_COMPRESSED'

        start_stamp = pd.Timestamp(bt.init_day).tz_localize('US/Central')
        bt.start_stamp_utc = start_stamp.tz_convert('utc')

        final_stamp = pd.Timestamp(bt.final_day).tz_localize('US/Central')
        bt.final_stamp_utc = final_stamp.tz_convert('utc')

        self.num_bdays = len(pd.bdate_range(bt.start_stamp_utc, bt.final_stamp_utc))

        bt.futures_db = FuturesDatabase()
        bt.range_bar = RangeBar(bt.instr_name, bt.RANGE)
        bt.daily_tick = DailyTick()
        set_strategies(bt)
        Transitions.determine_optimization(bt)

        print "Backtest start time: {}".format(pd.Timestamp(datetime.datetime.now()))
        print "------------------------------------------------"
        print "Instrument: {}".format(bt.instr_name)
        print "     Range: {}".format(bt.RANGE)
        print "     Start: {}".format(bt.init_day)
        print "       End: {}".format(bt.final_day)
        print "------------------------------------------------"

        new_state = "load_daily_data"

        return new_state, bt

    def load_daily_data_transitions(self, bt):

        stdout.write("\r%s" % "Running: " + str(bt.start_stamp_utc)[0:10] +
                     "   " + str(self.day_cnt) + "/" + str(self.num_bdays) + " business days completed")
        stdout.flush()

        if bt.gui:
            bt.gui.progressBar_backtest.setValue(min(self.day_cnt/float(self.num_bdays)*100, 100))
            if self.day_cnt > 0:
                elapsed_time = time.time() - self.backtest_start_time
                days_remaining = max(self.num_bdays - self.day_cnt, 0)
                time_remaining_sec = round(days_remaining/float(self.day_cnt)*elapsed_time)
                bt.gui.label_time_remaining.setText("Time Remaining: " + str(datetime.timedelta(seconds=time_remaining_sec)))

        self.day_cnt += 1

        if bt.start_stamp_utc < bt.final_stamp_utc:

            start_date = Transitions.timestamp_to_SQLstring(bt.start_stamp_utc)

            # get end of day timestamp
            end_stamp_utc = bt.start_stamp_utc + Day() - 45*Minute()

            end_date = Transitions.timestamp_to_SQLstring(end_stamp_utc)

            bt.daily_tick.df = bt.futures_db.fetch_between_dates(table_name=bt.table_name,
                                                                 start_date=start_date,
                                                                 end_date=end_date,
                                                                 time_zone='US/Central')

            bt.daily_tick.set_lists()

            new_state = "check_orders"

        else:
            new_state = "show_results"

        return new_state, bt

    def check_orders_transitions(self, bt):

        if bt.daily_tick.cnt < bt.daily_tick.df.shape[0]:

            if bt.log_intrabar_data:
                bt.range_bar.tick_list.append(bt.daily_tick.curr_last())

            # check for open orders and determine if they need to be filled
            if bt.daily_tick.curr_last() != bt.daily_tick.prev_last():
                for strat_name in bt.strategies:
                    strat = bt.strategies[strat_name]
                    if strat.market.position != "FLAT":
                        strat.order.update(bt, strat)

            new_state = "update_range_bar"

        else:

            bt.daily_tick.cnt = 0

            # increment to next day
            bt.start_stamp_utc += Day()

            # if start date is Thursday 5PM CST jump to Sunday 5PM CST
            if bt.start_stamp_utc.weekday() == 4:
                bt.start_stamp_utc += 2*Day()

            new_state = "load_daily_data"

        return new_state, bt

    def update_range_bar_transitions(self, bt):

        # compute range bar HLOC
        if bt.daily_tick.cnt == 0:  # first tick of day session
            bt.range_bar.init(bt)

        elif bt.daily_tick.cnt == (bt.daily_tick.df.shape[0]-1):  # last tick of day session
            bt.range_bar.update(bt)
            if not bt.range_bar.event_found:
                bt.range_bar.close()

        else:  # normal range bar check and update
            bt.range_bar.update(bt)

        # next state logic
        if bt.range_bar.event_found:
            new_state = "compute_indicators"
        else:
            bt.daily_tick.cnt += 1
            new_state = "check_orders"

        return new_state, bt

    def compute_indicators_transitions(self, bt):

        if bt.optimization:
            # Strategy Parameter Optimization (improved speed)
            strat = bt.strategies[bt.strategies.keys()[0]]
            for indicator_name in strat.indicators:
                strat.indicators[indicator_name].on_bar_update()

        else:
            # Indicator Parameter Optimization (most general and slowest)
            for strat_name in bt.strategies:
                strat = bt.strategies[strat_name]
                for indicator_name in strat.indicators:
                    strat.indicators[indicator_name].on_bar_update()

        new_state = "check_strategy"

        return new_state, bt

    def check_strategy_transitions(self, bt):

        for strat_name in bt.strategies:
            bt.strategies[strat_name].on_bar_update()

        new_state = "check_range_bar_finished"

        return new_state, bt

    # necessary in the case that a tick exceeds more than 1 range bar
    def check_range_bar_finished_transitions(self, bt):

        bt.range_bar.event_found = False

        if round((bt.daily_tick.curr_last() - bt.range_bar.curr.Low)/bt.range_bar.instr.TICK_SIZE) > bt.range_bar.RANGE:
            bt.range_bar.curr.Low = bt.range_bar.Close[0] + bt.range_bar.instr.TICK_SIZE
            bt.range_bar.curr.Open = bt.range_bar.curr.Low
            bt.range_bar.curr.Volume = 0

            if round((bt.daily_tick.curr_last() - bt.range_bar.curr.Low)/bt.range_bar.instr.TICK_SIZE) > bt.range_bar.RANGE:
                new_state = "update_range_bar"
            else:
                bt.range_bar.curr.High = bt.daily_tick.curr_last()
                bt.range_bar.curr.Close = bt.daily_tick.curr_last()
                bt.daily_tick.cnt += 1
                new_state = "check_orders"

        elif round((bt.range_bar.curr.High-bt.daily_tick.curr_last())/bt.range_bar.instr.TICK_SIZE) > bt.range_bar.RANGE:
            bt.range_bar.curr.High = bt.range_bar.Close[0] - bt.range_bar.instr.TICK_SIZE
            bt.range_bar.curr.Open = bt.range_bar.curr.High
            bt.range_bar.curr.Volume = 0

            if round((bt.range_bar.curr.High-bt.daily_tick.curr_last())/bt.range_bar.instr.TICK_SIZE) > bt.range_bar.RANGE:
                new_state = "update_range_bar"
            else:
                bt.range_bar.curr.Low = bt.daily_tick.curr_last()
                bt.range_bar.curr.Close = bt.daily_tick.curr_last()
                bt.daily_tick.cnt += 1
                new_state = "check_orders"
        else:
            bt.daily_tick.cnt += 1
            new_state = "check_orders"

        return new_state, bt

    def write_results_transitions(self, bt):

        if bt.gui:
            bt.gui.progressBar_backtest.setValue(100)

        stdout.write("\n")

        strat_name = np.sort(bt.strategies.keys())
        for s in strat_name:
            strat = bt.strategies[s]
            strat.trades.convert_to_dataframe()
            strat.trades.trade_log['cum_prof'] = np.cumsum(strat.trades.trade_log['profit'])
            winperc, winperc_pval = strat.trades.calc_win_perc()
            print "{}: {:.2%} on {} trades with pval: {:.6f}".format(s,
                                                                     winperc,
                                                                     strat.trades.trade_log.shape[0],
                                                                     winperc_pval)

            if bt.write_trade_data:
                Transitions.write_results_as_csv(bt, s, strat)

        if bt.write_bar_data:
            Transitions.write_bar_as_csv(bt)

        new_state = "finished"

        return new_state, bt

    @staticmethod
    def timestamp_to_SQLstring(timestamp):
        return str(timestamp)[:-6]

    @staticmethod
    def determine_optimization(bt):
        bt.unique_indicators = list(set([bt.strategies[strat_name].indicators[indicator_name]
                                         for strat_name in bt.strategies
                                         for indicator_name in bt.strategies[strat_name].indicators]))
        bt.optimization = len(bt.unique_indicators) == len(bt.strategies[bt.strategies.keys()[0]].indicators)

    @staticmethod
    def write_results_as_csv(backtest, strat_name, strat):
        header = ['Trade-#',
                  'Instrument',
                  'Account',
                  'Strategy',
                  'Market pos.',
                  'Quantity',
                  'Entry price',
                  'Exit price',
                  'Entry time',
                  'Exit time',
                  'Entry name',
                  'Exit name',
                  'Profit',
                  'Cum. profit',
                  'Commission',
                  'MAE',
                  'MFE',
                  'ETD',
                  'Bars']

        df = DataFrame(np.zeros((strat.trades.trade_log.shape[0], len(header))), columns=header)
        df['Market pos.'] = strat.trades.trade_log['market_pos'].apply(lambda x: x.lower()).apply(lambda x: x.title())
        df['Quantity'] = 1
        df['Entry price'] = strat.trades.trade_log['entry_price']
        df['Exit price'] = strat.trades.trade_log['exit_price']
        df['Entry time'] = strat.trades.trade_log['entry_time'].apply(lambda x: str(x)[:-6])
        df['Exit time'] = strat.trades.trade_log['exit_time'].apply(lambda x: str(x)[:-6])
        df['Exit name'] = strat.trades.trade_log['exit_name']
        df['Profit'] = strat.trades.trade_log['profit']
        df['Cum. profit'] = strat.trades.trade_log['cum_prof']

        folder_name = backtest.trade_data_root + '/PL' + re.findall(r'\d+', strat_name)[0] + '/'

        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        pathname = folder_name + strat_name + '.csv'

        df.to_csv(path_or_buf=pathname, index=False)

    @staticmethod
    def write_bar_as_csv(bt):
        range_bar_df = DataFrame({'Date': bt.range_bar.CloseTime,
                                  'H': bt.range_bar.High,
                                  'L': bt.range_bar.Low,
                                  'O': bt.range_bar.Open,
                                  'C': bt.range_bar.Close}, columns=['Date', 'H', 'L', 'O', 'C'])

        strat = bt.strategies[bt.strategies.keys()[0]]
        #print len(bt.range_bar.Close)
        #print bt.range_bar.CloseTime[0:5]
        #print bt.range_bar.CloseTime[-1:-6]
        for indicator_name in strat.indicators:
            #print len(strat.indicators[indicator_name].val)
            range_bar_df[indicator_name] = strat.indicators[indicator_name].val

        """
        print range_bar_df.head(n=3)
        print range_bar_df.tail(n=3)

        if not os.path.isdir(bt.bar_data_root):
            os.mkdir(bt.bar_data_root)

        pathname = bt.bar_data_root + bt.strategies.keys()[0] + '.csv'

        range_bar_df.to_csv(path_or_buf=pathname, index=False)
        """