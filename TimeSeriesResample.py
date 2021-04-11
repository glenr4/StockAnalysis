# Courtesy of https://gist.github.com/prithwi/339f87bf9c3c37bb3188#gistcomment-2395658

import pandas as pd

def weekly(df):
    output = df.resample('W').agg({
        'Open': lambda x: x[0],
        'High': 'max',
        'Low': 'min',
        'Close': lambda x: x[-1],
        'Adj Close': lambda x: x[-1],
        'Volume': 'sum'})

    output = output[['Open', 'High', 'Low', 'Close','Adj Close', 'Volume']]
    # output.index = output.index + pd.DateOffset(days=-6) # to put the labels to Monday

    return output

def monthly(df):
    output = df.resample('M').agg({
        'Open': lambda x: x[0],
        'High': 'max',
        'Low': 'min',
        'Close': lambda x: x[-1],
        'Adj Close': lambda x: x[-1],
        'Volume': 'sum'})

    output = output[['Open', 'High', 'Low', 'Close','Adj Close', 'Volume']]

    return output