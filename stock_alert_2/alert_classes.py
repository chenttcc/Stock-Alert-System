from utility_functions import send_change_notification, send_price_notification, send_exception_notification
import warnings
import pandas as pd
from datetime import datetime, timedelta
from pytz import utc, timezone
import config
import time

warnings.filterwarnings("ignore")
# these two class are used to monitor the second period of alerts,
# if the stock keep going up/down and the change exceeds some threshold, then send the alert

# N,market,'up',nc,cf,alert_i,timezone_ct

class CheckIsAlertChange:
    def __init__(self, name, X1A, Y1A, Z1, RAX, RBX, N, market, direction, nc, cf, alert_i,timezone_ct):
        self.Timezone = timezone_ct
        self.name = name
        self.start_time = datetime.now(timezone(self.Timezone))
        self.market = market
        self.X1A = X1A
        self.Y1A = int(Y1A)
        self.Z1 = int(Z1)
        self.RAX = RAX
        self.RBX = RBX
        self.change_list = pd.Series()
        self.direction = direction
        self.nc = nc
        self.cf = cf
        self.alert_i = alert_i
        self.N = N

    def append_check_change(self, change):
        now_time = datetime.now(timezone(self.Timezone))
        self.change_list[now_time] = change
        self.change_list = self.change_list[self.change_list.index >= now_time - timedelta(minutes=self.Y1A)]

        if len(self.change_list) > 1:

            now_change = change
            change_min = self.change_list.iloc[0:(len(self.change_list) - 1)].min()
            change_max = self.change_list.iloc[0:(len(self.change_list) - 1)].max()

            if ((self.name, 'change') not in config.alert_record.keys()) or \
                    ((self.name, 'change') in config.alert_record.keys() and (datetime.now(timezone('America/New_York')) - config.alert_record[
                        (self.name, 'change')]).total_seconds() > config.frozenperiod):

                if self.direction == 'up' and change_min >= (self.nc - self.RBX) and now_change - change_min > self.X1A:

                    send_change_notification(self.name, self.nc, self.cf, now_change, now_change - change_min,
                                             self.direction, self.Timezone, self.alert_i)
                    config.df_analysis_result[self.market]['CHANGE_analysis_result_' + str(self.alert_i + 1)][0] = config.df_analysis_result[self.market]['CHANGE_analysis_result_' + str(self.alert_i + 1)][0].append(
                        pd.Series([self.name,(datetime.now(timezone(self.Timezone)) + timedelta(minutes = self.N)).strftime('%I:%M%p'),pd.NA,
                                   now_time.strftime('%I:%M%p'),now_change,pd.NA]
                                   ,index = ['STOCK UP', 'TIME(t+n)', 'CHANGE(t+n)', 'TIME(t)', 'CHANGE(t)', 'Result'])
                    ,ignore_index=True)
                if self.direction == 'down' and change_max <= (
                        self.nc + self.RAX) and change_max - now_change > self.X1A:
                    send_change_notification(self.name, self.nc, self.cf, now_change, change_max - now_change,
                                             self.direction, self.Timezone, self.alert_i)
                    config.df_analysis_result[self.market]['CHANGE_analysis_result_' + str(self.alert_i + 1)][1] = config.df_analysis_result[self.market]['CHANGE_analysis_result_' + str(self.alert_i + 1)][1].append(
                        pd.Series([self.name,now_time.strftime('%I:%M%p'), now_change,
                                   (datetime.now(timezone(self.Timezone)) + timedelta(minutes=self.N)).strftime(
                                       '%I:%M%p'), pd.NA,
                                    pd.NA]
                                  , index=['STOCK DOWN','TIME(t)','CHANGE(t)','TIME(t+n)','CHANGE(t+n)','Result']),ignore_index=True)


    def check_existence(self):
        now_time = datetime.now(timezone(self.Timezone))
        if (now_time - self.start_time) >= timedelta(minutes=self.Z1):
            return True
        else:
            return False

class CheckIsAlertPrice:
    def __init__(self,name,X1A,Y1A,Z1,RAX,RBX,N,market,direction,np,pf,alert_i,timezone_ct):
        self.Timezone = timezone_ct
        self.name = name
        self.start_time = datetime.now(timezone(self.Timezone))
        self.market = market
        self.X1A = X1A
        self.Y1A = int(Y1A)
        self.Z1 = int(Z1)
        self.RAX = RAX
        self.RBX = RBX
        self.price_list = pd.Series()
        self.direction = direction
        self.np = np
        self.pf = pf
        self.alert_i = alert_i
        self.N = N
    def append_check_price(self,price):
        now_time = datetime.now(timezone(self.Timezone))
        self.price_list[now_time]= price
        self.price_list = self.price_list[self.price_list.index >= now_time - timedelta(minutes=self.Y1A)]

        if len(self.price_list) > 1:

            now_price = price
            price_min = self.price_list.iloc[0:(len(self.price_list) - 1)].min()
            price_max = self.price_list.iloc[0:(len(self.price_list) - 1)].max()

            if ((self.name, 'price') not in config.alert_record.keys()) or \
                    ((self.name, 'price') in config.alert_record.keys() and (datetime.now(timezone('America/New_York')) - config.alert_record[
                        (self.name, 'price')]).total_seconds() > config.frozenperiod):

                if self.direction == 'up' and price_min >= (self.np*(1 - self.RBX)) and (now_price/price_min - 1) > self.X1A:
                    send_price_notification(self.name,self.np,self.pf,now_price,now_price/price_min - 1,self.direction,self.Timezone, self.alert_i,'$' if self.market == 'US' else '￥')
                    config.df_analysis_result[self.market]['PRICE_analysis_result_' + str(self.alert_i + 1)][0] = config.df_analysis_result[self.market]['PRICE_analysis_result_' + str(self.alert_i + 1)][0].append(
                        pd.Series([self.name,
                                   (datetime.now(timezone(self.Timezone)) + timedelta(minutes=self.N)).strftime(
                                       '%I:%M%p'), pd.NA,
                                   now_time.strftime('%I:%M%p'), now_price, pd.NA]
                                  , index=['STOCK UP', 'TIME(t+n)', 'PRICE(t+n)', 'TIME(t)', 'PRICE(t)', 'Result'])
                    ,ignore_index=True)
                if self.direction == 'down' and price_max <= (self.np*(1 + self.RAX)) and (price_max/now_price - 1) > self.X1A:
                    send_price_notification(self.name,self.np,self.pf,now_price,price_max/now_price - 1,self.direction,self.Timezone, self.alert_i,'$' if self.market == 'US' else '￥')
                    config.df_analysis_result[self.market]['PRICE_analysis_result_' + str(self.alert_i + 1)][1] = config.df_analysis_result[self.market]['PRICE_analysis_result_' + str(self.alert_i + 1)][1].append(
                        pd.Series([self.name, now_time.strftime('%I:%M%p'), now_price,
                        (datetime.now(timezone(self.Timezone)) + timedelta(minutes=self.N)).strftime(
                            '%I:%M%p'), pd.NA,
                                   pd.NA]
                                  , index=['STOCK DOWN', 'TIME(t)', 'PRICE(t)', 'TIME(t+n)', 'PRICE(t+n)', 'Result']),ignore_index=True)


    def check_existence(self):
        now_time = datetime.now(timezone(self.Timezone))
        if (now_time - self.start_time) >= timedelta(minutes = self.Z1):
            return True
        else:
            return False