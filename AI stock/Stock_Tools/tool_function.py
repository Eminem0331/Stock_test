import pandas as pd
from sqlalchemy import create_engine
import numpy as np


def Stock_Quantile_qe(data, index, quantile, date):
    df = data[data['end_date'] == date]
    a = df[index].quantile(quantile)
    re = df[df[index] <= a]['ts_code']
    return re


def Stock_Quantile_le(data, index, quantile, date):
    df = data[data['end_date'] == date]
    a = df[index].quantile(quantile)
    re = df[df[index] > a]['ts_code']
    return re


def close_sql(ts_code, date1, date2, engine):
    engine1 = engine
    q = lambda x: pd.read_sql(x, engine1)
    sql = '''
     SELECT
     ts_code,close,trade_date
       FROM d_trade
     WHERE
      ts_code='{}'
      AND trade_date>='{}'
      AND trade_date<='{}'
     ORDER BY ts_code,trade_date
     ;
     '''.format(ts_code, date1, date2)
    close = list(q(sql)['close'])
    if len(close) == 0:
        re = [ts_code, -999, -999]
    elif len(close) == 1:
        re = [ts_code, close[0], close[0]]
    else:
        re = [ts_code, close[0], close[-1]]
    return re


def future_return(data):
    data['return'] = (data['close1'] - data['close']) / data['close']
    return data