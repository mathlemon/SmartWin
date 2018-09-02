# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from MA import  hull_ma
import talib


def calMACD(closedata, short=12, long1=26, mid=9):
    '''
    计算MACD
    :param closedata:
    :param short:
    :param long1:
    :param mid:
    :return:MACD,DEA,Bar,SEMA,LEMA
    '''
    # sema = pd.ewma(closedata, span=short)
    # lema  = pd.ewma(closedata, span=long1)
    sema = closedata.ewm(span=short, adjust=False).mean()
    lema = closedata.ewm(span=long1, adjust=False).mean()
    data_dif = sema - lema
    # data_dea = pd.ewma(data_dif, span=mid)
    data_dea = data_dif.ewm(span=mid, adjust=False).mean()
    data_bar = 2 * (data_dif - data_dea)
    return data_dif, data_dea, data_bar, sema, lema


def calNewMACD(lastClose, dea, sema, lema):
    '''
    计算单个MACD值
    :param closedata: 收盘价
    :param dea:
    :param sema:
    :param lema:
    :return: MACD,DEA,BAR,SEMA,LEMA
    '''
    newSema = sema * 11 / 13 + float(lastClose) * 2 / 13
    newLema = lema * 25 / 27 + float(lastClose) * 2 / 27
    newMACD = newSema - newLema
    newDea = dea * 8 / 10 + newMACD * 2 / 10
    newBar = (newMACD - newDea) * 2
    return newMACD, newDea, newBar, newSema, newLema


def dfCross(dfx, colum1, colum2):
    dfx['true'] = 0
    dfx.loc[dfx[colum1] > dfx[colum2], 'true'] = 1
    dfx.loc[dfx[colum1] < dfx[colum2], 'true'] = -1

    if dfx.ix[0, 'true'] == 0:
        dfx.ix[0, 'true'] = 1
    # 填充0值，修改为上一周期的取值
    zeroindex = dfx.loc[dfx['true'] == 0].index
    for zi in zeroindex:
        dfx.ix[zi, 'true'] = dfx.ix[zi - 1, 'true']

    dfx['true1'] = dfx['true'].shift(1).fillna(0)
    dfx['cross'] = 0
    dfx.loc[(dfx['true'] == 1) & (dfx['true1'] == -1), 'cross'] = 1
    dfx.loc[(dfx['true'] == -1) & (dfx['true1'] == 1), 'cross'] = -1
    true = dfx['true']
    cross = dfx['cross']
    dfx.drop('true', axis=1, inplace=True)
    dfx.drop('true1', axis=1, inplace=True)
    dfx.drop('cross', axis=1, inplace=True)
    return true, cross


def hull_macd(closedata, short=12, long=26, mid=9):
    """
    计算MACD
    :param closedata:
    :param short:
    :param long1:
    :param mid:
    :return:MACD,DEA,Bar,SEMA,LEMA
    """
    sema = hull_ma(closedata, short)
    lema = hull_ma(closedata, long)
    data_dif = sema - lema
    data_dea = talib.MA(data_dif, mid, matype=1)
    data_bar = 2 * (data_dif - data_dea)
    return data_dif, data_dea, data_bar, sema, lema


if __name__ == '__main__':
    import DATA_CONSTANTS as DC
    N = 10
    testdata = DC.getBarBySymbol('SHFE.RB', 'RB1810', 3600)
    testdata['data_dif'], testdata['data_dea'], testdata['data_bar'], testdata['sema'], testdata['lema'] = hull_macd(testdata['close'], 6, 24, 7)
    testdata.to_csv('hull_macd.csv')
    print testdata
