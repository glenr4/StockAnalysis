# https://medium.com/analytics-vidhya/using-plotly-for-building-candlestick-chart-for-the-stock-market-analysis-5305b48a5f75

import pandas as pd
import datetime as dt
import pandas_datareader.data as web
import plotly.express as px
import plotly.graph_objects as go

# Data
start = dt.datetime(2019,1,1)
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

avg10 = stocks.Close[stockSymbol].rolling(window=10,min_periods=1).mean()
avg50 = stocks.Close[stockSymbol].rolling(window=50, min_periods=1).mean()
avg200 = stocks.Close[stockSymbol].rolling(window=200, min_periods=1).mean()
diff = avg50 - avg200


# maDifference = {
#     'x': stocks.index,
#     'y': avg20,
#     'type': 'scatter',
#     'mode': 'lines',
#     'line': {
#         'width': 1,
#         'color': 'blue'
#     },
#     'name': 'Moving Average 20'
# }

maDifference = {
    'x': stocks.index,
    'y': diff,
    'type': 'bar',
    'marker':{'color':'green'},
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

# Chart
fig = go.Figure(data=[stockData, maDifference, maShort, maMedium, maLong],
                layout=go.Layout({
    'title':{
        'text': stockSymbol,
        'font':{
            'size': 25
        }
    },
    "yaxis": {
        "autorange": True,
        "fixedrange": False,

    }
}))
fig.show()


















































