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

# Moving averaged
avg10 = stocks.Close[stockSymbol].rolling(window=10,min_periods=1).mean()
avg50 = stocks.Close[stockSymbol].rolling(window=50, min_periods=1).mean()
avg200 = stocks.Close[stockSymbol].rolling(window=200, min_periods=1).mean()
maDiff = avg50 - avg200
maDiffChange = maDiff.diff()    # Difference from one row to the next

# Plot dictionaries
maDifference = {
    'x': stocks.index,
    'y': maDiffChange,
    'type': 'bar',
    'marker':{'color':'rgba(0, 127, 14, 0.3)'},
    'name': 'Moving Average Difference'
}

maShort = {
    'x': stocks.index,
    'y': avg10,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'purple'
    },
    'name': 'Moving Average 10'
}

maMedium = {
    'x': stocks.index,
    'y': avg50,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'red'
    },
    'name': 'Moving Average 50'
}

maLong = {
    'x': stocks.index,
    'y': avg200,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'blue'
    },
    'name': 'Moving Average 200'
}

# Chart with separate y-axes (secondary goes on top of primary)
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(stockData, secondary_y=True)
fig.add_trace(maShort, secondary_y=True)
fig.add_trace(maMedium, secondary_y=True)
fig.add_trace(maLong, secondary_y=True)

fig.add_trace(maDifference, secondary_y=False)
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


















































