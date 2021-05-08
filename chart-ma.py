# https://medium.com/analytics-vidhya/using-plotly-for-building-candlestick-chart-for-the-stock-market-analysis-5305b48a5f75
# Has now changed to use sub plots: https://plotly.com/python/multiple-axes/

# TODO: use this charting package instead, which has automatic y-axis scaling: https://github.com/highfestiva/finplot

import datetime as dt
import pandas_datareader.data as web
from plotly.subplots import make_subplots
from IPython.display import display
import pandas as pd
import TimeSeriesResample as tsr
import plotly.graph_objects as go
import numpy as np

# Settings
start = dt.datetime(2010,1,1)   # dt.datetime(2019,1,1)
tradeStart = dt.datetime(2011,1,1) # equal to or after start
end=dt.datetime.now()

# stockSymbol = 'SPY'
# stockSymbol = 'BTC-USD'
stockSymbol = 'TAN'
# stockSymbol = 'TRX-USD'
# stockSymbol = 'ETH-USD'
# stockSymbol = 'XRP-USD'
# stockSymbol = '^AXJO' # ASX200
# stockSymbol = 'GC=F'  # Gold Jun 21 (GC=F)
# stockSymbol = 'GLD'  # SPDR Gold Shares
# stockSymbol = 'SYS-USD'
# stockSymbol = '^TNX'    # US 10 year bond yield


startingEquity = 100.0
maShortPeriod = 10
maMediumPeriod = 50
maLongPeriod = 200
timePeriod = 'weekly' # daily, weekly or monthly
trailingStopPercent = 15.0

# Get data
stocks = web.DataReader(stockSymbol, 'yahoo', start, end)
if(timePeriod == 'weekly'):
    stocks = tsr.weekly(stocks)
if(timePeriod == 'monthly'):
    stocks = tsr.monthly(stocks)

# Moving averages
# TODO: use EMAs instead
stocks['maShort'] = stocks['Close'].rolling(window=maShortPeriod,min_periods=maShortPeriod).mean()
stocks['maMedium'] = stocks['Close'].rolling(window=maMediumPeriod, min_periods=maMediumPeriod).mean()
stocks['maLong'] = stocks['Close'].rolling(window=maLongPeriod, min_periods=maLongPeriod).mean()
stocks['maDiffMediumLong'] = stocks['maMedium'] - stocks['maLong']
stocks['maDiffMediumLongChange'] = stocks['maDiffMediumLong'].diff()    # Difference from one row to the next
stocks['maDiffShortMedium'] = stocks['maShort'] - stocks['maMedium']
stocks['maDiffShortMediumChange'] = stocks['maDiffShortMedium'].diff()    # Difference from one row to the next
# display(stocks)


# Calculate trade entry and exit points
stocks['entryTrigger1'] = (stocks['Close'] > stocks['maMedium'])
stocks['entryTrigger2'] = (stocks['maMedium'] >= (stocks['maMedium'].shift(1)))

stocks['entryTrigger'] = stocks['entryTrigger1'] & stocks['entryTrigger2']
entryTriggerText = "stocks['Close'] > stocks['maMedium'] and increasing stocks['maMedium']"

# Stop loss before is one possible exit, Trailing Stop gets applied after to give exitTrigger
stocks['stopLoss'] = (stocks['Close'] < stocks['maMedium'])
exitTriggerText = "stopLoss: stocks['Close'] < stocks['maMedium'] OR Trailing Stop {}%".format(trailingStopPercent)

# Trailing Stop
## To implement this, need to add a column to know when we are in a trade. The exitTrigger below
# is now going to be the Stop Loss. Then we can calculate when we are in a trade, calculate the
# Trailing Stop, then calculate the actual exitTrigger from either one signalling an exit.
# Trailing Stop is key for getting out early when the price turns.
# stocks['trailing_stop'] =
# https://wiki.python.org/moin/BitwiseOperators
stocks['inTrade'] = False
stocks['inTrade'] = ((stocks['entryTrigger'].shift(1).fillna(False) | stocks['inTrade'].shift(1).fillna(False)) \
                    & (~(stocks['stopLoss'].shift(1).fillna(False))))

# Could not figure out a way to use vector operations to calculate Trailing Stop
trailingStop = []
lastTrailingStop = 0.0
for row in stocks.iterrows():
    data = row[1] # Note: row[0] is date time, row[1] is the row data

    if data['inTrade']:
        if data['High'] > lastTrailingStop:
            trailingStop.append(data['High'])
            lastTrailingStop = data['High']
        else:
            trailingStop.append(lastTrailingStop)
    else:
        trailingStop.append(0.0)
        lastTrailingStop = 0.0

stocks['trailingStop'] = np.asarray(trailingStop) * (100.0 - trailingStopPercent)/100.0

# Exit Trigger
stocks['exitTrigger'] = stocks['stopLoss'] | (stocks['Close'] < stocks['trailingStop'])

# Calculate account equity
# We are using the Close price for all indicators, therefore when entering or closing a trade,
# we do it on the Open of the next bar
equity = []
lastEquity = startingEquity
inBullishTrade = False
buyNextPeriod = False
sellNextPeriod = False
lastPurchaseQty = 0
tradeCount = 0
firstTradeDayData = None

annotations = []
def addEntryArrow(date, price):
    annotations.append(
        {
            'x': date,
            'y': price['Low'],
            'xref': 'x',
            'yref': 'y2', # use candle's axis
            'showarrow': True,
            'arrowhead': 1,
            'arrowwidth': 3,
            'arrowcolor': 'black',
            'ax': 0,
            'ay': 40,
            'yshift': -10
        }
    )

def addExitArrow(date, price):
    annotations.append(
        {
            'x': date,
            'y': price['High'],
            'xref': 'x',
            'yref': 'y2',  # use candle's axis
            'showarrow': True,
            'arrowhead': 1,
            'arrowwidth': 3,
            'arrowcolor': 'black',
            'ax': 0,
            'ay': -40,
            'yshift': 10
        }
    )

for row in stocks.iterrows():
    if(row[0] > tradeStart):

        data = row[1] # Note: row[0] is date time, row[1] is the row data
        if firstTradeDayData is None:
            firstTradeDayData = row[1]
        # print(data)

        if (inBullishTrade):
            if(sellNextPeriod):
                # Exit trade
                equity.append(data['Open'] * lastPurchaseQty)
                sellNextPeriod = False
                buyNextPeriod = False
                inBullishTrade = False

                addExitArrow(row[0], row[1])

            else:
                equity.append(data['Close'] * lastPurchaseQty)

                # Check for exit trigger
                if (data['exitTrigger']):
                    sellNextPeriod = True
                    buyNextPeriod = False

        else:
            if(buyNextPeriod):
                # Buy at Open
                lastPurchaseQty = equity[-1] / data['Open']
                equity.append(data['Close'] * lastPurchaseQty) # Equity at end of day
                inBullishTrade = True
                buyNextPeriod = False
                tradeCount += 1

                addEntryArrow(row[0], row[1])
            else:
                # No change in equity
                equity.append(lastEquity)

                # Check for entry trigger
                if ((data['entryTrigger']) & (not data['exitTrigger'])):
                    buyNextPeriod = True
                    sellNextPeriod = False

        # Save values for next iteration
        lastEquity = equity[-1]
    else:
        # Haven't started trading yet
        equity.append(startingEquity)


stocks['equity'] = equity
# display(stocks)

# Return on Investment
roi = round(((stocks['equity'][-1] - startingEquity) / startingEquity) * 100, 2)
buyHoldRoi = round(((stocks['Close'][-1] - firstTradeDayData['Open']) / firstTradeDayData['Open']) * 100, 2)

print("Summary: {}% return on investment after {} trades".format(roi, tradeCount))
print("Buy and hold return on investment {}%".format(buyHoldRoi))

# Plot dictionaries
# Get the data for the stockSymbol and configure as hollow candlestick
stockData = {'x': stocks.index,
    'open': stocks['Open'],
    'high': stocks['High'],
    'low': stocks['Low'],
    'close': stocks['Close'],
    'type': 'candlestick',
    'increasing':{'fillcolor': '#FFFFFF'},
    'decreasing':{'fillcolor': '#FF0000'},
    'name': 'Price'
 }

maDiff1 = {
    'x': stocks.index,
    'y': stocks['maDiffMediumLongChange'],
    'type': 'bar',
    'marker':{'color':'blue'},
    'name': 'Medium-Long Difference Change'
}

maDiff2= {
    'x': stocks.index,
    'y': stocks['maDiffShortMediumChange'],
    'type': 'bar',
    'marker':{'color':'red'},
    'name': 'Short-Medium Difference Change'
}

# maShort = {
#     'x': stocks.index,
#     'y': stocks['maShort'],
#     'type': 'scatter',
#     'mode': 'lines',
#     'line': {
#         'width': 2,
#         'color': 'purple'
#     },
#     'name': 'Short Moving Average ({})'.format(maShortPeriod)
# }
# maShort = {
#     'x': stocks.index,
#     'y': stocks['inTrade'].astype(int)*50,
#     'type': 'scatter',
#     'mode': 'lines',
#     'line': {
#         'width': 2,
#         'color': 'purple'
#     },
#     'name': 'inTrade'
# }
maShort = {
    'x': stocks.index,
    'y': stocks['trailingStop'],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'purple'
    },
    'name': 'trailingStop'
}

maMedium = {
    'x': stocks.index,
    'y': stocks['maMedium'],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'red'
    },
    'name': 'Medium Moving Average ({})'.format(maMediumPeriod)
}


maLong = {
    'x': stocks.index,
    'y': stocks['maLong'],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'blue'
    },
    'name': 'Long Moving Average ({})'.format(maLongPeriod)
}

equityData = {
    'x': stocks.index,
    'y': stocks['equity'],
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
fig.add_trace(maDiff2, secondary_y=False)
fig.add_trace(maDiff1, secondary_y=False)
fig.add_trace(equityData, secondary_y=False)

def formatDate(date, separator='/'):
    return "{}{}{}{}{}".format(date.strftime("%d"), separator, date.strftime("%m"), separator, date.strftime("%Y"))
def formatDateTime(date, separator='/', timeSeparator=':'):
    return "{}{}{}{}{}_{}{}{}".format(date.strftime("%d"), separator, date.strftime("%m"), separator, date.strftime("%Y"), date.strftime("%H"), timeSeparator, date.strftime("%M"))


# Layout and configuration
dateSubtitle = "{} - {}".format(formatDate(tradeStart), formatDate(end))
roiSubtitle = "ROI: {}% from {} trades - Buy & Hold ROI: {}%".format(roi, tradeCount, buyHoldRoi)


fig.update_layout({
    'title':{
        'text': "{} ({})<br><span style='font-size: 18px'>{}<br>{}</span><br><span style='font-size: 14px'>Entry: {}<br>Exit: {}</span>" \
            .format(stockSymbol, timePeriod, dateSubtitle, roiSubtitle, entryTriggerText, exitTriggerText),
        'font':{
            'size': 25
        }
    },
    'annotations': annotations
})
fig.update_xaxes(showspikes=True)
fig.update_yaxes(title_text=stockSymbol, secondary_y=True)
fig.update_yaxes(title_text="Equity ($)", secondary_y=False)
# fig.update_layout(hovermode='x')
fig.show()

# Save chart
fig.write_html("export/{}_ROI{}_BHROI{}_Start{}_End{}.html".format(stockSymbol, roi, buyHoldRoi, formatDate(start, '-'), formatDateTime(end, '-', '-')))
















































