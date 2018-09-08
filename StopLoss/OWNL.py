# -*- coding: utf-8 -*-
"""
SmartWin回策框架
ownl止损出场
作者:Smart
新建时间：2018-09-08
"""
from StopLossTemplate import StopLossTemplate
import pandas as pd


class OwnlStopLoss(StopLossTemplate):
    """
    ownl止损出场
    """

    def __init__(self, para_dic):
        super(OwnlStopLoss, self).__init__(para_dic)
        self.para_dic = para_dic
        self.sl_name = 'ownl'
        self.sl_para_name_list = ['ownl_protect', 'ownl_floor']
        self.need_data_process_before_domain = False
        self.need_data_process_after_domain = False
        self.folder_prefix = 'ownl'
        self.file_suffix = 'result_ownl_'

        ownl_protect_list = para_dic['ownl_protect']
        ownl_floor_list = para_dic['ownl_floor']
        self.para_dic_list = []
        for ownl_protect in ownl_protect_list:
            for ownl_floor in ownl_floor_list:
                self.para_dic_list.append(
                    {
                        'para_name': '%.3f_%.1f' % (ownl_protect, ownl_floor),
                        'ownl_protect': ownl_protect,
                        'ownl_floor': ownl_floor
                    }
                )
        pass

    def get_opr_sl_result(self, opr, bar_df):
        result_dic = {}
        opr_type = opr['tradetype']
        open_price = opr['openprice']
        if opr_type == 1:
            df = pd.DataFrame({'high': bar_df['longHigh'], 'low': bar_df['longLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time']})
            df['max2here'] = df['high'].expanding().max()
            df['maxEarnRate'] = df['max2here'] / open_price - 1
            for ownl_para_dic in self.para_dic_list:
                ownl_protect = ownl_para_dic['ownl_protect']
                ownl_floor = ownl_para_dic['ownl_floor']
                df2 = df.loc[df['maxEarnRate'] > ownl_protect]
                if df2.shape[0] > 0:
                    protect_floor = open_price + ownl_floor
                    tempdf = df2.loc[df2['low'] <= protect_floor]
                    if tempdf.shape[0] > 0:
                        temp = tempdf.iloc[0]
                        newcloseprice = protect_floor[tempdf.index[0]]
                        strtime = temp['strtime']
                        utctime = temp['utc_time']
                        result_dic[ownl_para_dic['para_name']] = {
                            "new_closeprice": newcloseprice,
                            "new_closetime": strtime,
                            "new_closeutc": utctime,
                            "new_closeindex": 0
                        }
                    else:
                        result_dic[ownl_para_dic['para_name']] = {
                            "new_closeprice": opr['closeprice'],
                            "new_closetime": opr['closetime'],
                            "new_closeutc": opr['closeutc'],
                            "new_closeindex": opr['closeindex']
                        }
                else:
                    result_dic[ownl_para_dic['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        else:
            df = pd.DataFrame({'high': bar_df['shortHigh'], 'low': bar_df['shortLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time']})
            df['min2here'] = df['low'].expanding().min()
            df['maxEarnRate'] = 1 - df['min2here'] / open_price
            for ownl_para_dic in self.para_dic_list:
                ownl_protect = ownl_para_dic['ownl_protect']
                ownl_floor = ownl_para_dic['ownl_floor']
                df2 = df.loc[df['maxEarnRate'] > ownl_protect]
                if df2.shape[0] > 0:
                    protect_floor = open_price - ownl_floor
                    tempdf = df2.loc[df2['high'] >= protect_floor]
                    if tempdf.shape[0] > 0:
                        temp = tempdf.iloc[0]
                        newcloseprice = protect_floor[tempdf.index[0]]
                        strtime = temp['strtime']
                        utctime = temp['utc_time']
                        result_dic[ownl_para_dic['para_name']] = {
                            "new_closeprice": newcloseprice,
                            "new_closetime": strtime,
                            "new_closeutc": utctime,
                            "new_closeindex": 0
                        }
                    else:
                        result_dic[ownl_para_dic['para_name']] = {
                            "new_closeprice": opr['closeprice'],
                            "new_closetime": opr['closetime'],
                            "new_closeutc": opr['closeutc'],
                            "new_closeindex": opr['closeindex']
                        }
                else:
                    result_dic[ownl_para_dic['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        return result_dic
