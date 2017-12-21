#! /usr/bin/env python3
# standard library
import os, os.path
from datetime import datetime
from abc import ABCMeta, abstractmethod
# 3rd party
import pandas as pd
# local library
from event import MarketEvent

class DataHandler:
    # __metaclass__ property to let Python know that this is an ABC (Abstract Base Class)
    __metaclass__ = ABCMeta

    # @abstractmethod decorator to let Python know that the method will be overridden in subclasses
    @abstractmethod
    def get_latest_data(self,symbol, N=1):
        raise NotImplementedError

    @abstractmethod
    def update_data(self):
        raise NotImplementedError

class HistoricalCSV_DataHander(DataHandler):
    # HistoricalCSV_DataHandler is designed to read CSV files for each requested symbol
    # It does this in a manner identical to the way we will handle live data (a 'drip' method)
    def __init__(self, events_queue, csv_dir, symbol_list):
        # The handler requires the location of the CSV and the list of symbols
        # CSV files should be named 'symbol.csv' ---> 'aapl.csv'
        # List should look like this ['aapl','ibm',...]
        self.events_queue = events_queue
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
        combined_index = None
        for symb in self.symbol_list:
            # csv file should have NO header details (i.e. delete the row with the 'datetime', 'open', etc details)
            self.symbol_data[symb] = pd.read_csv(
                os.path.join(self.csv_dir, '{}.csv'.format(symb)),
                header = 0, index_col = 0,
                names = ['datetime','open','low','high','close','volume','oi']
            )

            # combine the index to 'pad' forward values
            if combined_index is None:
                combined_index = self.symbol_data[symb].index
            else:
                combined_index.union(self.symbol_data[symb].index)

            # set latest symbol_data to None
            self.latest_symbol_data[symb] = []

        # reindex the DataFrames
        for symb in self.symbol_list:
            self.symbol_data[symb] = self.symbol_data[symb].reindex(index = combined_index, method = 'pad').interrows()


    def _get_new_data_generator(self, symbol):
        # returns tuple of the latest data from the 'data feed'
        # (symbol, datetime, open, low, high, close, volume)
        for data in self.symbol_data[symbol]:
            yield tuple([symbol, datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S"),
                         data[1][0], data[1][1], data[1][2], data[1][3], data[1][4]])

    def get_latest_data(self,symbol, N=1):
        # try: return last N data/bars from the most recent symbol_list
        # else: return N-k
        try:
            data_list = self.latest_symbol_data[symbol]
        except:
            print("Symbol provided DNE in historical data set")
        else:
            return data_list[-N:]

    def update_data(self):
        # pushes the most recent data to the latest_symbol_data structure for each symbol
        for symb in self.symbol_list:
            try:
                data = self._get_new_data_generator(symb).__next__()
            except StopIteration:
                self.continue_backtest = False
            else:
                if data is None:
                    self.latest_symbol_data[symb].append(data)
        self.event.put(MarketEvent)
