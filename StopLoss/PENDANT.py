# -*- coding: utf-8 -*-
"""
SmartWin回策框架
pendant吊灯止损出场
作者:Smart
新建时间：2018-09-07
"""
from StopLossTemplate import StopLossTemplate
import pandas as pd
from Indexer import ATR


class PendantStopLoss(StopLossTemplate):
    """
    pendant吊灯止损出场
    """

    def __init__(self, para_dic):
        super(PendantStopLoss, self).__init__(para_dic)
        self.para_dic = para_dic
        self.sl_name = 'pendant'
        self.sl_para_name_list = ['pendant_n', 'pendant_rate']
        self.need_data_process_before_domain = True     # 需要在单连数据中计算ATR值
        self.need_data_process_after_domain = True  # 需要将ATR值映射到1min数据中
        self.folder_prefix = 'pendant'
        self.file_suffix = 'result_pendant_'

        self.pendant_n_list = para_dic['pendant_n']
        self.pendant_rate_list = para_dic['pendant_rate']
        self.price_tick = para_dic['price_tick']
        self.para_dic_list = []
        for pendant_n in self.pendant_n_list:
            for pendant_rate in self.pendant_rate_list:
                self.para_dic_list.append(
                    {
                        'para_name': '%d_%.1f' % (pendant_n, pendant_rate),
                        'pendant_n': pendant_n,
                        'pendant_rate': pendant_rate
                    })
        pass

    def get_opr_sl_result(self, opr, bar_df):
        result_dic = {}
        opr_type = opr['tradetype']
        open_price = opr['openprice']
        if opr_type == 1:
            df = pd.DataFrame({'high': bar_df['longHigh'], 'low': bar_df['longLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time']})
            # 多仓止损
            df['max2here'] = df['high'].expanding().max()
            df['dd2here'] = df['max2here'] - df['low']
            for n in self.pendant_n_list:
                n_cols = 'atr_%d' % n
                for rate in self.pendant_rate_list:
                    para_name = '%d_%.1f' % (n, rate)
                    df['pendant_value'] = bar_df[n_cols] * rate
                    df['pendant_dd'] = df['dd2here'] - df['pendant_value']  # 吊灯止损
                    rows = df.loc[df['pendant_dd'] >= 0]
                    if rows.shape[0] > 0:
                        temp = rows.iloc[0]
                        sl_price = temp['max2here'] - temp['pendant_value']  # 这个止损价格还需要再基于price tick做向上取整处理
                        close_price = sl_price // self.price_tick * self.price_tick
                        strtime = temp['strtime']
                        utctime = temp['utc_time']
                        result_dic[para_name] = {
                            "new_closeprice": close_price,
                            "new_closetime": strtime,
                            "new_closeutc": utctime,
                            "new_closeindex": 0
                        }
                    else:
                        result_dic[para_name] = {
                            "new_closeprice": opr['closeprice'],
                            "new_closetime": opr['closetime'],
                            "new_closeutc": opr['closeutc'],
                            "new_closeindex": opr['closeindex']
                        }
        else:
            df = pd.DataFrame({'high': bar_df['shortHigh'], 'low': bar_df['shortLow'], 'strtime': bar_df['strtime'],
                               'utc_time': bar_df['utc_time']})

            # 空仓止损
            df['min2here'] = df['low'].expanding().min()
            df['dd2here'] = df['high'] - df['min2here']
            for n in self.pendant_n_list:
                n_cols = 'atr_%d' % n
                for rate in self.pendant_rate_list:
                    para_name = '%d_%.1f' % (n, rate)
                    df['pendant_value'] = bar_df[n_cols] * rate
                    df['pendant_dd'] = df['dd2here'] - df['pendant_value']  # 吊灯止损
                    rows = df.loc[df['pendant_dd'] >= 0]
                    if rows.shape[0] > 0:
                        temp = rows.iloc[0]
                        sl_price = temp['min2here'] + temp['pendant_value']  # 这个止损价格还需要再基于price tick做向上取整处理
                        fprice = sl_price // self.price_tick * self.price_tick + max(self.price_tick, sl_price % self.price_tick)
                        strtime = temp['strtime']
                        utctime = temp['utc_time']
                        result_dic[para_name] = {
                            "new_closeprice": fprice,
                            "new_closetime": strtime,
                            "new_closeutc": utctime,
                            "new_closeindex": 0
                        }
                    else:
                        result_dic[para_name] = {
                            "new_closeprice": opr['closeprice'],
                            "new_closetime": opr['closetime'],
                            "new_closeutc": opr['closeutc'],
                            "new_closeindex": opr['closeindex']
                        }
        return result_dic


    def data_process_before_domain(self, bar1m_dic, barxm_dic):
        for symbol, barxm in barxm_dic.items():
            barxm_cloumns = barxm.columns.tolist()
            for n in self.pendant_n_list:
                cols_name = 'atr_%d' % n
                if cols_name not in barxm_cloumns:  # 如果打开了yoyo且n值相同，则不重复计算
                    barxm[cols_name] = ATR.ATR(barxm.high, barxm.low, barxm.close, n)
        return bar1m_dic, barxm_dic

    def data_process_after_domain(self, domain_bar_1m, domain_bar_xm):
        domain_bar_1m.set_index('utc_endtime', drop=False, inplace=True)
        domain_bar_1m.set_index('utc_endtime', drop=False, inplace=True)
        bar_1m_columns = domain_bar_1m.columns.tolist()
        for n in self.pendant_n_list:
            cols_name = 'atr_%d' % n
            if cols_name not in bar_1m_columns:   # 如果打开了yoyo且n值相同，则不重复计算
                domain_bar_1m[cols_name] = domain_bar_xm[cols_name]
                domain_bar_1m[cols_name] = domain_bar_1m[cols_name].shift(1)
        domain_bar_1m.fillna(method='ffill', inplace=True)

        domain_bar_xm.set_index('utc_time', drop=False, inplace=True)  # 开始时间对齐
        domain_bar_1m.set_index('utc_time', drop=False, inplace=True)
        return domain_bar_1m, domain_bar_xm
