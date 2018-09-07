# -*- coding: utf-8 -*-
import MultiLayerForward.MultiLayerForward as mtf
from datetime import datetime
import pandas as pd
import DataInterface.DataInterface as DI
import os
import multiprocessing
import Parameter
import StopLoss


def get_forward(strategyName, symbolinfo, K_MIN, parasetlist, rawdatapath, startdate, enddate, colslist, result_para_dic, indexcolsFlag, resultfilesuffix):
    forward_window_set = range(Parameter.forwardWinStart, Parameter.forwardWinEnd + 1)  # 白区窗口值
    nextmonth = enddate[0:7]
    symbol = symbolinfo.domain_symbol
    forwordresultpath = rawdatapath + '\\ForwardResults\\'
    forwardrankpath = rawdatapath + '\\ForwardRank\\'
    monthlist = [datetime.strftime(x, '%Y-%m') for x in list(pd.date_range(start=startdate, end=enddate, freq='M'))]
    monthlist.append(nextmonth)
    os.chdir(rawdatapath)
    try:
        os.mkdir('ForwardResults')
    except:
        print 'ForwardResults already exist!'
    try:
        os.mkdir('ForwardRank')
    except:
        print 'ForwardRank already exist!'
    try:
        os.mkdir('ForwardOprAnalyze')
    except:
        print 'ForwardOprAnalyze already exist!'

    starttime = datetime.now()
    print starttime
    # 多进程优化，启动一个对应CPU核心数量的进程池

    initialCash = result_para_dic['initialCash']
    positionRatio = result_para_dic['positionRatio']

    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    l = []
    for whiteWindows in forward_window_set:
        # l.append(mtf.runPara(strategyName,whiteWindows, symbolinfo, K_MIN, parasetlist, monthlist, rawdatapath, forwordresultpath, forwardrankpath, colslist, resultfilesuffix))
        l.append(pool.apply_async(mtf.runPara, (
        strategyName, whiteWindows, symbolinfo, K_MIN, parasetlist, monthlist, rawdatapath, forwordresultpath, forwardrankpath, colslist, resultfilesuffix)))
    pool.close()
    pool.join()
    mtf.calGrayResult(strategyName, symbol, K_MIN, forward_window_set, forwardrankpath, rawdatapath)
    indexcols = Parameter.ResultIndexDic

    # rawdata = DC.getBarData(symbol, K_MIN, monthlist[12] + '-01 00:00:00', enddate + ' 23:59:59').reset_index(drop=True)
    cols = ['open', 'high', 'low', 'close', 'strtime', 'utc_time', 'utc_endtime']
    barxmdic = DI.getBarDic(symbolinfo, K_MIN, cols)

    mtf.calOprResult(strategyName, rawdatapath, symbolinfo, K_MIN, nextmonth, colslist, barxmdic, positionRatio, initialCash, indexcols, indexcolsFlag, resultfilesuffix)
    endtime = datetime.now()
    print starttime
    print endtime


def get_mix_forward(strategyName, sltlist, symbolinfo, K_MIN, parasetlist, folderpath, startdate, enddate, result_para_dic):
    '''
    混合止损推进
    '''
    print ('multiSLT forward start!')
    colslist = mtf.getColumnsName(True)
    resultfilesuffix = 'result_multiSLT.csv'
    indexcolsFlag = True
    # 先生成参数列表
    allSltSetList = []  # 这是一个二维的参数列表，每一个元素是一个止损目标的参数dic列表
    for slt in sltlist:
        sltset = []
        for t in slt['paralist']:
            sltset.append({'name': slt['name'],
                           'sltValue': t,   # t是一个参数字典
                           'folder': ("%s%s\\" % (slt['folderPrefix'], t['para_name'])),
                           'fileSuffix': slt['fileSuffix'] + t['para_name'] + '.csv'
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
    print finalSltSetList
    for sltset in finalSltSetList:
        newfolder = ''
        for sltp in sltset:
            v = sltp['sltValue']
            newfolder += "{}_{}".format(sltp['name'], v["para_name"])
        rawdatapath = folderpath + newfolder + '\\'
        print ("multiSTL Target:%s" % newfolder)
        get_forward(strategyName, symbolinfo, K_MIN, parasetlist, rawdatapath, startdate, enddate, colslist, result_para_dic, indexcolsFlag, resultfilesuffix)
    print ('multiSTL forward finished!')


if __name__ == '__main__':
    # ======================================参数配置===================================================
    strategy_name = Parameter.strategy_name
    strategyParameterSet = []
    if not Parameter.multi_symbol_bt_swtich:
        # 单品种单周期模式
        paradic = {
            'strategyName': strategy_name,
            'exchange_id': Parameter.exchange_id,
            'sec_id': Parameter.sec_id,
            'K_MIN': Parameter.K_MIN,
            'startdate': Parameter.startdate,
            'enddate': Parameter.enddate,
            'result_para_dic': Parameter.result_para_dic,
        }
        forward_mode_dic = {}
        for mode, pdic in Parameter.forward_mode_para_dic.items():
            if pdic[mode]:
                forward_mode_dic[mode] = pdic
        paradic['forward_mode_dic'] = forward_mode_dic
        strategyParameterSet.append(paradic)
    else:
        # 多品种多周期模式
        symbolset = pd.read_excel(Parameter.strategy_folder + Parameter.forward_set_filename, index_col='No')
        symbolsetNum = symbolset.shape[0]
        for i in range(symbolsetNum):
            exchangeid = symbolset.ix[i, 'exchange_id']
            secid = symbolset.ix[i, 'sec_id']
            symbol_para_dic = {
                'strategyName': symbolset.ix[i, 'strategyName'],
                'exchange_id': exchangeid,
                'sec_id': secid,
                'K_MIN': symbolset.ix[i, 'K_MIN'],
                'startdate': symbolset.ix[i, 'startdate'],
                'enddate': symbolset.ix[i, 'enddate'],
                'result_para_dic': Parameter.result_para_dic
            }
            forward_mode_dic = {}
            for k, v in Parameter.forward_mode_para_dic.items():
                enable = symbolset.ix[i, k]
                sub_stop_loss_dic = {}
                if enable:
                    for k1 in v.values():
                        if k1 == k:
                            sub_stop_loss_dic[k1] = True
                        else:
                            sub_stop_loss_dic[k1] = Parameter.para_str_to_float(symbolset.ix[i, k1])
                forward_mode_dic[k] = sub_stop_loss_dic
            symbol_para_dic['forward_mode_dic'] = forward_mode_dic
            strategyParameterSet.append(symbol_para_dic)

    for strategyParameter in strategyParameterSet:

        strategyName = strategyParameter['strategyName']
        exchange_id = strategyParameter['exchange_id']
        sec_id = strategyParameter['sec_id']
        bar_type = strategyParameter['K_MIN']
        startdate = strategyParameter['startdate']
        enddate = strategyParameter['enddate']

        symbol = '.'.join([exchange_id, sec_id])

        result_para_dic = strategyParameter['result_para_dic']
        forward_mode_dic = strategyParameter['forward_mode_dic']

        symbol_info = DI.SymbolInfo(symbol, startdate, enddate)
        symbol_bar_folder_name = Parameter.strategy_folder + "%s %s %s %d" % (
            strategy_name, exchange_id, sec_id, bar_type)
        os.chdir(symbol_bar_folder_name)
        paraset_name = "%s %s %s %d Parameter.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        # 读取已有参数表
        parasetlist = pd.read_csv(paraset_name)['Setname'].tolist()
        # 混合止损模式
        sltlist = []
        for sl_name, stop_loss in forward_mode_dic.items():
            if sl_name != 'multi_sl' and sl_name != 'common':  # 混合标志和普通模式标志都是不带参数的
                stop_loss_class = StopLoss.strategy_mapping_dic[sl_name](stop_loss)
                sltlist.append({'name': sl_name,
                                'paralist': stop_loss_class.get_para_dic_list(),
                                'folderPrefix': stop_loss_class.get_folder_prefix(),
                                'fileSuffix': stop_loss_class.get_file_suffix()
                                })

        if 'multi_sl' in forward_mode_dic.keys():
            get_mix_forward(strategyName, sltlist, symbol_info, bar_type, parasetlist, symbol_bar_folder_name, startdate, enddate, result_para_dic)
        else:
            # 单止损模式
            if 'common' in forward_mode_dic.keys():
                colslist = mtf.getColumnsName(False)
                resultfilesuffix = 'result.csv'
                indexcolsFlag = False
                bt_folder = symbol_bar_folder_name + "%s %d backtesting\\" % (symbol, bar_type)
                get_forward(strategyName, symbol_info, bar_type, parasetlist, bt_folder, startdate, enddate, colslist, result_para_dic, indexcolsFlag,
                   resultfilesuffix)
            for slt in sltlist:
                colslist = mtf.getColumnsName(False)
                resultfilesuffix = slt['fileSuffix']
                folder_prefix = slt['folderPrefix']
                indexcolsFlag = False
                for stop_loss_para_dic in slt['paralist']:
                    para_name = stop_loss_para_dic['para_name']
                    raw_folder = symbol_bar_folder_name + "%s%s" % (folder_prefix, para_name)
                    get_forward(strategyName, symbol_info, bar_type, parasetlist, raw_folder, startdate, enddate, colslist, result_para_dic, indexcolsFlag,
                       resultfilesuffix+para_name+'.csv')
