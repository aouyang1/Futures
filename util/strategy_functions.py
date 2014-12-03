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

def enter_long_limit(strat, limit_price):
    strat.order.limit_price = limit_price
    strat.order.order_action = "BUY"
    strat.order.order_state = "WORKING"
    strat.order.order_type = "LIMIT"
    strat.market.position = "LONG"

def enter_short_limit(strat, limit_price):
    strat.order.limit_price = limit_price
    strat.order.order_action = "SELL"
    strat.order.order_state = "WORKING"
    strat.order.order_type = "LIMIT"
    strat.market.position = "SHORT"

def set_stop_loss(strat):
    if strat.order.order_action == "SELL":
        strat.order.stop_loss = strat.order.limit_price + strat.bt.range_bar.instr.TICK_SIZE*strat.PL
    elif strat.order.order_action == "BUY":
        strat.order.stop_loss = strat.order.limit_price - strat.bt.range_bar.instr.TICK_SIZE*strat.PL
    else:
        print "order does not exist"

def set_profit_target(strat):
    if strat.order.order_action == "SELL":
        strat.order.profit_target = strat.order.limit_price - strat.bt.range_bar.instr.TICK_SIZE*strat.PL
    elif strat.order.order_action == "BUY":
        strat.order.profit_target = strat.order.limit_price + strat.bt.range_bar.instr.TICK_SIZE*strat.PL
    else:
        print "order does not exist"

def cancel_order(strat):
    strat.market.position = "FLAT"
    strat.order.reset()