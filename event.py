#! /usr/bin/env python3

class Event:
    # abstract Events class
    pass

class MarketEvent(Event):
    # handles new market updates
    def __init__(self):
        self.type = 'MARKET'

class SignalEvent(Event):
    # handles sending events from Strategy to Portfolio
    def __init__(self, symbol, datetime, signal_type):
        # symbol: TSLA
        # datetime: timestamp at time signal event is instantiated
        # signal_type: LONG or SHORT
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type

class OrderEvent(Event):
    # handles sending Order events to the execution handler
    def __init__(self, symbol, order_type, quantity, direction):
        # symbol: TSLA
        # quantity: int < 0
        # direction: BUY(if long) or SELL(if short)
        self.type = 'ORDER'
        self.order_type = order_type
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction

    def printorder(self):
        print("ORDER: Symbol-{}, Order-Type-{}, Quantity-{}, Direction-{}".format(
            self.symbol,
            self.order_type,
            self.quantity,
            self.direction))

class FillEvent(Event):
    # returns info from the brokerage - price and cost of buying shares
    def __init__(self, timeindex, symbol, exchange, quantity, direction, fill_cost, commission=None):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost= fill_cost
        self.commission = commission