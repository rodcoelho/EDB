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
    # It does this in a manner identical to the way we will handle live data
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
        pass

