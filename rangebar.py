import pandas as pd


TickSizeDict = {'GC': 0.1,
                'CL': 0.01,
                'ZB': 0.03125}

TickValueDict = {'GC': 10.0,
                 'CL': 10.0,
                 'ZB': 31.25}

class RangeBar:

    def __init__(self, instrument, RANGE):
        self.curr = CurrentHLOC()
        self.instr = InstrumentTraits(instrument)
        self.RANGE = RANGE
        self.High = []
        self.Low = []
        self.Open = []
        self.Close = []
        self.Volume = []
        self.CloseTime = []
        self.bar_tick_list = []
        self.TickRecord = {}
        self.bar_cnt = 0
        self.event_found = False


    def init_bar(self, tick):
        self.curr.High = tick['Last']
        self.curr.Low = tick['Last']
        self.curr.Open = tick['Last']
        self.curr.Close = tick['Last']
        self.curr.Volume = tick['Volume']
        self.curr.CloseTime = tick.name


    def close_bar(self):
        self.High.insert(0, self.curr.High)
        self.Low.insert(0, self.curr.Low)
        self.Open.insert(0, self.curr.Open)
        self.Close.insert(0, self.curr.Close)
        self.Volume.insert(0, self.curr.Volume)
        self.CloseTime.insert(0, self.curr.CloseTime)
        self.TickRecord[self.bar_cnt] = self.bar_tick_list
        self.bar_cnt += 1
        self.bar_tick_list = []
        self.event_found = True
        # calculate new indicator values
        # check for strategy entry


    def update_range_bar(self, tick):

        self.curr.CloseTime = tick.name
        self.curr.Volume += tick['Volume']

        if round((tick['Last']-self.curr.Low)/self.instr.TICK_SIZE) > self.RANGE:    # check if range has broken above

            while round((tick['Last'] - self.curr.Low)/self.instr.TICK_SIZE) > self.RANGE:
                self.curr.High = self.curr.Low + self.RANGE*self.instr.TICK_SIZE
                self.curr.Close = self.curr.High
                self.close_bar()

                self.curr.Low = self.Close[0] + self.instr.TICK_SIZE
                self.curr.Open = self.curr.Low
                self.curr.Volume = 0

            self.curr.High = tick['Last']
            self.curr.Close = tick['Last']

        elif round((self.curr.High-tick['Last'])/self.instr.TICK_SIZE) > self.RANGE: # check if range has broken below

            while round((self.curr.High - tick['Last'])/self.instr.TICK_SIZE) > self.RANGE:
                self.curr.Low = self.curr.High - self.RANGE*self.instr.TICK_SIZE
                self.curr.Close = self.curr.Low
                self.close_bar()

                self.curr.High = self.Close[0] - self.instr.TICK_SIZE
                self.curr.Open = self.curr.High
                self.curr.Volume = 0

            self.curr.Low = tick['Last']
            self.curr.Close = tick['Last']

        elif tick['Last'] > self.curr.High:                          # check if new high in bar is made
            self.curr.High = tick['Last']

        elif tick['Last'] < self.curr.Low:                           # check if new low in bar is made
            self.curr.Low = tick['Last']

        else:                                                       # update current close of bar
            self.curr.Close = tick['Last']





    def get_ticks_in_bar(self, bars_from_current):
        return self.TickRecord[self.bar_cnt - bars_from_current - 1]


class CurrentHLOC:

    def __init__(self):
        self.High = 0
        self.Low = 0
        self.Open = 0
        self.Close = 0
        self.Volume = 0
        self.CloseTime = pd.Timestamp('01-01-1960 00:00:00')


class InstrumentTraits:

    def __init__(self, instrument):
        self.TICK_SIZE = TickSizeDict[instrument]
        self.TICK_VALUE = TickValueDict[instrument]
