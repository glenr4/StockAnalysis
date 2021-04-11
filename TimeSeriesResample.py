# Courtesy of https://gist.github.com/prithwi/339f87bf9c3c37bb3188#gistcomment-2395658

import pandas as pd

def weekly(df):
    def take_first(array_like):
        return array_like[0]

    def take_last(array_like):
        return array_like[-1]

    output = df.resample('W').agg({'Open': take_first,
        'High': 'max',
        'Low': 'min',
        'Close': take_last,
        'Adj Close': take_last,
        'Volume': 'sum'}) # to put the labels to Monday

    output = output[['Open', 'High', 'Low', 'Close','Adj Close', 'Volume']]
    output.index = output.index + pd.DateOffset(days=-6)

    return output
