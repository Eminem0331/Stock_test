# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os

class CalSignal(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        # rolling时最少存在的数据比例
        self.tolerance_rate = 0.7
        self.path = os.path.dirname(os.path.abspath(__file__)) + '//'
        self.data = pd.read_csv(self.path + stock + '.csv')
    
    #启明星形态，a是收盘价比例，初始值为0.001，b是t-1日开收盘价差的比例，初始值为0.8    
    def status1(self,a,b):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['diff_oc_-1'] = df['open-1'] - df['close-1']
        df['diff_oc'] = df['open'] - df['close']
        df['open+1'] = df['open'].shift(-1)
        df['close+1'] = df['close'].shift(-1)
        
        #计算t-1,t-3,t-5日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        
        #判断下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] < x['close-2'] and x['close-2'] < x['close-3']
                       or x['mean-1'] < x['mean-3'] and x['mean-3'] < x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t-1日k线判断：
        df['signal_2'] = df.apply(
            lambda x:1 if x['close-1'] < x['open-1'] and x['diff_oc_-1'] > a * x['close-1']
                       else 0,
                   axis = 1,
        )
        
        #t日k线判断：
        df['signal_3'] = df.apply(
            lambda x:1 if x['close'] < x['open'] and x['open'] < x['close-1'] and x['diff_oc'] < b * x['diff_oc_-1']
                       else 0,
                   axis = 1
        )
        
        #t+1日k线判断：
        df['signal_4'] = df.apply(
            lambda x:1 if x['close+1'] > x['open+1'] and x['close+1'] > x['close-1']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3'] * df['signal_4']
        df['status1'] = df['signal'].shift(1)
        df = df.loc[:, ['date', 'open','high','low','close', 'status1']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status1_' + stock + '.csv', index=False)
        
    #黄昏星形态，a是开盘价比例，初始值为0.001，b是t-1日开收盘价差的比例，初始值为0.8    
    def status2(self,a,b):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['diff_oc_-1'] = df['open-1'] - df['close-1']
        df['diff_co_-1'] = df['close-1'] - df['open-1']
        df['diff_oc'] = df['open'] - df['close']
        df['diff_co'] = df['close'] - df['open']
        df['open+1'] = df['open'].shift(-1)
        df['close+1'] = df['close'].shift(-1)
        df['diff_oc_abs'] = abs(df['diff_oc'])
        
        #计算开收盘均价
        df['mean'] = 0.5 * (df['open'] + df['close'])
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))        
        
        #判断上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] > x['close-2'] and x['close-2'] > x['close-3']
                       or x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t-1日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['close-1'] > x['open-1'] and x['diff_co_-1'] > a * x['open-1']
                       else 0,
                   axis = 1,
        )
        
        #t日k线判断
        df['signal_3'] = df.apply(
            lambda x:1 if x['close'] > x['open'] and x['open'] > x['close-1'] and x['diff_co'] < b * x['diff_co_-1']
                       else 0,
                   axis = 1
        )
        
        #t+1日k线判断：
        df['signal_4'] = df.apply(
            lambda x:1 if x['close+1'] < x['open+1'] and x['close+1'] < x['close-1']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3'] * df['signal_4']
        df['status2'] = df['signal'].shift(1)
        df = df.loc[:, ['date', 'open','high','low','close', 'status2']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status2_' + stock + '.csv', index=False)
    
    #黄昏星形态弱化版本,a是开盘价比例，初始值为0.001，b是t-1日开收盘价差的比例，初始值为0.8 
    def status3(self,a,b):
        df = self.data.copy()
       
       #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['diff_oc_-1'] = df['open-1'] - df['close-1']
        df['diff_co_-1'] = df['close-1'] - df['open-1']
        df['diff_oc'] = df['open'] - df['close']
        df['diff_co'] = df['close'] - df['open']
        df['open+1'] = df['open'].shift(-1)
        df['close+1'] = df['close'].shift(-1)
        df['diff_oc_abs'] = abs(df['diff_oc'])
        
        #计算开收盘均价
        df['mean'] = 0.5 * (df['open'] + df['close'])
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))        
        
        #判断上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] > x['close-2'] and x['close-2'] > x['close-3']
                       or x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t-1日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['close-1'] > x['open-1'] and x['diff_co_-1'] > a * x['open-1']
                       else 0,
                   axis = 1,
        )
        
        #t日k线形态判断
        df['signal_3'] = df.apply(
            lambda x:1 if x['mean'] > x['mean-1'] and x['diff_oc_abs'] < b * x['diff_co_-1']
                       else 0,
                   axis = 1
        )
        
        #t+1日k线判断：
        df['signal_4'] = df.apply(
            lambda x:1 if x['close+1'] < x['open+1'] and x['close+1'] < x['close-1']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3'] * df['signal_4']
        df['status3'] = df['signal'].shift(1)
        df = df.loc[:, ['date', 'open','high','low','close', 'status3']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status3_' + stock + '.csv', index=False)
    
    #十字启明星形态,a和ｂ分别是收盘价和开盘价的比例，初始值为0.001  
    def status4(self,a,b):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['diff_oc_-1'] = df['open-1'] - df['close-1']
        df['open+1'] = df['open'].shift(-1)
        df['close+1'] = df['close'].shift(-1)
        
        #计算t-1,t-3,t-5日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])
        
        #判断下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] < x['close-2'] and x['close-2'] < x['close-3']
                       or x['mean-1'] < x['mean-3'] and x['mean-3'] < x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t-1日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['close-1'] < x['open-1'] and x['diff_oc_-1'] > a * x['close-1']
                       else 0,
                   axis =1
        )
        
        #t日k线判断
        df['signal_3'] = df.apply(
            lambda x:1 if x['box'] < a * x['open'] and x['upline'] > x['box'] and x['downline'] > x['box']
                       else 0,
                   axis = 1
        )
        
        #t+1日k线判断：
        df['signal_4'] = df.apply(
            lambda x:1 if x['close+1'] > x['open+1'] and x['close+1'] > x['close-1']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3'] * df['signal_4']
        df['status4'] = df['signal'].shift(1)
        df = df.loc[:, ['date', 'open','high','low','close', 'status4']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status4_' + stock + '.csv', index=False)
        
    #十字启明星变形（弃婴底部形态），a和ｂ分别是收盘价和开盘价的比例，初始值为0.001  
    def status5(self,a,b):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['diff_oc_-1'] = df['open-1'] - df['close-1']
        df['open+1'] = df['open'].shift(-1)
        df['close+1'] = df['close'].shift(-1)
        df['low-1'] = df['low'].shift(1)
        
        #计算t-1,t-3,t-5日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])
        
        #判断下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] < x['close-2'] and x['close-2'] < x['close-3']
                       or x['mean-1'] < x['mean-3'] and x['mean-3'] < x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t-1日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['close-1'] < x['open-1'] and x['diff_oc_-1'] > a * x['close-1']
                       else 0,
                   axis =1
        )
        
        #t日k线判断
        df['signal_3'] = df.apply(
            lambda x:1 if x['box'] < a * x['open'] and x['upline'] > x['box'] and x['downline'] > x['box'] and x['high'] < x['low-1']
                       else 0,
                   axis = 1
        )
        
        #t+1日k线判断：
        df['signal_4'] = df.apply(
            lambda x:1 if x['close+1'] > x['open+1'] and x['close+1'] > x['close-1']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3'] * df['signal_4']
        df['status5'] = df['signal'].shift(1)
        df = df.loc[:, ['date', 'open','high','low','close', 'status5']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status5_' + stock + '.csv', index=False)
        
    #十字黄昏星形态,a是开盘价的比例，初始值为0.001  
    def status6(self,a):
        df = self.data.copy()

        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['diff_oc_-1'] = df['open-1'] - df['close-1']
        df['diff_co_-1'] = df['close-1'] - df['open-1']
        df['open+1'] = df['open'].shift(-1)
        df['close+1'] = df['close'].shift(-1)
        df['low-1'] = df['low'].shift(1)
        
        #计算t-1,t-3,t-5日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])       
        
        #判断上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] > x['close-2'] and x['close-2'] > x['close-3']
                       or x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t-1日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['close'] > x['open'] and x['diff_co_-1'] > a * x['open']
                       else 0,
                   axis = 1
        )
        
        #t日k线判断
        df['signal_3'] = df.apply(
            lambda x:1 if x['box'] < a * x['open'] and x['upline'] > x['box'] and x['downline'] > x['box'] 
                       else 0,
                   axis = 1
        )
        
        #t+1日k线判断：
        df['signal_4'] = df.apply(
            lambda x:1 if x['close+1'] < x['open+1'] and x['close+1'] < x['close-1']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3'] * df['signal_4']
        df['status6'] = df['signal'].shift(1)
        df = df.loc[:, ['date', 'open','high','low','close', 'status6']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status6_' + stock + '.csv', index=False)
        
    #十字黄昏星变形（弃婴顶部形态）,a是开盘价的比例，初始值为0.001  
    def status7(self,a):
        df = self.data.copy()

        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['diff_oc_-1'] = df['open-1'] - df['close-1']
        df['diff_co_-1'] = df['close-1'] - df['open-1']
        df['open+1'] = df['open'].shift(-1)
        df['close+1'] = df['close'].shift(-1)
        df['low-1'] = df['low'].shift(1)
        df['high-1'] = df['high'].shift(1)
        
        #计算t-1,t-3,t-5日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])

        #判断上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] > x['close-2'] and x['close-2'] > x['close-3']
                       or x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t-1日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['close'] > x['open'] and x['diff_co_-1'] > a * x['open']
                       else 0,
                   axis = 1
        )
        
        #t日k线判断
        df['signal_3'] = df.apply(
            lambda x:1 if x['box'] < a * x['open'] and x['upline'] > x['box'] and x['downline'] > x['box'] and x['low'] > x['high-1'] 
                       else 0,
                   axis = 1
        )
        
        #t+1日k线判断：
        df['signal_4'] = df.apply(
            lambda x:1 if x['close+1'] < x['open+1'] and x['close+1'] < x['close-1']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3'] * df['signal_4']
        df['status7'] = df['signal'].shift(1)
        df = df.loc[:, ['date', 'open','high','low','close', 'status7']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status7_' + stock + '.csv', index=False)
        
    #流星形态(非跳空版本),a,b,c的初始值分别是2,0.003,0.5
    def status8(self,a,b,c):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        
        #计算t-1,t-3,t-5日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])
        
        #判断上涨趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] > x['close-2'] and x['close-2'] > x['close-3']
                       or x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['upline'] > a * x['box'] and x['box'] < b * x['open'] and x['downline'] < c * x['box']
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status8'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status8']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status8_' + stock + '.csv', index=False)
        
    #流星形态(跳空版本),a,b,c的初始值分别是2,0.003,0.5
    def status9(self,a,b,c):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['min_oc'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'], axis = 1)
        df['max_oc_-1'] = df.apply(lambda x:x['open-1'] if x['open-1'] > x['close-1'] else x['close-1'], axis = 1)
        
        
        #计算t-1,t-3,t-5日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])
        
        #判断上涨趋势
        df['signal_1'] = df.apply(lambda x:1 if x['close-1'] > x['close-2'] and x['close-2'] > x['close-3']
                       or x['mean-1'] > x['mean-3'] and x['mean-3'] > x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['upline'] > a * x['box'] and x['box'] < b * x['open'] and x['downline'] < c * x['box'] and x['min_oc'] > x['max_oc_-1']  
                       else 0,
                   axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] 
        df['status9'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status9']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status9_' + stock + '.csv', index=False)        
        
    #倒锤子形态(非跳空版本),a,b,c的初始值分别是2,0.003,0.5
    def status10(self,a,b,c):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['min_oc'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'], axis = 1)
        df['max_oc_-1'] = df.apply(lambda x:x['open-1'] if x['open-1'] > x['close-1'] else x['close-1'], axis = 1)
        
        
        #计算t-1,t,t-3,t-5,t+1日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        df['mean'] = 0.5 * (df['open'] + df['close'])
        df['mean+1'] = 0.5 * (df['open'].shift(-1) + df['close'].shift(-1))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])
        
        #判断下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] < x['close-2'] and x['close-2'] < x['close-3']
                       or x['mean-1'] < x['mean-3'] and x['mean-3'] < x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['upline'] > a * x['box'] and x['box'] < b * x['open'] and x['downline'] < c * x['box'] and x['min_oc'] > x['max_oc_-1']  
                       else 0,
                   axis = 1
        )
        
        #t+1日验证信号
        df['signal_3'] = df.apply(
             lambda x:1 if x['mean+1'] > x['mean']
                        else 0,
                    axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3']
        df['status10'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status10']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status10_' + stock + '.csv', index=False)  

    #倒锤子形态(跳空版本),a,b,c的初始值分别是2,0.003,0.5
    def status11(self,a,b,c):
        df = self.data.copy()
        
        #计算开收盘价格
        df['close-1'] = df['close'].shift(1)
        df['close-2'] = df['close'].shift(2)
        df['close-3'] = df['close'].shift(3)
        df['open-1'] = df['open'].shift(1)
        df['open+1'] = df['open'].shift(-1)
        df['min_oc'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'], axis = 1)
        df['max_oc'] = df.apply(lambda x:x['open'] if x['open'] > x['close'] else x['close'], axis = 1)
        df['max_oc_-1'] = df.apply(lambda x:x['open-1'] if x['open-1'] > x['close-1'] else x['close-1'], axis = 1)
        
        #计算t-1,t,t-3,t-5,t+1日的开收盘均价
        df['mean-1'] = 0.5 * (df['open'].shift(1) + df['close'].shift(1))
        df['mean-3'] = 0.5 * (df['open'].shift(3) + df['close'].shift(3))
        df['mean-5'] = 0.5 * (df['open'].shift(5) + df['close'].shift(5))
        df['mean'] = 0.5 * (df['open'] + df['close'])
        df['mean+1'] = 0.5 * (df['open'].shift(-1) + df['close'].shift(-1))
        
        #计算上下影线、箱体
        df['upline'] = df['high'] - df.apply(lambda x:x['open'] if x['open']>x['close'] else x['close'],axis = 1)
        df['downline'] = df.apply(lambda x:x['open'] if x['open'] < x['close'] else x['close'],axis = 1) - df['low']
        df['box'] = abs(df['open'] - df['close'])
        
        #判断下跌趋势
        df['signal_1'] = df.apply(
            lambda x:1 if x['close-1'] < x['close-2'] and x['close-2'] < x['close-3']
                       or x['mean-1'] < x['mean-3'] and x['mean-3'] < x['mean-5'] 
                       else 0,
                   axis = 1
        )
        
        #t日k线判断
        df['signal_2'] = df.apply(
            lambda x:1 if x['upline'] > a * x['box'] and x['box'] < b * x['open'] and x['downline'] < c * x['box'] and x['min_oc'] > x['max_oc_-1']  
                       else 0,
                   axis = 1
        )
        
        #t+1日验证信号
        df['signal_3'] = df.apply(
             lambda x:1 if x['open+1'] > x['max_oc']
                        else 0,
                    axis = 1
        )
        
        df['signal'] = df['signal_1'] * df['signal_2'] * df['signal_3']
        df['status11'] = df['signal']
        df = df.loc[:, ['date', 'open','high','low','close', 'status11']]
        df = df[df['date'] >= self.start_date]
        print(df)
        df.to_csv(self.path + 'status11_' + stock + '.csv', index=False)  



        
if __name__ == '__main__':
    startdate = '2016/2/1'
    enddate = '2018/1/30'
    stock = '000016'
    cal = CalSignal(startdate, enddate) 
    # cal.status1(0.001,0.8)
    # cal.status2(0.001,0.8)
    # cal.status3(0.001,0.8)
    # cal.status4(0.001,0.001)
    # cal.status6(0.001)
    # cal.status8(2,0.001,1)
    # cal.status10(2,0.003,0.5)
    # cal.status11(2,0.003,0.5)
    
