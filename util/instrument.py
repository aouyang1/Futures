__author__ = 'aouyang1'

TickSizeDict = {'GC': 0.1,
                'CL': 0.01,
                'ZB': 0.03125}

TickValueDict = {'GC': 10.0,
                 'CL': 10.0,
                 'ZB': 31.25}


class InstrumentTraits:

    def __init__(self, instrument):
        self.TICK_SIZE = TickSizeDict[instrument]
        self.TICK_VALUE = TickValueDict[instrument]