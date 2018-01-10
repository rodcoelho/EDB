#! /usr/bin/env python3

import os, os.path
from datetime import datetime
from abc import ABCMeta, abstractmethod

import pandas as pd

from event import MarketEvent
import queue as Queue

class DataHandler:
    # __metaclass__ property to let Python know that this is an ABC (Abstract Base Class)
    __metaclass__ = ABCMeta

    # @abstractmethod decorator to let Python know that the method will be overridden in subclasses
    @abstractmethod
    def get_latest_bars(self,symbol, N=1):
        raise NotImplementedError

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError

class HistoricalCSV_DataHander(DataHandler):
    # HistoricalCSV_DataHandler is designed to read CSV files for each requested symbol
    # It does this in a manner identical to the way we will handle live data (a 'drip' method)
    def __init__(self, events, csv_dir, symbol_list):
        # The handler requires the location of the CSV and the list of symbols
        # CSV files should be named 'symbol.csv' ---> 'aapl.csv'
        # List should look like this ['aapl','ibm',...]
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        # Opens and converts the CSV into pd DataFrame

        # combined_index is the total/continuous index for all the stock symbols
        # (ex: if we first backtest data from TSLA and then backtest AAPL data, the index will continue)
        comb_index = None
        for s in self.symbol_list:
            # csv file should have NO header details (i.e. delete the row with the 'datetime', 'open', etc details)
            self.symbol_data[s] = pd.read_csv(
                os.path.join(self.csv_dir, '{}.csv'.format(s)),
                header = 0, index_col = 0,
                names = ['datetime','open','low','high','close','volume','oi']
            )

            # combine the index to 'pad' forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # set latest symbol_data to None
            self.latest_symbol_data[s] = []

        # reindex the DataFrames
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method = 'pad').iterrows()


    def _get_new_bar(self, symbol):
        # returns tuple of the latest data from the 'data feed'
        # (symbol, datetime, open, low, high, close, volume)
        for b in self.symbol_data[symbol]:
            yield tuple([symbol, datetime.strptime(b[0], "%Y-%m-%d"),
                         b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]])

    def get_latest_bars(self,symbol, N=1):
        # try: return last N data/bars from the most recent symbol_list
        # else: return N-k
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Symbol provided DNE in historical data set")
        else:
            return bars_list[-N:]

    def update_bars(self):
        # pushes the most recent data to the latest_symbol_data structure for each symbol
        for s in self.symbol_list:
            try:
                bar = self._get_new_bar(s).__next__()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())