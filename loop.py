from q import Que
import time
import datetime as datetime
TIME = 1 # should be hourly 10*60

from event import MarketEvent, SignalEvent, OrderEvent, FillEvent

from data import HistoricalCSV_DataHander
from strategy import BuyAndHoldStrategy
from portfolio import NaivePortfolio
from ib_execution import ExecutionHandler

csv_dir = '/Users/rodrigocoelho/traders/EDB/csv'
symbol_list = ['IBM','TSLA','FB']
que = Que()

bars = HistoricalCSV_DataHander(events=que,csv_dir=csv_dir,symbol_list=symbol_list)
strategy = BuyAndHoldStrategy(bars=bars,events=que)
portfolio = NaivePortfolio(bars=bars, events=que,start_date=datetime.datetime.now())
broker = ExecutionHandler()

# loop
while True:
    if bars.continue_backtest is True:
        bars.update_bars()

    else:
        break

    while True:
        try:
            print("GET BARS")
            event = bars.events.qget()
        except:
            print("BREAK")
            break
        else:
            if event is not None:
                print("LOOP")
                if event.type == "MARKET":
                    strategy.calculate_signals()
                    portfolio.update_timeindex(event)
                elif event.type == "SIGNAL":
                    portfolio.update_signal(event)
                elif event.type == "ORDER":
                    broker.execute_order(event)
                elif event.type == "FILL":
                    portfolio.update_fill(event)
        time.sleep(TIME)