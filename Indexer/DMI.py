# -*- coding: utf-8 -*-
"""'
TR := SUM(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(LOW-REF(CLOSE,1))),N);
HD := HIGH-REF(HIGH,1);
LD := REF(LOW,1)-LOW;
DMP:= SUM(IFELSE(HD>0 && HD>LD,HD,0),N);
DMM:= SUM(IFELSE(LD>0 && LD>HD,LD,0),N);
PDI: DMP*100/TR;
MDI: DMM*100/TR;
ADX: MA(ABS(MDI-PDI)/(MDI+PDI)*100,M);
ADXR:(ADX+REF(ADX,M))/2;
"""

import pandas as pd
import numpy as np
import MA


def DMI_old(df, N=14, M=6):
    high = df.high
    low = df.low
    close = df.close
    closeshift1 = close.shift(1).fillna(0)
    open = df.open
    c = high - low
    d = high - closeshift1
    df1 = pd.DataFrame({'c': c, 'd': d})
    df1['A'] = df1.max(axis=1)
    df1.drop('c', axis=1, inplace=True)
    df1.drop('d', axis=1, inplace=True)
    df1['B'] = np.abs(low - closeshift1)
    df1['C'] = df1.max(axis=1)

    # df1.drop('A',axis=1,inplace=True)
    # df1.drop('B',axis=1,inplace=True)

    df1['TR'] = df1['C'].rolling(N).sum()
    # 2、HD=最高价-昨日最高价
    # 3、LD=昨日最低价-最低价
    HD = high - high.shift(1).fillna(0)
    LD = low.shift(1).fillna(0) - low
    df1['HD'] = HD
    df1['LD'] = LD
    # DMP:= SUM(IFELSE(HD>0 && HD>LD,HD,0),N);
    # DMM:= SUM(IFELSE(LD>0 && LD>HD,LD,0),N);
    df2 = pd.DataFrame({'HD': HD, 'LD': LD})
    df2['DMP_1'] = df2[(df2['HD'] > df2['LD']) & (df2['HD'] > 0)]['HD']
    df2['DMM_1'] = df2[(df2['LD'] > df2['HD']) & (df2['LD'] > 0)]['LD']
    df2 = df2.fillna(0)
    df1['DMP'] = df2['DMP_1'].rolling(N).sum()
    df1['DMM'] = df2['DMM_1'].rolling(N).sum()
    del df2
    # 6、PDI=DMP*100/TR
    # 7、MDI=DMM*100/TR
    df1['PDI'] = df1['DMP'] * 100 / df1['TR']
    df1['MDI'] = df1['DMM'] * 100 / df1['TR']
    # ADX: MA(ABS(MDI-PDI)/(MDI+PDI)*100,M);
    # ADXR:(ADX+REF(ADX,M))/2;
    df1['ADX'] = MA.calMA(np.abs(df1['MDI'] - df1['PDI']) / (df1['MDI'] + df1['PDI']) * 100, M)
    df1['ADXR'] = (df1['ADX'] + df1['ADX'].shift(M).fillna(0)) / 2

    return df1['PDI'], df1['MDI'], df1['ADX'], df1['ADXR']


if __name__ == '__main__':
    testdata = pd.read_csv("test\\test 3600.csv")
    testdata['PDI'], testdata['MDI'], testdata['ADX'], testdata['ADXR'] = DMI_old(testdata, 30, 6)
    testdata.to_csv('test\\dmi.csv')
    print testdata.tail(10)