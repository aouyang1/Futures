__author__ = 'aouyang1'


def cross_above(dataseries, threshold):
    if len(dataseries) < 2:
        return False
    else:
        return dataseries[0] > threshold and dataseries[1] <= threshold

def cross_below(dataseries, threshold):
    if len(dataseries) < 2:
        return False
    else:
        return dataseries[0] < threshold and dataseries[1] >= threshold

def enter_long_limit(bt, limit_price):
    bt.order.limit_price = limit_price
    bt.order.order_action = "BUY"
    bt.order.order_state = "WORKING"
    bt.order.order_type = "LIMIT"
    bt.market.position = "LONG"

def enter_short_limit(bt, limit_price):
    bt.order.limit_price = limit_price
    bt.order.order_action = "SELL"
    bt.order.order_state = "WORKING"
    bt.order.order_type = "LIMIT"
    bt.market.position = "SHORT"

def set_stop_loss(bt, ticks):
    if bt.order.order_action == "SELL":
        bt.order.stop_loss = bt.order.limit_price + bt.range_bar.instr.TICK_SIZE*ticks
    elif bt.order.order_action == "BUY":
        bt.order.stop_loss = bt.order.limit_price - bt.range_bar.instr.TICK_SIZE*ticks
    else:
        print "order does not exist"

def set_profit_target(bt, ticks):
    if bt.order.order_action == "SELL":
        bt.order.profit_target = bt.order.limit_price - bt.range_bar.instr.TICK_SIZE*ticks
    elif bt.order.order_action == "BUY":
        bt.order.profit_target = bt.order.limit_price + bt.range_bar.instr.TICK_SIZE*ticks
    else:
        print "order does not exist"

def cancel_order(bt):
    bt.market.position = "FLAT"
    bt.order.reset()