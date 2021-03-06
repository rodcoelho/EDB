#!/usr/bin/env python3

import pandas as pd
import numpy as np
import math


strats = {'5.10': [0, 5, 10], '5.20': [0, 5, 20], '5.30': [0,5,30],
          '10.20': [0, 10, 20], '10.30': [0, 10, 30], '10.40': [0, 10, 40],
          '15.20': [0, 15, 20], '15.30': [0, 15, 30], '15.45': [0, 15, 45]}
            # key = 'MA1.MA2'                    MA      = Moving Average
            # value = [Returns, MA1, MA2]        Returns = At the end will reflect the strategy's return

def update_cash_buy(portfolio,price):                                   # Employing a "Buy Logic" strategy
    cash_to_spend = portfolio['cash']/2.0                               # where each buy signal
    portfolio['cash'] = cash_to_spend                                   # we will spend 50% of our total cash holdings
    quantity_shares_to_buy = math.floor(cash_to_spend/float(price))
    return float(quantity_shares_to_buy)

def update_shares_buy(portfolio, price, quantity):                      # Here we take the VWAP to know the
    price_VWAP = float(portfolio['wilshire']['VWAP'])                   # average price we paid per share
    if price_VWAP == 0.0:
        portfolio['wilshire']['VWAP'] = float(price)
        portfolio['wilshire']['shares'] = quantity
    else:
        quantity_VWAP = float(portfolio['wilshire']['shares'])
        new_VWAPtop = (float(price) * float(quantity)) + (float(price_VWAP) * float(quantity_VWAP))
        newVWAPbottom = (float(quantity_VWAP) + float(quantity))
        portfolio['wilshire']['VWAP'] = float(new_VWAPtop) / float(newVWAPbottom)
        portfolio['wilshire']['shares'] = newVWAPbottom

for key, value in strats.items():
    portfolio = {'cash': 1000000.0,
                 'wilshire': {'shares': 0, 'VWAP': 0.0}}
    file = 'files/WILL5000INDFC.csv'                                    # File Location
    data = pd.read_csv(file, names=['date', 'price'])                   # Create DataFrame
    data = data[data.price > '0.20']                                    # Get rid of rows with prices == 0 (holidays)
    data['MA-A'] = data['price'].rolling(value[1]).mean()               # MA1
    data['MA-B'] = data['price'].rolling(value[2]).mean()               # MA2
    data['ratio'] = data['MA-A'] / data['MA-B']                         # MA1 / MA2 Ratio
    data = data.dropna()                                                # Drop Non-Real Numbers
    num_of_rows = (data.shape)[0]                                       # Number of rows (to iterate over later)
    dbuy = data[data.ratio > 1.01]                                      # if ratio > 1, it's a buy signal
    dsell = data[data.ratio < 0.99]                                     # if ratio < 1, it's a sell signal

    last_transaction = 'SELL'                                           # keeps track of last transaction
    for i, (index, row) in enumerate(data.iterrows()):
        # BUY signal
        if row['ratio'] > 1.01 and last_transaction == 'SELL':
            # subtract cash and get quantity to buy
            quantity = float(update_cash_buy(portfolio,row['price']))
            # update portfolio - add quantity and get new VWAP in portfolio
            update_shares_buy(portfolio,float(row['price']),quantity)
            last_transaction = 'BUY'

        # SELL signal
        elif row['ratio'] < .999 and last_transaction == 'BUY':
            # get rid of half of shares
            share_quantity_to_sell = portfolio['wilshire']['shares']//2
            portfolio['wilshire']['shares'] = share_quantity_to_sell
            # add cash
            current_cash = float(portfolio['cash'])
            new_income = share_quantity_to_sell * float(row['price'])
            current_cash += float(new_income)
            portfolio['cash'] = float(current_cash)
            last_transaction = 'SELL'

        # if last item in dataframe, sell everything to see returns
        elif i == len(data) - 1:
            share_quantity_to_sell = portfolio['wilshire']['shares']
            current_cash = float(portfolio['cash'])
            new_income = share_quantity_to_sell * float(row['price'])
            current_cash += new_income
            portfolio['cash'] = float(current_cash)
            portfolio['wilshire']['shares'] = 0
            strats[key][0] = (portfolio['cash'] - 1000000.0) / 1000000.0

strategy_returns_sort = []
for keys, values in strats.items():
    strategy_returns_sort.append((keys, values[0] * 100))
strategy_returns_sort.sort(key=lambda tup: tup[1], reverse=True)
for tup in strategy_returns_sort:
    print("Returns from {} strategy: {:.2f}% ".format(tup[0], tup[1]))