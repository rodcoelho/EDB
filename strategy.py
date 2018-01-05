#! /usr/bin/env python3

import datetime

import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod

from event import SignalEvent
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

    def __init__(self, data, event):
        # initializes buy and hold forever strategy
        # data - the DataHandler object from data.py
        # event - the Event Queue object from event.py
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.event = event

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
        if event.type == 'MARKET':
            for s in self.symbol_list:
                data = self.data.get_latest_data(s, N=1)
                if data is not None and data != []:
                    if self.bought[s] == False:
                        # (Symbol, Datetime, Type = LONG, SHORT or EXIT)
                        signal = SignalEvent(data[0][0], data[0][1], 'LONG')
                        self.event.put(signal)
                        self.bought[s] = True