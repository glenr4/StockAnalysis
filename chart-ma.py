# https://medium.com/analytics-vidhya/using-plotly-for-building-candlestick-chart-for-the-stock-market-analysis-5305b48a5f75

import pandas as pd
import datetime as dt
import pandas_datareader.data as web
import plotly.express as px
import plotly.graph_objects as go

# Data
start = dt.datetime(2019,1,1)
end=dt.datetime.now()

stocks = web.DataReader(['FB','AMZN', 'AAPL', 'NFLX', 'GOOGL', 'MSFT'], 'yahoo', start, end)
stocks_close = pd.DataFrame(web.DataReader(['FB','AMZN', 'AAPL', 'NFLX', 'GOOGL', 'MSFT'], 'yahoo', start, end)['Close'])

# stocks.to_csv('c:/temp/stocks.csv')
stock = 'AAPL'

set1 = {'x': stocks.index,
'open': stocks[('Open',    stock)],
'high': stocks[('High',    stock)],
'low': stocks[('Low',    stock)],
'close': stocks[('Close',    stock)],
'type': 'candlestick',
'increasing':{'fillcolor': '#FFFFFF'},
'decreasing':{'fillcolor': '#FF0000'}
}

avg20 = stocks.Close[stock].rolling(window=20,min_periods=1).mean()
avg50 = stocks.Close[stock].rolling(window=50,min_periods=1).mean()
avg200 = stocks.Close[stock].rolling(window=200,min_periods=1).mean()

set2 = {
    'x': stocks.index,
    'y': avg20,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 1,
        'color': 'blue'
    },
    'name': 'Moving Average 20'
}

set3 = {
    'x': stocks.index,
    'y': avg50,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 1,
        'color': 'yellow'
    },
    'name': 'Moving Average 50'
}

set4 = {
    'x': stocks.index,
    'y': avg200,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 1,
        'color': 'black'
    },
    'name': 'Moving Average 200'
}

fig = go.Figure(data=[set1, set2, set3, set4],
                layout=go.Layout({
    'title':{
        'text': stock,
        'font':{
            'size': 25
        }
    }
}))
fig.show()