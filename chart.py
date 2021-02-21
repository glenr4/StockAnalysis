# https://medium.com/codex/financial-charts-and-visuals-with-plotly-in-python-843ffa9341a9
# https://plotly.com/python/reference/candlestick/

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

# Area chart
# area_chart = px.area(stocks_close.FB, title = 'FACEBOOK SHARE PRICE (2013-2020)')
#
# area_chart.update_xaxes(title_text = 'Date')
# area_chart.update_yaxes(title_text = 'FB Close Price', tickprefix = '$')
# area_chart.update_layout(showlegend = False)
#
# area_chart.show()

# Customized Area chart
# c_area = px.area(stocks_close.FB, title = 'FACBOOK SHARE PRICE (2013-2020)')
#
# c_area.update_xaxes(
#     title_text = 'Date',
#     rangeslider_visible = True,
#     rangeselector = dict(
#         buttons = list([
#             dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
#             dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
#             dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
#             dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
#             dict(step = 'all')])))
#
# c_area.update_yaxes(title_text = 'FB Close Price', tickprefix = '$')
# c_area.update_layout(showlegend = False,
#     title = {
#         'text': 'FACEBOOK SHARE PRICE (2013-2020)',
#         'y':0.9,
#         'x':0.5,
#         'xanchor': 'center',
#         'yanchor': 'top'})
#
# c_area.show()

# candlestick chart
# candlestick = go.Figure(data = [go.Candlestick(x = stocks.index,
#                                                open = stocks[('Open',    'AMZN')],
#                                                high = stocks[('High',    'AMZN')],
#                                                low = stocks[('Low',    'AMZN')],
#                                                close = stocks[('Close',    'AMZN')])])
#
# candlestick.update_layout(xaxis_rangeslider_visible = False, title = 'AMAZON SHARE PRICE (2013-2020)')
# candlestick.update_xaxes(title_text = 'Date')
# candlestick.update_yaxes(title_text = 'AMZN Close Price', tickprefix = '$')
#
# candlestick.show()

c_ohlc = go.Figure(data = [go.Candlestick(x = stocks.index,
                                               open = stocks[('Open',    'AAPL')],
                                               high = stocks[('High',    'AAPL')],
                                               low = stocks[('Low',    'AAPL')],
                                               close = stocks[('Close',    'AAPL')],
                                                increasing={'fillcolor': '#FFFFFF'},
                                                decreasing={'fillcolor': '#FF0000'}
)])

c_ohlc.update_xaxes(
    title_text = 'Date',
    rangeslider_visible = True,
    rangeselector = dict(
        buttons = list([
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))

c_ohlc.update_layout(
    title = {
        'text': 'APPLE SHARE PRICE (2013-2020)',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
c_ohlc.update_yaxes(title_text = 'AAPL Close Price', tickprefix = '$')
c_ohlc.show()