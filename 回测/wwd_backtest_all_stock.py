# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
from public_fuctions import *
import pickle

class CalSignal(object):
    def __init__(self, start_date, end_date, stocks, stocks_data):
        self.stocks_data = {}
        self.stocks =[]
        for stock in stocks:
            #回測范围
            test_day = list(map(lambda x: True if start_date <= x and x <= end_date else False, stocks_data[stock]['trading_date']))
            self.stocks_data[stock] = stocks_data[stock][test_day]
            self.stocks_data[stock] = self.stocks_data[stock].reset_index()
            #删掉一些数据量很小的股票
            if len(self.stocks_data[stock]['close']) > 100:
                self.stocks.append(stock)
        self.tolerance_rate = 0.7


    #多头排列，s, m, l对应短、中、长期, a是持仓时间，b是信号求和后确认的个数
    def status1(self, s, m, l, a, b):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        print()
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
        # 较前日上涨
            data['close_shift'] = data['close'].shift(1)
            data['signal1'] = data.apply(lambda x: 1 if x['close'] > x['close_shift'] else 0, axis=1)

        # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)

            data['mas_shift'] = data['mas'].shift(1)
            data['mam_shift'] = data['mam'].shift(1)
            data['mal_shift'] = data['mal'].shift(1)
            data['signal3'] = data.apply(lambda x: 1 if (x['mas'] > x['mas_shift'] and x['mam'] > x['mam_shift'] and
                                                     x['mal'] > x['mal_shift']) else 0, axis=1)

            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data['status1'] = data.apply(lambda x: 1 if x['signal_count'] > b else 0, axis=1)
            data = data.loc[:, ['date', 'close', 'status1']]
            close = list(data['close'])
            status1 = list(data['status1'])
            status1.append(0)
            # 回测
            sfs = back_test(status1, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status1_%s.xlsx'%(a,a), index=False, header=None)
        

    # 空头排列，s, m, l对应短、中、长期, a是持仓时间，b是信号求和后确认的个数
    def status2(self, s, m, l, a, b):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 较前日下跌
            data['close_shift'] = data['close'].shift(1)
            data['signal1'] = data.apply(lambda x: 1 if x['close'] < x['close_shift'] else 0, axis=1)

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)

            data['mas_shift'] = data['mas'].shift(1)
            data['mam_shift'] = data['mam'].shift(1)
            data['mal_shift'] = data['mal'].shift(1)
            data['signal3'] = data.apply(lambda x: 1 if (x['mas'] < x['mas_shift'] and x['mam'] < x['mam_shift'] and
                                                         x['mal'] < x['mal_shift']) else 0, axis=1)

            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data['status2'] = data.apply(lambda x: 1 if x['signal_count'] > b else 0, axis=1)
            data = data.loc[:, ['date', 'close', 'status2']]
            close = list(data['close'])
            status2 = list(data['status2'])
            status2.append(0)
            # 回测
            sfs = back_test(status2, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status2_%s.xlsx'%(a,a), index=False, header=None)
        

    # 黄金交叉，s, m, l对应短、中、长期, a是持仓时间, t是sm发生后sl再次发生的间隔时间, n是与n日之前相比看是否跌了, per是跌幅
    def status3(self, s, m, l, a, t, n, per):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            # 较前日上涨
            data['close_shift'] = data['close'].shift(1)
            data['signal1'] = data.apply(lambda x: 1 if x['close'] > x['close_shift'] else 0, axis=1)
            # 短中长期均线

            data['mas'] = MA(data['close'], s, self.tolerance_rate).fillna(0)
            data['mam'] = MA(data['close'], m, self.tolerance_rate).fillna(0)
            data['mal'] = MA(data['close'], l, self.tolerance_rate).fillna(0)

            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']

            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])

            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            data['sm_count'] = data['sm_delta'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2'] = data.apply(lambda x: 1 if x['sm_count'] >= 1 and x['sl_delta'] == 1 else 0, axis=1)

            # 较n日前下跌
            data['close_shift_n'] = data['close'].shift(n)
            data['signal3'] = data.apply(lambda x: 1 if x['close'] / x['close_shift_n'] - 1 < -per else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data['status3'] = data.apply(lambda x: 1 if x['signal_count'] > 0 else 0, axis=1)
            
            data = data.loc[:, ['date', 'close', 'status3']]
            close = list(data['close'])
            status3 = list(data['status3'])
            status3.append(0)
            # 回测
            sfs = back_test(status3, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status3_%s.xlsx'%(a,a), index=False, header=None)
        
    # 死亡交叉，s, m, l对应短、中、长期, t是sm发生后sl再次发生的间隔时间, n是与n日之前相比看是否涨了, per是涨幅
    def status4(self, s, m, l, a, t, n, per):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            
            # 较前日下跌
            data['close_shift'] = data['close'].shift(1)
            data['signal1'] = data.apply(lambda x: 1 if x['close'] < x['close_shift'] else 0, axis=1)
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            data['sm_count'] = data['sm_delta'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2'] = data.apply(lambda x: 1 if x['sm_count'] <= -1 and x['sl_delta'] == -1 else 0, axis=1)
        
            # 较n日前上涨
            data['close_shift_n'] = data['close'].shift(n)
            data['signal3'] = data.apply(lambda x: 1 if x['close'] / x['close_shift_n'] - 1 > per else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data['status4'] = data.apply(lambda x: 1 if x['signal_count'] > 0 else 0, axis=1)
            data = data.loc[:, ['date', 'close', 'status4']]
            close = list(data['close'])
            status4 = list(data['status4'])
            status4.append(0)
            # 回测
            sfs = back_test(status4, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status4_%s.xlsx'%(a,a), index=False, header=None)
        
        # 银山谷, s, m, l对应短、中、长期, a是持仓时间， t是交叉间隔的最大时间, n是银山谷与之前山谷的最小间隔时间
    def status5(self, s, m, l, a, t, n):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]  
            # 较前日上涨
            data['close_shift'] = data['close'].shift(1)
            data['signal1'] = data.apply(lambda x: 1 if x['close'] > x['close_shift'] else 0, axis=1)
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            
            data['cross_sm'] = data.apply(lambda x: 1 if x['sm_delta'] > 0 else 0, axis=1)
            data['cross_sm_count'] = data['cross_sm'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['cross_sl'] = data.apply(lambda x: 1 if (x['sl_delta'] > 0 and x['cross_sm_count'] >= 1) else 0, axis=1)
            data['cross_sl_count'] = data['cross_sl'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2'] = data.apply(lambda x: 1 if (x['ml_delta'] > 0 and x['cross_sl_count'] >= 1) else 0, axis=1)
            
            
            data['signal3'] = data['signal1'] * data['signal2']
            data['signal3_count'] = data['signal3'].rolling(n, round(n * self.tolerance_rate)).sum()
            data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal3_count'] == 1) else 0, axis=1)
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum() 
            data['status5'] = data.apply(lambda x: 1 if x['signal_count'] > 0 else 0, axis=1)
            
            data = data.loc[:, ['date', 'close', 'status5']]
            close = list(data['close'])
            status5 = list(data['status5'])
            status5.append(0)
            # 回测
            sfs = back_test(status5, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status5_%s.xlsx'%(a,a), index=False, header=None)
            
    
    # 金山谷, s, m, l对应短、中、长期,a是持仓时间， t是交叉间隔的最大时间, n是金山谷与银山谷之间最大间隔时间
    def status6(self, s, m, l, a, t, n):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            # 较前日上涨
            data['close_shift'] = data['close'].shift(1)
            data['signal1'] = data.apply(lambda x: 1 if x['close'] > x['close_shift'] else 0, axis=1)
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            
            data['cross_sm'] = data.apply(lambda x: 1 if x['sm_delta'] > 0 else 0, axis=1)
            data['cross_sm_count'] = data['cross_sm'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['cross_sl'] = data.apply(lambda x: 1 if (x['sl_delta'] > 0 and x['cross_sm_count'] >= 1) else 0, axis=1)
            data['cross_sl_count'] = data['cross_sl'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2'] = data.apply(lambda x: 1 if (x['ml_delta'] > 0 and x['cross_sl_count'] >= 1) else 0, axis=1)
            
            data['signal3'] = data['signal1'] * data['signal2']
            data['signal3_count'] = data['signal3'].rolling(n, round(n * self.tolerance_rate)).sum()
            data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal3_count'] == 2) else 0, axis=1)
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum() 
            data['status6'] = data.apply(lambda x: 1 if x['signal_count'] > 0 else 0, axis=1)
            data = data.loc[:, ['date', 'close', 'status6']]

            close = list(data['close'])
            status6 = list(data['status6'])
            status6.append(0)
            # 回测
            sfs = back_test(status6, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status6_%s.xlsx'%(a,a), index=False, header=None)
            
    # 死亡谷，s, m, l对应短、中、长期, a是持仓时间 ,t是交叉间隔的最大时间
    def status7(self, s, m, l, a, t):
        
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            
            # 较前日下跌
            data['close_shift'] = data['close'].shift(1)
            data['signal1'] = data.apply(lambda x: 1 if x['close'] < x['close_shift'] else 0, axis=1)
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            
            data['cross_sm'] = data.apply(lambda x: 1 if x['sm_delta'] < 0 else 0, axis=1)
            data['cross_sm_count'] = data['cross_sm'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['cross_sl'] = data.apply(lambda x: 1 if (x['sl_delta'] < 0 and x['cross_sm_count'] >= 1) else 0, axis=1)
            data['cross_sl_count'] = data['cross_sl'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2'] = data.apply(lambda x: 1 if (x['ml_delta'] < 0 and x['cross_sl_count'] >= 1) else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2']
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum() 
            data['status7'] = data.apply(lambda x: 1 if x['signal_count'] > 0 else 0, axis=1)
            
            data = data.loc[:, ['date', 'close', 'status7']]
            close = list(data['close'])
                
            status7 = list(data['status7'])
            status7.append(0)
            # 回测
            sfs = back_test(status7, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status7_%s.xlsx'%(a,a), index=False, header=None)

 # 首次粘合向上发散型，s, m, l对应短、中、长期, t是横盘粘合回溯天数, n是向上发散确认天数, count是判断横盘的交叉次数, u是上次向上发散间隔的最小时间
    def status8(self, s, m, l, a, t, n, count, u):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            
            # 均线缠绕粘合
            data['para1'] = abs(data['sm_delta']) + abs(data['sl_delta']) + abs(data['ml_delta'])
            data['para1_count'] = data['para1'].rolling(t, round(t * self.tolerance_rate)).sum().shift(-n)
            data['signal1'] = data.apply(lambda x: 1 if x['para1_count'] >= count else 0, axis=1)
            
            # 均线s>m>l
            data['para2'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para2_count'] = data['para2'].rolling(n, round(n * self.tolerance_rate)).sum()
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_UP(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_UP(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_UP(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['para2_count'] == n and x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)
                
            data['signal3'] = data['signal1'] * data['signal2']
            data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
            #x['signal2_count'] == 1:u时间内首次发散
            data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal2_count'] == 1) else 0, axis=1)
            
            data['status8'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data = data.loc[:, ['date', 'close', 'status8']]
            close = list(data['close'])
                
            status8 = list(data['status8'])
            status8.append(0)
            # 回测
            sfs = back_test(status8, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status8_%s.xlsx'%(a,a), index=False, header=None)            
    
    # 首次粘合向下发散型，s, m, l对应短、中、长期, t是横盘回溯天数, n是向下发散确认天数, count是判断粘合的交叉次数, u是上次向下发散间隔的最小时间
    def status9(self, s, m, l, a, t, n, count, u):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            
            # 均线缠绕粘合
            data['para1'] = abs(data['sm_delta']) + abs(data['sl_delta']) + abs(data['ml_delta'])
            data['para1_count'] = data['para1'].rolling(t, round(t * self.tolerance_rate)).sum().shift(-n)
            data['signal1'] = data.apply(lambda x: 1 if x['para1_count'] >= count else 0, axis=1)
            
            # 均线s<m<l
            data['para2'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)
            data['para2_count'] = data['para2'].rolling(n, round(n * self.tolerance_rate)).sum()
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_DOWN(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_DOWN(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_DOWN(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['para2_count'] == n and x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)

            data['signal3'] = data['signal1'] * data['signal2']
            data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
            data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal2_count'] == 1) else 0, axis=1)
            
            data['status9'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data = data.loc[:, ['date', 'close', 'status9']]
            close = list(data['close'])
                
            status9 = list(data['status9'])
            status9.append(0)
            # 回测
            sfs = back_test(status9, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status9_%s.xlsx'%(a,a), index=False, header=None)
    # 再次粘合向上发散型，s, m, l对应短、中、长期, t是横盘粘合回溯天数, n是向上发散确认天数, count是判断横盘的交叉次数, u是上次向上发散间隔的最大时间
    def status10(self, s, m, l, a, t, n, count, u):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']

            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            
            # 均线缠绕粘合
            data['para1'] = abs(data['sm_delta']) + abs(data['sl_delta']) + abs(data['ml_delta'])
            data['para1_count'] = data['para1'].rolling(t, round(t * self.tolerance_rate)).sum().shift(-n)
            data['signal1'] = data.apply(lambda x: 1 if x['para1_count'] >= count else 0, axis=1)
                
            # 均线s>m>l
            data['para2'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para2_count'] = data['para2'].rolling(n, round(n * self.tolerance_rate)).sum()
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_UP(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_UP(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_UP(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if (x['para2_count'] == n and x['para3'] == x['para4'] == x['para5'] == 1) else 0, axis=1)
            
            data['signal3'] = data['signal1'] * data['signal2']
            data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
            data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal2_count'] >= 2) else 0, axis=1)
            data['status10'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status10']]
            
            close = list(data['close'])
            status10 = list(data['status10'])
            status10.append(0)
            # 回测
            sfs = back_test(status10, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status10_%s.xlsx'%(a,a), index=False, header=None)
        
    # 再次粘合向下发散型，s, m, l对应短、中、长期, t是横盘粘合回溯天数, n是向下发散确认天数, count是判断横盘的交叉次数, u是上次向下发散间隔的最大时间
    def status11(self, s, m, l, a, t, n, count, u):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()

        n_count = 0
        
        for stock in stocks:
            n_count +=1

            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']

            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])

            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2

            # 均线缠绕粘合
            data['para1'] = abs(data['sm_delta']) + abs(data['sl_delta']) + abs(data['ml_delta'])
            data['para1_count'] = data['para1'].rolling(t, round(t * self.tolerance_rate)).sum().shift(-n)
            data['signal1'] = data.apply(lambda x: 1 if x['para1_count'] >= count else 0, axis=1)
            
            # 均线s<m<l
            data['para2'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)
            data['para2_count'] = data['para2'].rolling(n, round(n * self.tolerance_rate)).sum()
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_DOWN(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_DOWN(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_DOWN(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if (x['para2_count'] == n and
                                                         x['para3'] == x['para4'] == x['para5'] == 1) else 0, axis=1)

            data['signal3'] = data['signal1'] * data['signal2']
            data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
            data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal2_count'] >= 2) else 0, axis=1)
            data['status11'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data = data.loc[:, ['date', 'close', 'status11']]
            
            close = list(data['close'])
            status11 = list(data['status11'])
            status11.append(0)
            # 回测
            sfs = back_test(status11,close)
            # 计算信号胜率,1为看多策略，-1为看空策略
            r = count_rate(sfs,-1)
            
            rate.append(r)
            times.append(len(sfs))     
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status11_%s.xlsx'%(a,a), index=False, header=None)
    # 首次交叉向下发散型，s, m, l对应短、中、长期, t是向上发散回溯天数, n是发散确认天数, u是距离上次向下发散的最短时间
    def status12(self, s, m, l, a, t, n, u):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()

        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 均线s>m>l
            data['para1'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para1_count'] = data['para1'].rolling(n, round(n * self.tolerance_rate)).sum()
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_UP(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_UP(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_UP(data['ml'], n, self.tolerance_rate)
            data['signal1'] = data.apply(lambda x: 1 if (x['para1_count'] == n and
                                                         x['para3'] == x['para4'] == x['para5'] == 1) else 0, axis=1)
            
            # 均线s<m<l
            data['para2'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)
            data['para2_count'] = data['para2'].rolling(n, round(n * self.tolerance_rate)).sum()
            
            # 中短长均线间距逐日加大
            data['para6'] = JUDGE_DOWN(data['sm'], n, self.tolerance_rate)
            data['para7'] = JUDGE_DOWN(data['sl'], n, self.tolerance_rate)
            data['para8'] = JUDGE_DOWN(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if (x['para2_count'] == n and
                                                         x['para6'] == x['para7'] == x['para8'] == 1) else 0, axis=1)
            
            data['signal1_count'] = data['signal1'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
            #如果前t个时间内发生过连续向上发散，前u个时间内只发生这一次向下发散,此時也有一个确定的连续发散
            data['signal'] = data.apply(lambda x: 1 if (x['signal1_count'] >= 1 and x['signal2_count'] == 1 and x['signal2'] == 1) else 0, axis=1)
            data['status12'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data = data.loc[:, ['date', 'close', 'status12']]
            close = list(data['close'])
            status12 = list(data['status12'])
            status12.append(0)
            # 回测
            sfs = back_test(status12, close)
            # 计算信号胜率,1为看多策略，-1为看空策略
            r = count_rate(sfs,-1)
            
            rate.append(r)
            times.append(len(sfs))
            
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status12_%s.xlsx'%(a,a), index=False, header=None)
            
    # 再次交叉向下发散型，s, m, l对应短、中、长期, t是向上发散回溯天数, n是发散确认天数, u是距离上次向下发散的最长时间
    def status13(self, s, m, l, a, t, n, u):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 均线s>m>l
            data['para1'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para1_count'] = data['para1'].rolling(n, round(n * self.tolerance_rate)).sum()
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_UP(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_UP(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_UP(data['ml'], n, self.tolerance_rate)
            data['signal1'] = data.apply(lambda x: 1 if (x['para1_count'] == n and
                                                         x['para3'] == x['para4'] == x['para5'] == 1) else 0, axis=1)
            
            # 均线s<m<l
            data['para2'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)
            data['para2_count'] = data['para2'].rolling(n, round(n * self.tolerance_rate)).sum()
            
            # 中短长均线间距逐日加大
            data['para6'] = JUDGE_DOWN(data['sm'], n, self.tolerance_rate)
            data['para7'] = JUDGE_DOWN(data['sl'], n, self.tolerance_rate)
            data['para8'] = JUDGE_DOWN(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if (x['para2_count'] == n and
                                                         x['para6'] == x['para7'] == x['para8'] == 1) else 0, axis=1)
            
            data['signal1_count'] = data['signal1'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
            data['signal'] = data.apply(lambda x: 1 if (x['signal1_count'] >= 1 and x['signal2_count'] == 2 and x['signal2'] == 1) else 0,
                                        axis=1)
            data['status13'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data = data.loc[:, ['date', 'close', 'status13']]
            
            close = list(data['close'])
            status13 = list(data['status13'])
            status13.append(0)
            
            # 回测
            sfs = back_test(status13,close)
            # 计算信号胜率,1为看多策略，-1为看空策略
            r = count_rate(sfs,-1)
            
            rate.append(r)
            times.append(len(sfs))
            
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status13_%s.xlsx'%(a,a), index=False, header=None)
        
    # 上山爬坡型, s, m, l对应短、中、长期, t是回溯天数, x1,x2,x3分别对应短中长期均线差值的标准差阈值
    def status14(self, s, m, l, a, t, x1, x2, x3):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
            #前t天内，80%的天数都是满足短线在上，长线在下的形态
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / t >= 0.8 else 0, axis=1)
            
            # 均线值与前一日之差
            data['mas_delta'] = DELTA(data['mas'], 1)
            data['mam_delta'] = DELTA(data['mam'], 1)
            data['mal_delta'] = DELTA(data['mal'], 1)
            data['std_sd'] = STD(data['mas_delta'], t, self.tolerance_rate)
            data['std_md'] = STD(data['mam_delta'], t, self.tolerance_rate)
            data['std_ld'] = STD(data['mal_delta'], t, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['std_ld'] < x3 < x['std_md'] < x2 < x['std_sd'] < x1 else 0, axis=1)
            
            # 上涨趋势
            data['close_delta'] = DELTA(data['close'], t)
            data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] > 0 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status14'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data = data.loc[:, ['date', 'close', 'status14']]
            close = list(data['close'])
            status14 = list(data['status14'])
            status14.append(0)
            
            # 回测
            sfs = back_test(status14,close)
            
            # 计算信号胜率,1为看多策略，-1为看空策略
            r = count_rate(sfs,1)
            
            rate.append(r)
            times.append(len(sfs))
            
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status14_%s.xlsx'%(a,a), index=False, header=None)
        
    # 下山滑坡型, s, m, l对应短、中、长期, t是回溯天数, x1,x2,x3分别对应短中长期均线差值的标准差阈值
    def status15(self, s, m, l, a, t, x1, x2, x3):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)
            data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / t >= 0.8 else 0, axis=1)
            
            # 均线值与前一日之差
            data['mas_delta'] = DELTA(data['mas'], 1)
            data['mam_delta'] = DELTA(data['mam'], 1)
            data['mal_delta'] = DELTA(data['mal'], 1)
            data['std_sd'] = STD(data['mas_delta'], t, self.tolerance_rate)
            data['std_md'] = STD(data['mam_delta'], t, self.tolerance_rate)
            data['std_ld'] = STD(data['mal_delta'], t, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['std_ld'] < x3 < x['std_md'] < x2 < x['std_sd'] < x1 else 0, axis=1)
        
            # 下跌趋势
            data['close_delta'] = DELTA(data['close'], t)
            data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] < 0 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status15'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status15']]
            close = list(data['close'])
            status15 = list(data['status15'])
            status15.append(0)
            
            # 回测
            sfs = back_test(status15, close)
            
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs,-1)
            
            rate.append(r)
            times.append(len(sfs))
            
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status15_%s.xlsx'%(a,a), index=False, header=None)
    
    # 逐浪上升型, s, m, l对应短、中、长期, t是回溯天数
    def status16(self, s, m, l, a, t):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if (x['mas'] > x['mal'] and x['mam'] > x['mal']) else 0, axis=1)
            data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
            #60%的情況情况下，长均线托着中短均线
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / t >= 0.6 else 0, axis=1)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            data['cross_sm'] = data.apply(lambda x: 1 if x['sm_delta'] != 0 else 0, axis=1)
            data['cross_sm_count'] = data['cross_sm'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['cross_sl'] = data.apply(lambda x: 1 if x['sl_delta'] < 0 else 0, axis=1)
            data['cross_sl_count'] = data['cross_sl'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['cross_ml'] = data.apply(lambda x: 1 if x['ml_delta'] < 0 else 0, axis=1)
            data['cross_ml_count'] = data['cross_ml'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2'] = data.apply(lambda x: 1 if (x['cross_sm_count'] >= 5 and x['cross_sl_count'] <= 1 and
                                                         x['cross_ml_count'] <= 1) else 0, axis=1)

            # 上涨趋势
            data['close_delta'] = DELTA(data['close'], t)
            data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] > 0 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status16'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status16']]
            close = list(data['close'])
            status16 = list(data['status16'])
            status16.append(0)
            
            # 回测
            sfs = back_test(status16, close)
            
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs,1)
            
            rate.append(r)
            times.append(len(sfs))
            
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status16_%s.xlsx'%(a,a), index=False, header=None)
        
    # 逐浪下降型, s, m, l对应短、中、长期, t是回溯天数
    def status17(self, s, m, l, a, t):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if (x['mas'] < x['mal'] and x['mam'] < x['mal']) else 0, axis=1)
            data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / t >= 0.6 else 0, axis=1)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 不同周期的均线值之差的正负
            data['sm_sign'] = np.sign(data['sm'])
            data['sl_sign'] = np.sign(data['sl'])
            data['ml_sign'] = np.sign(data['ml'])
            
            # 计算交叉，1为上穿，-1为下穿，0为保持原上下关系
            data['sm_delta'] = DELTA(data['sm_sign'], 1) / 2
            data['sl_delta'] = DELTA(data['sl_sign'], 1) / 2
            data['ml_delta'] = DELTA(data['ml_sign'], 1) / 2
            data['cross_sm'] = data.apply(lambda x: 1 if x['sm_delta'] != 0 else 0, axis=1)
            data['cross_sm_count'] = data['cross_sm'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['cross_sl'] = data.apply(lambda x: 1 if x['sl_delta'] < 0 else 0, axis=1)
            data['cross_sl_count'] = data['cross_sl'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['cross_ml'] = data.apply(lambda x: 1 if x['ml_delta'] < 0 else 0, axis=1)
            data['cross_ml_count'] = data['cross_ml'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal2'] = data.apply(lambda x: 1 if (x['cross_sm_count'] >= 5 and x['cross_sl_count'] <= 1 and
                                                         x['cross_ml_count'] <= 1) else 0, axis=1)
            # 下跌趋势
            data['close_delta'] = DELTA(data['close'], t)
            data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] < 0 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status17'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status17']]
            close = list(data['close'])
            status17 = list(data['status17'])
            status17.append(0)
            
            # 回测
            sfs = back_test(status17, close)
            
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs,-1)
            
            rate.append(r)
            times.append(len(sfs))
            
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status17_%s.xlsx'%(a,a), index=False, header=None)
        
    # 加速上涨型, s, m, l对应短、中、长期, t是缓慢上涨天数, n是加速上涨天数
    def status18(self, s, m, l, a, t, n):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / (t + n) >= 0.6 else 0, axis=1)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_UP(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_UP(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_UP(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)
            
            # 上涨趋势加快:缓慢上涨区间的日均涨幅 < 快速上涨区间的日均涨幅
            data['close_shift_delta'] = DELTA(data['close'].shift(n), t) / t
            data['close_delta'] = DELTA(data['close'], n) / n
            data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] > x['close_shift_delta'] > 0 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status18'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status18']]
            close = list(data['close'])
            status18 = list(data['status18'])
            status18.append(0)
            
            # 回测
            sfs = back_test(status18, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status18_%s.xlsx'%(a,a), index=False, header=None)
        
    # 加速下跌型, s, m, l对应短、中、长期, t是缓慢下跌天数, n是加速下跌天数
    def status19(self, s, m, l, a, t, n):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)
            data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / (t + n) >= 0.6 else 0, axis=1)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_DOWN(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_DOWN(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_DOWN(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)
            
            # 下跌趋势加快
            data['close_shift_delta'] = DELTA(data['close'].shift(n), t) / t
            data['close_delta'] = DELTA(data['close'], n) / n
            data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] < x['close_shift_delta'] < 0 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status19'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status19']]
            close = list(data['close'])
            status19 = list(data['status19'])
            status19.append(0)
            
            # 回测
            sfs = back_test(status19, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status19_%s.xlsx'%(a,a), index=False, header=None)
    
    # 快速上涨型, s, m, l对应短、中、长期, n是快速上涨天数, ret是n日涨幅
    def status20(self, s, m, l, a, n, ret):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para_count'] = data['para'].rolling(n, round(n * self.tolerance_rate)).sum()
            #60%的天数是满足的
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / n >= 0.6 else 0, axis=1)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
        
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_UP(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_UP(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_UP(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)

            # 上涨趋势
            data['ret_n'] = DELTA(data['close'], n) / data['close'].shift(n)
            data['signal3'] = data.apply(lambda x: 1 if x['ret_n'] > ret else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status20'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status20']]
            close = list(data['close'])
            status20 = list(data['status20'])
            status20.append(0)
            
            # 回测
            sfs = back_test(status20, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status20_%s.xlsx'%(a,a), index=False, header=None)
            
    # 快速下跌型, s, m, l对应短、中、长期, n是快速下跌天数, ret是n日跌幅
    def status21(self, s, m, l, a, n, ret):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if x['mas'] < x['mam'] < x['mal'] else 0, axis=1)
            data['para_count'] = data['para'].rolling(n, round(n * self.tolerance_rate)).sum()
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / n >= 0.6 else 0, axis=1)
            
            # 不同周期的均线值之差
            data['sm'] = data['mas'] - data['mam']
            data['sl'] = data['mas'] - data['mal']
            data['ml'] = data['mam'] - data['mal']
            
            # 中短长均线间距逐日加大
            data['para3'] = JUDGE_DOWN(data['sm'], n, self.tolerance_rate)
            data['para4'] = JUDGE_DOWN(data['sl'], n, self.tolerance_rate)
            data['para5'] = JUDGE_DOWN(data['ml'], n, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)

            # 下跌趋势
            data['ret_n'] = DELTA(data['close'], n) / data['close'].shift(n)
            data['signal3'] = data.apply(lambda x: 1 if x['ret_n'] < -ret else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status21'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status21']]
            close = list(data['close'])
            status21 = list(data['status21'])
            status21.append(0)
            
            # 回测
            sfs = back_test(status21, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status21_%s.xlsx'%(a,a), index=False, header=None)
    
    # 烘云托月型, s, m, l对应短、中、长期, n是回溯时间, sigma是波动率的上限
    def status22(self, s, m, l, a, n, sigma):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            # 盘整
            data['std'] = STD(data['close'], n, self.tolerance_rate)
            data['signal1'] = data.apply(lambda x: 1 if x['std'] <= sigma else 0, axis=1)
            
            # 略微上涨
            data['delta'] = DELTA(data['close'], n)
            data['signal2'] = data.apply(lambda x: 1 if x['delta'] > 0 else 0, axis=1)
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if (x['mas'] > x['mal'] and x['mam'] > x['mal']) else 0, axis=1)
            data['para_count'] = data['para'].rolling(n, round(n * self.tolerance_rate)).sum()
            data['signal3'] = data.apply(lambda x: 1 if x['para_count'] / n >= 0.6 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status22'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status22']]
            close = list(data['close'])
            status22 = list(data['status22'])
            status22.append(0)
            
            # 回测
            sfs = back_test(status22, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status22_%s.xlsx'%(a,a), index=False, header=None)
    
    # 乌云密布型, s, m, l对应短、中、长期, n是回溯时间, sigma是波动率的上限
    def status23(self, s, m, l, a, n, sigma):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            # 盘整
            data['std'] = STD(data['close'], n, self.tolerance_rate)
            data['signal1'] = data.apply(lambda x: 1 if x['std'] <= sigma else 0, axis=1)
            
            # 略微下跌
            data['delta'] = DELTA(data['close'], n)
            data['signal2'] = data.apply(lambda x: 1 if x['delta'] < 0 else 0, axis=1)
            
            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['para'] = data.apply(lambda x: 1 if (x['mas'] < x['mal'] and x['mam'] < x['mal']) else 0, axis=1)
            data['para_count'] = data['para'].rolling(n, round(n * self.tolerance_rate)).sum()
            data['signal3'] = data.apply(lambda x: 1 if x['para_count'] / n >= 0.6 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data['status23'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status23']]
            close = list(data['close'])
            status23 = list(data['status23'])
            status23.append(0)
            
            # 回测
            sfs = back_test(status23, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status23_%s.xlsx'%(a,a), index=False, header=None)
        
    # 蛟龙出海型, s, m, l对应短、中、长期, t为回溯期, ret是最小跌幅
    def status24(self, s, m, l, a, t, ret):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['signal1'] = data.apply(lambda x: 1 if (x['open'] < min(x['mas'], x['mam'], x['mal']) <
                                                         max(x['mas'], x['mam'], x['mal']) < x['close']) else 0, axis=1)
            
            # 下跌或盘整后期
            data['ret'] = DELTA(data['close'], t) / data['close'].shift(t)
            data['signal2'] = data.apply(lambda x: 1 if x['ret'] < -ret else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2']
            data['status24'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status24']]
            close = list(data['close'])
            status24 = list(data['status24'])
            status24.append(0)
            
            # 回测
            sfs = back_test(status24, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, 1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status24_%s.xlsx'%(a,a), index=False, header=None)
    
    # 断头侧刀型, s, m, l对应短、中、长期, t为回溯期, ret是最小涨幅
    def status25(self, s, m, l, a, t, ret):
        rate = []
        times = []
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]

            # 短中长期均线
            data['mas'] = MA(data['close'], s, self.tolerance_rate)
            data['mam'] = MA(data['close'], m, self.tolerance_rate)
            data['mal'] = MA(data['close'], l, self.tolerance_rate)
            data['signal1'] = data.apply(lambda x: 1 if (x['open'] > max(x['mas'], x['mam'], x['mal']) >
                                                         min(x['mas'], x['mam'], x['mal']) > x['close']) else 0, axis=1)
            
            # 上涨或盘整后期
            data['ret'] = DELTA(data['close'], t) / data['close'].shift(t)
            data['signal2'] = data.apply(lambda x: 1 if x['ret'] > ret else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2']
            data['status25'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            
            data = data.loc[:, ['date', 'close', 'status25']]
            close = list(data['close'])
            status25 = list(data['status25'])
            status25.append(0)
            
            # 回测
            sfs = back_test(status25, close)
            # 计算信号胜率, 1为看多策略，-1为看空策略
            r = count_rate(sfs, -1)
            rate.append(r)
            times.append(len(sfs))
        s = [self.stocks,rate,times]
        jg = pd.DataFrame(s).T
        jg = jg.sort_values(by=[1],ascending=False)
        jg.to_excel('ans/holding_time=%s/status25_%s.xlsx'%(a,a), index=False, header=None)
    
if __name__ == '__main__':
    #preprocessing完成后，数据被存储在pickle文件中, 分别为股票代码（list），个股数据（dict）
    fr = open('data/stock_price.pickle', 'rb')  
    stocks = pickle.load(fr)[:]
    stocks_data = pickle.load(fr)
    fr.close
    
    startdate = 20020101
    enddate =   20180201
    cal = CalSignal(startdate, enddate, stocks, stocks_data)
    
    #设置持仓时间
    holding_time_list = [20]
    for holding_time in holding_time_list:
        print('holding_time=', holding_time)
        #多头排列, 空头排列, s, m, l对应短、中、长期, a是持仓时间，b是信号求和后确认的个数

        #cal.status1(5, 10, 20, holding_time, 0.03)
        #cal.status2(5, 10, 20, holding_time, 0.03)
            
        # 黄金交叉、死亡交叉，s, m, l对应短、中、长期, a是持仓时间, t是统计sm和sl交叉发生的时间, n是与n日之前相比看是否跌（漲）了, per是跌（漲）幅
        #cal.status3(5, 10, 20, holding_time, t=10, n=20, per=0.1)
        #cal.status4(5, 10, 20, holding_time, t=10, n=20, per=0.1)
        
        # 银山谷、金山谷、死亡谷, s, m, l对应短、中、长期, a是持仓时间, t是交叉间隔的最大时间, n是银山谷与之前山谷的最小间隔时间
        #cal.status5(5, 10, 20, holding_time, t=4, n=30)
        #cal.status6(5, 10, 20, holding_time, t=4, n=30)
        #cal.status7(5, 10, 20, holding_time, t=4)
        
        # 首次粘合向上发散型，首次粘合向下发散型,再次粘合向上发散型, 再次粘合向下发散型 , s, m, l对应短、中、长期, t是横盘粘合回溯天数, n是向上（向下）发散确认天数, count是判断横盘的交叉次数, u是上次向上（向下）发散间隔的最小时间
        #cal.status8(5, 10, 20, holding_time ,t=10, n=3, count=5, u=10)    
        #cal.status9(5, 10, 20, holding_time, t=10, n=3, count=5, u=10)
        #cal.status10(5, 10, 20, holding_time, t=10, n=3, count=5, u=10)
        #cal.status11(5, 10, 20, holding_time, t=10, n=3, count=5, u=10)
            
        # 首次交叉向下发散型, 再次交叉向下发散型, s, m, l对应短、中、长期, t是向上发散回溯天数, n是发散确认天数, u是距离上次向下发散的最短时间
        #cal.status12(5, 10, 20, holding_time, t=15, n=3, u=30)
        #cal.status13(5, 10, 20, holding_time, t=15, n=3, u=30)
            
        # 上山爬坡型,下山滑坡型 s, m, l对应短、中、长期, a是持仓时间，t是回溯天数, x1、x2、x3分别对应短中长期均线差值的标准差阈值
        #cal.status14(5, 10, 20, holding_time, t=10, x1=0.5, x2=0.3, x3=0.1)
        #cal.status15(5, 10, 20, holding_time, t=10, x1=0.5, x2=0.3, x3=0.1)
        
        # 逐浪上升型, 波浪下降型, s, m, l对应短、中、长期, t是回溯天数
        #cal.status16(5, 20, 60, holding_time, t=100)
        #cal.status17(5, 20, 60, holding_time, t=100)
        
        # 加速上涨型, 加速下跌型, s, m, l对应短、中、长期, t是缓慢上涨（下跌）天数, n是加速上涨（下跌）天数
        #cal.status18(5, 10, 20, holding_time, t=30, n=5)
        #cal.status19(5, 10, 20, holding_time, t=30, n=5)
        
        # 快速上涨型, 快速下跌型, s, m, l对应短、中、长期, n是快速上涨天数, ret是n日涨幅
        #cal.status20(5, 10, 20, holding_time, n=5, ret=0.06)
        cal.status21(5, 10, 20, holding_time, n=5, ret=0.06)
        
        # 烘云托月型,乌云密布型, s, m, l对应短、中、长期, n是回溯时间, sigma是波动率的上限
        #cal.status22(5, 10, 20, holding_time, n=10, sigma=0.2)
        #cal.status23(5, 10, 20, holding_time, n=10, sigma=0.2)
        
        # 蛟龙出海型, 断头侧刀, s, m, l对应短、中、长期, t为回溯期, ret是最小跌幅
        #cal.status24(5, 10, 20, holding_time, t=20, ret=0.03)
        #cal.status25(5, 10, 20, holding_time, t=20, ret=0.03)
        
        