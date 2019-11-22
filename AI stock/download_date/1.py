import tushare as ts
import pandas as pd

from sqlalchemy import create_engine

engine1 = create_engine("mysql+pymysql://root:123456@localhost:3306/stock?charset=utf8")
engine2 = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock?charset=utf8")

q = lambda x: pd.read_sql(x, engine2)
sql='''
SELECT
*
from
trade_cal
;
'''

df=q(sql)
print(df)
df.to_sql("trade_cal", con=engine1, if_exists='append', index=False, index_label="id")