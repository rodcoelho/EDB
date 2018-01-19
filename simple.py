#!/usr/bin/env python3

import pandas as pd
import numpy as np

file = 'files/WILL5000INDFC.csv'                        # File Location
data = pd.read_csv(file, names=['date','price'])        # Create DataFrame
data = data[data.price > '0.20']                        # Get rid of rows with prices == 0 (holidays)
data['MA5'] = data['price'].rolling(5).mean()           # 5 day moving average
data['MA10'] = data['price'].rolling(10).mean()         # 10 day moving average
data['ratio'] = data['MA5']/data['MA10']                # 5MA / 10MA Ratio
data = data.dropna()                                    # Drop Non-Real Numbers
num_of_rows = (data.shape)[0]                           # Number of rows (to iterate over later)

dbuy = data[data.ratio > 1.01]
dsell = data[data.ratio < 0.99]


#while num_of_rows > 0:


#print(data.head(20))

# # How to iterate over each row
# for index, row in data.iterrows():
#     print(row['MA5'], row['MA10'])

