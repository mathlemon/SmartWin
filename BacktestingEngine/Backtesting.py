# -*- coding: utf-8 -*-
"""
SmartWin回策框架
回测引擎
作者:Smart
新建时间：2018-09-02
"""
import Strategy
import pandas as pd
import os
import DataInterface.DataInterface as DI
import multiprocessing
import Parameter
import DataInterface.ResultStatistics as RS
import time


def getResult(strategyName, strategy_class, symbolinfo, K_MIN, rawdataDic, para, result_para_dic, indexcols, timestart):
    time1 = time.time()
    setname = para['Setname']
    print ("%s %s %d %s Enter %.3f" % (strategyName, symbolinfo.domain_symbol, K_MIN, setname, time1 - timestart))

    initialCash = result_para_dic['initialCash']
    positionRatio = result_para_dic['positionRatio']
    remove_polar_switch = result_para_dic['remove_polar_switch']
    remove_polar_rate = result_para_dic['remove_polar_rate']

    symbollist = symbolinfo.getSymbolList()
    symbolDomainDic = symbolinfo.getSymbolDomainDic()
    result = pd.DataFrame()
    last_domain_utc = None
    for symbol in symbollist:
        if last_domain_utc:
            # 如果上一个合约的最后一次平仓时间超过其主力合约结束时间，则要修改本次合约的开始时间为上一次平仓后
            symbol_domain_start = last_domain_utc
            symbolDomainDic[symbol][0] = last_domain_utc
        else:
            symbol_domain_start = symbolDomainDic[symbol][0]
        symbol_domain_end = symbolDomainDic[symbol][1]
        rawdata = rawdataDic[symbol]
        r = strategy_class.run_trade_logic(symbolinfo, rawdata, para)
        r['symbol'] = symbol  # 增加主力全约列
        r = r.loc[(r['openutc'] >= symbol_domain_start) & (r['openutc'] <= symbol_domain_end)]
        last_domain_utc = None
        if r.shape[0] > 0:
            last_close_utc = r.iloc[-1]['closeutc']
            if last_close_utc > symbol_domain_end:
                # 如果本合约最后一次平仓时间超过其主力合约结束时间，则要修改本合约的主力结束时间为平仓后
                symbolDomainDic[symbol][1] = last_close_utc
                last_domain_utc = last_close_utc
            result = pd.concat([result, r])
    result.reset_index(drop=True, inplace=True)

    # 去极值操作
    if remove_polar_switch:
        result = RS.opr_result_remove_polar(result, remove_polar_rate)

    # 全部操作结束后，要根据修改完的主力时间重新接出一份主连来计算dailyK
    domain_bar = pd.DataFrame()
    for symbol in symbollist[:-1]:
        symbol_domain_start = symbolDomainDic[symbol][0]
        symbol_domain_end = symbolDomainDic[symbol][1]
        rbar = rawdataDic[symbol]
        bars = rbar.loc[(rbar['utc_time'] >= symbol_domain_start) & (rbar['utc_endtime'] < symbol_domain_end)]
        domain_bar = pd.concat([domain_bar, bars])
    # 最后一个合约只截前不截后
    symbol = symbollist[-1]
    symbol_domain_start = symbolDomainDic[symbol][0]
    rbar = rawdataDic[symbol]
    bars = rbar.loc[rbar['utc_time'] >= symbol_domain_start]
    domain_bar = pd.concat([domain_bar, bars])

    dailyK = DI.generatDailyClose(domain_bar)
    result['commission_fee'], result['per earn'], result['own cash'], result['hands'] = RS.calcResult(result,
                                                                                                      symbolinfo,
                                                                                                      initialCash,
                                                                                                      positionRatio)
    bt_folder = "%s %d backtesting\\" % (symbolinfo.domain_symbol, K_MIN)

    result.to_csv(bt_folder + strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' result.csv', index=False)
    dR = RS.dailyReturn(symbolinfo, result, dailyK, initialCash)  # 计算生成每日结果
    dR.calDailyResult()
    dR.dailyClose.to_csv((bt_folder + strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' dailyresult.csv'))
    results = RS.getStatisticsResult(result, False, indexcols, dR.dailyClose)
    del result
    print results
    return [setname] + results  # 在这里附上setname


def getParallelResult(strategyParameter, strategy_class, parasetlist, paranum, indexcols):
    strategyName = strategyParameter['strategy_name']
    exchange_id = strategyParameter['exchange_id']
    sec_id = strategyParameter['sec_id']
    K_MIN = strategyParameter['K_MIN']
    startdate = strategyParameter['startdate']
    enddate = strategyParameter['enddate']
    domain_symbol = '.'.join([exchange_id, sec_id])
    result_para_dic = strategyParameter['result_para_dic']
    # ======================数据准备==============================================
    # 取合约信息
    symbolInfo = DI.SymbolInfo(domain_symbol, startdate, enddate)
    # 取跨合约数据
    # contractswaplist = DC.getContractSwaplist(domain_symbol)
    # swaplist = np.array(contractswaplist.swaputc)

    # 取K线数据
    # rawdata = DC.getBarData(symbol, K_MIN, startdate + ' 00:00:00', enddate + ' 23:59:59').reset_index(drop=True)
    rawdataDic = DI.getBarBySymbolList(domain_symbol, symbolInfo.getSymbolList(), K_MIN, startdate, enddate)

    timestart = time.time()
    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    l = []
    resultlist = pd.DataFrame(columns=['Setname'] + indexcols)
    strategy_para_name_list = strategy_class.get_para_name_list()
    for i in range(0, paranum):
        paraset = {}
        setname = parasetlist.ix[i, 'Setname']
        paraset['Setname'] = setname
        for strategy_para_name in strategy_para_name_list:
            paraset[strategy_para_name] = parasetlist.ix[i, strategy_para_name]
        #l.append(getResult(strategyName, strategy_class, symbolInfo, K_MIN, rawdataDic, paraset, result_para_dic, indexcols,timestart))
        l.append(pool.apply_async(getResult, (strategyName, strategy_class, symbolInfo, K_MIN, rawdataDic, paraset, result_para_dic, indexcols, timestart)))
    pool.close()
    pool.join()
    timeend = time.time()
    print ("total time %.2f" % (timeend - timestart))
    # 显示结果
    i = 0
    for res in l:
        resultlist.loc[i] = res.get()
        i += 1
    finalresults = ("%s %s %d finalresult.csv" % (strategyName, domain_symbol, K_MIN))
    resultlist.to_csv(finalresults)
    return resultlist


if __name__ == '__main__':
    # ====================参数和文件夹设置======================================
    indexcols = Parameter.ResultIndexDic

    # 策略参数设置
    strategy_name = Parameter.strategy_name
    strategy = Strategy.strategy_mapping_dic[strategy_name]()
    strategy_para_name_list = strategy.get_para_name_list()
    strategyParameterSet = []
    if not Parameter.multi_symbol_bt_swtich:
        # 单品种单周期模式
        default_para_dic = Parameter.strategy_para_dic[strategy_name]
        paradic = {
            'strategy_name': strategy_name,
            'exchange_id': Parameter.exchange_id,
            'sec_id': Parameter.sec_id,
            'K_MIN': Parameter.K_MIN,
            'startdate': Parameter.startdate,
            'enddate': Parameter.enddate,
            'result_para_dic': Parameter.result_para_dic,
            'new_para': default_para_dic['new_para']
        }
        if default_para_dic['new_para']:
            # 参数新增模式下，加载默认参数
            for para_name in strategy_para_name_list:
                paradic[para_name] = default_para_dic[para_name]
        strategyParameterSet.append(paradic)
    else:
        # 多品种多周期模式
        symbol_set = pd.read_excel(Parameter.strategy_folder + Parameter.symbol_KMIN_set_filename)
        for n, rows in symbol_set.iterrows():
            new_para = rows['new_para']
            exchangeid = rows['exchange_id']
            secid = rows['sec_id']
            para_dic = {
                'strategy_name': strategy_name,
                'exchange_id': exchangeid,
                'sec_id': secid,
                'K_MIN': int(rows['K_MIN']),
                'startdate': rows['startdate'],
                'enddate': rows['enddate'],
                'result_para_dic': Parameter.result_para_dic,
                'new_para': new_para
            }
            if new_para:
                # 参数新增模式下，加载参数
                for para_name in strategy_para_name_list:
                    para_dic[para_name] = Parameter.para_str_to_int(rows[para_name])
            strategyParameterSet.append(para_dic)

    allsymbolresult_cols = ['Setname'] + indexcols + ['strategy_name', 'exchange_id', 'sec_id', 'K_MIN']
    allsymbolresult = pd.DataFrame(columns=allsymbolresult_cols)
    for strategyParameter in strategyParameterSet:
        exchange_id = strategyParameter['exchange_id']
        sec_id = strategyParameter['sec_id']
        bar_type = strategyParameter['K_MIN']
        symbol_bar_folder_name = Parameter.strategy_folder + "%s %s %s %d" % (strategy_name, exchange_id, sec_id, bar_type)
        try:
            os.makedirs(symbol_bar_folder_name)
        except:
            pass
        finally:
            os.chdir(symbol_bar_folder_name)    # 将操作目录设为当前品种+周期的目录
        try:
            os.mkdir("%s.%s %d backtesting" % (exchange_id, sec_id, bar_type))
        except:
            pass

        paraset_name = "%s %s %s %d Parameter.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        if not strategyParameter['new_para']:
            # 读取已有参数表
            parasetlist = pd.read_csv(paraset_name)
        else:
            # 按参数新生成参数表
            para_list_dic = {}
            for para_name in strategy_para_name_list:
                para_list_dic[para_name] = strategyParameter[para_name]
            parasetlist = strategy.get_para_list(para_list_dic)
            parasetlist.to_csv(paraset_name)
        paranum = parasetlist.shape[0]

        r = getParallelResult(strategyParameter, strategy, parasetlist, paranum, indexcols)
        r['strategy_name'] = strategyParameter['strategy_name']
        r['exchange_id'] = strategyParameter['exchange_id']
        r['sec_id'] = strategyParameter['sec_id']
        r['K_MIN'] = strategyParameter['K_MIN']
        allsymbolresult = pd.concat([allsymbolresult, r])
    allsymbolresult.reset_index(drop=False, inplace=True)
    os.chdir(Parameter.strategy_folder)
    allsymbolresult.to_csv(strategy_name + "_multi_symbol_final_results.csv")
