import pandas as pd

data=pd.read_excel('index.xlsx')

# df=data[(data['净盈余ROE_除非']>=0.2)&(data['资产负债率']<0.3)]
# print(df)

def condition_re(df,index,Threshold):
    re=df[df[index] == Threshold]
    return re

def condition_le(df,index,Threshold):
    re=df[df[index] > Threshold]
    return re


def condition_qe(df, index, Threshold):
    re = df[df[index] < Threshold]
    return re

df=condition_le(data,'净盈余ROE_除非',0.2)
print(df)