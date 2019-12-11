# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os

#均线
def MA(A, n, tolerance_rate):
    return A.rolling(n, int(n * tolerance_rate)).mean()

class CalSignal(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        # rolling时最少存在的数据比例
        self.tolerance_rate = 0.7
        self.path = os.path.dirname(os.path.abspath(__file__)) + '//'
        self.data = pd.read_csv(self.path + stock + '.csv')
    
    #上吊线 x,y,z用于判断前序趋势
    def status1(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #上吊线的上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-3'] > x['mean-5'] 
                          and x['mean-1'] > x['mean-3'] 
                       else 0,
            axis = 1,
        )
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])
        
        #上吊线定义
        df['signal_2'] = df.apply(
            lambda x:1 if x['upline'] < 0.001 * x['close'] and x['downline'] > 2 * x['box'] else 0,
            axis = 1
        )
        
        #次日确认信号
        df['close_next'] = df['close'].shift(-1)
        df['signal_3'] = df.apply(
            lambda x:1 if x['close_next'] < x['close'] else 0,
            axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3']
        df['status1'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status1']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status1_' + stock + '.csv', index=False)
    
    #锤子线 x,y,z用于判断前序趋势
    def status2(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #锤子的下降趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-3'] < x['mean-5'] 
                          and x['mean-1'] < x['mean-3'] 
                       else 0,
            axis = 1,
        )

        #锤子线定义
        df['signal_2'] = df.apply(
            lambda x:1 if x['upline'] < 0.001 * x['close'] and x['downline'] > 2 * x['box'] else 0,
            axis = 1
        )
        
        #次日确认信号
        df['close_next'] = df['close'].shift(-1)
        df['signal_3'] = df.apply(
            lambda x:1 if x['close_next'] > x['close'] else 0,
            axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3']
        df['status2'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status2']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status2_' + stock + '.csv', index=False)
        
    #看涨吞没形态,x,y,z用于判断前序序列趋势
    def status3(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-3'] < x['mean-5'] 
                          and x['mean-1'] < x['mean-3'] 
                       else 0,
            axis = 1,
        )
        
        #前一日的开盘价和收盘价
        df['open_yesterday'] = df['open'].shift(1)
        df['close_yesterday'] = df['close'].shift(1)
        
        #看涨吞没形态的定义
        df['signal_2'] = df.apply(
            lambda x:1 if x['close_yesterday'] < x['open_yesterday'] 
                          and x['close'] > x['open'] 
                          and x['close'] > x['open_yesterday'] 
                          and x['open'] < x['close_yesterday'] 
                       else 0,
            axis = 1,
        )

        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status3'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status3']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status3_' + stock + '.csv', index=False)
        
    #看跌吞没形态，x,y,z用于判断前序序列趋势
    def status4(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-3'] > x['mean-5'] 
                          and x['mean-1'] > x['mean-3'] 
                       else 0,
            axis = 1,
        )
        
        #前一日的开盘价和收盘价
        df['open_yesterday'] = df['open'].shift(1)
        df['close_yesterday'] = df['close'].shift(1)
        
        #定义看跌吞没形态
        df['signal_2'] = df.apply(
            lambda x:1 if x['close_yesterday'] > x['open_yesterday'] 
                          and x['close'] < x['open'] 
                          and x['close'] < x['open_yesterday'] 
                          and x['open'] > x['close_yesterday'] 
                       else 0,
            axis = 1,
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status4'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status4']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status4_' + stock + '.csv', index=False)
        
    #看涨吞没形态的变形，ma是均线期间，x,y,z用于判断前序序列趋势
    def status5(self,x,y,z):
        df = self.data.copy()   
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-3'] < x['mean-5'] 
                          and x['mean-1'] < x['mean-3'] 
                       else 0,
            axis = 1,
        )
        
        #前一日的开盘价和收盘价;收盘价与开盘价之差
        df['open_yesterday'] = df['open'].shift(1)
        df['close_yesterday'] = df['close'].shift(1)
        df['diff_co_yesterday'] = df['close_yesterday'] - df['open_yesterday']
        
        #定义看涨吞没形态的变形
        df['signal_2'] = df.apply(
            lambda x:1 if x['close_yesterday'] > x['open_yesterday']
                          and x['diff_co_yesterday'] < 0.003 * x['close_yesterday']
                          and x['close'] > x['open']
                          and x['close'] > x['close_yesterday']
                          and x['open'] < x['open_yesterday']
                       else 0,
            axis = 1,
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status5'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status5']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status5_' + stock + '.csv', index=False)
        
        
    #看跌吞没形态的变形，x,y,z用于判断前序序列趋势
    def status6(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-3'] > x['mean-5'] 
                          and x['mean-1'] > x['mean-3'] 
                       else 0,
            axis = 1,
        )
        
        #前一日的开盘价和收盘价;开盘价与收盘价之差
        df['open_yesterday'] = df['open'].shift(1)
        df['close_yesterday'] = df['close'].shift(1)
        df['diff_oc_yesterday'] = df['open_yesterday'] - df['close_yesterday']
        
        #定义看涨吞没形态的变形
        df['signal_2'] = df.apply(
            lambda x:1 if x['close_yesterday'] < x['open_yesterday']
                          and x['diff_oc_yesterday'] < 0.003 * x['close_yesterday']
                          and x['close'] < x['open']
                          and x['close'] < x['close_yesterday']
                          and x['open'] > x['open_yesterday']
                       else 0,
            axis = 1,
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status6'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status6']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status6_' + stock + '.csv', index=False)
    
    #乌云盖顶形态 x,y,z是用于计算之前开收盘均价的参数
    def status7(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #前序序列处于上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] else 0,
            axis = 1
        )
        
        #计算t-1日相关价格
        df['open_yesterday'] = df['open'].shift(1)
        df['close_yesterday'] = df['close'].shift(1)
        df['high_yesterday'] = df['high'].shift(1)
        
        #定义乌云盖顶
        df['signal_2'] = df.apply(
            lambda x:1 if x['close_yesterday'] > x['open_yesterday']
                          and x['close'] < x['open']
                          and x['open'] > x['high_yesterday']
                          and x['close'] < x['close_yesterday']
                       else 0,
            axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status7'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status7']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status7_' + stock + '.csv', index=False)
        
    #乌云盖顶增强版 
    def status8(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #前序序列处于上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] else 0,
            axis = 1
        )
        
        #计算t-1日相关价格
        df['open_yesterday'] = df['open'].shift(1)
        df['close_yesterday'] = df['close'].shift(1)
        df['high_yesterday'] = df['high'].shift(1)
        
        #定义乌云盖顶增强版
        df['signal_2'] = df.apply(
            lambda x:1 if x['close_yesterday'] > x['open_yesterday']
                          and x['close'] < x['open']
                          and x['open'] > x['high_yesterday']
                          and x['close'] < 0.5 * (x['open_yesterday'] + x['close_yesterday'])
                       else 0,
            axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status7'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status7']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status7_' + stock + '.csv', index=False)
    
    #刺透形态    
    def status9(self,x,y,z):
        df = self.data.copy()
        
        #计算之前日期的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(x) + df['close'].shift(x))
        df['mean-3'] = 0.5 * (df['open'].shift(y) + df['close'].shift(y))
        df['mean-5'] = 0.5 * (df['open'].shift(z) + df['close'].shift(z))
        
        #前序序列处于下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['mean-1'] < x['mean-3'] and x['mean-3'] < x['mean-5'] else 0,
            axis = 1
        )
        
        #计算t-1日相关价格
        df['open_yesterday'] = df['open'].shift(1)
        df['close_yesterday'] = df['close'].shift(1)
        df['low_yesterday'] = df['low'].shift(1)
        
        #定义刺透形态
        df['signal_2'] = df.apply(
            lambda x:1 if x['close_yesterday'] < x['open_yesterday']
                          and x['close'] > x['open']
                          and x['open'] > x['low_yesterday']
                          and x['close'] > 0.5 * (x['open_yesterday'] + x['close_yesterday'])
                       else 0,
            axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status9'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status9']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status9_' + stock + '.csv', index=False)

       
if __name__ == '__main__':
    startdate = '2016/1/25'
    enddate = '2018/1/25'
    stock = '000001'
    cal = CalSignal(startdate, enddate)    
    # cal.status1(1,3,5) 
    # cal.status3(1,3,5)
    # cal.status7(1,3,5)
    # cal.status9(1,3,5)