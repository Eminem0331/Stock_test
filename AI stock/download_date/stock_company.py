import tushare as ts
import pandas as pd

from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock?charset=utf8")
# engine = create_engine("mysql+pymysql://root:123456@localhost:3306/stock?charset=utf8")
ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')
pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

exchange=['SZSE','SSE']
for i in exchange:
    try:
        print(i)
        df = pro.stock_company(exchange='SZSE',
                               fields='ts_code,exchange,chairman,manager,secretary,reg_capital,setup_date,'
                                      'province,city,introduction,website,email,office,employees,main_business,business_scope')
        print(df)
        df.to_sql("stock_company", con=engine, if_exists='append', index=False, index_label="id")
        # print('Eminem')
    except:
        print('哎哟卧槽')
        pass


