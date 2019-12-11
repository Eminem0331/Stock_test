import tushare as ts
import pandas as pd

from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock?charset=utf8")
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/stock?charset=utf8")
ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

df=pro.trade_cal(exchange='SSE', start_date='20200101', end_date='20201231',is_open='')
print(df)


a=list(df['is_open'][0:len(df)-1])
a.insert(0,1)
b=list(df['cal_date'][0:len(df)-1])
b.insert(0,20000104)
print(a)
print(b)
# print(len(a))
# b=df['cal_date']
c=[]
for n,i in enumerate(a):
    if i==1:
        c.append(b[n])
    else:
        c.append(c[n-1])

# print(c)
# print(len(c))

df['pretrade_date']=c
print(df)
df.to_sql("trade_cal", con=engine, if_exists='append', index=False, index_label="id")
