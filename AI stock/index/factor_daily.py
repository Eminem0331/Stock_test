from sqlalchemy import create_engine
import pandas as pd


engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
engine2 = create_engine('mysql+pymysql://root:123456@localhost/stock_data?charset=utf8', encoding='utf-8')
engine3 = create_engine('mysql+pymysql://root:Tang123456!@116.85.28.78/stock_data?charset=utf8', encoding='utf-8')

def daily_factor(date):
    q = lambda x: pd.read_sql(x, engine1)
    sql='''
    SELECT
    ts_code,
    trade_date,
    pe,
    pe_ttm ,
    pb,
    ps,
    ps_ttm,
    turnover_rate,
    turnover_rate_f,
    'daily_factor' factor_style, 
    'Daily' Update_frequency 
    from d_basic
    WHERE trade_date='{}'
    ORDER BY ts_code
    ;
    '''.format(date)
    df=q(sql)
    print(df)
    return df


q = lambda x: pd.read_sql(x, engine1)
sql2='''
SELECT
cal_date
FROM trade_cal
WHERE cal_date>='2000-01-01' and cal_date<='2019-12-31'
and is_open=1
;
'''
date_list=list(q(sql2)['cal_date'])

for date in date_list:
    print(date)
    try:
        df=daily_factor(date)
        df.to_sql("daily_factor", con=engine2, if_exists='append', index=False, index_label="id")
        df.to_sql("daily_factor", con=engine3, if_exists='append', index=False, index_label="id")
    except:
        print('Eminem')
        pass





