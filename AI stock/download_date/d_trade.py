import tushare as ts
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock?charset=utf8")
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/stock?charset=utf8")
ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

stock_list=data['ts_code']

for n,i in enumerate(stock_list):
    try:
        print(n)
        print(i)
        df = ts.pro_bar(ts_code=str(i), adj='qfq', start_date='20000101', end_date='20191118',
                        freq='D',ma=[5, 10, 20], factors=['tor', 'vr'])
        df = df.drop_duplicates(['trade_date'], keep='first')
        print(df)
        df.to_sql("d_trade", con=engine, if_exists='append', index=False, index_label="id")
    except:
        print('eminem')




