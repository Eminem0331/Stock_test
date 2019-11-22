import pandas as pd
import datetime
import time


data=pd.read_excel('result.xlsx')


def ic(df):
    a = pd.DataFrame([])
    a['roe_dt'] = df['roe_dt']
    a['rate'] = df['rate']
    a=a.dropna(axis=0, how='any')
    a=a.sort_values(by="roe_dt")
    b=list(range(len(a)))
    a['roe_dt_rank']=b
    a=a.sort_values(by="rate")
    c=list(range(len(a)))
    a['rate_rank']=c
    bb=0
    cc=list(a['roe_dt_rank'])
    l=len(cc)
    for n,i in enumerate(cc):
        bb=bb+(i-n)**2
    re=1-(6*bb)/(l*(l**2-1))
    return re


def grade(d,date):
    df = d[d['end_date'] == date]
    df = df.reset_index()
    # end_date=list(df['end_date'])
    # roe_dt=list(df['roe_dt'])
    # # close=list(df['close'])
    # # next_close=list(df['next_close'])
    # rate=list(df['rate'])
    re=pd.DataFrame([])
    re['end_date']=[date]
    re['IC']=[ic(df)]

    return re

uids = list(set(data['end_date']))
total =len(uids)
# # a=time.strftime("%Y-%m-%d", uids[0])
# a=str(uids[0])
# print(a)

re=pd.DataFrame([])
for n,i in enumerate(uids):
    print(n)
    aa=str(i)
    df = grade(data,aa)
    re = pd.concat([re, df], axis=0, ignore_index='True')

re.columns=['end_date','IC']
print(re)



# a=grade(data,'2017-09-30 00:00:00')
#
# print(a)