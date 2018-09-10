# -*- coding: utf-8 -*-
import pandas as pd
import DataInterface.DataInterface as DC
import Parameter
import os
import numpy as np
import DataInterface.ResultStatistics as RS
from datetime import datetime
import time
import matplotlib.pyplot as plt


def calc_single_final_result(domain_symbol, bar_type, folder_name):
    """
    计算单个品种回测结果的汇总finalresult文件
    :param domain_symbol: 主力合约编号
    :param bar_type: 周期
    :return:
    """
    strategy_folder = Parameter.strategy_folder
    exchange_id, sec_id = domain_symbol.split('.')
    symbol_folder = "%s %s %d" % (exchange_id, sec_id, bar_type)
    os.chdir(strategy_folder + symbol_folder)
    strategy_name = Parameter.strategy_name
    paraset_name = "%s %s %s %d Parameter.csv" % (strategy_name, exchange_id, sec_id, bar_type)
    parasetlist = pd.read_csv(paraset_name)['Setname'].tolist()
    file_name_1 = os.listdir(folder_name)[2]
    file_suffix = file_name_1[file_name_1.find('result'):]  # 读取文件名从result开始后的内容作为文件后缀
    if 'backtesting' in folder_name:
        new_flag = False
    else:
        new_flag = True
    indexcols = Parameter.ResultIndexDic
    new_indexcols = []
    para_name = 'common'
    if new_flag:
        para_name = folder_name
        for s in indexcols:
            new_indexcols.append('new_' + s)
    resultlist = pd.DataFrame(columns=['Setname', 'para_name', 'worknum'] + indexcols + new_indexcols)
    bt_folder = "%s.%s %d backtesting" % (exchange_id, sec_id, bar_type)
    i = 0
    for setname in parasetlist:
        print setname
        bt_result = pd.read_csv((bt_folder + strategy_name + ' ' + domain_symbol + str(bar_type) + ' ' + setname + ' result.csv'))
        bt_dailyClose= pd.read_csv((bt_folder + strategy_name + ' ' + domain_symbol + str(bar_type) + ' ' + setname + ' dailyresult.csv'))
        bt_results = RS.getStatisticsResult(bt_result, False, indexcols, bt_dailyClose)
        work_num = 0
        newr = []
        if new_flag:
            opr_file_name = "\\%s %s%d %s %s" % (strategy_name, domain_symbol, bar_type, setname, file_suffix)
            sl_reslt = pd.read_csv(folder_name + opr_file_name)
            opr_dialy_k_file_name = "\\%s %s%d %s daily%s" % (strategy_name, domain_symbol, bar_type, setname, file_suffix)
            sl_dailyClose = pd.read_csv(folder_name + opr_dialy_k_file_name)
            newr = RS.getStatisticsResult(sl_reslt, True, indexcols, sl_dailyClose)
            work_num = sl_reslt.loc[sl_reslt['new_closeutc'] != sl_reslt['closeutc']].shape[0]
        resultlist.loc[i] = [setname, para_name, work_num] + bt_results + newr #在这里附上setname
        i += 1
    finalresults = ("%s %s %d final%s" % (strategy_name, domain_symbol, bar_type, file_suffix))
    resultlist.to_csv(finalresults)


def re_concat_close_all_final_result(domain_symbol, bar_type, sl_type):
    """
    重新汇总某一止损类型所有参数的final_result， 止损的参数自动从Parameter中读
    :param domain_symbol: 主力合约编号
    :param bar_type: 周期
    :param sl_type: 止损类型 'DSL', 'OWNL', 'FRSL', 'ATR', 'GOWNL'
    :return:
    """
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    symbol_folder = domain_symbol.replace('.', ' ') + ' ' + str(bar_type)
    os.chdir(resultpath + symbol_folder)
    close_para_name_list = []
    if sl_type == 'DSL':
        folder_prefix = 'DynamicStopLoss'
        final_result_file_suffix = 'dsl'
        dsl_target_list = Parameter.dsl_target_list_close
        for dsl_target in dsl_target_list:
            close_para_name_list.append(str(dsl_target))
    elif sl_type == 'OWNL':
        folder_prefix = 'OnceWinNoLoss'
        final_result_file_suffix = 'ownl'
        ownl_protect_list = Parameter.ownl_protect_list_close
        ownl_floor_list = Parameter.ownl_floor_list_close
        for ownl_protect in ownl_protect_list:
            for ownl_floor in ownl_floor_list:
                close_para_name_list.append("%.3f_%d" % (ownl_protect, ownl_floor))
    elif sl_type == 'FRSL':
        folder_prefix = 'FixRateStopLoss'
        final_result_file_suffix = 'frsl'
        frsl_target_list = Parameter.frsl_target_list_close
        for frsl_target in frsl_target_list:
            close_para_name_list.append(str(frsl_target))
    elif sl_type == 'ATR':
        folder_prefix = 'ATRSL'
        final_result_file_suffix = 'atrsl'
        atr_pendant_n_list = Parameter.atr_pendant_n_list_close
        atr_pendan_rate_list = Parameter.atr_pendant_rate_list_close
        atr_yoyo_n_list = Parameter.atr_yoyo_n_list_close
        atr_yoyo_rate_list = Parameter.atr_yoyo_rate_list_close
        for atr_pendant_n in atr_pendant_n_list:
            for atr_pendant_rate in atr_pendan_rate_list:
                for atr_yoyo_n in atr_yoyo_n_list:
                    for atr_yoyo_rate in atr_yoyo_rate_list:
                        close_para_name_list.append('%d_%.1f_%d_%.1f' % (
                                atr_pendant_n, atr_pendant_rate, atr_yoyo_n, atr_yoyo_rate))
    elif sl_type == 'GOWNL':
        folder_prefix = 'GOWNL'
        final_result_file_suffix = 'gownl'
        gownl_protect_list = Parameter.gownl_protect_list_close
        gownl_floor_list = Parameter.gownl_floor_list_close
        gownl_step_list = Parameter.gownl_step_list_close
        for gownl_protect in gownl_protect_list:
            for gownl_floor in gownl_floor_list:
                for gownl_step in gownl_step_list:
                    close_para_name_list.append('%.3f_%.1f_%.1f' % (gownl_protect, gownl_floor, gownl_step))
    else:
        print "close name error"
        return
    final_result_name_0 = "%s %s%d finalresult_%s%s.csv" % (
    Parameter.strategyName, domain_symbol, bar_type, final_result_file_suffix, close_para_name_list[0])
    final_result_file = pd.read_csv("%s%s\\%s" % (folder_prefix, close_para_name_list[0], final_result_name_0))
    for para_name in close_para_name_list[1:]:
        final_result_name = "%s %s%d finalresult_%s%s.csv" % (
        Parameter.strategyName, domain_symbol, bar_type, final_result_file_suffix, para_name)
        final_result_file = pd.concat([final_result_file, pd.read_csv("%s%s\\%s" % (folder_prefix, para_name, final_result_name))])

    final_result_file.to_csv("%s %s%d finalresult_%s_reconcat.csv" % (
    Parameter.strategyName, domain_symbol, bar_type, final_result_file_suffix))


def re_concat_multi_symbol_final_result():
    """
    重新汇总多品种回测的final_result结果，自动从symbol_KMIN_set.xlsx文件读取品种列表
    :return:
    """
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    multi_symbol_df = pd.read_excel('%s_symbol_KMIN_set.xlsx' % Parameter.strategyName)
    all_final_result_list = []
    for n, row in multi_symbol_df.iterrows():
        strategy_name = row['strategyName']
        exchange_id = row['exchange_id']
        sec_id = row['sec_id']
        bar_type = row['K_MIN']
        symbol_folder_name = "%s %s %s %d\\" % (strategy_name, exchange_id, sec_id, bar_type)
        bt_folder = "%s.%s %d backtesting\\" % (exchange_id, sec_id, bar_type)
        result_file_name = "%s %s.%s %d finalresults.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        print result_file_name
        final_result_df = pd.read_csv(symbol_folder_name + result_file_name)
        final_result_df['strategy_name'] = strategy_name
        final_result_df['exchange_id'] = exchange_id
        final_result_df['sec_id'] = sec_id
        final_result_df['ba_type'] = bar_type
        all_final_result_list.append(final_result_df)

    multi_symbol_result_df = pd.concat(all_final_result_list)
    multi_symbol_result_df.to_csv('%s_symbol_KMIN_set_result.csv' % Parameter.strategyName)



def calResultByPeriod():
    '''
    按时间分段统计结果:
    1.设定开始和结束时间
    2.选择时间周期
    3.设定文件夹、买卖操作文件名、日结果文件名和要生成的新文件名
    :return:
    '''
    #设定开始和结束时间
    startdate = '2011-04-01'
    enddate = '2018-07-01'

    #2.选择时间周期
    #freq='YS' #按年统计
    #freq='2QS' #按半年统计
    #freq='QS' #按季度统计
    freq='MS' #按月统计，如需多个月，可以加上数据，比如2个月：2MS

    #3.设文件和文件夹状态
    filedir='D:\\002 MakeLive\myquant\HopeWin\Results\HopeMacdMaWin DCE J 3600\dsl_-0.022ownl_0.012\ForwardOprAnalyze\\' #文件所在文件夹
    oprfilename = 'HopeMacdMaWin DCE.J3600_Rank3_win9_oprResult.csv' #买卖操作文件名
    dailyResultFileName = 'HopeMacdMaWin DCE.J3600_Rank3_win9_oprdailyResult.csv' #日结果文件名
    newFileName = 'HopeMacdMaWin DCE.J3600_Rank3_win9_result_by_Period_M.csv' #要生成的新文件名
    os.chdir(filedir)
    oprdf = pd.read_csv(oprfilename)
    dailyResultdf = pd.read_csv(dailyResultFileName)

    oprdfcols = oprdf.columns.tolist()
    if 'new_closeprice' in oprdfcols:
        newFlag = True
    else:
        newFlag = False

    monthlist = [datetime.strftime(x, '%Y-%m-%d %H:%M:%S') for x in list(pd.date_range(start=startdate, end=enddate, freq=freq, normalize=True, closed='right'))]

    if not startdate in monthlist[0]:
        monthlist.insert(0,startdate+" 00:00:00")
    if not enddate in monthlist[-1]:
        monthlist.append(enddate+" 23:59:59")
    else:
        monthlist[-1]=enddate+" 23:59:59"
    rlist=[]
    for i in range(1,len(monthlist)):
        starttime=monthlist[i-1]
        endtime = monthlist[i]
        startutc = float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
        endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))

        resultdata = oprdf.loc[(oprdf['openutc'] >= startutc) & (oprdf['openutc'] < endutc)]
        dailydata = dailyResultdf.loc[(dailyResultdf['utc_time'] >= startutc) & (dailyResultdf['utc_time'] < endutc)]
        resultdata.reset_index(drop=True,inplace=True)
        if resultdata.shape[0]>0:
            rlist.append([starttime,endtime]+RS.getStatisticsResult(resultdata, newFlag, Parameter.ResultIndexDic, dailydata))
        else:
            rlist.append([0]*len(Parameter.ResultIndexDic))
    rdf = pd.DataFrame(rlist,columns=['StartTime','EndTime']+Parameter.ResultIndexDic)
    rdf.to_csv(newFileName)


def set_generator():
    setlist = []
    i = 0
    for n1 in range(15, 36, 5):
        for m1 in range(6, 17, 4):
            #   for m2 in range(3, 15, 3):
            for m2 in [3, 6, 9]:
                # for n in range(3, 16, 3):
                for n in [6, 10, 14, 18]:
                    # for ma_n in range(20, 51, 10):
                    for ma_n in [20, 30, 40, 50]:
                        setname = "Set%d N1_%d M1_%d M2_%d N_%d MaN_%d" % (i, n1, m1, m2, n, ma_n)
                        l = [setname, n1, m1, m2, n, ma_n]
                        setlist.append(l)
                        i += 1

    setpd = pd.DataFrame(setlist, columns=['Setname', 'N1', 'M1', 'M2', 'N', 'MaN'])
    # setpd['RSI1_UP'] = 70
    # setpd['RSI1_DOWN'] = 30

    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    setpd.to_csv(resultpath + Parameter.parasetname)


def stat_multi_symbol_result():
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    multi_symbol_df = pd.read_excel('HullRsiWin_symbol_KMIN_set.xlsx')
    for n, row in multi_symbol_df.iterrows():
        strategy_name = row['strategyName']
        exchange_id = row['exchange_id']
        sec_id = row['sec_id']
        bar_type = row['K_MIN']
        folder_name = "%s %s %s %d\\" % (strategy_name, exchange_id, sec_id, bar_type)
        result_file_name = "%s %s.%s %d finalresults.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        print result_file_name
        result_df = pd.read_csv(folder_name + result_file_name)
        multi_symbol_df.ix[n, 'OprTimes'] = result_df['OprTimes'].mean()
        multi_symbol_df.ix[n, 'Annual_max'] = result_df['Annual'].max()
        multi_symbol_df.ix[n, 'Annual_avg'] = result_df['Annual'].mean()
        multi_symbol_df.ix[n, 'EndCash_avg'] = result_df['EndCash'].mean()
        multi_symbol_df.ix[n, 'EndCash_max'] = result_df['EndCash'].max()
        multi_symbol_df.ix[n, 'own_cash_max_max'] = result_df['max_own_cash'].max()
        multi_symbol_df.ix[n, 'own_cash_max_avg'] = result_df['max_own_cash'].mean()
        multi_symbol_df.ix[n, 'Sharpe_max'] = result_df['Sharpe'].max()
        multi_symbol_df.ix[n, 'SR_avg'] = result_df['SR'].mean()
        multi_symbol_df.ix[n, 'DR_avg'] = result_df['DrawBack'].mean()
        multi_symbol_df.ix[n, 'SingleEarn_avg'] = result_df['MaxSingleEarnRate'].mean()
        multi_symbol_df.ix[n, 'SingleLoss_avg'] = result_df['MaxSingleLossRate'].mean()
        multi_symbol_df.ix[n, 'ProfitLossRate_avg'] = result_df['ProfitLossRate'].mean()
    multi_symbol_df.to_csv('HullRsiWin_symbol_KMIN_set2_result.csv')


def add_max_period_cash_to_finalresult():
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    para_set_list = pd.read_csv('ParameterSet_HullRsi.csv')['Setname'].tolist()
    multi_symbol_df = pd.read_excel('HullRsiWin_symbol_KMIN_set.xlsx')
    for n, row in multi_symbol_df.iterrows():
        strategy_name = row['strategyName']
        exchange_id = row['exchange_id']
        sec_id = row['sec_id']
        bar_type = row['K_MIN']
        folder_name = "%s %s %s %d\\" % (strategy_name, exchange_id, sec_id, bar_type)
        result_file_name = "%s %s.%s %d finalresults.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        # print result_file_name
        result_df = pd.read_csv(folder_name + result_file_name, index_col='Setname')
        for setname in para_set_list:
            set_file_name = "%s %s.%s%d %s result.csv" % (strategy_name, exchange_id, sec_id, bar_type, setname)
            print set_file_name
            set_result = pd.read_csv(folder_name + set_file_name)
            max_own_cash = set_result['own cash'].max()
            result_df.ix[setname, 'max_own_cash'] = max_own_cash
        result_df.to_csv(folder_name + result_file_name)
    pass


def plot_parameter_result_pic():
    """绘制finalresult结果中参数对应的end cash和max own cash的分布柱状图"""
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    symbol_sellected = pd.read_excel("multi_symbol_1st_xu.xlsx")
    for n , rows in symbol_sellected.iterrows():
        fig = plt.figure(figsize=(6, 12))
        exchange = rows['exchange']
        sec = rows['sec']
        bar_type = rows['bar_type']
        folder_name = "%s %s %s %d\\" % (Parameter.strategyName, exchange, sec, bar_type)
        final_result_file = pd.read_csv(folder_name + "%s %s.%s %d finalresults.csv" % (Parameter.strategyName, exchange, sec, bar_type))
        para_file = pd.read_csv(folder_name + "%s %s %d ParameterSet_HullRsi.csv" % (exchange, sec, bar_type))
        para_name_list = ['N', 'N1', 'M1', 'M2', 'MaN']
        for i in range(len(para_name_list)):
            para_name = para_name_list[i]
            final_result_file[para_name_list] = para_file[para_name_list]
            grouped = final_result_file.groupby(para_name)
            end_cash_grouped = grouped['EndCash'].mean()
            p = plt.subplot(len(para_name_list), 1, i+1)
            p.set_title(para_name)
            p.bar(end_cash_grouped.index.tolist(), end_cash_grouped.values)
            print end_cash_grouped
        fig.savefig('%s %s %s %d_para_distribute.png' % (Parameter.strategyName, exchange, sec, bar_type), dip=500)
    """
    for i in range(1, len(test_data) + 2):
        p = plt.subplot(2, 5, i)
        p.set_title(str(i))
        p.bar([1, 2, 3, 4], test_data_2)

    for i in range(1, len(test_data) + 2):
        p = plt.subplot(2, 5, i + 5)
        p.set_title(str(i))
        p.bar([1, 2, 3, 4], test_data_2)
    """

if __name__ == "__main__":
    """
        计算单个品种回测结果的汇总finalresult文件，包括普通回测和止损结果
        :param domain_symbol: 主力合约编号
        :param bar_type: 周期
        :param folder_name: 结果文件夹
        """
    # calc_single_final_result(domain_symbol='SHFE.RB', bar_type=3600， folder_name='dsl-0.018')

    """
    重新汇总某一止损类型所有参数的final_result， 止损的参数自动从Parameter中读
    :param domain_symbol: 主力合约编号
    :param bar_type: 周期
    :param sl_type: 止损类型 'DSL', 'OWNL', 'FRSL', 'ATR', 'GOWNL'
    """
    # re_concat_close_all_final_result(domain_symbol='SHFE.RB', bar_type=3600, sl_type='DSL')

    """
    重新汇总多品种回测的final_result结果，自动从symbol_KMIN_set.xlsx文件读取品种列表
    """
    # re_concat_multi_symbol_final_result()

    """
    分时间段统计结果，需要到函数中修改相关参数
    """
    # calResultByPeriod()

    """绘制finalresult结果中参数对应的end cash分布柱状图"""
    #plot_parameter_result_pic()
    src_str = "Set0 N0 N1_1 N2_3 result_dsl_-0.018.csv"
    start_i = src_str.find('result')
    print start_i
    print src_str[start_i:]
    pass
