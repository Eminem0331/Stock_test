import tushare as ts
import pandas

ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')
df = pro.fut_daily(ts_code='M2001.DCE', start_date='20180101', end_date='20200131')

# df = pro.index_basic(market='OTH')

#df = pro.index_daily(ts_code='M.NH', start_date='20080101', end_date='20191201')
#df.to_excel('.xlsx')
print(df)