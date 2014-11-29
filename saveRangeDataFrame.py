__author__ = 'MOLTRES'

import time
import compRange as cr

start_time = time.time()
"""
file_name_list = cr.build_file_name_list('TickData\GC',['GC 12-13.Last.txt',
                                                        'GC 02-14.Last.txt',
                                                        'GC 04-14.Last.txt',
                                                        'GC 06-14.Last.txt',
                                                        'GC 08-14.Last.txt'])
                                                        """

file_name_list = cr.build_file_name_list('TickData\GC',['GC 04-14.Last.txt'])

print 'Adding Data to Tick DataFrame...'
df = cr.build_tick_df(file_name_list)

print 'Calculating Range Bars...'
range_bars, status = cr.compute_range_bars(df, range_size=10, tick_size=0.1)
print status

print 'Writing to csv file'
range_bars.to_csv('GC_R10_14-4_v2.csv')

print 'Done!'

end_time = time.time()

print 'Elapsed time: ', end_time - start_time

df1 = pd.read_csv('GC_R10_14-4.csv')
df2 = pd.read_csv('GC_R10_14-4_v2.csv')
print (df1 == df2).all()