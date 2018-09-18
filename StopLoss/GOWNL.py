# -*- coding: utf-8 -*-
"""
SmartWin回策框架
gownl止损出场
作者:Smart
新建时间：2018-09-05
"""
from StopLossTemplate import StopLossTemplate
import pandas as pd


class GownlStopLoss(StopLossTemplate):
    """
    gownl止损出场
    """

    def __init__(self, para_dic):
        super(GownlStopLoss, self).__init__(para_dic)
        self.para_dic = para_dic
        self.sl_name = 'gownl'
        self.sl_para_name_list = ['gownl_protect', 'gownl_floor', 'gownl_step']
        self.need_data_process_before_domain = False
        self.need_data_process_after_domain = True  # gownl止损需要在主连数据上添加index_num数据，用于计算保护开启时长
        self.folder_prefix = 'gownl'
        self.file_suffix = 'result_gownl_'

        gownl_protect_list = para_dic['gownl_protect']
        gownl_floor_list = para_dic['gownl_floor']
        gownl_step_list = para_dic['gownl_step']
        self.price_tick = para_dic['price_tick']
        self.para_dic_list = []
        for gownl_protect in gownl_protect_list:
            for gownl_floor in gownl_floor_list:
                for gownl_step in gownl_step_list:
                    self.para_dic_list.append(
                        {
                            'para_name': '%.3f_%.1f_%d' % (gownl_protect, gownl_floor, gownl_step),
                            'gownl_protect': gownl_protect,
                            'gownl_floor': gownl_floor * self.price_tick,
                            'gownl_step': gownl_step * self.price_tick
                        }
                    )
        pass

    def get_opr_sl_result(self, opr, bar_df):
        result_dic = {}
        opr_type = opr['tradetype']
        open_price = opr['openprice']
        if opr_type == 1:
            df = pd.DataFrame({'high': bar_df['longHigh'], 'low': bar_df['longLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time'], 'index_num': bar_df['index_num']})
            df['max2here'] = df['high'].expanding().max()
            df['maxEarnRate'] = df['max2here'] / open_price - 1
            for gownl_para_dic in self.para_dic_list:
                gownl_protect = gownl_para_dic['gownl_protect']
                gownl_floor = gownl_para_dic['gownl_floor']
                gownl_step = gownl_para_dic['gownl_step']
                #df['protect_time'] = 0
                #df['protect_floor'] = 0
                df2 = df.loc[df['maxEarnRate'] > gownl_protect]
                if df2.shape[0] > 0:
                    protect_index_num = df2.iloc[0]['index_num']
                    #df2.loc[:, 'protect_time'] = df2['index_num'] - protect_index_num  # 计算出保护时长
                    #df2.loc[:, 'protect_floor'] = open_price + gownl_floor + df2['protect_time'] * gownl_step
                    protect_time = df2['index_num'] - protect_index_num
                    protect_floor = open_price + gownl_floor + protect_time * gownl_step
                    #tempdf = df2.loc[df2['low'] <= df2['protect_floor']]
                    tempdf = df2.loc[df2['low'] <= protect_floor]
                    if tempdf.shape[0] > 0:
                        temp = tempdf.iloc[0]
                        #newcloseprice = temp['protect_floor']
                        newcloseprice = protect_floor[tempdf.index[0]]
                        strtime = temp['strtime']
                        utctime = temp['utc_time']
                        #newcloseindex = temp['index_num']
                        result_dic[gownl_para_dic['para_name']] = {
                            "new_closeprice": newcloseprice,
                            "new_closetime": strtime,
                            "new_closeutc": utctime,
                            "new_closeindex": 0
                        }
                    else:
                        result_dic[gownl_para_dic['para_name']] = {
                            "new_closeprice": opr['closeprice'],
                            "new_closetime": opr['closetime'],
                            "new_closeutc": opr['closeutc'],
                            "new_closeindex": opr['closeindex']
                        }
                else:
                    result_dic[gownl_para_dic['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        else:
            df = pd.DataFrame({'high': bar_df['shortHigh'], 'low': bar_df['shortLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time'], 'index_num': bar_df['index_num']})
            df['min2here'] = df['low'].expanding().min()
            df['maxEarnRate'] = 1 - df['min2here'] / open_price
            for gownl_para_dic in self.para_dic_list:
                gownl_protect = gownl_para_dic['gownl_protect']
                gownl_floor = gownl_para_dic['gownl_floor']
                gownl_step = gownl_para_dic['gownl_step']

                df2 = df.loc[df['maxEarnRate'] > gownl_protect]
                if df2.shape[0] > 0:
                    protect_index_num = df2.iloc[0]['index_num']
                    #df2.loc[:,'protect_time'] = df2['index_num'] - protect_index_num  # 计算出保护时长
                    #df2.loc[:,'protect_floor'] = open_price - gownl_floor - df2['protect_time'] * gownl_step
                    protect_time = df2['index_num'] - protect_index_num
                    protect_floor = open_price - gownl_floor - protect_time * gownl_step
                    tempdf = df2.loc[df2['high'] >= protect_floor]
                    if tempdf.shape[0] > 0:
                        temp = tempdf.iloc[0]
                        newcloseprice = protect_floor[tempdf.index[0]]
                        strtime = temp['strtime']
                        utctime = temp['utc_time']
                        # timeindex = temp['index_num']
                        result_dic[gownl_para_dic['para_name']] = {
                            "new_closeprice": newcloseprice,
                            "new_closetime": strtime,
                            "new_closeutc": utctime,
                            "new_closeindex": 0
                        }
                    else:
                        result_dic[gownl_para_dic['para_name']] = {
                            "new_closeprice": opr['closeprice'],
                            "new_closetime": opr['closetime'],
                            "new_closeutc": opr['closeutc'],
                            "new_closeindex": opr['closeindex']
                        }
                else:
                    result_dic[gownl_para_dic['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        return result_dic

    def data_process_after_domain(self, domin_bar_1m, domain_bar_xm):
        domain_bar_xm['index_num'] = range(domain_bar_xm.shape[0])
        domin_bar_1m['index_num'] = domain_bar_xm['index_num']
        domin_bar_1m.fillna(method='ffill', inplace=True)  # 用上一个非0值来填充

        return domin_bar_1m, domain_bar_xm
