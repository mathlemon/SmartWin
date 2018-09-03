# -*- coding: utf-8 -*-
"""
SmartWin回策框架
止损出场基础模板
作者:Smart
新建时间：2018-09-03
"""
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

    def get_para_dic_list(self,):
        return self.para_dic_list

    def get_para_name_list(self):
        return self.sl_para_name_list

    def get_folder_prefix(self):
        return self.folder_prefix

    def get_file_suffix(self):
        return self.file_suffix

    def get_sl_name(self):
        return self.sl_name
