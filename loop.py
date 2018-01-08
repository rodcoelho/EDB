import queue as Queue
import time
TIME = 1 # should be hourly 10*60

from event import MarketEvent, SignalEvent, OrderEvent, FillEvent

from data import HistoricalCSV_DataHander
from strategy import BuyAndHoldStrategy
from portfolio import Portfolio
from ib_execution import ExecutionHandler

event_queue = Queue.Queue()
bars = HistoricalCSV_DataHander(events_queue=None, csv_dir=None, symbol_list=['aapl', 'tsla'])  # FIXME
strategy = BuyAndHoldStrategy
portfolio = Portfolio()
execution = ExecutionHandler()

# loop
while True:
    if bars.continue_backtest is True:
        bars.update_data()
    else:
        break

    while True:
        try:
            event = events.get(block = False)

        except Queue.Empty:
            break

        else:
            if event is not None:
                print("LOOP")
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