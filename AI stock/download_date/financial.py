import tushare as ts
import pandas as pd
import numpy as np
import time

from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock?charset=utf8")
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/stock?charset=utf8")
ts.set_token('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')

pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

stock_list=data['ts_code']
print(len(stock_list))

# d_basic=pd.DataFrame([])
# for n,i in enumerate(stock_list):
#     try:
#         print(n)
#         print(i)
#         df = pro.daily_basic(ts_code=str(i),start_date='20170101', end_date='20190801')
#         df = df.drop_duplicates(['trade_date'],keep='first')
#         print(df)
#         df.to_sql("d_basic", con=engine, if_exists='append', index=False, index_label="id")
#         # d_basic = pd.concat([d_basic, df], axis=0,ignore_index ='True')
#     except:
#         pass
# d_basic.to_excel('1.xlsx')

# fina_indicator=pd.DataFrame([])
# for n,i in enumerate(stock_list):
#     print(n)
#     print(i)
#     try:
#         if np.mod(n,50)==0 and n>0:
#             time.sleep(30)
#         df = pro.fina_indicator(ts_code=str(i),start_date='20070101', end_date='20191118')
#         df = df.drop_duplicates(['end_date'], keep='first')
#         print(df)
#         df.to_sql("fina_indicator", con=engine, if_exists='append', index=False, index_label="id")
#         # fina_indicator = pd.concat([fina_indicator, df], axis=0,ignore_index ='True')
#     except:
#         pass
#
# balancesheet=pd.DataFrame([])
# for n,i in enumerate(stock_list):
#     print(n)
#     print(i)
#     try:
#         if np.mod(n,50)==0 and n>0:
#             time.sleep(30)
#         df = pro.balancesheet(ts_code=str(i),start_date='20070101', end_date='20191118')
#         df = df.drop_duplicates(['end_date'], keep='first')
#         print(df)
#         df.to_sql("balancesheet", con=engine, if_exists='append', index=False, index_label="id")
#         # balancesheet = pd.concat([balancesheet, df], axis=0,ignore_index ='True')
#     except:
#         pass

income=pd.DataFrame([])
for n,i in enumerate(stock_list):
    print(n)
    print(i)
    try:
        if np.mod(n,40)==0 and n>0:
            time.sleep(60)
        df = pro.income(ts_code=str(i),start_date='20070101', end_date='20191118')
        df = df.drop_duplicates(['end_date'], keep='first')
        print(df)
        df.to_sql("income", con=engine, if_exists='append', index=False, index_label="id")
        # income = pd.concat([income, df], axis=0,ignore_index ='True')
    except:
        pass


# d_trade=pd.DataFrame([])
# for n,i in enumerate(stock_list):
#     try:
#         print(n)
#         print(i)
#         df = ts.pro_bar(pro_api=pro,ts_code=str(i), adj='qfq', start_date='20170101', end_date='20190801',
#                         freq='D',ma=[5, 10, 20], factors=['tor', 'vr'])
#         df = df.drop_duplicates(['trade_date'], keep='first')
#         d_trade = pd.concat([d_trade, df], axis=0,ignore_index ='True')
#     except:
#         pass




# print(d_trade)
# fina_indicator = pd.DataFrame(pro.fina_indicator(ts_code='000009.SZ', start_date='20100101', end_date='20190801'))
# balancesheet =  pd.DataFrame(pro.balancesheet(ts_code='000009.SZ', start_date='20100101', end_date='20190801'))
# income =  pd.DataFrame(pro.income(ts_code='000009.SZ', start_date='20100101', end_date='20190801'))
#
# d_trade =  pd.DataFrame(ts.pro_bar(ts_code='000009.SZ', adj='hfq', start_date='20101001', end_date='20190801', freq='D',
#                      ma=[5, 10, 20], factors=['tor', 'vr']))

# print(list(fina_indicator.columns))



# d_trade.to_sql("d_trade",con=engine,if_exists='append',index=False,index_label="id")
# d_basic.to_sql("d_basic",con=engine,if_exists='append',index=False,index_label="id")
# a=income.drop_duplicates(subset=['ts_code','end_date'],keep='first')

# print(fina_indicator,balancesheet,income)
# a.to_excel('1.xlsx')
