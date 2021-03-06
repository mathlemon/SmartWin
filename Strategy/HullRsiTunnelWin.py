# -*- coding: utf-8 -*-
"""
SmartWin回策框架
HullRsiTunnelWin策略
新建时间：2018-09-13
"""
from StrategyTemplate import StrategyTemplate
import pandas as pd
from Indexer import RSI, MA, dfCross


class HullRsiTunnelWin(StrategyTemplate):
    strategy_name = 'HullRsiTunnelWin'
    strategy_para_name_list = ['N1', 'M1', 'M2', 'N', 'TN']

    def __init__(self,):
        super(HullRsiTunnelWin, self).__init__()
        pass

    def run_trade_logic(self, symbol_info, raw_data, para_dic):
        para_n1 = para_dic['N1']
        para_m1 = para_dic['M1']
        para_m2 = para_dic['M2']
        para_n = para_dic['N']
        para_tunnel_n = para_dic['TN']

        rsi1 = pd.Series(RSI.rsi(raw_data['close'], para_n1))
        rsi_ema1 = MA.calEMA(rsi1, para_m1)
        rsi_ema2 = MA.calEMA(rsi_ema1, para_m2)
        rsi_new = rsi_ema1 - rsi_ema2
        hull_rsi = MA.hull_ma(rsi_new, para_n)
        raw_data['RSI_EMA1'] = rsi_ema1
        raw_data['HullRsi'] = hull_rsi
        raw_data['TOP_EMA'] = MA.calEMA(raw_data['high'], para_tunnel_n)
        raw_data['BOTTOM_EMA'] = MA.calEMA(raw_data['low'], para_tunnel_n)
        raw_data['zero'] = 0
        raw_data['Unnamed: 0'] = range(raw_data.shape[0])
        # 计算M金叉和死叉
        raw_data['HullRsi_True'], raw_data['HullRsi_Cross'] = dfCross(raw_data, 'HullRsi', 'zero')

        raw_data['next_strtime'] = raw_data['strtime'].shift(-1).fillna(method='ffill')
        raw_data['next_open'] = raw_data['open'].shift(-1).fillna(method='ffill')
        raw_data['next_utc'] = raw_data['utc_time'].shift(-1).fillna(method='ffill')

        # ================================ 找出买卖点================================================
        # 1.先找出SAR金叉的买卖点
        # 2.找到结合判决条件的买点
        # 3.从MA买点中滤出真实买卖点
        # 取出金叉点
        goldcrosslist = pd.DataFrame({'goldcrosstime': raw_data.loc[raw_data['HullRsi_Cross'] == 1, 'next_strtime']})
        goldcrosslist['goldcrossutc'] = raw_data.loc[raw_data['HullRsi_Cross'] == 1, 'next_utc']
        goldcrosslist['goldcrossindex'] = raw_data.loc[raw_data['HullRsi_Cross'] == 1, 'Unnamed: 0']
        goldcrosslist['goldcrossprice'] = raw_data.loc[raw_data['HullRsi_Cross'] == 1, 'next_open']
        #goldcrosslist['goldcrossrsi'] = raw_data.loc[raw_data['HullRsi_Cross'] == 1, 'RSI_EMA1']

        # 取出死叉点
        deathcrosslist = pd.DataFrame({'deathcrosstime': raw_data.loc[raw_data['HullRsi_Cross'] == -1, 'next_strtime']})
        deathcrosslist['deathcrossutc'] = raw_data.loc[raw_data['HullRsi_Cross'] == -1, 'next_utc']
        deathcrosslist['deathcrossindex'] = raw_data.loc[raw_data['HullRsi_Cross'] == -1, 'Unnamed: 0']
        deathcrosslist['deathcrossprice'] = raw_data.loc[raw_data['HullRsi_Cross'] == -1, 'next_open']
        #deathcrosslist['deathcrossrsi'] = raw_data.loc[raw_data['HullRsi_Cross'] == -1, 'RSI_EMA1']

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
        # openlongindex = raw_data.loc[
        #    (raw_data['HullRsi_Cross'] == 1) & (raw_data['RSI_EMA1'] < para_rsi1_up)].index
        # openshortindex = raw_data.loc[
        #    (raw_data['HullRsi_Cross'] == -1) & (raw_data['RSI_EMA1'] > para_rsi1_down)].index
        openlongindex = raw_data.loc[(raw_data['HullRsi_Cross'] == 1) & (raw_data['close'] > raw_data['TOP_EMA'])].index
        openshortindex = raw_data.loc[(raw_data['HullRsi_Cross'] == -1) & (raw_data['close'] < raw_data['BOTTOM_EMA'])].index
        # 从多仓序列中取出开多序号的内容，即为开多操作
        longopr = longcrosslist.loc[openlongindex]
        longopr['tradetype'] = 1
        longopr.rename(columns={'goldcrosstime': 'opentime',
                                'goldcrossutc': 'openutc',
                                'goldcrossindex': 'openindex',
                                'goldcrossprice': 'openprice',
                                'goldcrossrsi': 'open_rsi',
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
                                 'deathcrossrsi': 'open_rsi',
                                 'goldcrosstime': 'closetime',
                                 'goldcrossutc': 'closeutc',
                                 'goldcrossindex': 'closeindex',
                                 'goldcrossprice': 'closeprice'}, inplace=True)

        # 结果分析
        result = pd.concat([longopr, shortopr])
        result = result.sort_index()
        result = result.reset_index(drop=True)
        result = result.dropna()
        slip = symbol_info.getSlip()
        result['ret'] = ((result['closeprice'] - result['openprice']) * result['tradetype']) - slip
        result['ret_r'] = result['ret'] / result['openprice']
        return result

    def get_para_list(self, para_list_dic):
        n_list = para_list_dic['N']
        m1_list = para_list_dic['M1']
        m2_list = para_list_dic['M2']
        n1_list = para_list_dic['N1']
        tn_list = para_list_dic['TN']
        setlist = []
        i = 0
        for n1 in n1_list:
            for m1 in m1_list:
                for m2 in m2_list:
                    for n in n_list:
                        for tn in tn_list:
                            setname = "Set%d N1_%d M1_%d M2_%d N_%d TN_%d" % (i, n1, m1, m2, n, tn)
                            setlist.append([setname, n1, m1, m2, n, tn])
                            i += 1

        setpd = pd.DataFrame(setlist, columns=['Setname', 'N1', 'M1', 'M2', 'N', 'TN'])
        return setpd

    def get_para_name_list(self):
        return self.strategy_para_name_list
