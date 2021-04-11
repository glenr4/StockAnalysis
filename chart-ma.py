# https://medium.com/analytics-vidhya/using-plotly-for-building-candlestick-chart-for-the-stock-market-analysis-5305b48a5f75
# Has now changed to use sub plots: https://plotly.com/python/multiple-axes/

import datetime as dt
import pandas_datareader.data as web
from plotly.subplots import make_subplots

# Data
start = dt.datetime(2020,1,1)
end=dt.datetime.now()
stockSymbol = 'BTC-USD'
# stockSymbol = 'ETH-USD'

stocks = web.DataReader([stockSymbol], 'yahoo', start, end)
# display(stocks)

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

# Moving averages
stocks['maShort', stockSymbol] = stocks.Close[stockSymbol].rolling(window=10,min_periods=1).mean()
stocks['maMedium', stockSymbol] = stocks.Close[stockSymbol].rolling(window=50, min_periods=1).mean()
stocks['maLong', stockSymbol] = stocks.Close[stockSymbol].rolling(window=200, min_periods=1).mean()
stocks['maDiffMediumLong', stockSymbol] = stocks['maMedium', stockSymbol] - stocks['maLong', stockSymbol]
stocks['maDiffMediumLongChange', stockSymbol] = stocks['maDiffMediumLong', stockSymbol].diff()    # Difference from one row to the next
# display(stocks)

# Plot dictionaries
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

# Calculate trade entry and exit points
stocks['entry', stockSymbol] = ((stocks['maShort', stockSymbol] > stocks['maMedium', stockSymbol]) \
                              & (stocks['maShort', stockSymbol] > stocks['maLong', stockSymbol]) \
                              & (stocks['maDiffMediumLongChange', stockSymbol] > 0)).astype(int)

stocks['exit', stockSymbol] = (stocks['Close', stockSymbol] < stocks['maShort', stockSymbol]).astype(int)*-1
# display(stocks)

entryData={
    'x': stocks.index,
    'y': stocks['entry', stockSymbol],
    'type': 'bar',
    'marker':{'color':'black'},
    'name': 'Entry'
}

exitData={
    'x': stocks.index,
    'y': stocks['exit', stockSymbol],
    'type': 'bar',
    'marker':{'color':'red'},
    'name': 'Entry'
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


















































