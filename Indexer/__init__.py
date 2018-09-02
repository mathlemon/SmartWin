# -*- coding: utf-8 -*-



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