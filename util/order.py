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
        if self.order_type == "MARKET":
            pass
