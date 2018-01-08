#! /usr/bin/env python3

import datetime

import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod

from event import SignalEvent, MarketEvent
import queue as Queue

class Strategy:
    # abstract base class
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("should implement calculate_signals()")

class BuyAndHoldStrategy(Strategy):
    # simplest of strategies - it goes LONG on all symbols as soon as data comes in and never sells
    # used as a benchmark to test success of other strategies

    def __init__(self, bars, events):
        # initializes buy and hold forever strategy
        # data - the DataHandler object from data.py
        # event - the Event Queue object from event.py
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events

        # Once buy and hold signal is given, these are set to True
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        # this adds keys to the bought dictionary for all symbols
        # symbols values are all False
        # once bought, the value change to True
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def calculate_signals(self):
        if self.events.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=1)
                if bars is not None and bars != []:
                    if self.bought[s] == False:
                        # (Symbol, Datetime, Type = LONG, SHORT or EXIT)
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG')
                        self.events.put(signal)
                        self.bought[s] = True