# -*- coding: utf-8 -*-
"""
SmartWin回策框架
止损离场引擎
作者:Smart
新建时间：2018-09-02
"""
import StopLoss
import DataInterface.DataInterface as DI
import pandas as pd
import os
import numpy as np
import multiprocessing
import datetime
import Parameter
import time


def single_sl(strategy_name, symbol_info, bar_type, para_set_list, stop_loss_para_dic, result_para_dic, time_start):
    symbol = symbol_info.domain_symbol
    price_tick = symbol_info.getPriceTick()
    bt_folder = "%s %d backtesting\\" % (symbol, bar_type)
    oprdf = pd.read_csv(bt_folder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' result.csv')

    close_type_list = []
    all_final_result_dic = {}  # 这个是用来保存每个文件的RS结果，返回给外部调用的
    all_close_result_dic = {}  # 这个是用来保存每个参数每次操作的止损结果
    for close_para in all_close_para_list:
        close_type_list.append(close_para['name'])
        final_result_dic = {}
        for para in close_para['paralist']:
            final_result_dic[para['para_name']] = []
            all_close_result_dic[para['para_name']] = []
        all_final_result_dic[close_para['name']] = final_result_dic

    symbolDomainDic = symbol_info.amendSymbolDomainDicByOpr(oprdf)
    bar1m = DC.getDomainbarByDomainSymbol(symbol_info.getSymbolList(), bar1mdic, symbolDomainDic)
    bar1m = bar1mPrepare(bar1m)
    barxm = DC.getDomainbarByDomainSymbol(symbol_info.getSymbolList(), barxmdic, symbolDomainDic)

    barxm.set_index('utc_time', drop=False, inplace=True)  # 开始时间对齐
    bar1m.set_index('utc_time', drop=False, inplace=True)
    if 'gownl' in close_type_list:
        # gownl数据预处理
        barxm['index_num'] = range(barxm.shape[0])
        bar1m['index_num'] = barxm['index_num']
        bar1m.fillna(method='ffill', inplace=True)  # 用上一个非0值来填充

    positionRatio = result_para_dic['positionRatio']
    initialCash = result_para_dic['initialCash']

    oprnum = oprdf.shape[0]
    worknum = 0
    for i in range(oprnum):
        opr = oprdf.iloc[i]
        startutc = barxm.loc[opr['openutc'], 'utc_endtime'] - 60  # 从开仓的10m线结束后开始
        endutc = barxm.loc[opr['closeutc'], 'utc_endtime']  # 一直到平仓的10m线结束
        data1m = bar1m.loc[startutc:endutc]
        for close_type_para in all_close_para_list:
            close_type = close_type_para['name']
            close_function = close_function_map[close_type]
            close_para_list = close_type_para['paralist']
            for close_para in close_para_list:
                newcloseprice, strtime, utctime, timeindex = close_function(opr, data1m, close_para, price_tick)
                all_close_result_dic[close_para['para_name']].append({
                    'new_closeprice': newcloseprice,
                    'new_closetime': strtime,
                    'new_closeutc': utctime,
                    'new_closeindex': timeindex
                })

    slip = symbol_info.getSlip()

    olddailydf = pd.read_csv(
        bt_folder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' dailyresult.csv',
        index_col='date')
    oldr = RS.getStatisticsResult(oprdf, False, indexcols, olddailydf)
    dailyK = DC.generatDailyClose(barxm)

    # 全部止损完后，针对每个止损参数要单独计算一次结果
    for close_type_para in all_close_para_list:
        close_type = close_type_para['name']
        folder_prefix = close_type_para['folderPrefix']
        file_suffix = close_type_para['fileSuffix']
        close_para_list = close_type_para['paralist']
        for close_para in close_para_list:
            para_name = close_para['para_name']
            close_result_list = all_close_result_dic[para_name]
            result_df = pd.DataFrame(close_para_list)
            oprdf_temp = pd.concat([oprdf, result_df], axis=1)
            oprdf_temp['new_ret'] = ((oprdf_temp['new_closeprice'] - oprdf_temp['openprice']) * oprdf_temp[
                'tradetype']) - slip
            oprdf_temp['new_ret_r'] = oprdf_temp['new_ret'] / oprdf_temp['openprice']
            oprdf_temp['new_commission_fee'], oprdf_temp['new_per earn'], oprdf_temp['new_own cash'], oprdf_temp[
                'new_hands'] = RS.calcResult(oprdf_temp,
                                             symbol_info,
                                             initialCash,
                                             positionRatio, ret_col='new_ret')
            # 保存新的result文档
            tofolder = "%s%s\\" % (folder_prefix, para_name)
            oprdf_temp.to_csv(
                tofolder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' ' + file_suffix,
                index=False)

            dR = RS.dailyReturn(symbol_info, oprdf_temp, dailyK, initialCash)  # 计算生成每日结果
            dR.calDailyResult()
            dR.dailyClose.to_csv(
                (tofolder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' daily' + file_suffix))
            newr = RS.getStatisticsResult(oprdf, True, indexcols, dR.dailyClose)
            final_result_dic = all_final_result_dic[close_type]
            final_result_dic[para_name] = [setname, para_name, worknum] + oldr + newr

    return all_final_result_dic


def single_sl_engine(strategy_name, symbol_info, bar_type, para_set_list, stop_loss_para_dic, result_para_dic, time_start):
    symbol = symbolinfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    paranum = parasetlist.shape[0]
    all_result_dic = {}  # 这个保存的是每个止损参数的结果
    for close_para_dic in all_close_para_dic:
        close_folder_prefix = close_para_dic['folderPrefix']
        paralist = close_para_dic['paralist']
        result_dic = {}
        for para in paralist:
            para_name = para['para_name']
            folderName = '%s%s' % (close_folder_prefix, para_name)
            try:
                os.mkdir(folderName)  # 创建文件夹
            except:
                pass
            resultdf = pd.DataFrame(columns=['setname', close_para_dic['name'], 'worknum'] + indexcols + new_indexcols)
            result_dic[para_name] = resultdf
        all_result_dic[close_para_dic['name']] = result_dic
    timestart = time.time()
    setnum = 0
    numlist = range(0, paranum, 100)
    numlist.append(paranum)
    for n in range(1, len(numlist)):
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for a in range(numlist[n - 1], numlist[n]):
            setname = parasetlist.ix[a, 'Setname']
            l.append(pool.apply_async(all_close.all_close, (strategyName,
                                                            symbolinfo, bar_type, setname, bar1mdic, barxmdic,
                                                            all_close_para_dic, result_para_dic, indexcols, timestart)))
        pool.close()
        pool.join()

        for res in l:
            get_result_dic = res.get()
            for k, v in get_result_dic:
                result_dic = all_result_dic[k]
                for k1, v1 in v:
                    result_dic[k1].loc[setnum] = v1
            setnum += 1
    for close_para_dic in all_close_para_dic:
        close_folder_prefix = close_para_dic['folderPrefix']
        paralist = close_para_dic['paralist']
        close_type = close_para_dic['name']
        result_dic = all_result_dic[close_type]
        all_result_list = []
        for para in paralist:
            para_name = para['para_name']
            folderName = '%s%s' % (close_folder_prefix, para_name)
            resultdf = result_dic[para_name]
            resultdf.to_csv(
                folderName + '\\' + strategyName + ' ' + symbol + str(bar_type) + ' finalresult_%s%s.csv' % (
                    close_type, para_name),
                index=False)
            all_result_list.append(resultdf)
        all_final_result = pd.concat(all_result_list)
        all_final_result.to_csv(strategyName + ' ' + symbol + str(bar_type) + ' finalresult_%s.csv' % close_type,
                                index=False)
    timeend = time.time()
    timecost = timeend - timestart
    print (u"全部止损计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (paranum, timecost, timecost / paranum))


def multi_sl_engine(strategyName, symbolInfo, K_MIN, parasetlist, barxmdic, sltlist, result_para_dic, indexcols):
    """
    计算多个止损策略结合回测的结果
    :param strategyName:
    :param symbolInfo:
    :param K_MIN:
    :param parasetlist:
    :param sltlist:
    :param positionRatio:
    :param initialCash:
    :return:
    """
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    allresultdf_cols = ['setname', 'slt', 'slWorkNum'] + indexcols + new_indexcols
    allresultdf = pd.DataFrame(columns=allresultdf_cols)

    allnum = 0
    paranum = parasetlist.shape[0]

    # dailyK = DC.generatDailyClose(barxm)

    # 先生成参数列表
    allSltSetList = []  # 这是一个二维的参数列表，每一个元素是一个止损目标的参数dic列表
    for slt in sltlist:
        sltset = []
        for t in slt['paralist']:
            sltset.append({'name': slt['name'],
                           'sltValue': t,   # t是一个参数字典
                           'folder': ("%s%s\\" % (slt['folderPrefix'], t['para_name'])),
                           'fileSuffix': slt['fileSuffix']
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
            #newfolder += (sltp['name'] + '_%.3f' % (sltp['sltValue']))
            v = sltp['sltValue']
            newfolder += "{}_{}".format(sltp['name'], v["para_name"])
        try:
            os.mkdir(newfolder)  # 创建文件夹
        except:
            pass
        print (newfolder)
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for sn in range(0, paranum):
            setname = parasetlist.ix[sn, 'Setname']
            # l.append(msl.multiStopLosslCal(strategyName, symbolInfo, K_MIN, setname, sltset, positionRatio, initialCash,
            #                           newfolder + '\\'))
            l.append(pool.apply_async(msl.multiStopLosslCal,
                                      (strategyName, symbolInfo, K_MIN, setname, sltset, barxmdic, result_para_dic, newfolder, indexcols)))
        pool.close()
        pool.join()

        resultdf = pd.DataFrame(columns=allresultdf_cols)
        i = 0
        for res in l:
            resultdf.loc[i] = res.get()
            allresultdf.loc[allnum] = resultdf.loc[i]
            i += 1
            allnum += 1
        resultfilename = ("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, newfolder))
        resultdf.to_csv(newfolder + '\\' + resultfilename, index=False)

    allresultname = ''
    for slt in sltlist:
        allresultname += slt['name']
    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, allresultname), index=False)
    pass


if __name__ == '__main__':
    # 参数设置
    strategy_name = Parameter.strategy_name
    strategyParameterSet = []
    if not Parameter.multi_symbol_bt_swtich:
        # 单品种单周期模式
        paradic = {
            'strategy_name': strategy_name,
            'exchange_id': Parameter.exchange_id,
            'sec_id': Parameter.sec_id,
            'K_MIN': Parameter.K_MIN,
            'startdate': Parameter.startdate,
            'enddate': Parameter.enddate,
            'result_para_dic': Parameter.result_para_dic,
        }
        stop_loss_dic = {}
        for k, v in Parameter.stop_loss_para_dic.items():
            if v[k] == True:
                stop_loss_dic[k] = v
        paradic['stop_loss_dic'] = stop_loss_dic
        strategyParameterSet.append(paradic)
    else:
        # 多品种多周期模式
        symbolset = pd.read_excel(Parameter.strategy_folder + Parameter.stoploss_set_filename, index_col='No')
        symbolsetNum = symbolset.shape[0]
        for i in range(symbolsetNum):
            exchangeid = symbolset.ix[i, 'exchange_id']
            secid = symbolset.ix[i, 'sec_id']
            para_dic = {
                'strategy_name': symbolset.ix[i, 'strategy_name'],
                'exchange_id': exchangeid,
                'sec_id': secid,
                'K_MIN': symbolset.ix[i, 'K_MIN'],
                'startdate': symbolset.ix[i, 'startdate'],
                'enddate': symbolset.ix[i, 'enddate'],
                'result_para_dic': Parameter.result_para_dic
            }
            stop_loss_dic = {}
            for k, v in Parameter.stop_loss_para_dic.items():
                enable = symbolset.ix[i, k]
                sub_stop_loss_dic = {}
                if enable:
                    for k1 in v.values():
                        if k1 == k:
                            sub_stop_loss_dic[k1] = True
                        else:
                            sub_stop_loss_dic[k1] = Parameter.para_str_to_float(symbolset.ix[i, k1])
                stop_loss_dic[k] = sub_stop_loss_dic
            para_dic['stop_loss_dic'] = stop_loss_dic
            strategyParameterSet.append(para_dic)

    for strategyParameter in strategyParameterSet:

        strategy_name = strategyParameter['strategy_name']
        exchange_id = strategyParameter['exchange_id']
        sec_id = strategyParameter['sec_id']
        bar_type = strategyParameter['K_MIN']
        startdate = strategyParameter['startdate']
        enddate = strategyParameter['enddate']
        domain_symbol = '.'.join([exchange_id, sec_id])

        result_para_dic = strategyParameter['result_para_dic']
        stop_loss_dic = strategyParameter['stop_loss_dic']

        symbolinfo = DI.SymbolInfo(domain_symbol, startdate, enddate)

        symbol_bar_folder_name = Parameter.strategy_folder + "%s %s %s %d" % (
            strategy_name, exchange_id, sec_id, bar_type)
        os.chdir(symbol_bar_folder_name)
        paraset_name = "%s %s %s %d Parameter.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        # 读取已有参数表
        parasetlist = pd.read_csv(paraset_name)['Setname'].tolist()

        if 'multi_sl' in stop_loss_dic.keys():
            # 混合止损模式
            pass
        else:
            # 单止损模式
            pass
