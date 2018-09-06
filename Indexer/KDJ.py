# -*- coding: utf-8 -*-
"""
KDJ指标
RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
BACKGROUNDSTYLE(1);
K:SMA(RSV,M1,1);
D:SMA(K,M2,1);
J:3*K-2*D;
"""
import pandas as pd
from MA import calSMA
import numpy as np
import talib


def calKDJ(data, N=9, M1=3, M2=3):
    low_list = data['low'].rolling(N).min().fillna(data['low'])     # 使用low的值来填充前面的空白
    high_list = data['high'].rolling(N).max().fillna(data['high'])      # 使用high来填充
    rsv = (data['close'] - low_list) / (high_list - low_list) * 100
    kdj_k = calSMA(rsv, M1, 1)
    kdj_d = calSMA(kdj_k, M2, 1)
    kdj_j = 3 * kdj_k - 2 * kdj_d
    # kdjdata.fillna(0, inplace=True)
    return kdj_k, kdj_d, kdj_j


def calNewKDJ(data, kdjdata, N=9, M=2):
    '''
    计算单个KDJ的值
    1: 获取股票T日收盘价X
    2: 计算周期的未成熟随机值RSV(n)＝（Ct－Ln）/（Hn-Ln）×100，
    其中：C为当日收盘价，Ln为N日内最低价，Hn为N日内最高价，n为基期分别取5、9、19、36、45、60、73日。
    3: 计算K值，当日K值=(1-a)×前一日K值+a×当日RSV
    4: 计算D值，当日D值=(1-a)×前一日D值+a×当日K值。
    若无前一日K值与D值，则可分别用50来代替,a为平滑因子，不过目前已经约定俗成，固定为1/3。
    5: 计算J值，当日J值=3×当日K值-2×当日D值

    :return:
    '''
    datarow = data.shape[0]
    kdjrow = kdjdata.shape[0]
    closeT = data.ix[datarow - 1, 'close']
    Ln = min(data.ix[datarow - 9:, 'low'])
    Hn = max(data.ix[datarow - 9:, 'high'])
    if Hn == Ln:  # 防止出现Hn和Ln相等，导致分母为0的情况
        rsv = 100
    else:
        rsv = (closeT - Ln) / (Hn - Ln) * 100
    lastK = kdjdata.ix[kdjrow - 1, 'KDJ_K']
    lastD = kdjdata.ix[kdjrow - 1, 'KDJ_D']
    newK = 0.66667 * lastK + 0.33333 * rsv  # 不能用2/3和1/3来算，会变成int，结果变0
    newD = 0.66667 * lastD + 0.33333 * newK
    newJ = 3 * newK - 2 * newD
    kdjdata.loc[kdjrow] = [data.ix[datarow - 1, 'strdatetime'], data.ix[datarow - 1, 'utcdatetime'], Ln, Hn, rsv, newK, newD, newJ]
    # kdjdata.loc[kdjrow] = [data.ix[datarow-1, 'start_time'], rsv,Ln, Hn, newK, newD, newJ]
    pass


if __name__ == '__main__':
    testdata = pd.read_csv("test\\test 3600.csv")
    testdata['kdj_k'], testdata['kdj_d'], testdata['kdj_j'] = calKDJ(testdata, 9, 3, 3)
    testdata.to_csv('kdj.csv')
    print testdata.tail(10)

