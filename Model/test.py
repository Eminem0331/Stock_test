import tushare as ts
import pandas as pd

ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')


# fina_indicator = pro.fina_indicator( ts_code='000009.SZ', start_date='20100101', end_date='20190801')
# balancesheet = pro.balancesheet(ts_code='000009.SZ', start_date='20100101', end_date='20190801')
# income = pro.income(ts_code='000009.SZ', start_date='20100101', end_date='20190801')
#
# d_trade = ts.pro_bar(pro_api=pro,ts_code='000009.SZ', adj='qfq', start_date='20101001', end_date='20190801',freq='D',
#                     ma=[5,10,20],factors=['tor', 'vr'])
#
df = pro.daily_basic(ts_code='000009.SZ', trade_date='20181228')
print(df)