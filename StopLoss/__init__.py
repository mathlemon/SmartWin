# -*- coding: utf-8 -*-
"""
SmartWin回策框架
作者:Smart
新建时间：2018-09-02
"""

from DSL import DslStopLoss
from FRSL import FrslStopLoss
from GOWNL import GownlStopLoss
from PENDANT import PendantStopLoss
from MultiStopLoss import multi_stop_loss

strategy_mapping_dic = {
    'dsl': DslStopLoss,
    'frsl': FrslStopLoss,
    'gownl': GownlStopLoss,
    'pendant': PendantStopLoss
}
