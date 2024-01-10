
import pandas as pd

from alert_classes import CheckIsAlertChange, CheckIsAlertPrice
import config

# these function are used to check in the first period of monitoring (during the specific period), if there is any stock change (up/down) exceeding the threshold,
# if there is, initialize a new class (for the second period of monitoring)
def find_change_alert(market,alert_i,alert_information,change_data,timezone_ct,N):

    now_change = change_data.iloc[(change_data.shape[0])-1,:]
    if change_data.shape[0] > 1:
        change_min = change_data.iloc[0:(change_data.shape[0]-1),:].min(axis=0)
        change_max = change_data.iloc[0:(change_data.shape[0]-1),:].max(axis=0)

        df_min = pd.concat([(now_change - change_min), alert_information['X' + str(alert_i + 1)]], axis=1)
        df_min.columns = ['delta', 'X1']
        df_min = df_min[df_min.delta > df_min.X1]
        df_max = pd.concat([(change_max - now_change), alert_information['X' + str(alert_i + 1)]], axis=1)
        df_max.columns = ['delta', 'X1']
        df_max = df_max[df_max.delta > df_max.X1]

        for idx in df_min.index:
            alert_indi = alert_information.loc[alert_information.index == idx,:]
            nc = now_change[idx]
            cf = (now_change - change_min)[idx]
            new_alert = CheckIsAlertChange(idx,alert_indi['X'+str(alert_i + 1)+'A'].values[0],alert_indi[
                                          'Y'+str(alert_i + 1)+'A'].values[0],alert_indi['Z'+str(alert_i + 1)].values[0],
                                              alert_indi['R'+str(alert_i + 1)+'A'].values[0]*alert_indi['X'+str(alert_i + 1)].values[0],
                                              alert_indi['R'+str(alert_i + 1)+'B'].values[0]*alert_indi['X'+str(alert_i + 1)].values[0],
                                              N,market,'up',nc,cf,alert_i,timezone_ct)
            config.total_class[market + '_total_change_class'].append(new_alert)

        for idx in df_max.index:
            alert_indi = alert_information.loc[alert_information.index == idx, :]
            nc = now_change[idx]
            cf = (change_max - now_change)[idx]
            new_alert = CheckIsAlertChange(idx, alert_indi['X' + str(alert_i + 1) + 'A'].values[0], alert_indi[
                'Y' + str(alert_i + 1) + 'A'].values[0], alert_indi['Z' + str(alert_i + 1)].values[0],
              alert_indi['R' + str(alert_i + 1) + 'A'].values[0] *
              alert_indi['X' + str(alert_i + 1)].values[0],
              alert_indi['R' + str(alert_i + 1) + 'B'].values[0] *
              alert_indi['X' + str(alert_i + 1)].values[0],
                                              N, market,'down',nc,cf,alert_i,timezone_ct)
            config.total_class[market + '_total_change_class'].append(new_alert)

        for alert in config.total_class[market + '_total_change_class']:
            name = alert.name
            alert.append_check_change(now_change[name])

        for idx in range(len(config.total_class[market + '_total_change_class'])-1,-1,-1):
            if config.total_class[market + '_total_change_class'][idx].check_existence():
                del config.total_class[market + '_total_change_class'][idx]


def find_price_alert(market,alert_i,alert_information,price_data,timezone_ct,N):


    now_price = price_data.iloc[(price_data.shape[0])-1,:]
    if price_data.shape[0] > 1:
        price_min = price_data.iloc[0:(price_data.shape[0]-1),:].min(axis=0)
        price_max = price_data.iloc[0:(price_data.shape[0]-1),:].max(axis=0)

        df_min = pd.concat([(now_price/price_min - 1),alert_information['X'+str(alert_i + 1)]],axis = 1)
        df_min.columns = ['delta','X1']
        df_min = df_min[df_min.delta > df_min.X1]
        df_max = pd.concat([(price_max/now_price - 1),alert_information['X'+str(alert_i + 1)]],axis = 1)
        df_max.columns = ['delta', 'X1']
        df_max = df_max[df_max.delta > df_max.X1]

        for idx in df_min.index:
            alert_indi = alert_information.loc[alert_information.index == idx,:]
            nc = now_price[idx]
            cf = (now_price/price_min - 1)[idx]
            new_alert = CheckIsAlertPrice(idx,alert_indi['X'+str(alert_i + 1)+'A'].values[0],alert_indi[
                                          'Y'+str(alert_i + 1)+'A'].values[0],alert_indi['Z'+str(alert_i + 1)].values[0],
                                             alert_indi['R' + str(alert_i + 1) + 'A'].values[0] *
                                             alert_indi['X' + str(alert_i + 1)].values[0],
                                             alert_indi['R' + str(alert_i + 1) + 'B'].values[0] *
                                             alert_indi['X' + str(alert_i + 1)].values[0],
                                             N,market,'up',nc,cf,alert_i,timezone_ct)
            config.total_class[market + '_total_price_class'].append(new_alert)

        for idx in df_max.index:
            alert_indi = alert_information.loc[alert_information.index == idx, :]
            nc = now_price[idx]
            cf = (price_max/now_price - 1)[idx]
            new_alert = CheckIsAlertPrice(idx, alert_indi['X' + str(alert_i + 1) + 'A'].values[0], alert_indi[
                'Y' + str(alert_i + 1) + 'A'].values[0], alert_indi['Z' + str(alert_i + 1)].values[0],
                                             alert_indi['R' + str(alert_i + 1) + 'A'].values[0] *
                                             alert_indi['X' + str(alert_i + 1)].values[0],
                                             alert_indi['R' + str(alert_i + 1) + 'B'].values[0] *
                                             alert_indi['X' + str(alert_i + 1)].values[0],
                                              N,market, 'down',nc,cf,alert_i,timezone_ct)
            config.total_class[market + '_total_price_class'].append(new_alert)

        for alert in config.total_class[market + '_total_price_class']:
            name = alert.name
            alert.append_check_price(now_price[name])

        for idx in range(len(config.total_class[market + '_total_price_class'])-1,-1,-1):
            if config.total_class[market + '_total_price_class'][idx].check_existence():
                del config.total_class[market + '_total_price_class'][idx]