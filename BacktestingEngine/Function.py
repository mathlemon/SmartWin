# -*- coding: utf-8 -*-
import pandas as pd
import DataInterface.DataInterface as DC
import Parameter
import os
import DataInterface.ResultStatistics as RS
from datetime import datetime
import time
import matplotlib.pyplot as plt
import StopLoss
import Strategy


def calc_single_final_result(domain_symbol, bar_type, folder_name):
    """
    计算单个品种回测结果的汇总finalresult文件
    :param folder_name:
    :param domain_symbol: 主力合约编号
    :param bar_type: 周期
    :return:
    """
    strategy_folder = "%s%s\\" % (Parameter.root_path, Parameter.strategy_name)
    exchange_id, sec_id = domain_symbol.split('.')
    symbol_folder = "%s %s %s %d\\" % (Parameter.strategy_name, exchange_id, sec_id, bar_type)
    os.chdir(strategy_folder + symbol_folder)
    strategy_name = Parameter.strategy_name
    paraset_name = "%s %s %s %d Parameter.csv" % (strategy_name, exchange_id, sec_id, bar_type)
    parasetlist = pd.read_csv(paraset_name)['Setname'].tolist()
    file_name_1 = os.listdir(folder_name)[-2]
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
    else:
        resultlist = pd.DataFrame(columns=['Setname'] + indexcols)
    bt_folder = "%s.%s %d backtesting\\" % (exchange_id, sec_id, bar_type)
    i = 0
    for setname in parasetlist:
        print setname
        bt_result = pd.read_csv((bt_folder + strategy_name + ' ' + domain_symbol + str(bar_type) + ' ' + setname + ' result.csv'))
        bt_daily_close = pd.read_csv((bt_folder + strategy_name + ' ' + domain_symbol + str(bar_type) + ' ' + setname + ' dailyresult.csv'))
        bt_results = RS.getStatisticsResult(bt_result, False, indexcols, bt_daily_close)
        if new_flag:
            opr_file_name = "\\%s %s%d %s %s" % (strategy_name, domain_symbol, bar_type, setname, file_suffix)
            sl_reslt = pd.read_csv(folder_name + opr_file_name)
            opr_dialy_k_file_name = "\\%s %s%d %s daily%s" % (strategy_name, domain_symbol, bar_type, setname, file_suffix)
            sl_dailyClose = pd.read_csv(folder_name + opr_dialy_k_file_name)
            newr = RS.getStatisticsResult(sl_reslt, True, indexcols, sl_dailyClose)
            work_num = sl_reslt.loc[sl_reslt['new_closeutc'] != sl_reslt['closeutc']].shape[0]
            resultlist.loc[i] = [setname, para_name, work_num] + bt_results + newr  # 在这里附上setname
        else:
            resultlist.loc[i] = [setname] + bt_results
        i += 1
    finalresults = ("%s %s %d final%s" % (strategy_name, domain_symbol, bar_type, file_suffix))
    resultlist.to_csv(finalresults)


def re_concat_close_all_final_result(domain_symbol, bar_type, sl_type):
    """
    重新汇总某一止损类型所有参数的final_result， 止损的参数自动从Parameter中读
    :param domain_symbol: 主力合约编号
    :param bar_type: 周期
    :param sl_type: 止损类型 'dsl', 'ownl', 'frsl', 'gownl', 'pendant', 'yoyo'
    :return:
    """
    strategy_folder = "%s%s\\" % (Parameter.root_path, Parameter.strategy_name)
    exchange_id, sec_id = domain_symbol.split('.')
    symbol_folder = "%s %s %s %d" % (Parameter.strategy_name, exchange_id, sec_id, bar_type)
    os.chdir(strategy_folder + symbol_folder)
    sl_para_dic = Parameter.stop_loss_para_dic[sl_type]
    sl_para_dic['price_tick'] = 0
    stop_loss_class = StopLoss.strategy_mapping_dic[sl_type](sl_para_dic)
    stop_loss_para_list = stop_loss_class.get_para_dic_list()
    folder_prefix = stop_loss_class.get_folder_prefix()
    final_result_list = []
    for stop_loss_para in stop_loss_para_list:
        para_name = stop_loss_para['para_name']
        folder_name = "%s%s\\" % (folder_prefix, para_name)
        print folder_name
        final_result_name = "%s %s%d finalresult_%s%s.csv" % (
            Parameter.strategy_name, domain_symbol, bar_type, sl_type, para_name)
        final_result_file = pd.read_csv("%s\\%s" % (folder_name, final_result_name))
        final_result_list.append(final_result_file)
    all_final_result_file = pd.concat(final_result_list)

    all_final_result_file.to_csv("%s %s%d finalresult_%s.csv" % (
        Parameter.strategy_name, domain_symbol, bar_type, sl_type))


def re_concat_multi_symbol_final_result():
    """
    重新汇总多品种回测的final_result结果，自动从_multi_symbol_setting_bt.xlsx文件读取品种列表
    :return:
    """
    strategy_folder = "%s%s\\" % (Parameter.root_path, Parameter.strategy_name)
    os.chdir(strategy_folder)
    multi_symbol_df = pd.read_excel(Parameter.symbol_KMIN_set_filename)
    all_final_result_list = []
    for n, row in multi_symbol_df.iterrows():
        strategy_name = row['strategy_name']
        exchange_id = row['exchange_id']
        sec_id = row['sec_id']
        bar_type = row['K_MIN']
        symbol_folder_name = "%s %s %s %d\\" % (strategy_name, exchange_id, sec_id, bar_type)
        result_file_name = "%s %s.%s %d finalresult.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        print result_file_name
        final_result_df = pd.read_csv(symbol_folder_name + result_file_name)
        final_result_df['strategy_name'] = strategy_name
        final_result_df['exchange_id'] = exchange_id
        final_result_df['sec_id'] = sec_id
        final_result_df['ba_type'] = bar_type
        all_final_result_list.append(final_result_df)

    multi_symbol_result_df = pd.concat(all_final_result_list)
    multi_symbol_result_df.to_csv('%s_multi_symbol_final_results.csv' % Parameter.strategy_name)


def calResultByPeriod():
    """
    按时间分段统计结果:
    1.设定开始和结束时间
    2.选择时间周期
    3.设定文件夹、买卖操作文件名、日结果文件名和要生成的新文件名
    :return:
    """
    # 设定开始和结束时间
    startdate = '2011-04-01'
    enddate = '2018-07-01'

    # 2.选择时间周期
    # freq='YS' #按年统计
    # freq='2QS' #按半年统计
    # freq='QS' #按季度统计
    freq = 'MS'  # 按月统计，如需多个月，可以加上数据，比如2个月：2MS

    # 3.设文件和文件夹状态
    filedir = 'D:\\002 MakeLive\myquant\HopeWin\Results\HopeMacdMaWin DCE J 3600\dsl_-0.022ownl_0.012\ForwardOprAnalyze\\'  # 文件所在文件夹
    oprfilename = 'HopeMacdMaWin DCE.J3600_Rank3_win9_oprResult.csv'  # 买卖操作文件名
    dailyResultFileName = 'HopeMacdMaWin DCE.J3600_Rank3_win9_oprdailyResult.csv'  # 日结果文件名
    newFileName = 'HopeMacdMaWin DCE.J3600_Rank3_win9_result_by_Period_M.csv'  # 要生成的新文件名
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
        monthlist.insert(0, startdate + " 00:00:00")
    if not enddate in monthlist[-1]:
        monthlist.append(enddate + " 23:59:59")
    else:
        monthlist[-1] = enddate + " 23:59:59"
    rlist = []
    for i in range(1, len(monthlist)):
        starttime = monthlist[i - 1]
        endtime = monthlist[i]
        startutc = float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
        endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))

        resultdata = oprdf.loc[(oprdf['openutc'] >= startutc) & (oprdf['openutc'] < endutc)]
        dailydata = dailyResultdf.loc[(dailyResultdf['utc_time'] >= startutc) & (dailyResultdf['utc_time'] < endutc)]
        resultdata.reset_index(drop=True, inplace=True)
        if resultdata.shape[0] > 0:
            rlist.append([starttime, endtime] + RS.getStatisticsResult(resultdata, newFlag, Parameter.ResultIndexDic, dailydata))
        else:
            rlist.append([0] * len(Parameter.ResultIndexDic))
    rdf = pd.DataFrame(rlist, columns=['StartTime', 'EndTime'] + Parameter.ResultIndexDic)
    rdf.to_csv(newFileName)


def plot_parameter_result_pic():
    """绘制finalresult结果中参数对应的end cash和max own cash的分布柱状图"""
    strategy_folder = "%s%s\\" % (Parameter.root_path, Parameter.strategy_name)
    os.chdir(strategy_folder)
    setting_file = pd.read_excel(Parameter.bt_parameter_optimize_polt_filename)
    for n, rows in setting_file.iterrows():
        fig = plt.figure(figsize=(6, 12))
        exchange_id = rows['exchange_id']
        sec_id = rows['sec_id']
        bar_type = rows['bar_type']
        folder_name = "%s %s %s %d\\" % (Parameter.strategy_name, exchange_id, sec_id, bar_type)
        final_result_file = pd.read_csv(folder_name + "%s %s.%s %d finalresult.csv" % (Parameter.strategy_name, exchange_id, sec_id, bar_type))
        para_file = pd.read_csv(folder_name + "%s %s %s %d Parameter.csv" % (Parameter.strategy_name, exchange_id, sec_id, bar_type))
        strategy_class = Strategy.strategy_mapping_dic[Parameter.strategy_name]()
        para_name_list = strategy_class.get_para_name_list()
        for i in range(len(para_name_list)):
            para_name = para_name_list[i]
            final_result_file[para_name_list] = para_file[para_name_list]
            grouped = final_result_file.groupby(para_name)
            end_cash_grouped = grouped['EndCash'].mean()
            p = plt.subplot(len(para_name_list), 1, i + 1)
            p.set_title(para_name)
            p.bar(end_cash_grouped.index.tolist(), end_cash_grouped.values)
            print end_cash_grouped
        fig.savefig('%s %s %s %d_para_distribute.png' % (Parameter.strategy_name, exchange_id, sec_id, bar_type), dip=500)


def calc_multi_result_superposition(result_folder=Parameter.root_path + 'ResultSuperposition\\'):
    """
    计算多个交易结果叠加的结果
    :param result_folder: 结果存放文件，默认为Parameter设置的根目录下的ResultSuperposition文件夹
    :return:
    """
    mss = RS.MultiSymbolSuperposition(result_folder)
    multi_result = mss.get_superposition_result()
    multi_result.to_csv(result_folder + 'multi_result_superposition.csv', index=False)
    print u"多结果叠加计算完成"
    print u"开始时间:", mss.opr_df_reformed.ix[0, 'oprtime']
    print u"最终资金:%.3f" % mss.opr_df_reformed.iloc[-1]['own cash']
    print u"最大回撤:%.3f" % mss.opr_df_reformed['draw_back'].max()
    print u"品种列表及盈利情况:"
    for k in mss.strategy_symbol_bar_dic.keys():
        k_pnl = mss.opr_df_reformed.loc[mss.opr_df_reformed['symbol_name'] == k, 'per earn'].sum()
        print "%s 盈利:%.3f,仓位:%.2f" % (k, k_pnl, mss.strategy_symbol_bar_dic[k]['pos'])


if __name__ == "__main__":
    """
    计算单个品种回测结果的汇总finalresult文件，包括普通回测和止损结果
    :param domain_symbol: 主力合约编号
    :param bar_type: 周期
    :param folder_name: 结果文件夹
    """
    #calc_single_final_result(domain_symbol='SHFE.RB', bar_type=3600, folder_name='SHFE.RB 3600 backtesting')

    """
    重新汇总某一止损类型所有参数的final_result， 止损的参数自动从Parameter中读
    :param domain_symbol: 主力合约编号
    :param bar_type: 周期
    :param sl_type: 止损类型 'dsl', 'ownl', 'frsl', 'gownl', 'pendant', 'yoyo'
    :return:
    """
    #re_concat_close_all_final_result(domain_symbol='SHFE.RB', bar_type=3600, sl_type='dsl')

    """
    重新汇总多品种回测的final_result结果，自动从_multi_symbol_setting_bt.xlsx文件读取品种列表
    """
    # re_concat_multi_symbol_final_result()

    """
    分时间段统计结果，需要到函数中修改相关参数
    """
    # calResultByPeriod()

    """绘制finalresult结果中参数对应的end cash分布柱状图,自动从_backtesting_parameter_plot.xlsx读品种列表"""
    # plot_parameter_result_pic()

    """
    计算多个交易结果叠加的结果，各不同文件的仓位在文件名上设置
    只支持推进结果
    :param result_folder: 结果存放文件，默认为Parameter设置的根目录下的ResultSuperposition文件夹， 如果要改变文件只需要将新路径填入函数的函数
    如： calc_multi_result_superposition("新文件夹路径")
    """
    calc_multi_result_superposition()
