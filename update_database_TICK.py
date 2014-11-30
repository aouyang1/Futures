__author__ = 'MOLTRES'


import os
import datetime
import pandas as pd
from futuresdatabase import FuturesDatabase


instrument_list = ['GC', 'CL', 'ZB']

futures_db = FuturesDatabase()

for instrument in instrument_list:
    table_name = instrument + '_LAST'

    futures_db.drop_table_if_exist(table_name)

    futures_db.create_historical_table(table_name)

    rootPath = "/home/aouyang1/NinjaTrader/TickData/" + instrument
    folders = os.listdir(rootPath)

    fnames = os.listdir(rootPath)
    for fileNames in fnames:
        print fileNames
        df = pd.read_csv(rootPath + '/' + fileNames, delimiter=";", names=['Date', 'Last', 'Volume'], parse_dates=[0],
                         date_parser=lambda x: datetime.datetime.strptime(x, '%Y%m%d %H%M%S'))

        futures_db.upload_dataframe_to_table(df, table_name)

    futures_db.create_table_index(table_name, "Date")

futures_db.close_database_connection()
