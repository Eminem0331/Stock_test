import tushare as ts
import pandas as pd

ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
# data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
# print(data['ts_code'])

stock_list=data['ts_code']
print(stock_list)


for n,i in enumerate(stock_list):
    try:
        print(n)
        print(i)
        df = ts.pro_bar(pro_api=pro,ts_code=str(i), adj='None', start_date='20171001', end_date='20191001',freq='D',
                    ma=[5,10,20],factors=['tor', 'vr'])
        print(df)
        df.to_excel('/Users/eminem/Desktop/stock_data/stock_D3/{}.xlsx'.format(i))
    except:
        pass

