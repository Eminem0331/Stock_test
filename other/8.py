import tushare as ts
import pandas as pd

ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
# data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
#
# stock_list=data['ts_code']
# print(stock_list)

df = pro.fina_indicator( ts_code='000009.SZ', start_date='20180101', end_date='20190801')
df2 = pro.balancesheet(ts_code='000009.SZ', start_date='20180101', end_date='20190801')
df3 = pro.income(ts_code='000009.SZ', start_date='20180101', end_date='20190801')

# df=df.reset_index().drop(columns=['index'])
# print(df['end_date'])
re=[]
re=pd.DataFrame(re)

re['净盈余ROE']=df['roe_dt']

re['流动比率']=df['current_ratio']
re['速动比率']=df['quick_ratio']
re['资产负债率']=df['debt_to_assets']
# re['毛利率']=df['roe']
# re['销售毛利率']=df['grossprofit_margin']
re['营业总收入同比增长率']=df['tr_yoy']
re['营业收入同比增长率']=df['or_yoy']
# re['主营利润增长率']=df['roe']
re['营业利润同比增长率']=df['op_yoy']

re['每股现金流']=df['cfps']
stock_amount=df3['total_revenue']/df['total_revenue_ps']
# re['经营活动产生的现金流净额与净利润的比率']=df['ocf_to_profit']
# re['经营活动产生的现金流量净额／营业利润']=df['ocf_to_profit']
# re['净利润年复合增长率']=df['roe']
# re['每股货币资金']=df2['money_cap']
# re['市盈率=每股价格/每股收益']=df['roe']
# re['市净率=每股股价/每股净资产']=df['roe']
re['基本每股收益']=df['eps']
re['商誉']=df2['goodwill']
re['期末总股本']=df2['total_share']
re['年净益率']=df['eps']/df['bps']
# re['年股息率']=df['roe']

re['date1']=df['ann_date']
re['date2']=df['end_date']
re['date4']=df2['f_ann_date']
re['date5']=df2['end_date']
re['date7']=df3['f_ann_date']
re['date8']=df3['end_date']
print(re)

re.to_excel('data.xlsx')