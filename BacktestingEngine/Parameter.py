# -*- coding: utf-8 -*-
"""
策略参数设置
"""
# 参数设置
strategy_name = 'HullRsiWin'
exchange_id = 'SHFE'
sec_id = 'AU'
K_MIN = 3600
startdate = '2010-01-01'
enddate = '2018-07-01'
multi_symbol_bt_swtich = True  # 多品种多周期优化开关，打开后代码会从下面标识的文件中导入参数
result_para_dic = {  # 结果计算相关参数
    'positionRatio': 0.3,  # 持仓比例
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
        'new_para': True,
        "N1": [15, 20],
        "M1": [6, 10],
        "M2": [3, 6, 9],
        "N": [6, 10],
        "MaN": [20, 30]
    }
}
# ====================止损控制开关======================
progress_close = False      # 增量模式开关
calc_all_close = False      # 一次全部计算模式，该模式不能与混合止损同时打开
calcMultiSLT_close = True  # 混合止损开关


calcDsl_close = True   # dsl动态止损开关
dsl_target_list_close = [-0.018, -0.02, -0.022]

calcOwnl_close = True  # ownl有赚不亏开关
ownl_protect_list_close = [0.008, 0.009, 0.010, 0.011]    # ownl保护触发门限
ownl_floor_list_close = [3]   # ownl地板价：止损线(PT数量）

calcGownl_close = True  # gownl递进式有赚不亏开关
gownl_protect_list_close = [0.007, 0.009, 0.011]  # gownl保护触发门限
gownl_floor_list_close = [-4, -1, 2, 5]   # gownl地板价起始点
gownl_step_list_close = [1, 2]    # gownl地板价递进步伐

calcFrsl_close = False  # frsl固定比例止损开关
frsl_target_list_close = [-0.01, -0.011, -0.012]  # 固定止损比例

calcAtrsl_close = False     # atrsl ATR吊灯和yoyo止损开关
atr_pendant_n_list_close = [5, 8]     # 吊灯atr的n值
atr_pendant_rate_list_close = [1.0, 1.5, 2.0]     # 吊灯atr的最大回撤止损atr比例
atr_yoyo_n_list_close = [8, 16, 30]   # yoyo的atr n值
atr_yoyo_rate_list_close = [1, 1.2, 1.5]      # yoyo的止损atr比例

# =============推进控制开关===================
# nextMonthName='18-05'
forwardWinStart = 1
forwardWinEnd = 12

# 止损类型开关
multiSTL_forward = True  # 多止损混合推进开关（忽略common模式）
common_forward = False  # 普通回测结果推进
calcDsl_forward = False   # dsl动态止损开关
dsl_target_list_forward = [-0.018, -0.02, -0.022]

calcOwnl_forward = False  # ownl有赚不亏开关
ownl_protect_list_forward = [0.008, 0.009, 0.010, 0,011]    # ownl保护触发门限
ownl_floor_list_forward = [3]   # ownl地板价：止损线(PT数量）

calcGownl_forward = True  # gownl递进式有赚不亏开关
gownl_protect_list_forward = [0.007, 0.009, 0.011]  # gownl保护触发门限
gownl_floor_list_forward = [-4, -1, 2, 5]   # gownl地板价起始点
gownl_step_list_forward = [1, 2]    # gownl地板价递进步伐

calcFrsl_forward = False  # frsl固定比例止损开关
frsl_target_list_forward = [-0.01, -0.011, -0.012]  # 固定止损比例

calcAtrsl_forward = False     # atrsl ATR吊灯和yoyo止损开关
atr_pendant_n_list_forward = [5, 8]     # 吊灯atr的n值
atr_pendant_rate_list_forward = [1.0, 1.5, 2.0]     # 吊灯atr的最大回撤止损atr比例
atr_yoyo_n_list_forward = [8, 16, 30]   # yoyo的atr n值
atr_yoyo_rate_list_forward = [1, 1.2, 1.5]      # yoyo的止损atr比例

progress_forward = False      # 增量模式开关
calcMultiSLT_forward = False  # 混合止损开关

# ==================每月参数计算=====================
# newmonth='2018-05'#要生成参数的新月份
month_n = 7  # n+x的n值，即往前推多少个月

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
'''
#下面这个是指标全量，要加减从里面挑
ResultIndexDic=[
    "OprTimes", #操作次数
    "LongOprTimes",#多操作次数
    "ShortOprTimes",#空操作次数
    "EndCash",  # 最终资金
    "LongOprRate",#多操作占比
    "ShortOprRate",#空操作占比
    "Annual",#年化收益
    "Sharpe",#夏普
    "SR",#成功率
    "LongSR",#多操作成功率
    "ShortSR",#空操作成功率
    "DrawBack",#资金最大回撤
    "MaxSingleEarnRate",#单次最大盈利率
    "MaxSingleLossRate",#单次最大亏损率
    "ProfitLossRate",#盈亏比
    "LongProfitLossRate",#多操作盈亏比
    "ShoartProfitLossRate",#空操作盈亏比
    "MaxSuccessiveEarn",#最大连续盈利次数
    "MaxSuccessiveLoss",#最大连续亏损次数
    "AvgSuccessiveEarn",#平均连续盈利次数
    "AveSuccessiveLoss" #平均连续亏损次数'
]
'''


# 1.品种和周期组合文件
symbol_KMIN_set_filename = strategy_name + '_mulit_symbol_setting_bt.xlsx'
# 2.第一步的结果中挑出满足要求的项，做成双止损组合文件
stoploss_set_filename = strategy_name + '_stoploss_set.xlsx'
# 3.从第二步的结果中挑出满足要求的项，做推进
forward_set_filename = strategy_name + '_forward_set.xlsx'

# ====================系统参数==================================
root_path = 'D:\\BT_Results\\'
strategy_folder = "%s%s\\" % (root_path, strategy_name)

# ===================== 通用功能函数 =========================================
def para_str_to_float(para_str):
    # 功能函数：用于将从多品种多周期文件读取进来的字符串格式的参数列表转换为符点型列表
    para_float_list = []
    if type(para_str) != 'str':
        para_float_list.append(float(para_str))
    else:
        for x in para_str.split(','):
            para_float_list.append(float(x))
    return para_float_list


def para_str_to_int(para_str):
    # 功能函数：用于将从多品种多周期文件读取进来的字符串格式的参数列表转换为符点型列表
    para_float_list = []
    p_type = type(para_str)
    if p_type == int or p_type == long:
        para_float_list.append(int(para_str))
    else:
        for x in para_str.split(','):
            para_float_list.append(int(x))
    return para_float_list

def generat_para_file(para_list_dic = None):
    import pandas as pd
    """
    para_dic = strategy_para_dic
    keys = para_dic.keys()
    parasetlist = pd.DataFrame(columns=['Setname'] + keys)
    total_num = 1
    for v in para_dic.values():
        total_num *= len(v)
    parasetlist['No.'] = range(total_num)
    for i in range(total_num):
        parasetlist.ix[i, 'Setname'] = "Set%d" % i
    multipliter = total_num
    v_num = 1
    for k, v in para_dic.items():
        v_num = v_num * len(v)
        for i in range(v_num):
            v_value = v[i]
            multipliter = multipliter/v_num
            parasetlist.loc[i*multipliter: (i+1)*multipliter, k] = v_value
            parasetlist.loc[i*multipliter:(i+1)*multipliter, 'Setname'] = parasetlist.loc[i*multipliter:(i+1)*multipliter, 'Setname'] + " %s_%d" % (k, v_value)
    return parasetlist
    """
    if para_list_dic:
        n_list = para_str_to_int(para_list_dic['N'])
        m1_list = para_str_to_int(para_list_dic['M1'])
        m2_list = para_str_to_int(para_list_dic['M2'])
        n1_list= para_str_to_int(para_list_dic['N1'])
        man_list = para_str_to_int(para_list_dic['MaN'])
    else:
        n_list = strategy_para_dic['N']
        m1_list = strategy_para_dic['M1']
        m2_list = strategy_para_dic['M2']
        n1_list = strategy_para_dic['N1']
        man_list = strategy_para_dic['MaN']
    setlist = []
    i = 0
    for n1 in n1_list:
        for m1 in m1_list:
            #   for m2 in range(3, 15, 3):
            for m2 in m2_list:
                # for n in range(3, 16, 3):
                for n in n_list:
                    # for ma_n in range(20, 51, 10):
                    for ma_n in man_list:
                        setname = "Set%d N1_%d M1_%d M2_%d N_%d MaN_%d" % (i, n1, m1, m2, n, ma_n)
                        l = [setname, n1, m1, m2, n, ma_n]
                        setlist.append(l)
                        i += 1

    setpd = pd.DataFrame(setlist, columns=['Setname', 'N1', 'M1', 'M2', 'N', 'MaN'])
    return setpd
