##Event Driven Backtester 

The EDB consists of two loops. The outer loop, handles incoming data and gives them an event type.
The inner event-loop continually checks for new events and then performs actions based on events types
i.e. Market, Signal, Order, or Fill types. 

#### Step 1:

Run `$ python3 loop.py`

Files with data should be named after ticker symbol: `AAPL.csv`, `TSLA.csv`, etc...

#### Progress:

[ x ]Phase 1: Set up backtester environment with basic event-driven functionality

[ _ ]Phase 2: Test new event-driven strategies

