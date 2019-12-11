import tushare as ts
import pandas as pd
from sqlalchemy import create_engine
import datetime

today = (datetime.date.today()).strftime('%Y%m%d')

print(today)



engine1 = create_engine("mysql+pymysql://root:123456@localhost:3306/stock?charset=utf8")
engine2 = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock?charset=utf8")
# ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
stock_list=data['ts_code']
# df = ts.pro_bar(ts_code='000001.SZ',pro_api=pro, start_date='20180101', end_date='20181011', ma=[5, 20, 50])
# print(df)
for n,i in enumerate(stock_list):
    try:
        print(n)
        print(i)
        df = ts.pro_bar(ts_code=str(i),pro_api=pro, adj='qfq', start_date='20191010', end_date=today,
                        freq='D',ma=[5, 10, 20], factors=['tor', 'vr'])
        # print(df)
        df = df.drop_duplicates(['trade_date'], keep='first')
        df=df[df['trade_date']>='20191119']
        print(df)
        df.to_sql("d_trade", con=engine1, if_exists='append', index=False, index_label="id")
        df.to_sql("d_trade", con=engine2, if_exists='append', index=False, index_label="id")
    except:
        print('eminem')
        pass




