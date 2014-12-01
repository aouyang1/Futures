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

    def update(self, backtest):
        if self.order_state == "WORKING":
            # looking to fill limit order
            if self.order_action == "BUY":
                if backtest.tick['Last'] <= self.limit_price:
                    self.order_state = "FILLED"
                    backtest.trades.curr.entry_time = backtest.tick.name
            elif self.order_action == "SELL":
                if backtest.tick['Last'] >= self.limit_price:
                    self.order_state = "FILLED"
                    backtest.trades.curr.entry_time = backtest.tick.name

        elif self.order_state == "FILLED":
            # looking for profit target to hit, stop loss to hit, or eof day
            curr_time = backtest.tick.name.tz_localize('utc').tz_convert('US/Central')
            if self.order_action == "BUY":
                if backtest.tick['Last'] >= self.profit_target:
                    backtest.trades.curr.exit_time = backtest.tick.name
                    backtest.trades.curr.exit_price = self.profit_target
                    backtest.trades.curr.exit_name = 'Profit target'
                    backtest.trades.add_trade()
                    backtest.market.position = "FLAT"
                    self.reset()

                elif backtest.tick['Last'] <= self.stop_loss:
                    backtest.trades.curr.exit_time = backtest.tick.name
                    backtest.trades.curr.exit_price = backtest.tick['Last']
                    backtest.trades.curr.exit_name = 'Stop loss'
                    backtest.trades.add_trade()
                    backtest.market.position = "FLAT"
                    self.reset()

            elif self.order_action == "SELL":
                if backtest.tick['Last'] <= self.profit_target:
                    backtest.trades.curr.exit_time = backtest.tick.name
                    backtest.trades.curr.exit_price = self.profit_target
                    backtest.trades.curr.exit_name = 'Profit target'
                    backtest.trades.add_trade()
                    backtest.market.position = "FLAT"
                    self.reset()

                elif backtest.tick['Last'] >= self.stop_loss:
                    backtest.trades.curr.exit_time = backtest.tick.name
                    backtest.trades.curr.exit_price = backtest.tick['Last']
                    backtest.trades.curr.exit_name = 'Stop loss'
                    backtest.trades.add_trade()
                    backtest.market.position = "FLAT"
                    self.reset()

            elif curr_time.hour == 16 and curr_time.minute == 14 and 59 <= curr_time.second >= 30:
                    # TODO need to fix exit on close
                    backtest.trades.curr.exit_time = backtest.tick.name
                    backtest.trades.curr.exit_price = backtest.tick['Last']
                    backtest.trades.curr.exit_name = 'Exit on close'
                    backtest.trades.add_trade()
                    backtest.market.position = "FLAT"
                    self.reset()


