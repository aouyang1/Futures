__author__ = 'aouyang1'


from util.strategy_functions import *
from util.order import Order
from util.market import Market
from util.trades import Trades


class FT_Quicky_Base:

    def __init__(self, backtest, indicators, PL, offset, FTdthresh, FTthresh, maxBars):
        self.bt = backtest
        self.indicators = indicators
        self.order = Order()
        self.market = Market()
        self.trades = Trades()
        self.PL = PL
        self.offset = offset
        self.FTdthresh = FTdthresh
        self.FTthresh = FTthresh
        self.maxBars = maxBars
        self.in_trend = False
        self.bars_passed = 0

    def on_bar_update(self):
        FT = self.indicators['FT'].val
        FTd = self.indicators['FTD'].val

        curr_bar_time = self.bt.range_bar.CloseTime[0]
        hod = curr_bar_time.hour
        entry_permitted = not(hod == 16 or hod == 17)

        if entry_permitted:
            if self.in_trend:
                if self.market.position == 'FLAT':
                    if FT[0] > self.FTthresh:
                        if FTd[0] < -self.FTdthresh:
                            limit_price = self.bt.range_bar.Close[0]+self.offset*self.bt.range_bar.instr.TICK_SIZE
                            enter_short_limit(self, limit_price)
                            set_profit_target(self)
                            set_stop_loss(self)
                            self.market.position = "SHORT"
                            self.bars_passed = 0
                            self.trades.curr.market_pos = self.market.position
                            self.trades.curr.entry_price = limit_price

                    elif FT[0] < -self.FTthresh:
                        if FTd[0] > self.FTdthresh:
                            limit_price = self.bt.range_bar.Close[0]-self.offset*self.bt.range_bar.instr.TICK_SIZE
                            enter_long_limit(self, limit_price)
                            set_profit_target(self)
                            set_stop_loss(self)
                            self.market.position = "LONG"
                            self.bars_passed = 0
                            self.trades.curr.market_pos = self.market.position
                            self.trades.curr.entry_price = limit_price

        if self.order.order_state == "WORKING":
            self.bars_passed += 1
            if self.bars_passed > self.maxBars:
                cancel_order(self)
                self.in_trend = False

        if cross_above(FT, self.FTthresh) or cross_below(FT, -self.FTthresh):
            self.in_trend = True
        elif cross_below(FT, self.FTthresh) or cross_above(FT, -self.FTthresh):
            self.in_trend = False
