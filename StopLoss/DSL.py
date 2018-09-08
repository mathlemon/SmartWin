# -*- coding: utf-8 -*-
"""
SmartWin回策框架
dsl止损出场
作者:Smart
新建时间：2018-09-03
"""
from StopLossTemplate import StopLossTemplate
import pandas as pd


class DslStopLoss(StopLossTemplate):
    """
    dsl止损出场
    """

    def __init__(self, para_dic):
        super(DslStopLoss, self).__init__(para_dic)
        self.para_dic = para_dic
        self.sl_name = 'dsl'
        self.sl_para_name_list = ['dsl_target']
        self.need_data_process_before_domain = False
        self.need_data_process_after_domain = False
        self.folder_prefix = 'dsl'
        self.file_suffix = 'result_dsl_'

        dsl_target_list = para_dic['dsl_target']
        self.price_tick = para_dic['price_tick']
        self.para_dic_list = []
        for dsl_target in dsl_target_list:
            self.para_dic_list.append({
                'para_name': str(dsl_target),
                'dsl_target': dsl_target
            })
        pass

    def get_opr_sl_result(self, opr, bar_df):
        result_dic = {}
        opr_type = opr['tradetype']
        if opr_type == 1:
            df = pd.DataFrame({'high': bar_df['longHigh'], 'low': bar_df['longLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time']})
            df['max2here'] = df['high'].expanding().max()
            df['dd2here'] = df['low'] / df['max2here'] - 1
            for dsl_target in self.para_dic_list:
                dsl_target_value = dsl_target['dsl_target']
                df['dd'] = df['dd2here'] - dsl_target_value
                tempdf = df.loc[df['dd'] < 0]
                if tempdf.shape[0] > 0:
                    temp = tempdf.iloc[0]
                    maxprice = temp['max2here']
                    strtime = temp['strtime']
                    utctime = temp['utc_time']
                    pprice = maxprice * (1 + dsl_target_value)
                    close_price = pprice // self.price_tick * self.price_tick
                    result_dic[dsl_target['para_name']] = {
                        "new_closeprice": close_price,
                        "new_closetime": strtime,
                        "new_closeutc": utctime,
                        "new_closeindex": 0
                    }
                else:
                    result_dic[dsl_target['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        else:
            df = pd.DataFrame({'high': bar_df['shortHigh'], 'low': bar_df['shortLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time']})
            df['min2here'] = df['low'].expanding().min()
            df['dd2here'] = 1 - df['high'] / df['min2here']
            for dsl_target in self.para_dic_list:
                dsl_target_value = dsl_target['dsl_target']
                df['dd'] = df['dd2here'] - dsl_target_value
                tempdf = df.loc[df['dd'] < 0]
                if tempdf.shape[0] > 0:
                    temp = tempdf.iloc[0]
                    maxprice = temp['min2here']
                    strtime = temp['strtime']
                    utctime = temp['utc_time']
                    pprice = maxprice * (1 - dsl_target_value)
                    close_price = pprice // self.price_tick * self.price_tick + self.price_tick
                    result_dic[dsl_target['para_name']] = {
                        "new_closeprice": close_price,
                        "new_closetime": strtime,
                        "new_closeutc": utctime,
                        "new_closeindex": 0
                    }
                else:
                    result_dic[dsl_target['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        return result_dic
