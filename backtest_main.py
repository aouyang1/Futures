__author__ = 'Austin Ouyang'

import time
from util.statemachine import StateMachine
from util.transitions import Transitions
from util.backtest import Backtest

if __name__ == "__main__":

    m = StateMachine()
    t = Transitions()       # next state functions for state machine

    m.add_state("initialize", t.initialize_transitions)
    m.add_state("load_daily_data", t.load_daily_data_transitions)
    m.add_state("search_for_event", t.search_for_event_transitions)
    m.add_state("compute_indicators", t.compute_indicators_transitions)
    m.add_state("check_strategy", t.check_strategy_transitions)
    m.add_state("show_results", t.write_results_transitions)
    m.add_state("finished", None, end_state=1)

    m.set_start("initialize")

    start_time = time.time()
    bt = Backtest()
    m.run(bt)
    elapsed_time = time.time() - start_time

    print "Total time: {}".format(elapsed_time)
