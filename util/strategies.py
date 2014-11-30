__author__ = 'aouyang1'

from util.strategy_functions import *

class FT_Quicky_Base:

    def __init__(self, backtest, PL, offset, FTdthresh, FTthresh, maxBars):
        self.bt = backtest
        self.PL = PL
        self.offset = offset
        self.FTdthresh = FTdthresh
        self.FTthresh = FTthresh
        self.maxBars = maxBars
        self.in_trend = False

    def on_bar_update(self):
        FT = self.bt.indicators['FisherTransform'].val
        FTd = self.bt.indicators['LinRegSlope'].val

        curr_bar_time = self.bt.range_bar.CloseTime[0].tz_localize('utc').tz_convert('US/Central')
        hod = curr_bar_time.hour
        entry_permitted = not(hod == 16 or hod == 17)

        if entry_permitted:
            if self.in_trend:
                if self.bt.market.position == 'FLAT':
                    if FT[0] > self.FTthresh:
                        if FTd[0] < -self.FTdthresh:
                            print "go SHORT at {}".format(curr_bar_time)
                    elif FT[0] < -self.FTthresh:
                        if FTd[0] > self.FTdthresh:
                            print "go LONG at {}".format(curr_bar_time)

        if cross_above(FT, self.FTthresh) or cross_below(FT, -self.FTthresh):
            self.in_trend = True
        elif cross_below(FT, self.FTthresh) or cross_above(FT, -self.FTthresh):
            self.in_trend = False

