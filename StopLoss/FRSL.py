# -*- coding: utf-8 -*-
"""
SmartWin回策框架
frsl止损出场
作者:Smart
新建时间：2018-09-04
"""
from StopLossTemplate import StopLossTemplate
import pandas as pd


class FrslStopLoss(StopLossTemplate):
    """
    frsl止损出场
    """
    def __init__(self, para_dic):
        super(FrslStopLoss, self).__init__(para_dic)
        self.para_dic = para_dic
        self.sl_name = 'frsl'
        self.sl_para_name_list = ['frsl_target']
        self.need_data_process_before_domain = False
        self.need_data_process_after_domain = False
        self.folder_prefix = 'frsl'
        self.file_suffix = 'result_frsl_'

        para_target_list = para_dic['frsl_target']
        self.price_tick = para_dic['price_tick']
        self.para_dic_list = []
        for para_target in para_target_list:
            self.para_dic_list.append({
                'para_name': str(para_target),
                'frsl_target': para_target
            })
        pass

    def get_opr_sl_result(self, opr, bar_df):
        result_dic = {}
        opr_type = opr['tradetype']
        open_price = opr['openprice']
        if opr_type == 1:
            df = pd.DataFrame({'high': bar_df['longHigh'], 'low': bar_df['longLow'], 'strtime': bar_df['strtime'], 'utc_time': bar_df['utc_time']})
            df['lossRate'] = df['low'] / open_price - 1
            for frsl_target in self.para_dic_list:
                frsl_target_value = frsl_target['frsl_target']
                df2 = df.loc[df['lossRate'] <= frsl_target_value]
                if df2.shape[0] > 0:
                    temp = df2.iloc[0]
                    pprice = open_price * (1 + frsl_target_value)
                    close_price = pprice // self.price_tick * self.price_tick
                    strtime = temp['strtime']
                    utctime = temp['utc_time']
                    result_dic[frsl_target['para_name']] = {
                        "new_closeprice": close_price,
                        "new_closetime": strtime,
                        "new_closeutc": utctime,
                        "new_closeindex": 0
                    }
                else:
                    result_dic[frsl_target['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        else:
            df = pd.DataFrame({'high': bar_df['shortHigh'], 'low': bar_df['shortLow'], 'strtime': bar_df['strtime'], 'utc_time': bar_df['utc_time']})
            df['lossRate'] = 1 - df['high'] / open_price
            for frsl_target in self.para_dic_list:
                frsl_target_value = frsl_target['frsl_target']
                df2 = df.loc[df['lossRate'] <= frsl_target_value]
                if df2.shape[0] > 0:
                    temp = df2.iloc[0]
                    pprice = open_price * (1 - frsl_target_value)
                    close_price = pprice // self.price_tick * self.price_tick + self.price_tick
                    strtime = temp['strtime']
                    utctime = temp['utc_time']
                    result_dic[frsl_target['para_name']] = {
                        "new_closeprice": close_price,
                        "new_closetime": strtime,
                        "new_closeutc": utctime,
                        "new_closeindex": 0
                    }
                else:
                    result_dic[frsl_target['para_name']] = {
                        "new_closeprice": opr['closeprice'],
                        "new_closetime": opr['closetime'],
                        "new_closeutc": opr['closeutc'],
                        "new_closeindex": opr['closeindex']
                    }
        return result_dic
