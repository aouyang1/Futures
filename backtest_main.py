__author__ = 'Austin Ouyang'

import time
from util.statemachine import StateMachine
from util.transitions import Transitions
from util.backtest import Backtest
import cProfile
import pstats

if __name__ == "__main__":

    m = StateMachine()
    t = Transitions()       # next state functions for state machine

    m.add_state("initialize", t.initialize_transitions)
    m.add_state("load_daily_data", t.load_daily_data_transitions)
    m.add_state("check_orders", t.check_orders_transitions)
    m.add_state("update_range_bar", t.update_range_bar_transitions)
    m.add_state("compute_indicators", t.compute_indicators_transitions)
    m.add_state("check_strategy", t.check_strategy_transitions)
    m.add_state("check_range_bar_finished", t.check_range_bar_finished_transitions)
    m.add_state("show_results", t.write_results_transitions)
    m.add_state("finished", None, end_state=1)

    m.set_start("initialize")

    start_time = time.time()
    bt = Backtest()
    cProfile.run('m.run(bt)', 'backtest_profile')
    elapsed_time = time.time() - start_time

    print "Total time: {}".format(elapsed_time)

    p = pstats.Stats('backtest_profile')
    p.strip_dirs().sort_stats('cumulative').print_stats('transitions')