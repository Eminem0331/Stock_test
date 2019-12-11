# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import tushare as ts
import os
from public_fuctions import *


class CalSignal(object):
    def __init__(self, start_date, end_date):
        self.path = '~/Desktop/stock'
        self.nn = []
        self.stock = []
        self.tolerance_rate = 0.7
        for i in range(20):
            df = ts.get_hist_data(stock[i],start=startdate,end=enddate)
            df.to_csv(self.path+'%s.csv'%i)

    def status1(self, s, m, l, b):
        signal_list = []
        
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
            data['signal2'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)

            data['mas_shift'] = data['mas'].shift(1)
            data['mam_shift'] = data['mam'].shift(1)
            data['mal_shift'] = data['mal'].shift(1)
            data['signal3'] = data.apply(lambda x: 1 if (x['mas'] > x['mas_shift'] and x['mam'] > x['mam_shift'] and
                                                     x['mal'] > x['mal_shift']) else 0, axis=1)

            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data = data.loc[:, ['signal','close','open','trading_date']]
            #将信号存在第i组holding time下
            signal_list.append(data)
            save_siganl(signal_list,'average_record/status1')
        for a in self.holding_time_list:
            rate = []#胜率
            times = []#交易次数
            ratio = []#盈亏比
            for data in signal_list:

                data['signal_count'] = data['signal'].rolling(a, round(a * self.tolerance_rate)).sum()
                data['status'] = data.apply(lambda x: 1 if x['signal_count'] > b else 0, axis=1)
                status1 = list(data['status'])
                status1.append(0)
                open_price = list(data['open'])
                #print(len(open_price),len(status1))
                # 回测
                #sfs = back_test(status1, close)
                sfs = back_test2(status1, open_price)
                # 计算信号胜率, 1为看多策略，-1为看空策略
                r = count_rate(sfs, 1)
                win_loss_ratio = count_win_loss_ratio(np.array(sfs), 1)
                rate.append(r)
                times.append(len(sfs))
                ratio.append(win_loss_ratio)
            s = [self.stocks,rate,times,ratio]
            jg = pd.DataFrame(s).T
            jg.to_excel('ans/holding_time=%s/status1_%s.xlsx'%(a,a), index=False, header=None)

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
    # cal.status2(5, 10, 20, 7, 0.03)
    # cal.status3(5, 10, 20, 7, 2, 0.5)