import MLE
import pandas as pd

def pre_para(x):
    d = 1/252
    p0 = [0.02, 0.02, 0.02]
    for i in range(10):
        print(i)
        re =MLE.mle(x,d,p0)
        if p0 == re:
            break
        else:
            p0 = re
    return re

def pre_Seq(x,m):
    list_p=[]
    n=len(x)-m+1
    for i in range(n):
        print(i)
        y=list(x[i:i+m-1])
        list_p.append(pre_para(y))
        # print(list_p)

    return list_p

x=pd.read_excel('data.xlsx')
x=x['data']
x=x[0:2000]
#
#
re=pre_Seq(x,150)
re=pd.DataFrame(re)
re.to_excel('re.xlsx')
#
# print(re)