# -*- coding: utf-8 -*-
"""
策略参数设置
"""
import numpy

# 参数设置
strategy_name = 'HullRsiWin'
exchange_id = 'SHFE'
sec_id = 'RB'
K_MIN = 3600
startdate = '2010-01-01'
enddate = '2018-09-01'
multi_symbol_bt_swtich = False  # 多品种多周期优化开关，打开后代码会从下面标识的文件中导入参数
result_para_dic = {  # 结果计算相关参数
    'positionRatio': 0.2,  # 持仓比例
    'initialCash': 1000000,  # 起始资金
    'remove_polar_switch': False,
    'remove_polar_rate': 0.01
}

strategy_para_dic = {
    # 该参数表用于各品种模式下的测试，当new为True时使用该参数表生成参数文件，为False时读取策略品种文件夹中已有的参数文件
    'MacdMaWin': {
        'new_para': True,
        'MS': [5, 10],
        'MM': [10, 20],
        "ML": [20, 30],
        "MA": [30, 40]
    },
    'HullRsiWin': {
        'new_para': False,
        "N1": [15, 20],
        "M1": [6, 10],
        "M2": [3],
        "N": [6, 10],
        "MaN": [20, 30]
    },
    'LvyiWin': {
        'new_para': True,
        "MS": [5, 8],
        "ML": [10, 15],
        "KDJ_N": [20],
        "DMI_N": [26, 30]
    }
}
# ====================止损控制开关=====================
stop_loss_para_dic = {
    "multi_sl": {
        "multi_sl": True  # 混合止损开关
    },
    "dsl": {
        "dsl": True,  # 动态止损开关
        "dsl_target": [-0.018, -0.02, -0.022]
    },
    "ownl": {
        "ownl": False,
        "ownl_protect": [0.008, 0.009, 0.010, 0.011],  # ownl保护触发门限
        "ownl_floor": [3]  # ownl地板价：止损线(PT数量）
    },
    "frsl": {
        "frsl": True,
        "frsl_target": [-0.01, -0.011, -0.012]  # 固定止损比例
    },
    "gownl": {
        "gownl": True,
        "gownl_protect": [0.007, 0.009, 0.011],  # gownl保护触发门限
        "gownl_floor": [-4, 5],  # gownl地板价起始点
        "gownl_step": [1, 3]  # gownl地板价递进步伐
    },
    "pendant": {
        "pendant": False,
        "pendant_n": [3, 5, 7],  # 吊灯atr的n值
        "pendant_rate": [1.0, 1.5, 2.0]  # 吊灯atr的最大回撤止损atr比例
    },
    "yoyo": {
        "yoyo": False,
        "yoyo_n": [8, 16, 30],  # yoyo的atr n值
        "yoyo_rate": [1, 1.2, 1.5]  # yoyo的止损atr比例
    }
}

# ====================推进控制开关===================
forwardWinStart = 5
forwardWinEnd = 8
month_n = 7  # n+x的n值，即往前推多少个月

forward_mode_para_dic = {
    "multi_sl": {
        "multi_sl": False  # 混合止损开关
    },
    "common": {
        "common": False  # 普通回测结果推进
    },
    "dsl": {
        "dsl": True,  # 动态止损开关
        "dsl_target": [-0.018]
    },
    "ownl": {
        "ownl": False,
        "ownl_protect": [0.008, 0.009, 0.010, 0.011],  # ownl保护触发门限
        "ownl_floor": [3]  # ownl地板价：止损线(PT数量）
    },
    "frsl": {
        "frsl": False,
        "frsl_target": [-0.01, -0.011, -0.012]  # 固定止损比例
    },
    "gownl": {
        "gownl": False,
        "gownl_protect": [0.007, 0.009, 0.011],  # gownl保护触发门限
        "gownl_floor": [-4, 5],  # gownl地板价起始点
        "gownl_step": [1, 3]  # gownl地板价递进步伐
    },
    "pendant": {
        "pendant": False,
        "pendant_n": [3, 5, 7],  # 吊灯atr的n值
        "pendant_rate": [1.0, 1.5, 2.0]  # 吊灯atr的最大回撤止损atr比例
    },
    "yoyo": {
        "yoyo": False,
        "yoyo_n": [8, 16, 30],  # yoyo的atr n值
        "yoyo_rate": [1, 1.2, 1.5]  # yoyo的止损atr比例
    }
}

# ====================系统参数==================================
# 1.品种和周期组合文件
symbol_KMIN_set_filename = strategy_name + '_multi_symbol_setting_bt.xlsx'
# 2.第一步的结果中挑出满足要求的项，做成双止损组合文件
stoploss_set_filename = strategy_name + '_multi_symbol_setting_stoploss.xlsx'
# 3.从第二步的结果中挑出满足要求的项，做推进
forward_set_filename = strategy_name + '_multi_symbol_setting_forward'

root_path = 'D:\\BT_Results\\'
strategy_folder = "%s%s\\" % (root_path, strategy_name)     # 每个策略对应一个文件夹

# =================结果指标开关====================
ResultIndexDic = [
    "OprTimes",  # 操作次数
    "LongOprTimes",  # 多操作次数
    "ShortOprTimes",  # 空操作次数
    "EndCash",  # 最终资金
    "MaxOwnCash",  # 最大期间资金
    "LongOprRate",  # 多操作占比
    "ShortOprRate",  # 空操作占比
    "Annual",  # 年化收益
    "Sharpe",  # 夏普
    "SR",  # 成功率
    "LongSR",  # 多操作成功率
    "ShortSR",  # 空操作成功率
    "DrawBack",  # 资金最大回撤
    "MaxSingleEarnRate",  # 单次最大盈利率
    "MaxSingleLossRate",  # 单次最大亏损率
    "ProfitLossRate",  # 盈亏比
    "LongProfitLossRate",  # 多操作盈亏比
    "ShoartProfitLossRate",  # 空操作盈亏比
    "MaxSuccessiveEarn",  # 最大连续盈利次数
    "MaxSuccessiveLoss",  # 最大连续亏损次数
    "AvgSuccessiveEarn",  # 平均连续盈利次数
    "AveSuccessiveLoss"  # 平均连续亏损次数'
]


# ===================== 通用功能函数 =========================================
def para_str_to_float(para_str):
    # 功能函数：用于将从多品种多周期文件读取进来的字符串格式的参数列表转换为符点型列表
    p_type = type(para_str)
    para_float_list = []
    if p_type == numpy.int64 or p_type == numpy.float64 or p_type == float:
        para_float_list.append(float(para_str))
    else:
        for x in para_str.split(','):
            para_float_list.append(float(x))
    return para_float_list


def para_str_to_int(para_str):
    # 功能函数：用于将从多品种多周期文件读取进来的字符串格式的参数列表转换为符点型列表
    para_float_list = []
    p_type = type(para_str)
    if p_type == numpy.int64 or p_type == numpy.float64 or p_type == float:
        para_float_list.append(int(para_str))
    else:
        for x in para_str.split(','):
            para_float_list.append(int(x))
    return para_float_list
