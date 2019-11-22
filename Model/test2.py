from sqlalchemy import create_engine
import pandas as pd


conn = create_engine('mysql+pymysql://root:root@localhost/stock?charset=utf8', encoding='utf-8')
q = lambda x: pd.read_sql(x, conn)
sql='''
SELECT
    a.ts_code 股票代码,
    a.ann_date 公告日期,
    a.end_date 结束日期,
    a.roe_dt 净盈余ROE_除非,
    a.current_ratio 流动比率,
    a.quick_ratio 速动比率,
    a.debt_to_assets 资产负债率,
    a.tr_yoy 营业总收入同比增长率,
    a.or_yoy 营业收入同比增长率,
    b.money_cap/(c.total_revenue/a.total_revenue_ps) 每股货币资金,
    a.eps 基本每股收益,
    b.goodwill 商誉营,
    a.or_yoy 业收入同比增长率,
    b.total_share 期末总股本,
    a.eps/a.bps 年净益率,
    e.pe 市盈率,
    e.pe_ttm 市盈率_TTM,
    e.pb 市净率,
    f.close
  FROM fina_indicator a join balancesheet b on a.end_date=b.end_date
JOIN income c on b.end_date=c.end_date
JOIN trade_cal d on c.end_date=d.cal_date
JOIN d_basic e on e.trade_date=d.pretrade_date
JOIN d_trade f on e.trade_date=f.trade_date

WHERE a.end_date>='2017-01-01' and a.end_date<='2019-01-01'
AND a.ts_code=b.ts_code
AND a.ts_code=c.ts_code
AND a.ts_code=e.ts_code
AND a.ts_code=f.ts_code
ORDER BY a.ts_code,a.end_date
;
'''

index=q(sql)
print(index)
index.to_excel('index.xlsx')


