import pandas as pd
from sqlalchemy import create_engine
import numpy as np


def get_daily_data(date,engine):
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
    AND a.end_date='{}'
    ;
    '''.format(date)
    data = q(sql)
    return data

def get_date_list(engine):
    q = lambda x: pd.read_sql(x, engine)
    sql = '''
       select
       distinct end_date
       from stock_data.fina_factor 
       ;
       '''
    date_list=q(sql)
    return date_list

def Stock_Quantile_qe(data,index,quantile,date):
     df=data[data['end_date']==date]
     a=df[index].quantile(quantile)
     re=df[df[index]<=a]['ts_code']
     return re

def Stock_Quantile_le(data,index,quantile,date):
     df = data[data['end_date'] == date]
     a = df[index].quantile(quantile)
     re = df[df[index] > a]['ts_code']
     return re

def close_sql(ts_code,date1,date2,engine):
     q = lambda x: pd.read_sql(x, engine)
     sql='''
     SELECT
     ts_code,close,trade_date
       FROM d_trade
     WHERE
      ts_code='{}'
      AND trade_date>='{}'
      AND trade_date<='{}'
     ORDER BY ts_code,trade_date
     ;
     '''.format(ts_code,date1,date2)
     close=list(q(sql)['close'])
     if len(close)==0:
          re = [ts_code,-999, -999]
     elif len(close)==1:
          re = [ts_code, close[0], close[0]]
     else:
          re = [ts_code,close[0],close[-1]]
     return re

def future_return(data):
     data['return']=(data['close1']-data['close'])/data['close']
     return data

def turnover(data1,data2):
     same = list(set(data1) & set(data2))
     re=1-len(same)/len(data1)
     return re

def get_ic(data,index,date):
     df = data[data['end_date'] == date]
     a = pd.DataFrame([])
     a[index] = df[index]
     a['return'] = df['return']
     a=a.dropna(axis=0, how='any')
     a=a.sort_values(by=index)
     b=list(range(len(a)))
     a['{}_rank'.format(index)]=b
     a=a.sort_values(by="return")
     c=list(range(len(a)))
     a['return_rank']=c
     cc=list(a['{}_rank'.format(index)])
     l=len(cc)
     bb = 0
     for n,i in enumerate(cc):
        bb=bb+(i-n)**2
     re=1-(6*bb)/(l*(l**2-1))
     return re

# def rank(d,date,index):
#     df = d[d['end_date'] == date]
#     df = df.reset_index()
#     re=pd.DataFrame([])
#     re[index]=[index]
#     re['end_date']=[date]
#     re['IC']=[get_ic(df,index,date)]
#     return re

def main():
    # result=pd.DataFrame([])
    engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
    # engine2 = create_engine('mysql+pymysql://root:123456@localhost/stock_data?charset=utf8', encoding='utf-8')
    engine2 = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock_data?charset=utf8")

    date_list = list(get_date_list(engine1)['end_date'])
    print(date_list)

    for n,date in enumerate(date_list[0:-1]):
         print(date)
         data=get_daily_data(date,engine1)
         index_list = list(data)[4:-2]
         print(index_list)

         rrr = []
         for index in index_list:
              df = data[data['end_date'] == date]
              print(df)
              print(index)

              #计算IC
              stock=df['ts_code']
              re=[]
              for m in stock:
                   re.append(close_sql(m, date, date_list[n + 1],engine1))
              re = pd.DataFrame(re, columns=['ts_code', 'close', 'close1'])
              re[index]=list(df[index])
              re['end_date']=list(df['end_date'])
              re['return']=(re['close1']-re['close'])/re['close']
              IC=get_ic(re,index,date)

              #计算分位数换手率与换手率
              stock1=Stock_Quantile_qe(data,index,0.2,date)
              stock2=Stock_Quantile_qe(data,index,0.2,date_list[n+1])
              turnover1=turnover(stock1,stock2)
              stock3=Stock_Quantile_le(data,index,0.8,date)
              stock4=Stock_Quantile_le(data,index,0.8,date_list[n+1])
              turnover2=turnover(stock3,stock4)
              re1=[]
              for j in stock1:
                   # print(j)
                   ddd=close_sql(j,date,date_list[n+1],engine1)
                   re1.append(ddd)
              re2=[]
              for k in stock3:
                   # print(k)
                   dddd=close_sql(k,date,date_list[n+1],engine1)
                   re2.append(dddd)
              re1=pd.DataFrame(re1,columns=['ts_code','close','close1'])
              re2=pd.DataFrame(re2,columns=['ts_code','close','close1'])

              future_return1=np.mean(future_return(re1)['return'])
              future_return2=np.mean(future_return(re2)['return'])

              rrr.append([index,date,future_return1,future_return2,turnover1,turnover2,IC])

         rrr=pd.DataFrame(rrr,columns=['factor_name','end_date','Minimum_quantile_return','Maximum_quantile_return',
                                       'Minimum_quantile_turnover','Maximum_quantile_turnover','IC'])
         rrr.to_sql("test", con=engine2, if_exists='append', index=False, index_label="id")
#      result=pd.concat([result,rrr],axis=0,ignore_index=True)
#
#
# print(result)

main()










