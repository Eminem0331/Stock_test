# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import tushare as ts
import os
from public_fuctions import *


class CalSignal(object):
    def __init__(self, start_date, end_date):
        self.path = '~/Desktop/stock'
        self.nn=[]
        self.stock=[]
        self.tolerance_rate = 0.7
        for i in range(len(stock)-1):
            df = ts.get_hist_data(stock[i], start=start_date, end=end_date)
            if not df is None and len(df['close']) > 100:
                df = df.reset_index()
                self.nn.append(df)
                self.stock.append(stock[i])
        # print(len(self.nn))
        # print(len(self.stock))


    #多头排列，s, m, l对应短、中、长期, a是信号求和的期间，b是信号求和后确认的个数
    def status1(self, s, m, l, a, b):
        rate = []
        nn = self.nn.copy()
        stock = self.stock.copy()
        for i in range(len(stock)):
            data = nn[i]
            data = data.copy()
            data = data.sort_values(['date'])
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
            data = data.loc[:, ['date','close', 'status1']]
            close = list(data['close'])
            status1 = list(data['status1'])
            status1.append(0)
            sf = 0
            sfs = []
            for i in range(len(status1)-1):
                if status1[i] == 1:
                    if sf == 0:
                        first = close[i]
                        sf = sf+1
                    if status1[i + 1] == 0:
                        last = close[i]
                        sf = 0
                        sfs.append(last - first)
            #计算信号胜率
            num = 0
            if len(sfs)==0:
                r = -10
            else:
                for i in range(len(sfs)-1):
                    if sfs[i] > 0:
                        num = num+1
                r = num/len(sfs)
            rate.append(r)

        s = []
        s.append(self.stock)
        s.append(rate)
        jg = pd.DataFrame(s).T
        jg.to_excel('/Users/eminem/Desktop/stock/status1.xlsx',index=False, header=None)

    # 空头排列，s, m, l对应短、中、长期, a是信号求和的期间，b是信号求和后确认的个数
    def status2(self, s, m, l, a, b):
        rate = []
        nn = self.nn.copy()
        stock = self.stock.copy()
        for i in range(len(stock)):
            data = nn[i]
            data = data.copy()
            data = data.sort_values(['date'])
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

            data['signal'] = data['signal1'] * data['signal2']
            data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
            data['status2'] = data.apply(lambda x: 1 if x['signal_count'] > b else 0, axis=1)
            data = data.loc[:, ['date', 'close', 'status2']]
            close = list(data['close'])
            status2 = list(data['status2'])
            status2.append(0)
            sf = 0
            sfs = []
            for i in range(len(status2)-1):
                if status2[i] == 1:
                    if sf == 0:
                        first = close[i]
                        sf = sf+1
                    if status2[i + 1] == 0:
                        last = close[i]
                        sf = 0
                        sfs.append(last - first)
            #计算信号胜率
            num = 0
            if len(sfs)==0:
                r = -10
            else:
                for i in range(len(sfs)-1):
                    if sfs[i] < 0:
                        num = num+1
                r = num/len(sfs)
            rate.append(r)

        s = []
        s.append(stock)
        s.append(rate)
        jg = pd.DataFrame(s).T
        jg.to_excel('/Users/eminem/Desktop/stock/status2.xlsx',index=False, header=None)


    # 黄金交叉，s, m, l对应短、中、长期, t是统计sm和sl交叉发生的时间, n是与n日之前相比看是否跌了, per是跌幅
    def status3(self, s, m, l, t, n, per):
        rate = []
        nn = self.nn.copy()
        stock = self.stock.copy()
        for i in range(len(stock)):
            data = nn[i]
            data = data.copy()
            data = data.sort_values(['date'])
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
            data['status3'] = data['signal']
            data = data.loc[:, ['date', 'close', 'status3']]
            close = list(data['close'])
            status3 = list(data['status3'])
            status3.append(0)
            sf = 0
            sfs = []
            for i in range(len(status3) - 1):
                if status3[i] == 1:
                    if sf == 0:
                        first = close[i]
                        sf = sf + 1
                    if status3[i + 1] == 0:
                        last = close[i]
                        sf = 0
                        sfs.append(last - first)
            # 计算信号胜率
            num = 0
            if len(sfs) == 0:
                r = -10
            else:
                for i in range(len(sfs) - 1):
                    if sfs[i] > 0:
                        num = num + 1
                r = num / len(sfs)
            rate.append(r)
        s = []
        s.append(stock)
        s.append(rate)
        jg = pd.DataFrame(s).T
        jg.to_excel('/Users/eminem/Desktop/stock/status3.xlsx', index=False, header=None)



if __name__ == '__main__':
    startdate = '2015/01/01'
    enddate = '2017/12/31'
    bench = ts.get_stock_basics()
    bench = bench.reset_index()
    stock = bench.loc[:, ['code']]
    stock = stock.sort_values(['code'])
    stock = list(stock['code'])
    stock = stock[0:51]
    cal = CalSignal(startdate, enddate)
    cal.status1(5, 10, 20, 7, 0.03)
    cal.status2(5, 10, 20, 7, 0.03)
    cal.status3(5, 10, 20, 7, 2, 0.5)
