__author__ = 'aouyang1'


class Order:

    def __init__(self):
        self.order_action = None    # buy, sell
        self.limit_price = None
        self.order_id = None
        self.order_type = None      # limit, market
        self.order_state = None     # working, filled
        self.stop_loss = None
        self.profit_target = None

    def reset(self):
        self.order_action = None    # buy, sell
        self.limit_price = None
        self.order_id = None
        self.order_type = None      # limit, market
        self.order_state = None     # working, filled
        self.stop_loss = None
        self.profit_target = None

    def update(self, backtest, strat):
        if self.order_state == "WORKING":
            # looking to fill limit order
            if self.order_action == "BUY":
                if backtest.daily_tick.curr_last() <= self.limit_price:
                    self.order_state = "FILLED"
                    strat.trades.curr.entry_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.entry_bar = backtest.range_bar.cnt
            elif self.order_action == "SELL":
                if backtest.daily_tick.curr_last() >= self.limit_price:
                    self.order_state = "FILLED"
                    strat.trades.curr.entry_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.entry_bar = backtest.range_bar.cnt

        elif self.order_state == "FILLED":
            # looking for profit target to hit, stop loss to hit, or eof day
            curr_time = backtest.daily_tick.curr_date()
            if self.order_action == "BUY":
                if backtest.daily_tick.curr_last() >= self.profit_target:
                    strat.trades.curr.exit_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.exit_bar = backtest.range_bar.cnt
                    strat.trades.curr.exit_price = self.profit_target
                    strat.trades.curr.exit_name = 'Profit target'
                    self.calculate_profit(backtest, strat)
                    strat.trades.add_trade()
                    strat.market.position = "FLAT"
                    self.reset()

                elif backtest.daily_tick.curr_last() <= self.stop_loss:
                    strat.trades.curr.exit_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.exit_bar = backtest.range_bar.cnt
                    strat.trades.curr.exit_price = backtest.daily_tick.curr_last()
                    strat.trades.curr.exit_name = 'Stop loss'
                    self.calculate_profit(backtest, strat)
                    strat.trades.add_trade()
                    strat.market.position = "FLAT"
                    self.reset()

                elif curr_time.hour == 16 and curr_time.minute == 14 and 30 <= curr_time.second <= 59:
                    strat.trades.curr.exit_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.exit_bar = backtest.range_bar.cnt
                    strat.trades.curr.exit_price = backtest.daily_tick.curr_last()
                    strat.trades.curr.exit_name = 'Exit on close'
                    self.calculate_profit(backtest, strat)
                    strat.trades.add_trade()
                    strat.market.position = "FLAT"
                    self.reset()

            elif self.order_action == "SELL":
                if backtest.daily_tick.curr_last() <= self.profit_target:
                    strat.trades.curr.exit_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.exit_bar = backtest.range_bar.cnt
                    strat.trades.curr.exit_price = self.profit_target
                    strat.trades.curr.exit_name = 'Profit target'
                    self.calculate_profit(backtest, strat)
                    strat.trades.add_trade()
                    strat.market.position = "FLAT"
                    self.reset()

                elif backtest.daily_tick.curr_last() >= self.stop_loss:
                    strat.trades.curr.exit_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.exit_bar = backtest.range_bar.cnt
                    strat.trades.curr.exit_price = backtest.daily_tick.curr_last()
                    strat.trades.curr.exit_name = 'Stop loss'
                    self.calculate_profit(backtest, strat)
                    strat.trades.add_trade()
                    strat.market.position = "FLAT"
                    self.reset()

                elif curr_time.hour == 16 and curr_time.minute == 14 and 30 <= curr_time.second <= 59:
                    strat.trades.curr.exit_time = backtest.daily_tick.curr_date()
                    strat.trades.curr.exit_bar = backtest.range_bar.cnt
                    strat.trades.curr.exit_price = backtest.daily_tick.curr_last()
                    strat.trades.curr.exit_name = 'Exit on close'
                    self.calculate_profit(backtest, strat)
                    strat.trades.add_trade()
                    strat.market.position = "FLAT"
                    self.reset()

    def calculate_profit(self, backtest, strat):
        tick_size = backtest.range_bar.instr.TICK_SIZE
        tick_value = backtest.range_bar.instr.TICK_VALUE
        entry_price = strat.trades.curr.entry_price
        exit_price = strat.trades.curr.exit_price
        if self.order_action == "BUY":
            strat.trades.curr.profit = round((exit_price - entry_price)/tick_size)*tick_value
        elif self.order_action == "SELL":
            strat.trades.curr.profit = -round((exit_price - entry_price)/tick_size)*tick_value
