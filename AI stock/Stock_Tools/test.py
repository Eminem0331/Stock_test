import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import Stock_Tools.tool_function as tf



engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
engine2 = create_engine('mysql+pymysql://root:123456@localhost/stock_data?charset=utf8', encoding='utf-8')
engine3 = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock_data?charset=utf8", encoding='utf-8')

q = lambda x: pd.read_sql(x, engine1)
sql = '''
select
a.*
from stock_data.fina_factor a join stock.stock_basic b on a.ts_code=b.ts_code
where
left(b.name,2)<>'ST'
and
left(b.name,3)<>'*ST'
and datediff(a.end_date,b.list_date)>=365
and a.end_date='2015-03-31'
;
'''
data=q(sql)
stock_list=data['ts_code']
index_list=list(data)[4:-2]
print(index_list)
print(stock_list)
# tf.Stock_Quantile_le(data,)