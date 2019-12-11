import tushare as ts
import pandas as pd
from sqlalchemy import create_engine
import time, datetime
import calendar as cal
import numpy as np



engine1 = create_engine("mysql+pymysql://root:123456@localhost:3306/stock?charset=utf8")
engine2 = create_engine("mysql+pymysql://root:123456@localhost:3306/stock_index?charset=utf8")
engine3 = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock_index?charset=utf8")



def get_month(year1,year2):
    year_statr=year1
    year_end=year2
    start=[]
    end=[]
    for year in range(year_statr,year_end):
        for m in range(1, 13):
            d = cal.monthrange(year, m)[1]
            if m<10:
                a=str('{}0{}01'.format(year,m))
                b=str('{}0{}{}'.format(year,m,d))
                start.append(a)
                end.append(b)
            else:
                a=str('{}{}01'.format(year,m))
                b=str('{}{}{}'.format(year,m,d))
                start.append(a)
                end.append(b)
    return start,end

def get_trade_date(engine):
    conn=engine
    q = lambda x: pd.read_sql(x, conn)
    sql = '''
select
date_format(cal_date,"%%Y%%m%%d") date
from trade_cal
where is_open=1
;
    '''
    date_list=q(sql)
    return date_list





pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')



index_list=['000010.SH','000905.SH','000903.SH','000132.SH','399330.SZ']
# index_list=['399300.SZ','000016.SH','000010.SH','000905.SH','000903.SH','000132.SH','399330.SZ']
# index_name=['沪深300','上证50','上证180','中证500','中证100','上证100','深证100']
index_name=['上证180','中证500','中证100','上证100','深证100']
# date_list=list(get_trade_date(engine1)['date'][1270::])
#
# index=index_list[0]
# date=date_list[0]
# print(index,date)
# df = pro.index_weight(index_code=index, trade_date=date)
# print(df)

date_list=get_trade_date(engine1)['date']
for n,index in enumerate(index_list):
        print(index_name[n])
        print(index)
        for m, date in enumerate(date_list):
            print(m)
            print(date)
            try:
                if np.mod(m, 60) == 0 and m>0:
                    time.sleep(60)
                df= pro.index_weight(index_code=index,trade_date=date)
                print(len(df))
                a=[index_name[n]]*len(df)
                df['index_name']=a
                df.to_sql(index, con=engine2, if_exists='append', index=False, index_label="id")
                print('Hello')
                # df.to_sql(index, con=engine3, if_exists='append', index=False, index_label="id")
            except:
                print('Eminem')
                pass


