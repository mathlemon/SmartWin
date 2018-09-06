# -*- coding: utf-8 -*-
"""
SmartWin回策框架
作者:Smart
新建时间：2018-09-02
"""

from MacdMaWin import MacdMaWin
from HullRsiWin import HullRsiWin
from LvyiWin import LvyiWin

strategy_mapping_dic = {
    'MacdMaWin': MacdMaWin,
    'HullRsiWin': HullRsiWin,
    'LvyiWin': LvyiWin
}
