import tushare as ts
import pandas as pd

from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock?charset=utf8")
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/stock2?charset=utf8")
ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')



#
df = pro.stock_basic(exchange='',
                    fields='ts_code,symbol,name,area,industry,fullname,enname,'
                            'market,exchange,curr_type,list_status,list_date,delist_date,is_hs')


print(df)


df.to_sql("stock_basic", con=engine, if_exists='append', index=False, index_label="id")