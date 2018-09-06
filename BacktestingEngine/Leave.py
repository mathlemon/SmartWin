# -*- coding: utf-8 -*-
"""
SmartWin回策框架
止损离场引擎
作者:Smart
新建时间：2018-09-02
"""
import StopLoss
import DataInterface.DataInterface as DI
import DataInterface.ResultStatistics as RS
import pandas as pd
import os
import multiprocessing
import Parameter
import time


def bar1m_prepare(bar1m):
    bar1m['longHigh'] = bar1m['high']
    bar1m['shortHigh'] = bar1m['high']
    bar1m['longLow'] = bar1m['low']
    bar1m['shortLow'] = bar1m['low']
    bar1m['highshift1'] = bar1m['high'].shift(1).fillna(0)
    bar1m['lowshift1'] = bar1m['low'].shift(1).fillna(0)
    bar1m.loc[bar1m['open'] < bar1m['close'], 'longHigh'] = bar1m['highshift1']
    bar1m.loc[bar1m['open'] > bar1m['close'], 'shortLow'] = bar1m['lowshift1']
    bar1m.drop('highshift1', axis=1, inplace=True)
    bar1m.drop('lowshift1', axis=1, inplace=True)
    # bar1m['Unnamed: 0'] = range(bar1m.shape[0])
    return bar1m


def single_sl(strategy_name, symbol_info, bar_type, setname, bar1m_dic, barxm_dic, stop_loss_class_list, result_para_dic, indexcols, timestart):
    print setname
    symbol = symbol_info.domain_symbol
    bt_folder = "%s %d backtesting\\" % (symbol, bar_type)
    oprdf = pd.read_csv(bt_folder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' result.csv')

    close_type_list = []
    all_final_result_dic = {}  # 这个是用来保存每个文件的RS结果，返回给外部调用的
    all_stop_loss_opr_result_dic = {}  # 这个是用来保存每个参数每次操作的止损结果
    for stop_loss_class in stop_loss_class_list:
        sl_name = stop_loss_class.get_sl_name()
        close_type_list.append(sl_name)
        final_result_dic = {}
        stop_loss_opr_result_dic = {}
        for para in stop_loss_class.get_para_dic_list():
            final_result_dic[para['para_name']] = []
            stop_loss_opr_result_dic[para['para_name']] = []
        all_stop_loss_opr_result_dic[sl_name] = stop_loss_opr_result_dic
        all_final_result_dic[sl_name] = final_result_dic

    for stop_loss_class in stop_loss_class_list:
        if stop_loss_class.need_data_process_before_domain:
            bar1m_dic, barxm_dic = stop_loss_class.data_process_before_domain(bar1m_dic, barxm_dic)

    symbolDomainDic = symbol_info.amendSymbolDomainDicByOpr(oprdf)
    bar1m = DI.getDomainbarByDomainSymbol(symbol_info.getSymbolList(), bar1m_dic, symbolDomainDic)
    bar1m = bar1m_prepare(bar1m)
    barxm = DI.getDomainbarByDomainSymbol(symbol_info.getSymbolList(), barxm_dic, symbolDomainDic)

    barxm.set_index('utc_time', drop=False, inplace=True)  # 开始时间对齐
    bar1m.set_index('utc_time', drop=False, inplace=True)

    for stop_loss_class in stop_loss_class_list:
        if stop_loss_class.need_data_process_after_domain:
            bar1m, barxm = stop_loss_class.data_process_after_domain(bar1m, barxm)

    positionRatio = result_para_dic['positionRatio']
    initialCash = result_para_dic['initialCash']

    oprnum = oprdf.shape[0]
    worknum = 0

    for i in range(oprnum):
        opr = oprdf.iloc[i]
        #startutc = barxm.loc[opr['openutc'], 'utc_endtime']  # 从开仓的10m线结束后开始
        #endutc = barxm.loc[opr['closeutc'], 'utc_endtime'] - 60  # 一直到平仓的10m线结束
        startutc = opr['openutc']
        endutc = opr['closeutc']
        data_1m = bar1m.loc[startutc:endutc]
        data1m= data_1m.drop(data_1m.index[-1])     # 因为loc取数是含头含尾的，所以要去掉最后一行
        for stop_loss_class in stop_loss_class_list:
            sl_name = stop_loss_class.get_sl_name()
            stop_loss_opr_result_dic = all_stop_loss_opr_result_dic[sl_name]
            opr_result_dic = stop_loss_class.get_opr_sl_result(opr, data1m)
            for para in stop_loss_class.get_para_dic_list():
                stop_loss_opr_result_dic[para['para_name']].append(opr_result_dic[para['para_name']])

    slip = symbol_info.getSlip()

    olddailydf = pd.read_csv(bt_folder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' dailyresult.csv', index_col='date')
    oldr = RS.getStatisticsResult(oprdf, False, indexcols, olddailydf)
    dailyK = DI.generatDailyClose(barxm)

    for stop_loss_class in stop_loss_class_list:
        sl_name = stop_loss_class.get_sl_name()
        stop_loss_opr_result_dic = all_stop_loss_opr_result_dic[sl_name]
        final_result_dic = all_final_result_dic[sl_name]
        folder_prefix = stop_loss_class.get_folder_prefix()
        file_suffix = stop_loss_class.get_file_suffix()
        for para_name, opr_result_dic_list in stop_loss_opr_result_dic.items():
            result_df = pd.DataFrame(opr_result_dic_list)
            oprdf_temp = pd.concat([oprdf, result_df], axis=1)
            oprdf_temp['new_ret'] = ((oprdf_temp['new_closeprice'] - oprdf_temp['openprice']) * oprdf_temp['tradetype']) - slip
            oprdf_temp['new_ret_r'] = oprdf_temp['new_ret'] / oprdf_temp['openprice']
            oprdf_temp['new_commission_fee'], oprdf_temp['new_per earn'], oprdf_temp['new_own cash'], oprdf_temp['new_hands'] = \
                RS.calcResult(oprdf_temp, symbol_info, initialCash, positionRatio, ret_col='new_ret')
            # 保存新的result文档
            tofolder = "%s%s\\" % (folder_prefix, para_name)
            oprdf_temp.to_csv(tofolder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' ' + file_suffix + para_name + '.csv', index=False)
            dR = RS.dailyReturn(symbol_info, oprdf_temp, dailyK, initialCash)  # 计算生成每日结果
            dR.calDailyResult()
            dR.dailyClose.to_csv(tofolder + strategy_name + ' ' + symbol + str(bar_type) + ' ' + setname + ' daily' + file_suffix + para_name + '.csv')
            newr = RS.getStatisticsResult(oprdf_temp, True, indexcols, dR.dailyClose)
            worknum = oprdf_temp.loc[oprdf_temp['new_closeindex'] != oprdf_temp['closeindex']].shape[0]
            final_result_dic[para_name] = [setname, para_name, worknum] + oldr + newr

    return all_final_result_dic


def single_sl_engine(strategy_name, symbol_info, bar_type, para_set_list, stop_loss_para_dic, result_para_dic, bar1m_dic, barxm_dic, time_start):
    time_enter_sl_engine = time.time()
    print ("time_enter_sl_engine:%.4f" % (time_enter_sl_engine - time_start))
    symbol = symbol_info.domain_symbol
    price_tick = symbol_info.getPriceTick()
    indexcols = Parameter.ResultIndexDic
    new_indexcols = []
    for col in indexcols:
        new_indexcols.append('new_' + col)
    paranum = len(para_set_list)
    all_result_dic = {}  # 这个保存的是每个止损参数的结果
    stop_loss_class_list = []
    for k, v in stop_loss_para_dic.items():
        v['price_tick'] = price_tick  # 传入的止损参数中加入price_tick，部分止损方式定价时要用到
        stop_loss_class = StopLoss.strategy_mapping_dic[k](v)
        stop_loss_class_list.append(stop_loss_class)
        folder_prefix = stop_loss_class.get_folder_prefix()
        para_list = stop_loss_class.get_para_dic_list()
        result_dic = {}
        for para in para_list:
            para_name = para['para_name']
            folder_name = '%s%s' % (folder_prefix, para_name)
            try:
                os.mkdir(folder_name)  # 创建文件夹
            except:
                pass
            resultdf = pd.DataFrame(columns=['setname', 'para_name', 'worknum'] + indexcols + new_indexcols)
            result_dic[para_name] = resultdf
        all_result_dic[k] = result_dic
    timestart = time.time()
    setnum = 0
    numlist = range(0, paranum, 100)
    numlist.append(paranum)
    time_start_sl_cals = time.time()
    print ("time start sl cals:%.4f" % (time_start_sl_cals - time_enter_sl_engine))
    for n in range(1, len(numlist)):
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for a in range(numlist[n - 1], numlist[n]):
            setname = para_set_list[a]
            #l.append(single_sl(strategy_name, symbol_info, bar_type, setname, bar1m_dic, barxm_dic,
            #                   stop_loss_class_list, result_para_dic, indexcols, timestart))
            l.append(pool.apply_async(single_sl, (strategy_name, symbol_info, bar_type, setname, bar1m_dic, barxm_dic,
                                                  stop_loss_class_list, result_para_dic, indexcols, timestart)))
        pool.close()
        pool.join()

        for res in l:
            get_result_dic = res.get()
            for sl_name, result_dic in get_result_dic.items():
                to_result_dic = all_result_dic[sl_name]
                for para_name, para_result in result_dic.items():
                    to_result_dic[para_name].loc[setnum] = para_result
            setnum += 1
    time_fininsh_calc = time.time()
    print ("time finish calc:%.4f" % (time_fininsh_calc - time_start_sl_cals))
    for stop_loss_class in stop_loss_class_list:
        sl_name = stop_loss_class.get_sl_name()
        result_dic = all_result_dic[sl_name]
        folder_prefix = stop_loss_class.get_folder_prefix()
        all_result_list = []
        for para_name, para_result_df in result_dic.items():
            folderName = '%s%s' % (folder_prefix, para_name)
            para_result_df.to_csv(folderName + '\\' + strategy_name + ' ' + symbol + str(bar_type) + ' finalresult_%s%s.csv' % (sl_name, para_name), index=False)
            all_result_list.append(para_result_df)
        all_final_result = pd.concat(all_result_list)
        all_final_result.to_csv(strategy_name + ' ' + symbol + str(bar_type) + ' finalresult_%s.csv' % sl_name, index=False)
    time_finish_saving_file = time.time()
    print ("time_finish_saving_file:%.4f" % (time_finish_saving_file - time_fininsh_calc))
    timeend = time.time()
    timecost = timeend - timestart
    print (u"全部止损计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (paranum, timecost, timecost / paranum))


def multi_sl_engine(strategyName, symbolInfo, K_MIN, parasetlist, barxmdic, sltlist, result_para_dic):
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
    indexcols = Parameter.ResultIndexDic
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    allresultdf_cols = ['setname', 'slt', 'slWorkNum'] + indexcols + new_indexcols
    allresultdf = pd.DataFrame(columns=allresultdf_cols)

    allnum = 0
    paranum = len(parasetlist)

    # dailyK = DC.generatDailyClose(barxm)

    # 先生成参数列表
    allSltSetList = []  # 这是一个二维的参数列表，每一个元素是一个止损目标的参数dic列表
    for slt in sltlist:
        sltset = []
        for t in slt['paralist']:
            sltset.append({'name': slt['name'],
                           'sltValue': t,  # t是一个参数字典
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
            # newfolder += (sltp['name'] + '_%.3f' % (sltp['sltValue']))
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
            setname = parasetlist[sn]
            #l.append(StopLoss.multi_stop_loss(strategyName, symbolInfo, K_MIN, setname, sltset, barxmdic, result_para_dic, newfolder, indexcols))
            l.append(pool.apply_async(StopLoss.multi_stop_loss,
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
    time_start = time.time()
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
            if v[k]:
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

        symbol_info = DI.SymbolInfo(domain_symbol, startdate, enddate)

        symbol_bar_folder_name = Parameter.strategy_folder + "%s %s %s %d" % (
            strategy_name, exchange_id, sec_id, bar_type)
        os.chdir(symbol_bar_folder_name)
        paraset_name = "%s %s %s %d Parameter.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        # 读取已有参数表
        parasetlist = pd.read_csv(paraset_name)['Setname'].tolist()

        cols = ['open', 'high', 'low', 'close', 'strtime', 'utc_time', 'utc_endtime']
        bar1m_dic = DI.getBarBySymbolList(domain_symbol, symbol_info.getSymbolList(), 60, startdate, enddate, cols)
        barxm_dic = DI.getBarBySymbolList(domain_symbol, symbol_info.getSymbolList(), bar_type, startdate, enddate, cols)

        if 'multi_sl' in stop_loss_dic.keys():
            # 混合止损模式
            sltlist = []
            price_tick = symbol_info.getPriceTick()
            for sl_name, stop_loss in stop_loss_dic.items():
                if sl_name != 'multi_sl':
                    stop_loss['price_tick'] = price_tick  # 传入的止损参数中加入price_tick，部分止损方式定价时要用到
                    stop_loss_class = StopLoss.strategy_mapping_dic[sl_name](stop_loss)
                    sltlist.append({'name': sl_name,
                                    'paralist': stop_loss_class.get_para_dic_list(),
                                    'folderPrefix': stop_loss_class.get_folder_prefix(),
                                    'fileSuffix':  stop_loss_class.get_file_suffix()
                                    })

            multi_sl_engine(strategy_name, symbol_info, bar_type, parasetlist, barxm_dic, sltlist, result_para_dic)
        else:
            # 单止损模式
            single_sl_engine(strategy_name, symbol_info, bar_type, parasetlist, stop_loss_dic, result_para_dic, bar1m_dic, barxm_dic, time_start)
