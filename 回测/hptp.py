#encoding = utf-8
import pandas as pd 
import numpy as np
import cx_Oracle as database 
import time
import datetime
from  copy import copy
import csv
from matplotlib import pyplot as plt


k = 1    #k个标准差
N = 20   #MA
P = 4    #清洗高低点
M = 10   #分箱
Q = 2    #高点个数要求
holdday = 45   #持仓时间上限
delta360 = datetime.timedelta(days=360)     #回溯时间
delta1 = datetime.timedelta(days=1)
goods = 'ZN.SHF'                            #标的资产，以锌为例


def MA(a,T):                                #计算MA
    avg=[]
    for i in range(len(a)):
        if i<T-1:
            avg.append(0)
        else:
            s=0.0
            for j in range(T):
                s=s+a[i-j]
            avg.append(s/T)
    return avg

def SD(a,T):                               #计算标准差
    sd=[]
    for i in range(len(a)):
        if i<T-1:
            sd.append(0)
        else:
            b = a[i-T+1:i+1] 
            std = np.std(b, ddof = 1)
            sd.append(std)
    return sd
          
start = time.time()

begin_date = '20090101'
end_date   = '20171031'

conn = database.connect('wind_guest/readonly@192.168.10.236:1521/orcl')
db   = conn.cursor()

     
sql  = '''select S_DQ_OPEN,S_DQ_CLOSE,S_DQ_CHANGE,TRADE_DT,S_INFO_WINDCODE from wind.CCommodityFuturesEODPrices 
        where S_INFO_WINDCODE='ZN.SHF' AND TRADE_DT between %s and %s 
        order by S_INFO_WINDCODE,TRADE_DT'''%(begin_date,end_date)
sql_result = db.execute(sql)
data = sql_result.fetchall()  
df = pd.DataFrame(data)

ind_p = pd.pivot_table(df,0,3,4)
index = ind_p.index
columns = ind_p.columns
open_p = pd.pivot_table(df,values=0,index=3,columns=4).loc[:,columns]
close_p = pd.pivot_table(df,values=1,index=3,columns=4).loc[:,columns]
chg_p = pd.pivot_table(df,values=2,index=3,columns=4).loc[:,columns]
open_list0 = open_p[goods]
close_list0 = close_p[goods]
dates = df.iloc[:,3]
 
first = 1200            #任取某一日，向前计算高低点和阻力位

while first<1201:          #某天开始向前追溯360天
    qs = 0                       #趋势默认为0，上升1，下降-1
    hp = []
    lp = []
    hpday = []
    lpday = []
    count_hp = [0]*M
    count_lp = [0]*M
    d = datetime.datetime.strptime(dates[first], '%Y%m%d')
    dbegin = d - delta360
    dbegins = dbegin.strftime('%Y%m%d')
    dend = d - delta1
    dends = dend.strftime('%Y%m%d')
    open_list = open_list0[dbegins:dends]      #截取360天的开盘和收盘价，计算布林带
    close_list = close_list0[dbegins:dends]
    ma_p = np.array(MA(close_list,N))
    sd_p = np.array(SD(close_list,N))
    close_pp = np.array(close_list)
    ub_p = ma_p + k * sd_p
    lb_p = ma_p - k * sd_p
    for i in range(len(close_pp)):            #判断上升下降趋势，找高低点
        if close_list[i]>ub_p[i] and qs == 0:
            qs = 1
            hptemp = close_list[i]
            hpdaytemp = i
        if close_list[i]<lb_p[i] and qs == 0:
            qs = -1
            lptemp = close_list[i]
            lpdaytemp = i
        if close_list[i]>=lb_p[i] and qs == 1:
            if close_list[i]>hptemp:
                hptemp = close_list[i]
                hpdaytemp = i
        if close_list[i]<lb_p[i] and qs == 1:
            qs = -1
            hp.append(hptemp)
            hpday.append(hpdaytemp)
            lptemp = close_list[i]
            lpdaytemp = i
        if close_list[i]<=ub_p[i] and qs == -1:
            if close_list[i]<lptemp:
                lptemp = close_list[i]
                lpdaytemp = i
        if close_list[i]>ub_p[i] and qs == -1:
            qs = 1
            lp.append(lptemp)
            lpday.append(lpdaytemp)
            hptemp = close_list[i]
            hpdaytemp = i
    
    if hpday[0]<lpday[0]:              #清洗高低点
        for i in range(len(lpday)):
            if (lpday[i]-hpday[i])<P:
                lpday[i]=-1
                hpday[i]=-1
                lp[i]=-1
                hp[i]=-1
            if i+1<len(hpday):
                if(hpday[i+1]-lpday[i])<P:
                    lpday[i]=-1
                    hpday[i+1]=-1
                    lp[i]=-1
                    hp[i+1]=-1
        if -1 in lpday: 
            lpday.remove(-1)
            hpday.remove(-1)
            lp.remove(-1)
            hp.remove(-1)

    if lpday[0]<hpday[0]:           #清洗高低点
        for i in range(len(hpday)):
            if (hpday[i]-lpday[i])<P:
                lpday[i]=-1
                hpday[i]=-1
                lp[i]=-1
                hp[i]=-1
            if i+1<len(lpday):
                if(lpday[i+1]-hpday[i])<P:
                    hpday[i]=-1
                    lpday[i+1]=-1
                    hp[i]=-1
                    lp[i+1]=-1
        if -1 in lpday:
            lpday.remove(-1)
            hpday.remove(-1)
            lp.remove(-1)
            hp.remove(-1)
        
    width_hp = (max(hp)-min(hp))/M   #计算箱体
    for i in range(M):
        if i==M-1:
            count_hp[i]=count_hp[i]+1
        for a in hp:
            if a>=(min(hp)+i*width_hp) and a<(min(hp)+(i+1)*width_hp):
                count_hp[i]=count_hp[i]+1   
    resist = 0            
    for i in range(M):              #计算阻力位
        if count_hp[M-i-1]>=Q and i<(M/3):
            resist = min(hp)+(M-i)*width_hp
            break
    first = first + 1    

db.close()
conn.close()
print ('over')
end = time.time()

print (end-start)
        
   
