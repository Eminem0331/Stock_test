from sqlalchemy import create_engine
import pandas as pd


engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
engine2 = create_engine('mysql+pymysql://root:123456@localhost/stock_data?charset=utf8', encoding='utf-8')
def fina_factor():
    q = lambda x: pd.read_sql(x, engine1)
    sql='''
    SELECT
        a.ts_code ,
        a.ann_date,
        a.end_date ,
        a.roe_dt ,
        a.current_ratio ,
        a.quick_ratio ,
        a.debt_to_assets ,
        a.tr_yoy ,
        a.or_yoy ,
        b.money_cap/(c.total_revenue/a.total_revenue_ps) money_cap_ps,
        a.eps ,
        b.goodwill ,
        a.or_yoy ,
        b.total_share ,
        a.eps/a.bps,
        'fina_factor' factor_style, 
        'Season' Update_frequency 
      FROM fina_indicator a join balancesheet b on a.end_date=b.end_date
    JOIN income c on b.end_date=c.end_date
    WHERE a.end_date>='2000-01-01' and a.end_date<='2019-12-31'
    AND a.ts_code=b.ts_code
    AND a.ts_code=c.ts_code
    ORDER BY a.ts_code,a.end_date
    '''
    index=q(sql)
    print(index)
    index.to_sql("fina_factor", con=engine2, if_exists='append', index=False, index_label="id")

fina_factor()


