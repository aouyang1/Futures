__author__ = 'Austin Ouyang'

import time
import datetime
import pandas as pd
from util.statemachine import StateMachine
from util.transitions import Transitions


if __name__ == "__main__":

    instr_name = 'GC'
    RANGE = 10
    init_day = '2013-09-15 17:00:00'
    final_day = '2013-09-22 16:59:59'

    m = StateMachine()
    t = Transitions()       # next state functions for state machine

    m.add_state("initialize", t.initialize_transitions)
    m.add_state("load_daily_data", t.load_daily_data_transitions)
    m.add_state("search_for_event", t.search_for_event_transitions)
    m.add_state("compute_indicators", t.compute_indicators_transitions)
    m.add_state("check_strategy", t.check_strategy_transitions)
    m.add_state("show_results", t.show_results_transitions)
    m.add_state("finished", None, end_state=1)

    m.set_start("initialize")

    print "Backtest start time: {}".format(pd.Timestamp(datetime.datetime.now()))
    print "------------------------------------------------"
    print "Instrument: {}".format(instr_name)
    print "     Range: {}".format(RANGE)
    print "     Start: {}".format(init_day)
    print "       End: {}".format(final_day)
    print "------------------------------------------------"

    start_time = time.time()
    m.run((instr_name, RANGE, init_day, final_day))
    elapsed_time = time.time() - start_time

    print "Total time: {}".format(elapsed_time)
