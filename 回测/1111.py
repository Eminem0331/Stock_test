# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import tushare as ts
import os
from public_fuctions import *


class CalSignal(object):
    def __init__(self, start_date, end_date):
        self.path = '~/Desktop/stock/'
        self.start_date = start_date
        self.end_date = end_date
        for i in range(20):
            try:
                df = ts.get_hist_data(stock[i],start=startdate,end=enddate)
                df.to_csv(self.path+'%s.csv'%i)
            except:
                pass

    #多头排列，s, m, l对应短、中、长期, a是信号求和的期间，b是信号求和后确认的个数
    def status1(self, s, m, l, a, b):
        self.path = '~/Desktop/stock/'
        for i in range(20):
            self.tolerance_rate = 0.7
            data = pd.read_csv(self.path + '%s.csv' % i)
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
            data = data[data['date'] >= self.start_date]
            print(data)
            data.to_csv(self.path + 'status1_' + stock[i] + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)


if __name__ == '__main__':
    startdate = '2015/01/01'
    enddate = '2017/12/31'
    bench = ts.get_stock_basics()
    bench.to_csv('~/Desktop/bench.csv')
    stock = pd.read_csv('~/Desktop/bench.csv', dtype=str)
    stock = stock.loc[:, ['code']]
    stock = list(stock['code'])
    cal = CalSignal(startdate, enddate)
    cal.status1(5, 10, 20, 20, 0.03)
