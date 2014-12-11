__author__ = 'MOLTRES'

import sqlalchemy as sqlalch
import pandas as pd
import numpy as np
from sys import stdout
import ipdb

class FuturesDatabase:

    def __init__(self, user="root", password="asdf1234", database="futures", blockSize=1000):
        self.engine = sqlalch.create_engine("mysql+mysqldb://" + user + ":" + password + "@localhost/" + database + "?charset-utf8&use_unicode=0")
        self.con = self.engine.connect()
        self.blockSize = blockSize

    def fetch_between_dates(self, table_name, start_date, end_date, convert_to_float=True, time_zone='utc'):
        sql = "SELECT * FROM " + table_name + \
              " WHERE DATE BETWEEN '" + start_date + \
              "' and '" + end_date + "';"
        df = pd.read_sql_query(sql=sql, con=self.engine, index_col='Date')

        if df.shape[0] != 0:
            if convert_to_float:
                df['Last'] = df['Last'].astype('float')

            df.index = df.index.tz_localize('utc')
            if time_zone != 'utc':
                df.index = df.index.tz_convert(time_zone)

        return df


    def drop_table_if_exist(self, table_name):
        sql = "DROP TABLE IF EXISTS " + table_name

        self.con.execute(sql)


    def create_historical_table(self, table_name):
        sql = "CREATE TABLE " + table_name +" ( \
               Date        datetime, \
               Last        char(255), \
               Volume      int)"

        self.con.execute(sql)


    def create_PL_table(self, table_name):
        sql = "CREATE TABLE " + table_name + " ( \
               PL          int, \
               TradeNum    int, \
               Instrument  char(255), \
               Account     char(255), \
               Strategy    char(255), \
               Market_pos  char(255), \
               Quantity    int, \
               Entry_price char(255), \
               Exit_price  char(255), \
               Entry_time  datetime, \
               Exit_time   datetime, \
               Entry_name  char(255), \
               Exit_name   char(255), \
               Profit      char(255), \
               Cum_profit  char(255), \
               Commission  char(255), \
               MAE         char(255), \
               MFE         char(255), \
               ETD         char(255), \
               Bars        int)"

        self.con.execute(sql)


    def upload_dataframe_to_table(self, df, table_name):
        numBlocks = int(np.ceil(df.shape[0]/float(self.blockSize)))
        for i in np.arange(numBlocks):
            df[i*self.blockSize:min((i+1)*self.blockSize-1,df.shape[0])].to_sql(name=table_name, con=self.engine, if_exists='append', index=False)
            percComplete = i/float(numBlocks)
            if percComplete > 0:
                stdout.write("\r%s" % '{:.2%}'.format(percComplete))
                stdout.flush()

        if percComplete > 0:
            stdout.write("\n")


    def create_table_index(self, table_name, column_name):
        sql = "CREATE INDEX " + column_name + " ON " + table_name + " (" + column_name + ")"

        self.con.execute(sql)


    def close_database_connection(self):
        self.con.close()