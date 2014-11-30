__author__ = 'aouyang1'


class FT_Quicky_Base:

    def __init__(self, backtest, PL, offset, FTdthresh, FTthresh, maxBars):
        self.range_bar = backtest.range_bar
        self.indicators = backtest.indicators
        self.order = backtest.order
        self.PL = PL
        self.offset = offset
        self.FTdthresh = FTdthresh
        self.FTthresh = FTthresh
        self.maxBars = maxBars


    def on_bar_update(self):
        FT = self.indicators['FisherTransform'].val

        # TODO implement on bar update for FT_Quicky_Base strategy

