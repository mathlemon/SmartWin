# -*- coding: utf-8 -*-
"""
SmartWin回策框架
策略基础模块
作者:Smart
新建时间：2018-09-02
"""
class StrategyTemplate(object):
    """
    策略基础模板
    """
    strategy_name = 'basic_template'
    strategy_para_name_list = []

    def __init__(self,):
        pass

    def run_trade_logic(self, symbol_info, raw_data, para_dic):
        pass

    def get_para_list(self, para_list_dic):
        pass

    def get_para_name_list(self):
        return self.strategy_para_name_list
