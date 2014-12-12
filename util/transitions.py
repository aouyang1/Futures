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
from util.backtest import Backtest
from util.futuresdatabase import FuturesDatabase
from util.rangebar import RangeBar
from util.dailytick import DailyTick
from util.strategies import *
from util.indicators import *
import time
from sys import stdout

order_time = 0.0
indicator_time = 0.0
strategy_time = 0.0
num_bdays = 0
day_cnt = 0


class Transitions:

    @staticmethod
    def set_strategies(bt):

        PL = 4
        offset = 3
        FTper = 25
        FTthresh = 2.5
        maxBars = 1

        indicators = {}
        indicators['FT'] = FisherTransform(bt, bt.range_bar.Close, FTper)
        indicators['FTD'] = Diff(bt, indicators['FT'].val, 2)
        bt.strategies['PL' + str(PL) +
                      '_FTper' + str(FTper) +
                      '_offset' + str(offset) +
                      '_FTthresh' + str(FTthresh) +
                      '_maxBars' + str(maxBars)] = FT_Quicky_Base(backtest=bt,
                                                                indicators=indicators,
                                                                PL=PL,
                                                                offset=offset,
                                                                FTdthresh=0.1,
                                                                FTthresh=FTthresh,
                                                                maxBars=maxBars)
        """
        # FT_QUICKY_BASE for GC
        indicators = {}
        indicators['FT'] = FisherTransform(bt, bt.range_bar.Close, 15)
        indicators['FTD'] = Diff(bt, indicators['FT'].val, 2)
        for PL in range(11, 41):
            bt.strategies['FT_Quicky_Base_PL' + str(PL)] = FT_Quicky_Base(backtest=bt,
                                                                          indicators=indicators,
                                                                          PL=PL,
                                                                          offset=3,
                                                                          FTdthresh=0.1,
                                                                          FTthresh=2.5,
                                                                          maxBars=1)
        """

    def initialize_transitions(self, (instr_name, RANGE, init_day, final_day)):

        table_name = instr_name + '_LAST_COMPRESSED'

        start_stamp = pd.Timestamp(init_day).tz_localize('US/Central')
        start_stamp_utc = start_stamp.tz_convert('utc')

        final_stamp = pd.Timestamp(final_day).tz_localize('US/Central')
        final_stamp_utc = final_stamp.tz_convert('utc')

        global num_bdays
        num_bdays = len(pd.bdate_range(start_stamp_utc, final_stamp_utc))

        bt = Backtest(table_name, RANGE, start_stamp_utc, final_stamp_utc)

        bt.futures_db = FuturesDatabase()
        bt.range_bar = RangeBar(instr_name, RANGE)
        bt.daily_tick = DailyTick()

        self.set_strategies(bt)

        new_state = "load_daily_data"

        return new_state, bt

    def load_daily_data_transitions(self, bt):

        global day_cnt
        stdout.write("\r%s" % "Running: " + str(bt.start_stamp_utc)[0:10] + "   " + str(day_cnt) + "/" + str(num_bdays))
        stdout.flush()
        day_cnt += 1

        if bt.start_stamp_utc < bt.final_stamp_utc:
            start_date = self.timestamp_to_SQLstring(bt.start_stamp_utc)

            # get end of day timestamp
            end_stamp_utc = bt.start_stamp_utc + Day() - 45*Minute()

            end_date = self.timestamp_to_SQLstring(end_stamp_utc)

            bt.daily_tick.df = bt.futures_db.fetch_between_dates(table_name=bt.table_name,
                                                                 start_date=start_date,
                                                                 end_date=end_date,
                                                                 )

            bt.daily_tick.set_lists()

            new_state = "search_for_event"

        else:
            new_state = "show_results"

        return new_state, bt

    @staticmethod
    def search_for_event_transitions(bt):

        if bt.daily_tick.cnt < bt.daily_tick.df.shape[0]:

            bt.tick = bt.daily_tick.get_curr_tick()
            bt.prev_tick = bt.daily_tick.get_prev_tick()
            #bt.range_bar.tick_list.append(bt.tick['Last'])

            # check for open orders and determine if they need to be filled
            start_time = time.time()
            if bt.tick['Last'] != bt.prev_tick['Last']:
                for strat_name in bt.strategies:
                    strat = bt.strategies[strat_name]
                    if strat.market.position != "FLAT":
                        strat.order.update(bt, strat)
            global order_time
            order_time += time.time() - start_time

            # compute range bar HLOC
            if bt.daily_tick.cnt == 0:  # first tick of day session
                bt.range_bar.init(bt)

            elif bt.daily_tick.cnt == (bt.daily_tick.df.shape[0]-1):  # last tick of day session
                bt.range_bar.update(bt)
                bt.range_bar.close()

            else:  # normal range bar check and update
                bt.range_bar.update(bt)

            # next state logic
            if bt.range_bar.event_found:
                new_state = "compute_indicators"
                bt.range_bar.event_found = False
            else:
                new_state = "search_for_event"

            bt.daily_tick.cnt += 1

        else:

            bt.daily_tick.cnt = 0

            # increment to next day
            bt.start_stamp_utc += Day()

            # if start date is Thursday 5PM CST jump to Sunday 5PM CST
            if bt.start_stamp_utc.weekday() == 4:
                bt.start_stamp_utc += 2*Day()

            new_state = "load_daily_data"

        return new_state, bt

    @staticmethod
    def compute_indicators_transitions(bt):
        start_time = time.time()

        # Indicator Parameter Optimization (most general and slowest)
        for strat_name in bt.strategies:
            strat = bt.strategies[strat_name]
            for indicator_name in strat.indicators:
                strat.indicators[indicator_name].on_bar_update()

        """
        # Strategy Parameter Optimization (improved speed)
        strat = bt.strategies[bt.strategies.keys()[0]]
        for indicator_name in strat.indicators:
            strat.indicators[indicator_name].on_bar_update()
        """

        global indicator_time
        indicator_time += time.time() - start_time

        new_state = "check_strategy"

        return new_state, bt

    @staticmethod
    def check_strategy_transitions(bt):
        start_time = time.time()
        for strat_name in bt.strategies:
            bt.strategies[strat_name].on_bar_update()

        global strategy_time
        strategy_time += time.time() - start_time

        new_state = "search_for_event"

        return new_state, bt

    def show_results_transitions(self, bt):
        stdout.write("\n")
        strat_name = np.sort(bt.strategies.keys())
        for s in strat_name:
            strat = bt.strategies[s]
            strat.trades.convert_to_dataframe()
            strat.trades.trade_log['cum_prof'] = np.cumsum(strat.trades.trade_log['profit'])
            print "{}: {:.2%} on {} trades with pval: {}".format(s,
                                                                 strat.trades.calc_win_perc(),
                                                                 strat.trades.trade_log.shape[0],
                                                                 strat.trades.calc_pval())
            """
            col = ['market_pos', 'entry_price', 'exit_price', 'entry_time', 'exit_time', 'exit_name', 'profit', 'cum_prof']
            print strat.trades.trade_log[col].head()
            """
            #self.write_results(s, strat)

        print "------------------------------------------------"
        print "    Order time: {:.2f}".format(order_time)
        print "Indicator time: {:.2f}".format(indicator_time)
        print " Strategy time: {:.2f}".format(strategy_time)
        print "------------------------------------------------"
        new_state = "finished"

        return new_state, bt

    def timestamp_to_SQLstring(self, timestamp):
        return str(timestamp)[:-6]

    def write_results(self, strat_name, strat):
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

        folder_name = '/home/aouyang1/Dropbox/Futures Trading/FT_QUICKY_v3/GC/BASE (copy)/PL' + \
                      re.findall(r'\d+', strat_name)[0] + \
                      '_py_comp/'

        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        pathname = folder_name + strat_name + '.csv'

        df.to_csv(path_or_buf=pathname, index=False)
