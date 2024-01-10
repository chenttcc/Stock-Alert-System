from urllib.request import urlopen
import warnings
import certifi
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from pytz import utc, timezone
import time
import threading as th
import urllib
from config import FMP_api
from errors import stocknonexist

warnings.filterwarnings("ignore")





def get_jsonparsed_data(url):

    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

# Almost every second request the real-time data for stocks, return the change data and price data
def get_stocks_fmp(stocks_name,timezone_ct):
    url = ("https://financialmodelingprep.com/api/v3/quote/" + ','.join(
        stocks_name) + "?apikey=" + FMP_api)
    try:
        data = pd.DataFrame(get_jsonparsed_data(url))
    except urllib.error.HTTPError as e:
        print(e.__str__)
    except urllib.error.URLError as e:
        print(e.__str__)

    for stock_i in stocks_name:
        if stock_i not in data.loc[:, 'symbol'].tolist():
            raise stocknonexist('Stock %s does not exist' % stock_i)

    data = data[['symbol', 'price', 'changesPercentage']]
    data.columns = ['stock', 'price', 'changesPercentage']
    data.loc[:, 'dtime'] = datetime.now(timezone(timezone_ct))
    data['change'] = data.changesPercentage * 0.01
    data_change = pd.pivot_table(data, values='change', index='dtime', columns='stock')
    data_price = pd.pivot_table(data, values='price', index='dtime', columns='stock')

    return data_change, data_price


# now_change = ['dtime',stock_name]
# index = ['STOCK UP', 'TIME(t+n)', 'CHANGE(t+n)', 'TIME(t)', 'CHANGE(t)', 'Result']
# Because after sending the alert message, it still needs to keep monitoring the stock alerted, these two
# function is to track the change/price after a period of time to check whether the trading decision is correct.
def add_to_analysis_result_change(now_change_data,change_analysis_result_alert):
    change_analysis_result_alert_up = change_analysis_result_alert[0]
    change_analysis_result_alert_down = change_analysis_result_alert[1]
    now_change_data = now_change_data.T.reset_index()
    dtime = now_change_data.columns[1].strftime('%I:%M%p')
    now_change_data.columns = ['stock','CHANGE(t+n)']
    now_change_data['TIME(t+n)'] = dtime
    now_change_data = now_change_data[['stock','TIME(t+n)','CHANGE(t+n)']]

    change_analysis_result_alert_up = change_analysis_result_alert_up.merge(now_change_data, how='left',
                                                                            left_on=['STOCK UP', 'TIME(t+n)'],
                                                                            right_on=['stock', 'TIME(t+n)'],
                                                                            suffixes=('_table1', '_table2'))
    change_analysis_result_alert_up['CHANGE(t+n)'] = change_analysis_result_alert_up['CHANGE(t+n)_table2'].fillna(
        change_analysis_result_alert_up['CHANGE(t+n)_table1'])
    change_analysis_result_alert_up = change_analysis_result_alert_up[
        ['STOCK UP', 'TIME(t+n)', 'CHANGE(t+n)', 'TIME(t)', 'CHANGE(t)', 'Result']]

    change_analysis_result_alert_down = change_analysis_result_alert_down.merge(now_change_data, how='left',
                                                                            left_on=['STOCK DOWN', 'TIME(t+n)'],
                                                                            right_on=['stock', 'TIME(t+n)'],
                                                                            suffixes=('_table1', '_table2'))
    change_analysis_result_alert_down['CHANGE(t+n)'] = change_analysis_result_alert_down['CHANGE(t+n)_table2'].fillna(
        change_analysis_result_alert_down['CHANGE(t+n)_table1'])
    change_analysis_result_alert_down = change_analysis_result_alert_down[
        ['STOCK DOWN', 'TIME(t)', 'CHANGE(t)', 'TIME(t+n)', 'CHANGE(t+n)', 'Result']]

    return [change_analysis_result_alert_up, change_analysis_result_alert_down]

def add_to_analysis_result_price(now_price_data,price_analysis_result_alert):
    price_analysis_result_alert_up = price_analysis_result_alert[0]
    price_analysis_result_alert_down = price_analysis_result_alert[1]
    now_price_data = now_price_data.T.reset_index()
    dtime = now_price_data.columns[1].strftime('%I:%M%p')
    now_price_data.columns = ['stock', 'PRICE(t+n)']
    now_price_data['TIME(t+n)'] = dtime
    now_price_data = now_price_data['stock', 'TIME(t+n)', 'PRICE(t+n)']

    price_analysis_result_alert_up = price_analysis_result_alert_up.merge(now_price_data, how='left',
                                                                            left_on=['STOCK UP', 'TIME(t+n)'],
                                                                            right_on=['stock', 'TIME(t+n)'],
                                                                            suffixes=('_table1', '_table2'))
    price_analysis_result_alert_up['PRICE(t+n)'] = price_analysis_result_alert_up['PRICE(t+n)_table2'].fillna(
        price_analysis_result_alert_up['PRICE(t+n)_table1'])
    price_analysis_result_alert_up = price_analysis_result_alert_up[
        ['STOCK UP', 'TIME(t+n)', 'PRICE(t+n)', 'TIME(t)', 'PRICE(t)', 'Result']]

    price_analysis_result_alert_down = price_analysis_result_alert_down.merge(now_price_data, how='left',
                                                                                left_on=['STOCK DOWN', 'TIME(t+n)'],
                                                                                right_on=['stock', 'TIME(t+n)'],
                                                                                suffixes=('_table1', '_table2'))
    price_analysis_result_alert_down['PRICE(t+n)'] = price_analysis_result_alert_down['PRICE(t+n)_table2'].fillna(
        price_analysis_result_alert_down['PRICE(t+n)_table1'])
    price_analysis_result_alert_down = price_analysis_result_alert_down[
        ['STOCK DOWN', 'TIME(t)', 'PRICE(t)', 'TIME(t+n)', 'PRICE(t+n)', 'Result']]

    return [price_analysis_result_alert_up, price_analysis_result_alert_down]


