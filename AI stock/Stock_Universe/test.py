import pandas as pd
from sqlalchemy import create_engine
import numpy as np

engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
engine2 = create_engine('mysql+pymysql://root:123456@localhost/stock_data?charset=utf8', encoding='utf-8')
engine3 = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock_data?charset=utf8")


def get_factor_data(date,engine):
    q = lambda x: pd.read_sql(x, engine)
    sql = '''
    select
    a.*
    from stock_data.fina_factor a join stock.stock_basic b on a.ts_code=b.ts_code
    where
    left(b.name,2)<>'ST'
    and
    left(b.name,3)<>'*ST'
    and datediff(a.end_date,b.list_date)>=365
    and a.end_date='{}'
    ;
    '''.format(date)
    data=q(sql)

    return data


def rule(data,index,rule,Threshold):
    if rule == '=':
        re = data[data[index]==Threshold]
    elif rule == '>':
        re = data[data[index] > Threshold]
    elif rule == '>=':
        re = data[data[index] >= Threshold]
    elif rule == '<':
        re = data[data[index] < Threshold]
    elif rule == '<=':
        re = data[data[index] <= Threshold]
    return re

def my_universe(data,factor_list,rule_list,Threshold_list):
    for i in range(len(factor_list)):
        data=rule(data,factor_list[0],rule_list[0],Threshold_list[0])
    re=data
    return re





