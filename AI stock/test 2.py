import pandas as pd
from sqlalchemy import create_engine
import pandas as pd
import index


conn = create_engine('mysql+pymysql://root:root@localhost/stock?charset=utf8', encoding='utf-8')

data=pd.read_excel('index.xlsx')
# print(data)
data=data[0:16]
index_list=list(data)[3:-1]


def get_data(df,index):
    data=pd.DataFrame([])
    data['股票代码']=df['股票代码']
    data['结束日期']=df['结束日期']
    data[index]=df[index]
    data['close']=df['close']
    return data

# for i in index_list:
#     re=get_data(data,i)
#     print(re)
#     re.to_excel('/Users/eminem/Desktop/代码/Stock/AI stock selection system/data/index11_{}.xlsx'.format(i))

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


uids = list(set(data['股票代码']))
total =len(uids)


for i in index_list:
    ddd = get_data(data, i)
    print(i)
    re = pd.DataFrame([])
    for n,j in enumerate(uids):
        print(n)
        print(j)
        df = grade(ddd,j,i)
        re = pd.concat([re, df], axis=0, ignore_index='True')

    re.columns = ['ts_code', 'end_date', i ,'close', 'next_close', 'rate']
    print(re)
#
# re.columns=['ts_code','end_date','roe_dt','close','next_close','rate']
# print(re)

# re=pd.DataFrame(re,columns=['ts_code','end_date','roe_dt','close','next_close','rate'])
# print(re)
# re.to_excel('result.xlsx')
# a=final_grade('000002.SZ')
# print(a)