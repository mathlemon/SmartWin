# -*- coding: utf-8 -*-
"""
SmartWin回策框架
LvyiWin策略核心
作者:Smart
新建时间：2018-09-06
"""
from StrategyTemplate import StrategyTemplate
import pandas as pd
from Indexer import MA, DMI, KDJ, dfCross


class LvyiWin(StrategyTemplate):
    strategy_name = 'LvyiWin'
    strategy_para_name_list = ['KDJ_N', 'DMI_N', 'MS', 'ML']

    def __init__(self,):
        super(LvyiWin, self).__init__()
        pass

    def run_trade_logic(self, symbol_info, raw_data, para_dic):
        setname = para_dic['Setname']
        KDJ_N = para_dic['KDJ_N']
        KDJ_M = 3
        KDJ_HLim = 85
        KDJ_LLim = 15
        DMI_N = para_dic['DMI_N']
        DMI_M = 6
        MA_Short = para_dic['MS']
        MA_Long = para_dic['ML']
        raw_data['Unnamed: 0'] = range(raw_data.shape[0])
        beginindex = raw_data.ix[0, 'Unnamed: 0']

        raw_data['next_strtime'] = raw_data['strtime'].shift(-1).fillna(method='ffill')
        raw_data['next_open'] = raw_data['open'].shift(-1).fillna(method='ffill')
        raw_data['next_utc'] = raw_data['utc_time'].shift(-1).fillna(method='ffill')

        # 处理KDJ数据：KDJ_OPEN做为最终KDJ的触发信号
        # KDJ_True=1:80>k>D
        # KDJ_True=-1:20<K<D
        raw_data['KDJ_K'], raw_data['KDJ_D'], raw_data['KDJ_J'] = KDJ.calKDJ(raw_data, N=KDJ_N, M1=KDJ_M, M2=KDJ_M)

        raw_data['KDJ_True'] = 0
        raw_data.loc[(KDJ_HLim > raw_data['KDJ_K']) & (raw_data['KDJ_K'] > raw_data['KDJ_D']), 'KDJ_True'] = 1
        raw_data.loc[(KDJ_LLim < raw_data['KDJ_K']) & (raw_data['KDJ_K'] < raw_data['KDJ_D']), 'KDJ_True'] = -1

        # 处理DMI数据：DMI_GOLD_CROSS做为DMI的触发信号
        # DMI_True=1:and PDI>MDI
        # DMI_True=-1:and PDI<MDI
        raw_data['PDI'], raw_data['MDI'], adx, adxr = DMI.calDMI(raw_data, N=DMI_N, M=DMI_M)
        raw_data['DMI_True'] = DMI.dmi_true(raw_data)

        # 处理MA数据：MA_Cross做为MA的触发信号
        # MA20_True=1:close>MA20
        # MA20_True=-1:close<MA20
        raw_data['MA_Short'] = MA.calMA(raw_data['close'], MA_Short)
        raw_data['MA_Long'] = MA.calMA(raw_data['close'], MA_Long)
        raw_data['MA_True'], raw_data['MA_Cross'] = dfCross(raw_data, 'MA_Short', 'MA_Long')

        # 找出买卖点：
        # 1.先找出MA金叉的买卖点
        # 2.找到结合判决条件的买点
        # 3.从MA买点中滤出真实买卖点
        # 取出金叉点
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
            longcrosslist = pd.concat([goldcrosslist, deathcrosslist.shift(-1).fillna(0)], axis=1)
        longcrosslist = longcrosslist.set_index(pd.Index(longcrosslist['goldcrossindex']), drop=True)

        # 生成空仓序列（死叉在前，金叉在后）
        if deathcrosslist.ix[0, 'deathcrossindex'] < goldcrosslist.ix[0, 'goldcrossindex']:
            shortcrosslist = pd.concat([deathcrosslist, goldcrosslist], axis=1)
        else:  # 如果第一个金叉的序号在死叉前，则要将金叉往上移1格
            shortcrosslist = pd.concat([deathcrosslist, goldcrosslist.shift(-1).fillna(0)], axis=1)
        shortcrosslist = shortcrosslist.set_index(pd.Index(shortcrosslist['deathcrossindex']), drop=True)

        # 取出开多序号和开空序号
        openlongindex = raw_data.loc[(raw_data['MA_Cross'] == 1) & (raw_data['KDJ_True'] == 1) & (raw_data['DMI_True'] == 1)].index
        openshortindex = raw_data.loc[(raw_data['MA_Cross'] == -1) & (raw_data['KDJ_True'] == -1) & (raw_data['DMI_True'] == -1)].index

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
        result.drop(result.shape[0] - 1, inplace=True)
        # 去掉跨合约的操作
        # 使用单合约，不用再去掉跨合约
        # result = removeContractSwap(result, contractswaplist)

        slip = symbol_info.getSlip()
        result['ret'] = ((result['closeprice'] - result['openprice']) * result['tradetype']) - slip
        result['ret_r'] = result['ret'] / result['openprice']
        return result

    def get_para_list(self, para_list_dic):
        mashort_list = para_list_dic['MS']
        malong_list = para_list_dic['ML']
        kdj_n_list = para_list_dic['KDJ_N']
        dmi_n_list = para_list_dic['DMI_N']
        setlist = []
        i = 0
        for ms in mashort_list:
            for ml in malong_list:
                for kn in kdj_n_list:
                    for dn in dmi_n_list:
                        setname = 'Set' + str(i) + ' MS' + str(ms) + ' ML' + str(ml) + ' KN' + str(kn) + ' DN' + str(dn)
                        l = [setname, ms, ml, kn, dn]
                        setlist.append(l)
                        i += 1
        setpd = pd.DataFrame(setlist, columns=['Setname', 'MS', 'ML', 'KDJ_N', 'DMI_N'])
        return setpd

    def get_para_name_list(self):
        return self.strategy_para_name_list

