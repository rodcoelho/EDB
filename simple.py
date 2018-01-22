#!/usr/bin/env python3

import pandas as pd
import numpy as np
import math

portfolio = {'cash':1000000.0,'wilshire':{'shares': 0,'VWAP': 0.0}}

strats = {'5.10': [0, 5, 10], '5.20': [0, 5, 20], '5.30': [0,5,30]}

file = 'files/WILL5000INDFC.csv'                         # File Location
data = pd.read_csv(file, names=['date','price'])         # Create DataFrame
data = data[data.price > '0.20']                         # Get rid of rows with prices == 0 (holidays)
data['MA-A'] = data['price'].rolling(5).mean()           # 5 day moving average
data['MA-B'] = data['price'].rolling(10).mean()          # 10 day moving average
data['ratio'] = data['MA-A']/data['MA-B']                # 5MA / 10MA Ratio
data = data.dropna()                                     # Drop Non-Real Numbers
num_of_rows = (data.shape)[0]                            # Number of rows (to iterate over later)

dbuy = data[data.ratio > 1.01]
dsell = data[data.ratio < 0.99]

def update_cash_buy(portfolio,price):
    cash_to_spend = portfolio['cash']/2.0
    portfolio['cash'] = cash_to_spend
    quantity_shares_to_buy = math.floor(cash_to_spend/float(price))
    return float(quantity_shares_to_buy)

def update_shares_buy(portfolio, price, quantity):
    price_VWAP = float(portfolio['wilshire']['VWAP'])
    if price_VWAP == 0.0:
        portfolio['wilshire']['VWAP'] = float(price)
        portfolio['wilshire']['shares'] = quantity
    else:
        quantity_VWAP = float(portfolio['wilshire']['shares'])
        new_VWAPtop = (float(price) * float(quantity)) + (float(price_VWAP) * float(quantity_VWAP))
        newVWAPbottom = (float(quantity_VWAP) + float(quantity))
        portfolio['wilshire']['VWAP'] = float(new_VWAPtop) / float(newVWAPbottom)
        portfolio['wilshire']['shares'] = newVWAPbottom


last_transaction = 'SELL'
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

# calculate total returns
pnl = (portfolio['cash'] - 1000000.0) / 1000000.0
print("Returns from strategy: % {:.2f}".format(pnl*100))