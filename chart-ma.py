# https://medium.com/analytics-vidhya/using-plotly-for-building-candlestick-chart-for-the-stock-market-analysis-5305b48a5f75
# Has now changed to use sub plots: https://plotly.com/python/multiple-axes/

import datetime as dt
import pandas_datareader.data as web
from plotly.subplots import make_subplots
from IPython.display import display
import pandas as pd

# Settings
startingEquity = 1000.0
maShortPeriod = 10
maMediumPeriod = 50
maLongPeriod = 200

# Data
start = dt.datetime(2018,1,1)
end=dt.datetime.now()
stockSymbol = 'BTC-USD'
# stockSymbol = 'ETH-USD'

stocks = web.DataReader([stockSymbol], 'yahoo', start, end)
# display(stocks)

# Moving averages
stocks['maShort', stockSymbol] = stocks.Close[stockSymbol].rolling(window=maShortPeriod,min_periods=1).mean()
stocks['maMedium', stockSymbol] = stocks.Close[stockSymbol].rolling(window=maMediumPeriod, min_periods=1).mean()
stocks['maLong', stockSymbol] = stocks.Close[stockSymbol].rolling(window=maLongPeriod, min_periods=1).mean()
stocks['maDiffMediumLong', stockSymbol] = stocks['maMedium', stockSymbol] - stocks['maLong', stockSymbol]
stocks['maDiffMediumLongChange', stockSymbol] = stocks['maDiffMediumLong', stockSymbol].diff()    # Difference from one row to the next
# display(stocks)

# Calculate trade entry and exit points
entryExitScaling = startingEquity
stocks['entry', stockSymbol] = ((stocks['maShort', stockSymbol] > stocks['maMedium', stockSymbol]) \
                              & (stocks['maShort', stockSymbol] > stocks['maLong', stockSymbol]) \
                              & (stocks['maDiffMediumLongChange', stockSymbol] > 0)).astype(int) * entryExitScaling

stocks['exit', stockSymbol] = (stocks['Close', stockSymbol] < stocks['maShort', stockSymbol]).astype(int) * -entryExitScaling
# display(stocks)

# Calculate account equity
# We are using the Close price for all indicators, therefore when entering or closing a trade,
# we do it on the Open of the next bar
equity = []
lastEquity = startingEquity
inBullishTrade = False
buyNextPeriod = False
sellNextPeriod = False
lastPurchaseQty = 0

for row in stocks.iterrows():
    data = row[1] # Note: row[0] is date time, row[1] is the row data
    # print(data)

    # if(pd.Timestamp('2020-11-26') == row[0]):
    #     print('here')

    if (inBullishTrade):
        if(sellNextPeriod):
            # Exit trade
            equity.append(data['Open', stockSymbol] * lastPurchaseQty)
            sellNextPeriod = False
            buyNextPeriod = False
            inBullishTrade = False
        else:
            equity.append(data['Close', stockSymbol] * lastPurchaseQty)

            # Check for exit trigger
            if (data['exit', stockSymbol] == -entryExitScaling):
                sellNextPeriod = True
                buyNextPeriod = False

    else:
        if(buyNextPeriod):
            # Buy at Open
            lastPurchaseQty = equity[-1] / data['Open', stockSymbol]
            equity.append(data['Close', stockSymbol] * lastPurchaseQty) # Equity at end of day
            inBullishTrade = True
            buyNextPeriod = False
        else:
            # No change in equity
            equity.append(lastEquity)

            # Check for entry trigger
            if((data['entry', stockSymbol] == entryExitScaling) & (data['exit', stockSymbol] == 0)):
                buyNextPeriod = True
                sellNextPeriod = False

    # Save values for next iteration
    lastEquity = equity[-1]

stocks['equity', stockSymbol] = equity
display(stocks)

# Plot dictionaries
# Get the data for the stockSymbol and configure as hollow candlestick
stockData = {'x': stocks.index,
    'open': stocks[('Open', stockSymbol)],
    'high': stocks[('High', stockSymbol)],
    'low': stocks[('Low', stockSymbol)],
    'close': stocks[('Close', stockSymbol)],
    'type': 'candlestick',
    'increasing':{'fillcolor': '#FFFFFF'},
    'decreasing':{'fillcolor': '#FF0000'}
 }

maDiffMediumLongChange = {
    'x': stocks.index,
    'y': stocks['maDiffMediumLongChange', stockSymbol],
    'type': 'bar',
    'marker':{'color':'rgba(0, 127, 14, 0.3)'},
    'name': 'Medium-Long Difference Change'
}

maShort = {
    'x': stocks.index,
    'y': stocks['maShort', stockSymbol],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'purple'
    },
    'name': 'Short Moving Average'
}

maMedium = {
    'x': stocks.index,
    'y': stocks['maMedium', stockSymbol],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'red'
    },
    'name': 'Medium Moving Average'
}

maLong = {
    'x': stocks.index,
    'y': stocks['maLong', stockSymbol],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'blue'
    },
    'name': 'Long Moving Average'
}

entryData={
    'x': stocks.index,
    'y': stocks['entry', stockSymbol],
    'type': 'bar',
    'marker':{'color':'rgba(0, 0, 0, 0.3)'},
    'name': 'Entry'
}

exitData={
    'x': stocks.index,
    'y': stocks['exit', stockSymbol],
    'type': 'bar',
    'marker':{'color':'rgba(255, 0, 0, 0.3)'},
    'name': 'Exit'
}

equityData = {
    'x': stocks.index,
    'y': stocks['equity', stockSymbol],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'black'
    },
    'name': 'Account Equity'
}

# Chart with separate y-axes (secondary goes on top of primary)
fig = make_subplots(specs=[[{"secondary_y": True}]])

# First subplot
fig.add_trace(stockData, secondary_y=True)
fig.add_trace(maShort, secondary_y=True)
fig.add_trace(maMedium, secondary_y=True)
fig.add_trace(maLong, secondary_y=True)

# Second subplot
fig.add_trace(maDiffMediumLongChange, secondary_y=False)
fig.add_trace(entryData, secondary_y=False)
fig.add_trace(exitData, secondary_y=False)
fig.add_trace(equityData, secondary_y=False)

# Layout and configuration
fig.update_layout({
    'title':{
        'text': stockSymbol,
        'font':{
            'size': 25
        }
    }
})
fig.update_xaxes(showspikes=True)
fig.update_yaxes(title_text=stockSymbol, secondary_y=True)
fig.update_yaxes(title_text="EMA Difference Change", secondary_y=False)
fig.update_layout(hovermode='x')
fig.show()


















































