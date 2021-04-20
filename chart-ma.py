# https://medium.com/analytics-vidhya/using-plotly-for-building-candlestick-chart-for-the-stock-market-analysis-5305b48a5f75
# Has now changed to use sub plots: https://plotly.com/python/multiple-axes/

import datetime as dt
import pandas_datareader.data as web
from plotly.subplots import make_subplots
from IPython.display import display
import pandas as pd
import TimeSeriesResample as tsr
import plotly.graph_objects as go

# Settings
start = dt.datetime(2019,1,1)
end=dt.datetime.now()
tradeStart = dt.datetime(2020,12,1) # dt.datetime(2020,10,14) # equal to or after start
stockSymbol = 'BTC-USD'
# stockSymbol = 'TRX-USD'
# stockSymbol = 'ETH-USD'
# stockSymbol = 'XRP-USD'
# stockSymbol = '^AXJO' # ASX200
startingEquity = 1000.0
maShortPeriod = 10
maMediumPeriod = 50
maLongPeriod = 200
timePeriod = 'daily' # daily, weekly or monthly
exportData = False

# Get data
stocks = web.DataReader(stockSymbol, 'yahoo', start, end)
if(timePeriod == 'weekly'):
    stocks = tsr.weekly(stocks)
if(timePeriod == 'monthly'):
    stocks = tsr.monthly(stocks)

# Moving averages
stocks['maShort'] = stocks['Close'].rolling(window=maShortPeriod,min_periods=maShortPeriod).mean()
stocks['maMedium'] = stocks['Close'].rolling(window=maMediumPeriod, min_periods=maMediumPeriod).mean()
stocks['maLong'] = stocks['Close'].rolling(window=maLongPeriod, min_periods=maLongPeriod).mean()
stocks['maDiffMediumLong'] = stocks['maMedium'] - stocks['maLong']
stocks['maDiffMediumLongChange'] = stocks['maDiffMediumLong'].diff()    # Difference from one row to the next
stocks['maDiffShortMedium'] = stocks['maShort'] - stocks['maMedium']
stocks['maDiffShortMediumChange'] = stocks['maDiffShortMedium'].diff()    # Difference from one row to the next
# display(stocks)

# Calculate trade entry and exit points
entryExitScaling = startingEquity
stocks['entryTrigger'] = ((stocks['maShort'] > stocks['maMedium']) \
                              & (stocks['maShort'] > stocks['maLong']) \
                              & (stocks['maDiffMediumLongChange'] > 0)).astype(int) * entryExitScaling

stocks['exitTrigger'] = (stocks['Close'] < stocks['maShort']).astype(int) * -entryExitScaling
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
tradeCounter = 0
firstTradeDayData = None

for row in stocks.iterrows():
    if(row[0] > tradeStart):

        data = row[1] # Note: row[0] is date time, row[1] is the row data
        if firstTradeDayData is None:
            firstTradeDayData = row[1]
        # print(data)

        # if(pd.Timestamp('2020-11-26') == row[0]):
        #     print('here')

        if (inBullishTrade):
            if(sellNextPeriod):
                # Exit trade
                equity.append(data['Open'] * lastPurchaseQty)
                sellNextPeriod = False
                buyNextPeriod = False
                inBullishTrade = False
            else:
                equity.append(data['Close'] * lastPurchaseQty)

                # Check for exit trigger
                if (data['exitTrigger'] == -entryExitScaling):
                    sellNextPeriod = True
                    buyNextPeriod = False

        else:
            if(buyNextPeriod):
                # Buy at Open
                lastPurchaseQty = equity[-1] / data['Open']
                equity.append(data['Close'] * lastPurchaseQty) # Equity at end of day
                inBullishTrade = True
                buyNextPeriod = False
                tradeCounter += 1
            else:
                # No change in equity
                equity.append(lastEquity)

                # Check for entry trigger
                if((data['entryTrigger'] == entryExitScaling) & (data['exitTrigger'] == 0)):
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

print("Summary: {}% return on investment after {} trades".format(roi, tradeCounter))
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

maDiffMediumLongChange = {
    'x': stocks.index,
    'y': stocks['maDiffMediumLongChange'],
    'type': 'bar',
    'marker':{'color':'rgba(0, 127, 14, 0.3)'},
    'name': 'Medium-Long Difference Change'
}

maDiffShortMediumChange= {
    'x': stocks.index,
    'y': stocks['maDiffShortMediumChange'],
    'type': 'bar',
    'marker':{'color':'rgba(0, 127, 255, 0.3)'},
    'name': 'Short-Medium Difference Change'
}

maShort = {
    'x': stocks.index,
    'y': stocks['maShort'],
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
    'y': stocks['maMedium'],
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
    'y': stocks['maLong'],
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
    'y': stocks['entryTrigger'],
    'type': 'bar',
    'marker':{'color':'rgba(0, 0, 0, 0.3)'},
    'name': 'Entry Trigger'
}

exitData={
    'x': stocks.index,
    'y': stocks['exitTrigger'],
    'type': 'bar',
    'marker':{'color':'rgba(255, 0, 0, 0.3)'},
    'name': 'Exit Trigger'
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
fig.add_trace(maDiffShortMediumChange, secondary_y=False)
fig.add_trace(maDiffMediumLongChange, secondary_y=False)
fig.add_trace(entryData, secondary_y=False)
fig.add_trace(exitData, secondary_y=False)
fig.add_trace(equityData, secondary_y=False)

def formatDate(dt):
    return "{}/{}/{}".format(dt.strftime("%d"), dt.strftime("%m"), dt.strftime("%Y"))


# Layout and configuration
dateSubtitle = "{} - {}".format(formatDate(tradeStart), formatDate(end))
roiSubtitle = "ROI: {}% - Buy & Hold ROI: {}%".format(roi, buyHoldRoi)
fig.update_layout({
    'title':{
        'text': "{} ({})<br><span style='font-size: 18px'>{}<br>{}</span>".format(stockSymbol, timePeriod, dateSubtitle, roiSubtitle),
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

# Write to excel
if(exportData):
    stocks.to_csv("export/{}_{}_short{}_med{}_long{}.csv".format(stockSymbol, timePeriod, maShortPeriod, maMediumPeriod, maLongPeriod))
















































