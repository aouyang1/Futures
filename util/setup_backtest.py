__author__ = 'aouyang1'

import ipdb
from util.strategies import *
from util.indicators import *


# Define general backtesting parameters
def set_backtest_options(bt):
    bt.instr_name = 'GC'
    bt.RANGE = 10
    bt.init_day = '2014-09-10 17:00:00'
    bt.final_day = '2014-11-30 16:59:59'

    bt.optimization = True          # if indicators are the same across all strategies, set True
    bt.log_intrabar_data = False    # setting true can significantly slowdown backtesting

    bt.write_trade_data = False
    bt.trade_data_root = '/home/aouyang1/Dropbox/Futures Trading/FT_QUICKY_v3/BASE (copy)'

    bt.write_bar_data = True
    bt.bar_data_root = '/home/aouyang1/Dropbox/Futures Trading/Backtester/FT_QUICKY_GC_BASE'


# Setup number of strategies and indicators
def set_strategies(bt):

    # FT_QUICKY_BASE for GC
    indicators = {}
    indicators['FT'] = FisherTransform(bt, bt.range_bar.Close, 15)
    indicators['FTD'] = Diff(bt, indicators['FT'].val, 2)
    bt.strategies['FT_Quicky_Base_PL17'] = FT_Quicky_Base(backtest=bt,
                                                                      indicators=indicators,
                                                                      PL=17,
                                                                      offset=3,
                                                                      FTdthresh=0.1,
                                                                      FTthresh=2.5,
                                                                      maxBars=1)
    """
    # FT_QUICKY_BASE for GC
    for PL in range(17, 25):
        indicators = {}
        indicators['FT'] = FisherTransform(bt, bt.range_bar.Close, 15)
        indicators['FTD'] = Diff(bt, indicators['FT'].val, 2)
        bt.strategies['FT_Quicky_Base_PL' + str(PL)] = FT_Quicky_Base(backtest=bt,
                                                                      indicators=indicators,
                                                                      PL=PL,
                                                                      offset=3,
                                                                      FTdthresh=0.1,
                                                                      FTthresh=2.5,
                                                                      maxBars=1)
    """



