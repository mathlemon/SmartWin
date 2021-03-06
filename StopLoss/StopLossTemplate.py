# -*- coding: utf-8 -*-
"""
SmartWin回策框架
止损出场基础模板
作者:Smart
新建时间：2018-09-03
"""
import pandas as pd
import numpy as np

class StopLossTemplate(object):
    """
    止损出场基础模板
    """
    sl_name = 'basic_template'
    sl_para_name_list = []
    need_data_process_before_domain = False
    need_data_process_after_domain = False
    folder_prefix = ''
    file_suffix = ''
    para_dic_list = []

    def __init__(self, para_dic):
        pass

    def get_opr_sl_result(self, opr, bar_df):
        pass

    def data_process_before_domain(self, bar_dic_1m, bar_dic_xm):
        pass

    def data_process_after_domain(self, domin_bar_1m, domain_bar_xm):
        pass

    def get_para_dic_list(self, ):
        return self.para_dic_list

    def get_para_name_list(self):
        return self.sl_para_name_list

    def get_folder_prefix(self):
        return self.folder_prefix

    def get_file_suffix(self):
        return self.file_suffix

    def get_sl_name(self):
        return self.sl_name

    def final_result_pivot(self, final_result_df):
        para_name = len(self.sl_para_name_list)
        pivot_cols = ['para_name']
        if para_name > 1:
            pivot_cols = self.sl_para_name_list
            a = final_result_df['para_name'].str.split('_', expand=True)
            for i in range(para_name):
                final_result_df[self.sl_para_name_list[i]] = a[i]
        final_result_df['worknum'] = pd.to_numeric(final_result_df['worknum'])
        final_result_df['OprTimes'] = pd.to_numeric(final_result_df['OprTimes'])
        pv_df = pd.pivot_table(final_result_df, index=pivot_cols, values=['worknum', 'OprTimes', 'Annual', 'new_Annual', 'Sharpe', 'new_Sharpe', 'SR', 'new_SR',
                                                                          'DrawBack', 'new_DrawBack'])
        pv_df = pv_df.ix[:, ['worknum', 'OprTimes', 'Annual', 'new_Annual', 'Sharpe', 'new_Sharpe', 'SR', 'new_SR',
                                                                          'DrawBack', 'new_DrawBack']]
        return pv_df
