__author__ = 'aouyang1'

import ipdb
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
from pandas.tseries.offsets import *
from util.futuresdatabase import FuturesDatabase
import time

def timestamp_to_SQLstring(timestamp):
    return str(timestamp)[:-6]


instr_name = 'GC'
TICK_SIZE = 0.1
init_day = '2013-09-10 17:00:00'
final_day = '2014-11-30 16:59:59'

table_name = instr_name + '_LAST'
compressed_table_name = table_name + '_COMPRESSED'

start_stamp = pd.Timestamp(init_day).tz_localize('US/Central')
start_stamp_utc = start_stamp.tz_convert('utc')

final_stamp = pd.Timestamp(final_day).tz_localize('US/Central')
final_stamp_utc = final_stamp.tz_convert('utc')

futures_db = FuturesDatabase()

futures_db.drop_table_if_exist(compressed_table_name)
futures_db.create_historical_table(compressed_table_name)

df_compressed = DataFrame(columns=['Date', 'Last', 'Volume'])

while start_stamp_utc < final_stamp_utc:

    start_date = timestamp_to_SQLstring(start_stamp_utc)

    # get end of day timestamp
    end_stamp_utc = start_stamp_utc + Day() - 45*Minute()

    end_date = timestamp_to_SQLstring(end_stamp_utc)

    df = futures_db.fetch_between_dates(table_name=table_name,
                                        start_date=start_date,
                                        end_date=end_date,
                                        convert_to_float=False)

    tick = df['Last'].astype(float)

    total_ticks = df.shape[0]
    repeated_ticks = np.sum(abs(tick.diff()) <= TICK_SIZE/2.0)
    unrepeated_ticks = total_ticks - repeated_ticks

    if total_ticks > 0:
        print "{} {:.2%} compression with {}/{} ticks repeated".format(start_stamp_utc,
                                                                       repeated_ticks/float(total_ticks),
                                                                       repeated_ticks,
                                                                       total_ticks)

        date_list = ['']*unrepeated_ticks
        last_list = ['']*unrepeated_ticks
        volume_list = [0]*unrepeated_ticks

        df_daily_compressed_cnt = 0

        prev_tick = df.ix[0]
        prev_date = prev_tick.name
        prev_last = prev_tick['Last']
        prev_volume = prev_tick['Volume']

        start_time = time.time()
        for df_cnt in range(1, total_ticks):

            curr_tick = df.ix[df_cnt]
            curr_date = curr_tick.name
            curr_last = curr_tick['Last']
            curr_volume = curr_tick['Volume']

            if curr_last == prev_last:
                prev_volume += curr_volume
                prev_date = curr_date
            else:
                date_list[df_daily_compressed_cnt] = prev_date
                last_list[df_daily_compressed_cnt] = prev_last
                volume_list[df_daily_compressed_cnt] = prev_volume

                df_daily_compressed_cnt += 1
                prev_volume = curr_volume

            prev_date = curr_date
            prev_last = curr_last

        date_list[df_daily_compressed_cnt] = curr_date
        last_list[df_daily_compressed_cnt] = curr_last
        volume_list[df_daily_compressed_cnt] = curr_volume

        df_daily_compressed = DataFrame({'Date': date_list, 'Last': last_list, 'Volume': volume_list})

        df_compressed = df_compressed.append(df_daily_compressed)

    # increment to next day
    start_stamp_utc += Day()

    # if start date is Thursday 5PM CST jump to Sunday 5PM CST
    if start_stamp_utc.weekday() == 4:
        start_stamp_utc += 2*Day()

futures_db.upload_dataframe_to_table(df_compressed, compressed_table_name)
futures_db.create_table_index(compressed_table_name, "Date")
futures_db.close_database_connection()


