__author__ = 'Austin Ouyang'

from statemachine import StateMachine
from transitions import Transitions


if __name__ == "__main__":

    instr_name = 'GC'
    RANGE = 10
    init_day = '2014-05-07 17:00:00'
    final_day = '2014-05-09 16:59:59'

    m = StateMachine()
    t = Transitions()       # next state functions for state machine

    m.add_state("initialize", t.initialize_transitions)
    m.add_state("load_daily_data", t.load_daily_data_transitions)
    m.add_state("search_for_event", t.search_for_event_transitions)
    m.add_state("compute_indicators", t.compute_indicators_transitions)
    m.add_state("check_strategy", t.check_strategy_transitions)

    m.add_state("finished", None, end_state=1)

    m.set_start("initialize")

    m.run((instr_name, RANGE, init_day, final_day))

    print 'Done'