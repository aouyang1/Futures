__author__ = 'aouyang1'


from util.instrument import InstrumentTraits
from util.hloc import CurrentHLOC


class RangeBar:

    def __init__(self, instrument, RANGE):
        self.curr = CurrentHLOC()
        self.instr = InstrumentTraits(instrument)
        self.RANGE = RANGE
        self.High = []      # 0 index is newest data
        self.Low = []       # 0 index is newest data
        self.Open = []      # 0 index is newest data
        self.Close = []     # 0 index is newest data
        self.Volume = []    # 0 index is newest data
        self.CloseTime = [] # 0 index is newest data
        self.tick_list = []
        self.TickRecord = {} # self.cnt index is newest data
        self.cnt = 0
        self.event_found = False

    def init(self, bt):
        self.curr.High = bt.tick['Last']
        self.curr.Low = bt.tick['Last']
        self.curr.Open = bt.tick['Last']
        self.curr.Close = bt.tick['Last']
        self.curr.Volume = bt.tick['Volume']
        self.curr.CloseTime = bt.tick['Date']

    def close(self):
        self.High.insert(0, self.curr.High)
        self.Low.insert(0, self.curr.Low)
        self.Open.insert(0, self.curr.Open)
        self.Close.insert(0, self.curr.Close)
        self.Volume.insert(0, self.curr.Volume)
        self.CloseTime.insert(0, self.curr.CloseTime)
        self.TickRecord[self.cnt] = self.tick_list
        self.cnt += 1
        self.tick_list = []
        self.event_found = True

    def update(self, bt):

        self.curr.CloseTime = bt.tick['Date']
        self.curr.Volume += bt.tick['Volume']

        if bt.tick['Last'] != bt.prev_tick['Last']:
            if round((bt.tick['Last']-self.curr.Low)/self.instr.TICK_SIZE) > self.RANGE:    # check if range has broken above
                self.curr.High = self.curr.Low + self.RANGE*self.instr.TICK_SIZE
                self.curr.Close = self.curr.High
                self.close()

            elif round((self.curr.High-bt.tick['Last'])/self.instr.TICK_SIZE) > self.RANGE: # check if range has broken below
                self.curr.Low = self.curr.High - self.RANGE*self.instr.TICK_SIZE
                self.curr.Close = self.curr.Low
                self.close()

            elif bt.tick['Last'] > self.curr.High:                          # check if new high in bar is made
                self.curr.High = bt.tick['Last']

            elif bt.tick['Last'] < self.curr.Low:                           # check if new low in bar is made
                self.curr.Low = bt.tick['Last']

            else:                                                       # update current close of bar
                self.curr.Close = bt.tick['Last']

    def get_ticks_in_bar(self, bars_from_current):
        return self.TickRecord[self.cnt - bars_from_current - 1]





