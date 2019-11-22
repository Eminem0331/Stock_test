import pandas as pd
from sqlalchemy import create_engine
import numpy as np

engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
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
;
'''
df=q(sql)
print(list(df)[4:-2])