from q import Que
import time
import datetime as datetime
TIME = 1 # should be hourly 10*60

from event import MarketEvent, SignalEvent, OrderEvent, FillEvent

from data import HistoricalCSV_DataHander
from strategy import BuyAndHoldStrategy
from portfolio import NaivePortfolio
from execution import SimulatedExecutionHandler

csv_dir = '/Users/rodrigocoelho/traders/EDB/csv'
symbol_list = ['IBM','TSLA','FB']
que = Que()

bars = HistoricalCSV_DataHander(events=que,csv_dir=csv_dir,symbol_list=symbol_list)
portfolio = NaivePortfolio(bars=bars, events=que,start_date=datetime.datetime.now())
broker = SimulatedExecutionHandler(events=que)

# loop
while True:
    if bars.continue_backtest is True:
        print('get new data and make event, add event to queue 111')
        bars.update_bars()

    else:
        break

    while True:
        try:
            print("get the next event in queue 222")
            event = bars.events.qget()
        except:
            print("BREAK")
            break
        else:
            if event is not None:
                if event.type == "MARKET":
                    print('send market event to strategy 333')
                    strategy = BuyAndHoldStrategy(bars=bars, events=event)
                    strategy.calculate_signals()
                elif event.type == "SIGNAL":
                    ### still need to have strategy create the event for portfolio to receive
                    print('portfolio receiving signal 555')
                    portfolio.update_signal(event)
                elif event.type == "ORDER":
                    print('broker receiving order 666')
                    broker.execute_order(event)
                elif event.type == "FILL":
                    print('portfolio being updated to reflect changes 777')
                    portfolio.update_fill(event)
                print('end of loop')
        time.sleep(TIME)