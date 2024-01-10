from data_retrieval import get_jsonparsed_data, get_stocks_fmp, add_to_analysis_result_change, add_to_analysis_result_price
from alert_processing import find_change_alert, find_price_alert

import warnings
import pandas as pd
from datetime import datetime, timedelta
from pytz import utc, timezone
import time
import threading
import config

warnings.filterwarnings("ignore")

def compute_sleep_time(now_time):
    if now_time.weekday() in [5,6]:
        first_weekday = now_time + timedelta(days = 7 - now_time.weekday())
        return max(0,int((datetime(first_weekday.year,first_weekday.month,first_weekday.day,9,32,0) - now_time.replace(tzinfo=None)).total_seconds()))
    else:
        if now_time.strftime("%H:%M") >= '09:32' and now_time.strftime("%H:%M") <= '16:00':
            return 0
        elif now_time.strftime("%H:%M") > '16:00':
            return max(0,int((datetime(now_time.year,now_time.month,now_time.day,23,59,59) - now_time.replace(tzinfo=None)).total_seconds()) + 34320)
        else:
            return max(0,int((datetime(now_time.year,now_time.month,now_time.day,9,32,0) - now_time.replace(tzinfo=None)).total_seconds()))


class MarketThread(threading.Thread):
    def __init__(self, name, timezone_ct, all_alerts_variables):
        super().__init__()
        self.name = name
        self.timezone_ct = timezone_ct
        self.all_alerts_variables = all_alerts_variables
        self.price_alert_num = all_alerts_variables['PRICE_alert_num']
        self.change_alert_num = all_alerts_variables['CHANGE_alert_num']
        self.stock_storage = {}
        for alert_i in range(self.price_alert_num):
            self.stock_storage['all_data_price_' + str(alert_i + 1)] = pd.DataFrame()
        for alert_i in range(self.change_alert_num):
            self.stock_storage['all_data_change_' + str(alert_i + 1)] = pd.DataFrame()
        self.alert_parameters = {}
        self.get_alert_information(all_alerts_variables['CHANGE_sheet'], all_alerts_variables['PRICE_sheet'])

    def get_alert_information(self,change_sheet, price_sheet):

        self.stocks_name = list(
            set(change_sheet.index.astype('str').to_list() + price_sheet.index.astype('str').to_list()))

        for alert_i in range(self.change_alert_num):
            self.alert_parameters['alert_data_change_parameter_' + str(alert_i + 1)] = change_sheet.loc[:,
                                                                              ['X' + str(alert_i + 1),
                                                                               'X' + str(alert_i + 1) + 'A', \
                                                                               'Y' + str(alert_i + 1) + 'A',
                                                                               'Z' + str(alert_i + 1),
                                                                               'R' + str(alert_i + 1) + 'A',
                                                                               'R' + str(alert_i + 1) + 'B']]
        for alert_i in range(self.price_alert_num):
            self.alert_parameters['alert_data_price_parameter_' + str(alert_i + 1)] = price_sheet.loc[:,
                                                                             ['X' + str(alert_i + 1),
                                                                              'X' + str(alert_i + 1) + 'A', \
                                                                              'Y' + str(alert_i + 1) + 'A',
                                                                              'Z' + str(alert_i + 1),
                                                                              'R' + str(alert_i + 1) + 'A',
                                                                              'R' + str(alert_i + 1) + 'B']]


    def run(self):
        while True:
            sleep_time = compute_sleep_time(datetime.now(timezone(self.timezone_ct)))
            print(self.name+' stocks sleep:', sleep_time)
            time.sleep(sleep_time)
            time.sleep(1)
            # try:
            data_change, data_price = get_stocks_fmp(self.stocks_name,self.timezone_ct)
            now_time = datetime.now(timezone(self.timezone_ct))

            for alert_i in range(self.price_alert_num):
                # Update stock storage with latest data
                # Perform price alert checks and update results
                # Update analysis result with the latest data
                self.stock_storage['all_data_price_' + str(alert_i + 1)] = pd.concat(
                    [self.stock_storage['all_data_price_' + str(alert_i + 1)], data_price], axis=0)
                self.stock_storage['all_data_price_' + str(alert_i + 1)] = self.stock_storage['all_data_price_' + str(alert_i + 1)].loc[
                                                                           self.stock_storage['all_data_price_' + str(alert_i + 1)].index > (now_time - timedelta(
                    minutes=self.all_alerts_variables['PRICE_Y' + str(alert_i + 1)])), :]

                find_price_alert(self.name, alert_i,
                                  self.alert_parameters['alert_data_price_parameter_' + str(alert_i + 1)],
                                  self.stock_storage['all_data_price_' + str(alert_i + 1)],self.timezone_ct,self.all_alerts_variables['PRICE_N' + str(alert_i + 1)])
                config.df_analysis_result[self.name]['PRICE_analysis_result_' + str(alert_i + 1)] = add_to_analysis_result_price(data_price, config.df_analysis_result[self.name]['PRICE_analysis_result_' + str(alert_i + 1)])

            for alert_i in range(self.change_alert_num):
                # Update stock storage with latest data
                # Perform change alert checks and update results
                # Update analysis result with the latest data
                self.stock_storage['all_data_change_' + str(alert_i + 1)] = pd.concat(
                    [self.stock_storage['all_data_change_' + str(alert_i + 1)], data_change], axis=0)

                self.stock_storage['all_data_change_' + str(alert_i + 1)] = self.stock_storage['all_data_change_' + str(alert_i + 1)].loc[
                                                                            self.stock_storage['all_data_change_' + str(alert_i + 1)].index > now_time - timedelta(
                    minutes=self.all_alerts_variables['CHANGE_Y' + str(alert_i + 1)]), :]

                find_change_alert(self.name,alert_i,self.alert_parameters['alert_data_change_parameter_' + str(alert_i + 1)],self.stock_storage['all_data_change_' + str(alert_i + 1)],self.timezone_ct,
                                  self.all_alerts_variables['CHANGE_N' + str(alert_i + 1)])

                config.df_analysis_result[self.name]['CHANGE_analysis_result_' + str(alert_i + 1)] = add_to_analysis_result_change(data_change,config.df_analysis_result[self.name]['CHANGE_analysis_result_' + str(alert_i + 1)])



            print(self.name +' stock', datetime.now(timezone(self.timezone_ct)))
