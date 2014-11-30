__author__ = 'MOLTRES'

import os
import datetime
from sys import stdout

import pandas as pd

from util.futuresdatabase import FuturesDatabase


table_name_list = ['ftkgc',
                   'ft_quicky',
                   'ft_quicky_base']

rootname_list = ["/home/aouyang1/Dropbox/Futures Trading/FTKGC_v5/PL",
                 "/home/aouyang1/Dropbox/Futures Trading/FT_QUICKY_v3/GC/CON1/PL",
                 "/home/aouyang1/Dropbox/Futures Trading/FT_QUICKY_v3/GC/BASE/PL"]

plrange_list = [range(13, 22, 2),
                range(11, 41),
                range(11, 41)]

col_names = ['PL', 'TradeNum', 'Instrument', 'Account', 'Strategy', 'Market_pos', 'Quantity',
             'Entry_price', 'Exit_price', 'Entry_time', 'Exit_time', 'Entry_name', 'Exit_name',
             'Profit', 'Cum_profit', 'Commission', 'MAE', 'MFE', 'ETD', 'Bars']

fdb = FuturesDatabase()

for table_name, rootname, plrange in zip(table_name_list, rootname_list, plrange_list):
    #ipdb.set_trace()
    fdb.drop_table_if_exist(table_name)

    fdb.create_PL_table(table_name)

    for PL in plrange:
        rootPath = rootname + str(PL)
        filelist = os.listdir(rootPath)

        for fname in filelist:
            try:
                df = pd.read_csv(rootPath + '/' + fname, parse_dates=[8, 9],
                             date_parser=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p'))
            except:
                df = pd.read_csv(rootPath + '/' + fname, parse_dates=[8, 9],
                             date_parser=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y %I:%M'))
                print '{} in PL {} has a different time format...'.format(fname, PL)

            try:
                df.drop('Unnamed: 19', axis=1, inplace=True)
            except:
                print '{} in PL {} has no Unnamed: 19 column...'.format(fname, PL)

            df['PL'] = PL
            cols = df.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            df = df[cols]
            df.columns = col_names

            fdb.upload_dataframe_to_table(df, table_name)

        stdout.write("\r%s" % table_name + " " + str(PL) + "/" + str(max(plrange)))
        stdout.flush()

    stdout.write("\n")
    fdb.create_table_index(table_name, "PL")

    print "---------------------"

fdb.close_database_connection()