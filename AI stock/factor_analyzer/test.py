from sqlalchemy import create_engine
import pandas as pd


conn = create_engine('mysql+pymysql://root:root@localhost/stock?charset=utf8', encoding='utf-8')

data=pd.read_excel('index.xlsx')
index_list=list(data)[3:-1]
# index_list=list(data)
print(index_list)


def get_data(df,index):
    data=pd.DataFrame([])
    data['股票代码']=df['股票代码']
    data['结束日期']=df['结束日期']
    data[index]=df[index]
    data['close']=df['close']
    return data

def grade(d,ts_code,index):
    df = d[d['股票代码'] == ts_code]
    df=df.reset_index()
    end_date=list(df['结束日期'])
    index=list(df[index])
    close=list(df['close'])
    re=[]
    for i in range(len(df)-2):
        a=[df['股票代码'][i],end_date[i],index[i],close[i],
            close[i+2],(close[i+2]-close[i])/close[i]]
        re.append(a)
    re=pd.DataFrame(re)
    return re

def ic(df,index):
    a = pd.DataFrame([])
    a[index] = df[index]
    a['rate'] = df['rate']
    a=a.dropna(axis=0, how='any')
    a=a.sort_values(by=index)
    b=list(range(len(a)))
    a['{}_rank'.format(index)]=b
    a=a.sort_values(by="rate")
    c=list(range(len(a)))
    a['rate_rank']=c
    cc=list(a['{}_rank'.format(index)])
    l=len(cc)
    bb = 0
    for n,i in enumerate(cc):
        bb=bb+(i-n)**2
    re=1-(6*bb)/(l*(l**2-1))
    return re

def rank(d,date,index):
    df = d[d['end_date'] == date]
    df = df.reset_index()
    re=pd.DataFrame([])
    re[index]=[index]
    re['end_date']=[date]
    re['IC']=[ic(df,index)]
    return re


uids = list(set(data['股票代码']))
total =len(uids)

RE=pd.DataFrame([])
for i in index_list:
    print(i)
    ddd = get_data(data, i)
    re = pd.DataFrame([])
    for n,j in enumerate(uids):
        # print(n)
        # print(j)
        df = grade(ddd,j,i)
        re = pd.concat([re, df], axis=0, ignore_index='True')
    re.columns = ['ts_code', 'end_date', i ,'close', 'next_close', 'rate']

    aaa = list(set(re['end_date']))
    lll = len(aaa)
    IC = pd.DataFrame([])
    for nn, ii in enumerate(aaa):
        # print(nn)
        aa = str(ii)
        dfdf = rank(re,aa,i)
        IC = pd.concat([IC, dfdf], axis=0, ignore_index='True')
    IC=IC.sort_values(by='end_date')
    IC.columns = ['index', 'end_date', 'IC']
    # print(IC)
    # IC.to_excel('/Users/eminem/Desktop/代码/Stock/data/Rank IC_{}.xlsx'.format(i))
    RE=pd.concat([RE, IC], axis=0, ignore_index='True')

RE.to_excel('/Users/eminem/Desktop/代码/Stock/data/result.xlsx')
print(RE)
