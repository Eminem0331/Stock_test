# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import statsmodels.api as sm


def MA(A, n, tolerance_rate):
    return A.rolling(n, round(n * tolerance_rate)).mean()


def STD(A, n, tolerance_rate):
    return A.rolling(n, round(n * tolerance_rate)).std()


def DELTA(A, n):
    return A - A.shift(n)


def EMA(A, n, tolerance_rate):
    def ema(a):
        nn = len(a)
        w = range(1, nn + 1, 1)
        c = nn * (nn + 1) / 2
        b = a * w
        return sum(b) / c

    rolling_ema = A.rolling(n, min_periods=round(n * tolerance_rate)).apply(lambda x: ema(x))
    return rolling_ema


def LLV(A, n, tolerance_rate):
    return A.rolling(n, min_periods=round(n * tolerance_rate)).min()


def JUDGE_UP(A, n, tolerance_rate):
    def judge(a):
        result = 1
        for i in range(len(a) - 1):
            if 0 < a[i] < a[i + 1]:
                continue
            else:
                result = 0
        return result

    rolling_judge = A.rolling(n, min_periods=round(n * tolerance_rate)).apply(lambda x: judge(x))
    return rolling_judge


def JUDGE_DOWN(A, n, tolerance_rate):
    def judge(a):
        result = 1
        for i in range(len(a) - 1):
            if 0 > a[i] > a[i + 1]:
                continue
            else:
                result = 0
        return result

    rolling_judge = A.rolling(n, min_periods=round(n * tolerance_rate)).apply(lambda x: judge(x))
    return rolling_judge


def HHV(A, n, tolerance_rate):
    return A.rolling(n, min_periods=round(n * tolerance_rate)).max()


def CAL_PARA(data, tolerance_rate):
    data['AA'] = (data['close'] * 2 + data['high'] + data['low'] + data['open']) / 5
    data['A0'] = MA(data['close'], 5, tolerance_rate)
    data['A1'] = (EMA(data['AA'], 4, tolerance_rate) + MA(data['AA'], 8, tolerance_rate) + MA(data['AA'], 16,
                                                                                              tolerance_rate)) / 3
    data['A2'] = (EMA(data['AA'], 9, tolerance_rate) + MA(data['AA'], 18, tolerance_rate) + MA(data['AA'], 36,
                                                                                               tolerance_rate)) / 3
    data['A3'] = (EMA(data['AA'], 13, tolerance_rate) + MA(data['AA'], 26, tolerance_rate) + MA(data['AA'], 52,
                                                                                                tolerance_rate)) / 3
    data['A4'] = (EMA(data['AA'], 24, tolerance_rate) + MA(data['AA'], 48, tolerance_rate) + MA(data['AA'], 96,
                                                                                                tolerance_rate)) / 3
    data['para'] = 100 * (data['close'] - LLV(data['low'], 100, tolerance_rate)) / (
    HHV(data['high'], 100, tolerance_rate) - LLV(data['low'], 100, tolerance_rate))
    data['A5'] = EMA(data['para'], 5, tolerance_rate)
    data['A6'] = data['A5'] / 4
    data['A7'] = data.apply(lambda x: max(x['A1'], x['A2'], x['A3'], x['A4']), axis=1)
    data['A7'] = data.apply(lambda x: min(x['A1'], x['A2'], x['A3'], x['A4']), axis=1)
    data['A9'] = data.apply(lambda x: min(x['A1'], x['A2'], x['A3']), axis=1)
    data['A10'] = data.apply(lambda x: max(x['A1'], x['A2'], x['A3']), axis=1)
    return data


def YUAN_HU_DI(data, tolerance_rate):
    df = CAL_PARA(data, tolerance_rate)
    df['judge'] = df.apply(lambda x: 0 if x['A1'] < x['A3'] else 1, axis=1)
    df['longcross'] = df['judge'].rolling(31, round(31 * tolerance_rate)).apply(lambda x: sum(x) == 1 and x[-1] == 1)
    df['yuanhudi'] = df.apply(
        lambda x: 1 if x['longcross'] == 1 and (x['A4'] - x['A3']) / x['A3'] < 0.05 and x['A10'] < x['A4'] else 0,
        axis=1)
    return df['yuanhudi']
