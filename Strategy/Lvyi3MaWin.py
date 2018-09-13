# -*- coding: utf-8 -*-
"""
SmartWin回策框架
Lvyi3MaWin策略
作者:Smart
新建时间：2018-09-13
"""
from StrategyTemplate import StrategyTemplate
import pandas as pd
from Indexer import MA, MACD, dfCross


class Lvyi3MaWin(StrategyTemplate):
    strategy_name = 'Lvyi3MaWin'
    strategy_para_name_list = ['MS', 'MM', 'ML']

    def __init__(self,):
        super(Lvyi3MaWin, self).__init__()
        pass

    def run_trade_logic(self, symbol_info, raw_data, para_dic):
        MS = para_dic['MS']
        MM = para_dic['MM']
        ML = para_dic['ML']
        raw_data['Unnamed: 0'] = range(raw_data.shape[0])
        beginindex = raw_data.ix[0, 'Unnamed: 0']

        raw_data['MA_Short'] = MA.calMA(raw_data['close'], MS)
        raw_data['MA_Mid'] = MA.calMA(raw_data['close'], MM)
        raw_data['MA_Long'] = MA.calMA(raw_data['close'], ML)
        raw_data['MA_True'], raw_data['MA_Cross'] = dfCross(raw_data, 'MA_Short', 'MA_Mid')

        raw_data['next_strtime'] = raw_data['strtime'].shift(-1).fillna(method='ffill')
        raw_data['next_open'] = raw_data['open'].shift(-1).fillna(method='ffill')
        raw_data['next_utc'] = raw_data['utc_time'].shift(-1).fillna(method='ffill')

        goldcrosslist = pd.DataFrame({'goldcrosstime': raw_data.loc[raw_data['MA_Cross'] == 1, 'next_strtime']})
        goldcrosslist['goldcrossutc'] = raw_data.loc[raw_data['MA_Cross'] == 1, 'next_utc']
        goldcrosslist['goldcrossindex'] = raw_data.loc[raw_data['MA_Cross'] == 1, 'Unnamed: 0'] - beginindex
        goldcrosslist['goldcrossprice'] = raw_data.loc[raw_data['MA_Cross'] == 1, 'next_open']

        # 取出死叉点
        deathcrosslist = pd.DataFrame({'deathcrosstime': raw_data.loc[raw_data['MA_Cross'] == -1, 'next_strtime']})
        deathcrosslist['deathcrossutc'] = raw_data.loc[raw_data['MA_Cross'] == -1, 'next_utc']
        deathcrosslist['deathcrossindex'] = raw_data.loc[raw_data['MA_Cross'] == -1, 'Unnamed: 0'] - beginindex
        deathcrosslist['deathcrossprice'] = raw_data.loc[raw_data['MA_Cross'] == -1, 'next_open']
        goldcrosslist = goldcrosslist.reset_index(drop=True)
        deathcrosslist = deathcrosslist.reset_index(drop=True)

        # 生成多仓序列（金叉在前，死叉在后）
        if goldcrosslist.ix[0, 'goldcrossindex'] < deathcrosslist.ix[0, 'deathcrossindex']:
            longcrosslist = pd.concat([goldcrosslist, deathcrosslist], axis=1)
        else:  # 如果第一个死叉的序号在金叉前，则要将死叉往上移1格
            longcrosslist = pd.concat([goldcrosslist, deathcrosslist.shift(-1)], axis=1)
        longcrosslist = longcrosslist.set_index(pd.Index(longcrosslist['goldcrossindex']), drop=True)

        # 生成空仓序列（死叉在前，金叉在后）
        if deathcrosslist.ix[0, 'deathcrossindex'] < goldcrosslist.ix[0, 'goldcrossindex']:
            shortcrosslist = pd.concat([deathcrosslist, goldcrosslist], axis=1)
        else:  # 如果第一个金叉的序号在死叉前，则要将金叉往上移1格
            shortcrosslist = pd.concat([deathcrosslist, goldcrosslist.shift(-1)], axis=1)
        shortcrosslist = shortcrosslist.set_index(pd.Index(shortcrosslist['deathcrossindex']), drop=True)

        # 取出开多序号和开空序号
        openlongindex = raw_data.loc[(raw_data['MA_Cross'] == 1) & (raw_data['MA_Short'] >= raw_data['MA_Long']) & (raw_data['MA_Mid'] >= raw_data['MA_Long'])].index
        openshortindex = raw_data.loc[(raw_data['MA_Cross'] == -1) & (raw_data['MA_Short'] <= raw_data['MA_Long']) & (raw_data['MA_Mid'] <= raw_data['MA_Long'])].index

        # 从多仓序列中取出开多序号的内容，即为开多操作
        longopr = longcrosslist.loc[openlongindex]
        longopr['tradetype'] = 1
        longopr.rename(columns={'goldcrosstime': 'opentime',
                                'goldcrossutc': 'openutc',
                                'goldcrossindex': 'openindex',
                                'goldcrossprice': 'openprice',
                                'deathcrosstime': 'closetime',
                                'deathcrossutc': 'closeutc',
                                'deathcrossindex': 'closeindex',
                                'deathcrossprice': 'closeprice'}, inplace=True)

        # 从空仓序列中取出开空序号的内容，即为开空操作
        shortopr = shortcrosslist.loc[openshortindex]
        shortopr['tradetype'] = -1
        shortopr.rename(columns={'deathcrosstime': 'opentime',
                                 'deathcrossutc': 'openutc',
                                 'deathcrossindex': 'openindex',
                                 'deathcrossprice': 'openprice',
                                 'goldcrosstime': 'closetime',
                                 'goldcrossutc': 'closeutc',
                                 'goldcrossindex': 'closeindex',
                                 'goldcrossprice': 'closeprice'}, inplace=True)

        # 结果分析
        result = pd.concat([longopr, shortopr])
        result = result.sort_index()
        result = result.reset_index(drop=True)
        # result.drop(result.shape[0] - 1, inplace=True)
        result = result.dropna()
        slip = symbol_info.getSlip()

        result['ret'] = ((result['closeprice'] - result['openprice']) * result['tradetype']) - slip
        result['ret_r'] = result['ret'] / result['openprice']
        return result

    def get_para_list(self, para_list_dic):
        ms_list = para_list_dic['MS']
        ml_list = para_list_dic['ML']
        mm_list = para_list_dic['MM']
        setlist = []
        i = 0
        for s1 in ms_list:
            for m1 in mm_list:
                for l1 in ml_list:
                    setname = "Set%d MS%d MM%d ML%d" % (i, s1, m1, l1)
                    setlist.append([setname, s1, m1, l1])
                    i += 1
        setpd = pd.DataFrame(setlist, columns=['Setname', 'MS', 'MM', 'ML'])
        return setpd

    def get_para_name_list(self):
        return self.strategy_para_name_list
