# We will be assessing the performance of a strategy post-backtest using the equity curve DataFrame from the Portfolio object
# We use the Sharpe ratio to assess risk - Sharpe ratio is a measure of risk to reward
# It has a single parameter, that of the number of periods to adjust for when scaling up to the annualised value.
# Usually this value is set to 252, which is the number of trading days in the US per year.
PERIODS = 252 #days
# However, if your strategy trades within the hour you need to adjust the Sharpe to correctly annualise it.
# Thus you need to set periods to 252∗6.5=1638252∗6.5=1638, which is the number of US trading hours within a year.
# If you trade on a minutely basis, then this factor must be set to 252∗6.5∗60=98280252∗6.5∗60=98280.

import numpy as np
import pandas as pd

def create_sharpe_ratio(returns, periods = PERIODS):
    # ratio characterises how much risk (as defined by asset path standard deviation) is being taken per unit of return
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(equity_curve):
    # the "drawdown" is defined as the largest peak-to-trough drop along an equity curve
    # Calculate the largest peak-to-trough drawdown of the PnL curve as well as the duration of the drawdown.
    # returns maximum drawdown AND maximum drawdown duration

    # calculate the cumulative returns curve
    # then set the High Water Mark
    # then create the drawdown and duration series
    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index = eq_idx)
    duration = pd.Series(index = eq_idx)

    # loop over the index range
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], equity_curve[t])
        hwm.append(cur_hwm)
        drawdown[t] = hwm[t] - equity_curve[t]
        duration[t] = 0 if drawdown[t] == 0 else duration[t-1] + 1
    return drawdown.max(), duration.max()

