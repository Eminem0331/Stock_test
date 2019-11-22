from sqlalchemy import create_engine
import pandas as pd


engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
engine2 = create_engine('mysql+pymysql://root:123456@localhost/stock_data?charset=utf8', encoding='utf-8')
# engine2 = create_engine('mysql+pymysql://root:Tang123456!@116.85.28.78/stock_data?charset=utf8', encoding='utf-8')
def factor_daily():
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
    turnover_rate_f
    from d_basic
    WHERE trade_date>='2000-01-01' and trade_date<='2019-12-31'
    ORDER BY ts_code,trade_date
    ;
    '''
    index=q(sql)
    print(index)
    index.to_sql("factor_daily", con=engine2, if_exists='append', index=False, index_label="id")

factor_daily()


