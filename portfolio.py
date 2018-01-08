# Portfolio's Goal: to keep track of all current market positions and the market value of the positions (known as the "holdings")
# 2ndly: Risk and position sizing techniques

import datetime
from math import floor
from abc import ABCMeta, abstractmethod

import numpy as np
import pandas as pd

import queue as Queue
from event import FillEvent, OrderEvent
from performance import create_sharpe_ratio, create_drawdowns

class Portfolio:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_signal(self, event):
        # responds to SignalEvent to generate new orders based on portfolio logic
        raise NotImplementedError("Should implement update_signal")

    @abstractmethod
    def update_fill(self, event):
        # updates portfolio's current positions and holdings from the FillEvent
        raise NotImplementedError("Should implement update_fill()")

class NaivePortfolio(Portfolio):
    #  NaivePortfolio class is designed to handle position sizing and current holdings,
    # and will carry out trading orders in a "dumb" manner
    # It will simply send orders directly to the brokerage with a predetermined fixed quantity size
    # irrespective of cash held.
    def __init__(self, bars, events, start_date, initial_capital = 100000.0):
        self.bars = bars                             # DataHandler object w/current market data
        self.events = events                           # Event Queue object
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date                 # Start date of portfolio
        self.initial_capital = initial_capital       # Starting capital

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict( (k,v) for k,v in [(s, 0) for s in self.symbol_list])

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def construct_all_positions(self):
        # constructs all positions list using start_date to determine when the time index will begin
        d = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        # constructs the holdings list using the start_date to determine when the time index will begin
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commision'] = 0.0
        d['total'] = self.initial_capital
        return[d]

    def construct_current_holdings(self):
        # constructs the dict that will hold the instantaneous value of the portfolio across all symbols
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    def update_timeindex(self,event):
        # adds a new record to the positions matrix for the current market data at current price
        # employs MarketEvent from events queue
        bars = {}
        for sym in self.symbol_list:
            bars[sym] = self.bars.get_latest_data(sym, N=1)

        # update positions
        # dp = dictionary of positions
        dp = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dp['datetime'] = bars[self.symbol_list[0]][0][1]

        for s in self.symbol_list:
            dp[s] = self.current_positions[s]

        # append current positions
        self.all_positions.append(dp)

        # update holdings
        # dh = dictionary of holdings
        dh = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dh['datetime'] = bars[self.symbol_list[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # approximation to real market value
            market_value = self.current_positions[s] * bars[s][0][5]
            dh[s] = market_value
            dh['total'] += market_value

        # append the current holdings
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        # determines whether a FillEvent is a Buy or a Sell
        # then updates the current_positions dictionary accordingly by adding/subtracting the correct quantity of shares

        #check whether fill is buy or sell:
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        # determines whether FillEvent is Buy or Sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # then updates holdings list with new quantities
        fill_cost = self.bars.get_latest_data(fill.symbol)[0][5]
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        # updates portfolio current positions and holdings from FillEvent
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        # simplest form of dealing with an OrderEvent
        # standard quantity of sizing (eg. buy/sell 100 shares each time)

        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength

        mkt_quantity = floor(100 * strength)
        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order

    def update_signal(self, event):
        # responds to SignalEvent to generate new orders based on portfolio 'logic'
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        # simply creates a returns stream, useful for performance calculation
        # then normalises the equity curve to be percentage based
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace = True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        # creates a list of summary statistics for the portfolio (ie. sharpie and markdown info)
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        max_dd, dd_duration = create_drawdowns(pnl)

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        return stats