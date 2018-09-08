# -*- coding: utf-8 -*-
"""
SmartWin回策框架
yoyo止损出场
作者:Smart
新建时间：2018-09-08
"""
from StopLossTemplate import StopLossTemplate
import pandas as pd
from Indexer import ATR


class YoyoStopLoss(StopLossTemplate):
    """
    yoyo止损出场
    """

    def __init__(self, para_dic):
        super(YoyoStopLoss, self).__init__(para_dic)
        self.para_dic = para_dic
        self.sl_name = 'yoyo'
        self.sl_para_name_list = ['yoyo_n', 'yoyo_rate']
        self.need_data_process_before_domain = True     # 需要在单连数据中计算ATR值
        self.need_data_process_after_domain = True  # 需要将ATR值映射到1min数据中
        self.folder_prefix = 'yoyo'
        self.file_suffix = 'result_yoyo_'

        self.yoyo_n_list = para_dic['yoyo_n']
        self.yoyo_rate_list = para_dic['yoyo_rate']
        self.price_tick = para_dic['price_tick']
        self.para_dic_list = []
        for yoyo_n in self.yoyo_n_list:
            for yoyo_rate in self.yoyo_rate_list:
                self.para_dic_list.append(
                    {
                        'para_name': '%d_%.1f' % (yoyo_n, yoyo_rate),
                        'yoyo_n': yoyo_n,
                        'yoyo_rate': yoyo_rate
                    })
        pass

    def get_opr_sl_result(self, opr, bar_df):
        result_dic = {}
        opr_type = opr['tradetype']
        open_price = opr['openprice']
        if opr_type == 1:
            bardf = pd.DataFrame({'high': bar_df['longHigh'], 'low': bar_df['longLow'], 'strtime': bar_df['strtime'],
                                  'utc_time': bar_df['utc_time'], 'last_close': bar_df['last_close']})
            # 多仓止损
            for n in self.yoyo_n_list:
                n_cols = 'atr_%d' % n
                for rate in self.yoyo_rate_list:
                    para_name = '%d_%.1f' % (n, rate)
                    bardf['yoyo_value'] = bar_df[n_cols] * rate
                    bardf['yoyo_dd'] = bardf['last_close'] - bardf['low'] - bardf['yoyo_value']
                    rows2 = bardf.loc[bardf['yoyo_dd'] >= 0]
                    if rows2.shape[0] > 0:
                        temp2 = rows2.iloc[0]
                        sl_price = temp2['last_close'] - temp2['yoyo_value']
                        close_price = sl_price // self.price_tick * self.price_tick
                        strtime = temp2['strtime']
                        utctime = temp2['utc_time']
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
            bardf = pd.DataFrame({'high': bar_df['shortHigh'], 'low': bar_df['shortLow'], 'strtime': bar_df['strtime'],
                                  'utc_time': bar_df['utc_time'], 'last_close': bar_df['last_close']})
            # 空仓止损
            for n in self.yoyo_n_list:
                n_cols = 'atr_%d' % n
                for rate in self.yoyo_rate_list:
                    para_name = '%d_%.1f' % (n, rate)
                    bardf['yoyo_value'] = bar_df[n_cols] * rate
                    bardf['yoyo_dd'] = bardf['high'] - bardf['last_close'] - bardf['yoyo_value']
                    rows2 = bardf.loc[bardf['yoyo_dd'] >= 0]
                    if rows2.shape[0] > 0:
                        temp2 = rows2.iloc[0]
                        sl_price = temp2['last_close'] + temp2['yoyo_value']
                        fprice = sl_price // self.price_tick * self.price_tick + max(self.price_tick, sl_price % self.price_tick)
                        strtime = temp2['strtime']
                        utctime = temp2['utc_time']
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
            for n in self.yoyo_n_list:
                cols_name = 'atr_%d' % n
                if cols_name not in barxm_cloumns:  # 如果打开了pendant且n值相同，则不重复计算
                    barxm[cols_name] = ATR.ATR(barxm.high, barxm.low, barxm.close, n)
        return bar1m_dic, barxm_dic

    def data_process_after_domain(self, domain_bar_1m, domain_bar_xm):
        domain_bar_1m.set_index('utc_endtime', drop=False, inplace=True)
        domain_bar_1m.set_index('utc_endtime', drop=False, inplace=True)
        bar_1m_columns = domain_bar_1m.columns.tolist()
        for n in self.yoyo_n_list:
            cols_name = 'atr_%d' % n
            if cols_name not in bar_1m_columns:   # 如果打开了pendant且n值相同，则不重复计算
                domain_bar_1m[cols_name] = domain_bar_xm[cols_name]
                domain_bar_1m[cols_name] = domain_bar_1m[cols_name].shift(1)
        domain_bar_1m['last_close'] = domain_bar_1m['close'].shift(1)
        domain_bar_1m['last_close'] = domain_bar_1m['last_close'].shift(1)
        domain_bar_1m.fillna(method='ffill', inplace=True)

        domain_bar_xm.set_index('utc_time', drop=False, inplace=True)  # 开始时间对齐
        domain_bar_1m.set_index('utc_time', drop=False, inplace=True)
        return domain_bar_1m, domain_bar_xm
