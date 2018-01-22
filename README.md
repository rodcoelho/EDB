## Event Driven Backtester 

The EDB consists of two loops. The outer loop, handles incoming data and gives them an event type.
The inner event-loop continually checks for new events and then performs actions based on events types
i.e. Market, Signal, Order, or Fill types. 

#### Configuration:

Files with data should be named after ticker symbol: `AAPL.csv`, `TSLA.csv`, etc... and should be placed in 
a directory named `csv`

#### Application:

[ x ]Phase 1a: Set up environment without Event-Driven logic: Run `$ python3 simple.py`

[ x ]Phase 1b: Set up backtester environment with Basic Event-Driven functionality: Run `$ python3 loop.py`

[ _ ]Phase 2: Test new event-driven strategies to Event Driven logic