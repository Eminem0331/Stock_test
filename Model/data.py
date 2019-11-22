import pandas as pd

def handle_data(x):
    df=pd.read_excel(x)
    df=pd.DataFrame(df,columns=['trade_date', 'open', 'close', 'high', 'low'])
    df=df.iloc[df['trade_date'].argsort()].reset_index().drop(columns=['index'])


    data1=(df['open']+df['close'])/2
    data2=(df['high']+df['low'])/2
    data3=2*data1-data2
    df['data1'] = data1
    df['data2'] = data2
    df['data3'] = data3

    SY_rate=[0]
    for i in range(len(df['close'])-1):
        SY_rate.append((df['close'][i+1]-df['close'][i])/df['close'][i])

    df['SY_rate']=SY_rate
    return df


# x=handle_data('000858.SZ.xlsx')
#
# print(x)
