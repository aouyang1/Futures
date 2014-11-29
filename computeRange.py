__author__ = 'MOLTRES'

import time
import ipdb
import pandas as pd
from pandas.tseries.offsets import *
from futuresdatabase import FuturesDatabase
from rangebar import RangeBar
from matplotlib.finance import candlestick
import matplotlib.pyplot as plt


def timestamp_to_SQLstring(timestamp):
    return str(timestamp)[:-6]


# range bar settings
#----------------------------------
instrument = 'GC'
RANGE = 10
init_day = '2014-05-07 17:00:00'
final_day = '2014-05-8 16:59:59'
#----------------------------------
print "Running..."

table_name = instrument + '_LAST'

start_stamp = pd.Timestamp(init_day).tz_localize('US/Central')
start_stamp_utc = start_stamp.tz_convert('utc')

final_stamp = pd.Timestamp(final_day).tz_localize('US/Central')
final_stamp_utc = final_stamp.tz_convert('utc')

fdb = FuturesDatabase()
bar = RangeBar(instrument, RANGE)

while start_stamp_utc < final_stamp_utc:
    print start_stamp_utc

    start_date = timestamp_to_SQLstring(start_stamp_utc)

    # get end of day timestamp
    end_stamp_utc = start_stamp_utc + Day() - 45*Minute()

    end_date = timestamp_to_SQLstring(end_stamp_utc)

    df = fdb.fetch_between_dates(table_name=table_name, start_date=start_date, end_date=end_date)

    bar.compute_range(df)

    # increment to next day
    start_stamp_utc += Day()

    # if start date is Thursday 5PM CST jump to Sunday 5PM CST
    if start_stamp_utc.weekday()==4:
        start_stamp_utc += 2*Day()


print "Finished..."
ipdb.set_trace()
"""
#ipdb.set_trace()
BarTuple = zip(range(len(bar.Close)),
                bar.Open[::-1],
                bar.Close[::-1],
                bar.High[::-1],
                bar.Low[::-1],
                bar.Volume[::-1])
"""