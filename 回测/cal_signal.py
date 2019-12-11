# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import os
from public_fuctions import *


class CalSignal(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        # rolling时最少存在的数据比例
        self.tolerance_rate = 0.7
        self.path = os.path.dirname(os.path.abspath(__file__)) + '//'
        self.data = pd.read_csv(self.path + stock + '.csv')

    # 多头排列，s, m, l对应短、中、长期, a是信号求和的期间，b是信号求和后确认的个数
    def status1(self, s, m, l, a, b):
        data = self.data.copy()

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
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status1_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 空头排列，s, m, l对应短、中、长期, a是信号求和的期间，b是信号求和后确认的个数
    def status2(self, s, m, l, a, b):
        data = self.data.copy()

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
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status2_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 黄金交叉，s, m, l对应短、中、长期, t是统计sm和sl交叉发生的时间, n是与n日之前相比看是否跌了, per是跌幅
    def status3(self, s, m, l, t, n, per):
        data = self.data.copy()

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
        data['sm_count'] = data['sm_delta'].rolling(t, round(t * self.tolerance_rate)).sum()
        data['signal2'] = data.apply(lambda x: 1 if x['sm_count'] >= 1 and x['sl_delta'] == 1 else 0, axis=1)

        # 较n日前下跌
        data['close_shift_n'] = data['close'].shift(n)
        data['signal3'] = data.apply(lambda x: 1 if x['close'] / x['close_shift_n'] - 1 < -per else 0, axis=1)

        data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
        data['status3'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status3']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status3_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 死亡交叉，s, m, l对应短、中、长期, t是统计sm和sl交叉发生的时间, n是与n日之前相比看是否涨了, per是涨幅
    def status4(self, s, m, l, t, n, per):
        data = self.data.copy()

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
        data['status4'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status4']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status4_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 银山谷, s, m, l对应短、中、长期, t是交叉间隔的最大时间, n是银山谷与之前山谷的最小间隔时间
    def status5(self, s, m, l, t, n):
        data = self.data.copy()

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
        data['cross_ml'] = data.apply(lambda x: 1 if (x['ml_delta'] > 0 and x['cross_sl_count'] >= 1) else 0, axis=1)
        data['cross_ml_count'] = data['cross_ml'].rolling(t, round(t * self.tolerance_rate)).sum()
        data['signal2'] = data.apply(lambda x: 1 if x['cross_ml_count'] >= 1 else 0, axis=1)

        data['signal3'] = data['signal1'] * data['signal2']
        data['signal3_count'] = data['signal3'].rolling(n, round(n * self.tolerance_rate)).sum()
        data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal3_count'] == 1) else 0, axis=1)
        data['status5'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status5']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status5_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 金山谷, s, m, l对应短、中、长期, t是交叉间隔的最大时间, n是金山谷与银山谷之间最大间隔时间
    def status6(self, s, m, l, t, n):
        data = self.data.copy()

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
        data['cross_ml'] = data.apply(lambda x: 1 if (x['ml_delta'] > 0 and x['cross_sl_count'] >= 1) else 0, axis=1)
        data['cross_ml_count'] = data['cross_ml'].rolling(t, round(t * self.tolerance_rate)).sum()
        data['signal2'] = data.apply(lambda x: 1 if x['cross_ml_count'] >= 1 else 0, axis=1)

        data['signal3'] = data['signal1'] * data['signal2']
        data['signal3_count'] = data['signal3'].rolling(n, round(n * self.tolerance_rate)).sum()
        data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal3_count'] == 2) else 0, axis=1)
        data['status6'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status6']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status6_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 死亡谷，s, m, l对应短、中、长期, t是交叉间隔的最大时间
    def status7(self, s, m, l, t):
        data = self.data.copy()

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
        data['cross_ml'] = data.apply(lambda x: 1 if (x['ml_delta'] < 0 and x['cross_sl_count'] >= 1) else 0, axis=1)
        data['cross_ml_count'] = data['cross_ml'].rolling(t, round(t * self.tolerance_rate)).sum()
        data['signal2'] = data.apply(lambda x: 1 if x['cross_ml_count'] >= 1 else 0, axis=1)

        data['signal'] = data['signal1'] * data['signal2']
        data['status7'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status7']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status7_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 首次粘合向上发散型，s, m, l对应短、中、长期, t是横盘粘合回溯天数, n是向上发散确认天数, count是判断横盘的交叉次数, u是上次向上发散间隔的最小时间
    def status8(self, s, m, l, t, n, count, u):
        data = self.data.copy()

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
        data['signal2'] = data.apply(
            lambda x: 1 if x['para2_count'] == n and x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)

        data['signal3'] = data['signal1'] * data['signal2']
        data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
        data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal2_count'] == 1) else 0, axis=1)
        data['status8'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status8']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status8_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 首次粘合向下发散型，s, m, l对应短、中、长期, t是横盘回溯天数, n是向下发散确认天数, count是判断粘合的交叉次数, u是上次向下发散间隔的最小时间
    def status9(self, s, m, l, t, n, count, u):
        data = self.data.copy()

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
        data['signal2'] = data.apply(
            lambda x: 1 if x['para2_count'] == n and x['para3'] == x['para4'] == x['para5'] == 1 else 0, axis=1)

        data['signal3'] = data['signal1'] * data['signal2']
        data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
        data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal2_count'] == 1) else 0, axis=1)
        data['status9'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status9']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status9_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 再次粘合向上发散型，s, m, l对应短、中、长期, t是横盘粘合回溯天数, n是向上发散确认天数, count是判断横盘的交叉次数, u是上次向上发散间隔的最大时间
    def status10(self, s, m, l, t, n, count, u):
        data = self.data.copy()

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
        data['signal2'] = data.apply(lambda x: 1 if (x['para2_count'] == n and
                                                     x['para3'] == x['para4'] == x['para5'] == 1) else 0, axis=1)

        data['signal3'] = data['signal1'] * data['signal2']
        data['signal2_count'] = data['signal2'].rolling(u, round(u * self.tolerance_rate)).sum()
        data['signal'] = data.apply(lambda x: 1 if (x['signal3'] == 1 and x['signal2_count'] >= 2) else 0, axis=1)
        data['status10'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status10']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status10_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 再次粘合向下发散型，s, m, l对应短、中、长期, t是横盘粘合回溯天数, n是向下发散确认天数, count是判断横盘的交叉次数, u是上次向下发散间隔的最大时间
    def status11(self, s, m, l, t, n, count, u):
        data = self.data.copy()

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
        data['status11'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status11']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status11_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 首次交叉向下发散型，s, m, l对应短、中、长期, t是向上发散回溯天数, n是发散确认天数, u是距离上次向下发散的最短时间
    def status12(self, s, m, l, t, n, u):
        data = self.data.copy()

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
        data['signal'] = data.apply(lambda x: 1 if (x['signal1_count'] >= 1 and x['signal2_count'] == 1) else 0, axis=1)
        data['status12'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status12']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status12_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 再次交叉向下发散型，s, m, l对应短、中、长期, t是向上发散回溯天数, n是发散确认天数, u是距离上次向下发散的最长时间
    def status13(self, s, m, l, t, n, u):
        data = self.data.copy()

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
        data['signal'] = data.apply(lambda x: 1 if (x['signal1_count'] >= 1 and x['signal2_count'] == 2) else 0,
                                    axis=1)
        data['status13'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status13']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status13_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 上山爬坡型, s, m, l对应短、中、长期, t是回溯天数, abc分别对应短中长期均线差值的标准差阈值
    def status14(self, s, m, l, t, a, b, c):
        data = self.data.copy()

        # 短中长期均线
        data['mas'] = MA(data['close'], s, self.tolerance_rate)
        data['mam'] = MA(data['close'], m, self.tolerance_rate)
        data['mal'] = MA(data['close'], l, self.tolerance_rate)
        data['para'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
        data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
        data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / t >= 0.8 else 0, axis=1)

        # 均线值与前一日之差
        data['mas_delta'] = DELTA(data['mas'], 1)
        data['mam_delta'] = DELTA(data['mam'], 1)
        data['mal_delta'] = DELTA(data['mal'], 1)
        data['std_sd'] = STD(data['mas_delta'], t, self.tolerance_rate)
        data['std_md'] = STD(data['mam_delta'], t, self.tolerance_rate)
        data['std_ld'] = STD(data['mal_delta'], t, self.tolerance_rate)
        data['signal2'] = data.apply(lambda x: 1 if x['std_ld'] < c < x['std_md'] < b < x['std_sd'] < a else 0, axis=1)

        # 上涨趋势
        data['close_delta'] = DELTA(data['close'], t)
        data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] > 0 else 0, axis=1)

        data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
        data['status14'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status14']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status14_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 下山滑坡型, s, m, l对应短、中、长期, t是回溯天数, abc分别对应短中长期均线差值的标准差阈值
    def status15(self, s, m, l, t, a, b, c):
        data = self.data.copy()

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
        data['signal2'] = data.apply(lambda x: 1 if x['std_ld'] < c < x['std_md'] < b < x['std_sd'] < a else 0, axis=1)

        # 下跌趋势
        data['close_delta'] = DELTA(data['close'], t)
        data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] < 0 else 0, axis=1)

        data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
        data['status15'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status15']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status15_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 逐浪上升型, s, m, l对应短、中、长期, t是回溯天数
    def status16(self, s, m, l, t):
        data = self.data.copy()

        # 短中长期均线
        data['mas'] = MA(data['close'], s, self.tolerance_rate)
        data['mam'] = MA(data['close'], m, self.tolerance_rate)
        data['mal'] = MA(data['close'], l, self.tolerance_rate)
        data['para'] = data.apply(lambda x: 1 if (x['mas'] > x['mal'] and x['mam'] > x['mal']) else 0, axis=1)
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

        # 上涨趋势
        data['close_delta'] = DELTA(data['close'], t)
        data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] > 0 else 0, axis=1)

        data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
        data['status16'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status16']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status16_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 逐浪下降型, s, m, l对应短、中、长期, t是回溯天数
    def status17(self, s, m, l, t):
        data = self.data.copy()

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
        data['status17'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status17']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status17_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 加速上涨型, s, m, l对应短、中、长期, t是缓慢上涨天数, n是加速上涨天数
    def status18(self, s, m, l, t, n):
        data = self.data.copy()

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

        # 上涨趋势加快
        data['close_shift_delta'] = DELTA(data['close'].shift(n), t) / t
        data['close_delta'] = DELTA(data['close'], n) / n
        data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] > x['close_shift_delta'] > 0 else 0, axis=1)

        data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
        data['status18'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status18']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status18_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 加速下跌型, s, m, l对应短、中、长期, t是缓慢下跌天数, n是加速下跌天数
    def status19(self, s, m, l, t, n):
        data = self.data.copy()

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
        data['status19'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status19']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status19_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 快速上涨型, s, m, l对应短、中、长期, n是快速上涨天数, ret是n日涨幅
    def status20(self, s, m, l, n, ret):
        data = self.data.copy()

        # 短中长期均线
        data['mas'] = MA(data['close'], s, self.tolerance_rate)
        data['mam'] = MA(data['close'], m, self.tolerance_rate)
        data['mal'] = MA(data['close'], l, self.tolerance_rate)
        data['para'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
        data['para_count'] = data['para'].rolling(n, round(n * self.tolerance_rate)).sum()
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
        data['status20'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status20']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status20_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 快速下跌型, s, m, l对应短、中、长期, n是快速下跌天数, ret是n日跌幅
    def status21(self, s, m, l, n, ret):
        data = self.data.copy()

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
        data['status21'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status21']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status21_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 烘云托月型, s, m, l对应短、中、长期, n是回溯时间, sigma是波动率的上限
    def status22(self, s, m, l, n, sigma):
        data = self.data.copy()

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
        data['status22'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status22']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status22_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 乌云密布型, s, m, l对应短、中、长期, n是回溯时间, sigma是波动率的上限
    def status23(self, s, m, l, n, sigma):
        data = self.data.copy()

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
        data['status23'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status23']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status23_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 蛟龙出海型, s, m, l对应短、中、长期, t为回溯期, ret是最小跌幅
    def status24(self, s, m, l, t, ret):
        data = self.data.copy()

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
        data['status24'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status24']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status24_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)

    # 断头侧刀型, s, m, l对应短、中、长期, t为回溯期, ret是最小涨幅
    def status25(self, s, m, l, t, ret):
        data = self.data.copy()

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
        data['status25'] = data['signal']
        data = data.loc[:, ['date', 'close', 'status25']]
        data = data[data['date'] >= self.start_date]
        print(data)
        data.to_csv(self.path + 'status25_' + stock + '_' + str(s) + '_' + str(m) + '_' + str(l) + '.csv', index=False)


if __name__ == '__main__':
    startdate = '2010/01/01'
    enddate = '2017/12/31'
    stock = '002568'
    cal = CalSignal(startdate, enddate)
    # cal.status12(5,10,20,3,3,20)
    # cal.status13(5,10,20,3,3,20)
    # cal.status14(5,10,20,20,0.5, 0.3, 0.1)
    # cal.status15(5, 10, 20,20, 0.5, 0.3, 0.1)
    # cal.status16(10,20,60,100)
    # cal.status17(10, 20, 60, 100)
    # cal.status18(5,10,20,30,5)
    # cal.status19(5, 10, 20, 30, 5)
    # cal.status20(5, 10, 20, 5, 0.08)
    # cal.status21(5, 10, 20, 5, 0.08)
    # cal.status24(5, 10, 20, 20, 0.03)
    cal.status25(5, 10, 20, 20, 0.03)
    # cal.status23(5, 10, 20, 10, 0.2)
