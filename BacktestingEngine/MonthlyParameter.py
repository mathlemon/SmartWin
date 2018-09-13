# -*- coding: utf-8 -*-
import MultiLayerForward.MultiLayerForward as mtf
import pandas as pd
import DataInterface.DataInterface as DC
import StopLoss
import os
import Parameter
import numpy as np
from datetime import datetime


def getmultiStlMonthParameter(strategyName, sltlist, symbolinfo, K_MIN, parasetlist, startmonth, endmonth):
    colslist = mtf.getColumnsName(True)
    resultfilesuffix = 'result_multiSLT.csv'
    # 先生成参数列表
    allSltSetList = []  # 这是一个二维的参数列表，每一个元素是一个止损目标的参数dic列表
    for slt in sltlist:
        sltset = []
        for t in slt['paralist']:
            sltset.append({'name': slt['name'],
                           'sltValue': t
                           })
        allSltSetList.append(sltset)
    finalSltSetList = []  # 二维数据，每个一元素是一个多个止损目标的参数dic组合
    for sltpara in allSltSetList[0]:
        finalSltSetList.append([sltpara])
    for i in range(1, len(allSltSetList)):
        tempset = allSltSetList[i]
        newset = []
        for o in finalSltSetList:
            for t in tempset:
                newset.append(o + [t])
        finalSltSetList = newset
    for sltset in finalSltSetList:
        newfolder = ''
        for sltp in sltset:
            newfolder += (sltp['name'] + '_%s' % (sltp['sltValue']['para_name']))
        print newfolder
        rawdatapath = newfolder + '\\'
        df = mtf.getMonthParameter(strategyName, startmonth, endmonth, symbolinfo, K_MIN, parasetlist, rawdatapath, colslist, resultfilesuffix)
        filenamehead = ("%s%s_%s_%d_%s_parameter_%s" % (rawdatapath, strategyName, symbolinfo.domain_symbol, K_MIN, endmonth, newfolder))
        df.to_csv(filenamehead + '.csv')


if __name__ == '__main__':
    # 文件路径

    # 生成月份列表，取开始月
    newmonth = Parameter.enddate[:7]
    month_n = Parameter.month_n
    monthlist = [datetime.strftime(x, '%Y-%m') for x in
                 list(pd.date_range(start=Parameter.startdate, end=newmonth + '-01', freq='M'))]
    startmonth = monthlist[-month_n]
    # ======================================参数配置==================================================
    strategy_name = Parameter.strategy_name
    exchange_id = Parameter.exchange_id
    sec_id = Parameter.sec_id
    bar_type = Parameter.K_MIN
    symbol = '.'.join([exchange_id, sec_id])
    symbolinfo = DC.SymbolInfo(symbol)

    price_tick = symbolinfo.getPriceTick()

    symbol_bar_folder_name = Parameter.strategy_folder + "%s %s %s %d\\" % (
        strategy_name, exchange_id, sec_id, bar_type)
    os.chdir(symbol_bar_folder_name)
    paraset_name = "%s %s %s %d Parameter.csv" % (strategy_name, exchange_id, sec_id, bar_type)
    # 读取已有参数表
    parasetlist = pd.read_csv(paraset_name)['Setname'].tolist()
    paranum = len(parasetlist)
    sltlist = []
    calcMultiSLT = False
    for sl_name, stop_loss in Parameter.forward_mode_para_dic.items():
        if sl_name == 'multi_sl':
            calcMultiSLT = stop_loss['multi_sl']
        elif sl_name != 'common':  # 混合标志和普通模式标志都是不带参数的
            if stop_loss[sl_name]:
                stop_loss['price_tick'] = price_tick
                stop_loss_class = StopLoss.strategy_mapping_dic[sl_name](stop_loss)
                sltlist.append({'name': sl_name,
                                'paralist': stop_loss_class.get_para_dic_list(),
                                'folderPrefix': stop_loss_class.get_folder_prefix(),
                                'fileSuffix': stop_loss_class.get_file_suffix()
                                })

    if calcMultiSLT:
        getmultiStlMonthParameter(strategy_name, sltlist, symbolinfo, bar_type, parasetlist, startmonth, newmonth)
    else:
        commom_dic = Parameter.forward_mode_para_dic['common']
        if commom_dic['common']:
            colslist = mtf.getColumnsName(False)
            resultfilesuffix = ' result.csv'
            bt_folder = symbol_bar_folder_name + "%s %d backtesting\\" % (symbol, bar_type)
            df = mtf.getMonthParameter(strategy_name, startmonth, newmonth, symbolinfo, bar_type, parasetlist, bt_folder, colslist, resultfilesuffix)
            filenamehead = ("%s_%s_%d_%s_parameter_common" % (strategy_name, symbolinfo.domain_symbol, bar_type, newmonth))
            df.to_csv(filenamehead + '.csv')
        for slt in sltlist:
            colslist = mtf.getColumnsName(False)
            sl_name = slt['name']
            resultfilesuffix = slt['fileSuffix']
            folder_prefix = slt['folderPrefix']
            indexcolsFlag = False
            for stop_loss_para_dic in slt['paralist']:
                para_name = stop_loss_para_dic['para_name']
                raw_folder = symbol_bar_folder_name + "%s%s\\" % (folder_prefix, para_name)
                df = mtf.getMonthParameter(strategy_name, startmonth, newmonth, symbolinfo, bar_type, parasetlist, raw_folder, colslist, resultfilesuffix + para_name + '.csv')
                filenamehead = ("%s%s_%s_%d_%s_parameter_%s%s" % (raw_folder, strategy_name, symbolinfo.domain_symbol, bar_type, newmonth, sl_name, para_name))
                df.to_csv(filenamehead + '.csv')
