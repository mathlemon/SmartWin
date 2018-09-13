# -*- coding: utf-8 -*-
"""
SmartWin回策框架
作者:Smart
新建时间：2018-09-02
"""

from MacdMaWin import MacdMaWin
from HullMacdMaWin import HullMacdMaWin
from HullRsiWin import HullRsiWin
from HullRsiTunnelWin import HullRsiTunnelWin
from LvyiWin import LvyiWin
from Lvyi3MaWin import Lvyi3MaWin

strategy_mapping_dic = {
    'MacdMaWin': MacdMaWin,
    'HullMacdMaWin': HullMacdMaWin,
    'HullRsiWin': HullRsiWin,
    'HullRsiTunnelWin': HullRsiTunnelWin,
    'LvyiWin': LvyiWin,
    'Lvyi3MaWin': Lvyi3MaWin
}
