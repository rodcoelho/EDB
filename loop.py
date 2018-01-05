import queue as Queue
import time
TIME = 10*60 # hourly

from event import MarketEvent, SignalEvent, OrderEvent, FillEvent

from data import HistoricalCSV_DataHander
from strategy import BuyAndHoldStrategy
from portfolio import Portfolio
from ib_execution import ExecutionHandler

event_queue = Queue.Queue()
data = HistoricalCSV_DataHander("parameter1", "parameter2", "parameter3")  # FIXME - events_queue, csv_dir, symbol_list
strategy = BuyAndHoldStrategy
portfolio = Portfolio()
execution = ExecutionHandler()

# loop
while True:
    if data.continue_backtest is True:
        data.update_data()
    else:
        break

    while True:
        try:
            event = event_queue.get(block = False)

        except Queue.Empty:
            break

        if event is not None:
            pass
            # TODO if MarketEvent
                # do something
            # TODO if SignalEvent
                # do something
            # TODO if OrderEvent
                # do something
            # TODO if FillEvent
                # do something

        time.sleep(TIME)