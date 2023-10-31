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


warnings.filterwarnings("ignore")


def get_jsonparsed_data(url):
    """
    Retrieves JSON data from a given URL.

    Args:
        url (str): The URL to fetch JSON data from.

    Returns:
        dict: Parsed JSON data.

    """
    # Open the URL with SSL certificate verification
    response = urlopen(url, cafile=certifi.where())

    # Read the response and decode it as UTF-8
    data = response.read().decode("utf-8")

    # Parse the JSON data and return as dictionary
    return json.loads(data)

# This function finds change alerts for stocks based on the provided data and timezone (TZ).
def find_change_alert(change_data,TZ):
    # Filter the change data to keep only 'stock' and 'change' columns, and remove duplicates.
    change_data = change_data[['stock','change']].drop_duplicates()

    # Depending on the timezone, choose the appropriate alert information dataframe.
    if TZ == 'US':
        alert_information = us_alert_information[['LB','LB ALERT % CHANGE', 'SS', 'SS ALERT % CHANGE']]
    elif TZ == 'CH':
        alert_information = ch_fmp_alert_information[['LB','LB ALERT % CHANGE', 'SS', 'SS ALERT % CHANGE']]

    #LB alert_change-w ~ alert_change
    alert_data = pd.merge(alert_information[['LB','LB ALERT % CHANGE']].dropna(),change_data,left_on='LB',
                          right_on='stock',how = 'left').drop_duplicates().reset_index(drop = True)
    alert_data = pd.merge(alert_data,w_all_values,left_on='LB',right_on='index',how='left').drop_duplicates().reset_index(drop = True)
    for i in alert_data.loc[alert_data.w_value.isnull(),'LB'].values:
        send_exception_notification("%s w_value doesn't exist"%i)

    # For each alert condition met, send a notification.
    alert_data_1 = alert_data.loc[(alert_data.change >= alert_data['LB ALERT % CHANGE']-alert_data.w_value) &
                                (alert_data.change <= alert_data['LB ALERT % CHANGE'])
    , :].reset_index(drop=True)

    for i in range(alert_data_1.shape[0]):
        stock = alert_data_1.loc[i, 'LB']
        alert_change = alert_data_1.loc[i, 'LB ALERT % CHANGE']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
            'value2': '%s =/< %.2f%%'%(stock,alert_change*100)}
        elif TZ == 'CH':
            payload = {"value1":  datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< %.2f%%'%(stock,alert_change*100)}
        send_change_notification(stock, payload,'LB_1')

    #LB ~alert_change - w
    alert_data_2 = alert_data.loc[(alert_data.change <= alert_data['LB ALERT % CHANGE'] - alert_data.w_value)&
                                  (alert_data.change >= alert_data['LB ALERT % CHANGE'] - 2*alert_data.w_value)
    , :].reset_index(drop=True)

    for i in range(alert_data_2.shape[0]):
        stock = alert_data_2.loc[i, 'LB']
        alert_change = alert_data_2.loc[i, 'LB ALERT % CHANGE'] - alert_data_2.loc[i, 'w_value']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< %.2f%%**' % (stock, alert_change * 100)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< %.2f%%**' % (stock, alert_change * 100)}
        send_change_notification(stock, payload, 'LB_2')

    # LB ~alert_change-2*w
    alert_data_3 = alert_data.loc[(alert_data.change <= alert_data['LB ALERT % CHANGE'] - 2*alert_data.w_value)
    , :].reset_index(drop=True)

    for i in range(alert_data_3.shape[0]):
        stock = alert_data_3.loc[i, 'LB']
        alert_change = alert_data_3.loc[i, 'LB ALERT % CHANGE'] - 2*alert_data_3.loc[i, 'w_value']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< %.2f%%***' % (stock, alert_change * 100)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< %.2f%%***' % (stock, alert_change * 100)}
        send_change_notification(stock, payload, 'LB_3')

    # SS alert_change ~ alert_change +w
    alert_data = pd.merge(alert_information[['SS', 'SS ALERT % CHANGE']].dropna(), change_data, left_on='SS',
                          right_on='stock', how='left').drop_duplicates().reset_index(drop=True)
    alert_data = pd.merge(alert_data, w_all_values, left_on='SS', right_on='index',
                          how='left').drop_duplicates().reset_index(drop=True)
    for i in alert_data.loc[alert_data.w_value.isnull(), 'SS'].values:
        send_exception_notification("%s w_value doesn't exist" % i)
    alert_data_1 = alert_data.loc[
                   (alert_data.change >= alert_data['SS ALERT % CHANGE']) &
                   (alert_data.change <= alert_data['SS ALERT % CHANGE'] + alert_data.w_value)
    , :].reset_index(drop=True)

    for i in range(alert_data_1.shape[0]):
        stock = alert_data_1.loc[i, 'SS']
        alert_change = alert_data_1.loc[i, 'SS ALERT % CHANGE']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> %.2f%%' % (stock, alert_change * 100)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> %.2f%%' % (stock, alert_change * 100)}
        send_change_notification(stock, payload, 'SS_1')

    # SS alert_change+w~alert_change+2*w
    alert_data_2 = alert_data.loc[(alert_data.change >= alert_data['SS ALERT % CHANGE'] + alert_data.w_value) &
                                  (alert_data.change <= alert_data['SS ALERT % CHANGE'] + 2*alert_data.w_value)
    , :].reset_index(drop=True)

    for i in range(alert_data_2.shape[0]):
        stock = alert_data_2.loc[i, 'SS']
        alert_change = alert_data_2.loc[i, 'SS ALERT % CHANGE'] + alert_data_2.loc[i, 'w_value']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> %.2f%%**' % (stock, alert_change * 100)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> %.2f%%**' % (stock, alert_change * 100)}
        send_change_notification(stock, payload, 'SS_2')

    # SS alert_change+2*w~
    alert_data_3 = alert_data.loc[
                                  (alert_data.change >= alert_data['SS ALERT % CHANGE'] + 2 * alert_data.w_value)
    , :].reset_index(drop=True)

    for i in range(alert_data_3.shape[0]):
        stock = alert_data_3.loc[i, 'SS']
        alert_change = alert_data_3.loc[i, 'SS ALERT % CHANGE'] + 2*alert_data_3.loc[i, 'w_value']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> %.2f%%***' % (stock, alert_change * 100)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> %.2f%%***' % (stock, alert_change * 100)}
        send_change_notification(stock, payload, 'SS_3')

    # return alert_data


def find_price_alert(price_data, TZ):
    # Filter and select unique stock and price data
    price_data = price_data[['stock', 'price']].drop_duplicates()

    # Select alert information based on timezone
    if TZ == 'US':
        alert_information = us_alert_information[['LB', 'LB ALERT PRICE', 'SS', 'SS ALERT PRICE']]
    elif TZ == 'CH':
        alert_information = ch_fmp_alert_information[['LB', 'LB ALERT PRICE', 'SS', 'SS ALERT PRICE']]

    # For each alert condition met, send a notification.

    # LB alert_price*(1-w) ~ alert_price
    alert_data = pd.merge(alert_information[['LB', 'LB ALERT PRICE']].dropna(), price_data, left_on='LB',
                          right_on='stock', how='left').drop_duplicates().reset_index(drop=True)
    alert_data = pd.merge(alert_data, w_all_values, left_on='LB', right_on='index',
                          how='left').drop_duplicates().reset_index(drop=True)
    for i in alert_data.loc[alert_data.w_value.isnull(), 'LB'].values:
        send_exception_notification("%s w_value doesn't exist" % i)
    alert_data_1 = alert_data.loc[(alert_data.price >= alert_data['LB ALERT PRICE'] * (1 - alert_data.w_value)) &
                                  (alert_data.price <= alert_data['LB ALERT PRICE'])
    , :].reset_index(drop=True)

    for i in range(alert_data_1.shape[0]):
        stock = alert_data_1.loc[i, 'LB']
        alert_price = alert_data_1.loc[i, 'LB ALERT PRICE']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< $%.2f' % (stock, alert_price)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< ￥%.2f' % (stock, alert_price)}
        send_price_notification(stock, payload, 'LB_1')

    # LB alert_price*(1-2*w)~alert_price*(1-w)
    alert_data_2 = alert_data.loc[(alert_data.price <= alert_data['LB ALERT PRICE'] * (1 - alert_data.w_value))&
                                  (alert_data.price >= alert_data['LB ALERT PRICE'] * (1 - 2*alert_data.w_value))
    , :].reset_index(drop=True)

    for i in range(alert_data_2.shape[0]):
        stock = alert_data_2.loc[i, 'LB']
        alert_price = alert_data_2.loc[i, 'LB ALERT PRICE'] * (1 - alert_data_2.loc[i, 'w_value'])
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< $%.2f**' % (stock, alert_price)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< ￥%.2f**' % (stock, alert_price)}
        send_price_notification(stock, payload, 'LB_2')

    # LB ~alert_price*(1-2*w)
    alert_data_3 = alert_data.loc[
                                  (alert_data.price <= alert_data['LB ALERT PRICE'] * (1 - 2 * alert_data.w_value))
    , :].reset_index(drop=True)

    for i in range(alert_data_3.shape[0]):
        stock = alert_data_3.loc[i, 'LB']
        alert_price = alert_data_3.loc[i, 'LB ALERT PRICE'] * (1 - 2*alert_data_3.loc[i, 'w_value'])
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< $%.2f***' % (stock, alert_price)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/< ￥%.2f***' % (stock, alert_price)}
        send_price_notification(stock, payload, 'LB_3')

    # SS alert_price ~ alert_price*(1+w)
    alert_data = pd.merge(alert_information[['SS', 'SS ALERT PRICE']].dropna(), price_data, left_on='SS',
                          right_on='stock', how='left').drop_duplicates().reset_index(drop=True)
    alert_data = pd.merge(alert_data, w_all_values, left_on='SS', right_on='index',
                          how='left').drop_duplicates().reset_index(drop=True)
    for i in alert_data.loc[alert_data.w_value.isnull(), 'SS'].values:
        send_exception_notification("%s w_value doesn't exist" % i)
    alert_data_1 = alert_data.loc[
                   (alert_data.price >= alert_data['SS ALERT PRICE']) &
                   (alert_data.price <= alert_data['SS ALERT PRICE'] * (1 + alert_data.w_value))
    , :].reset_index(drop=True)

    for i in range(alert_data_1.shape[0]):
        stock = alert_data_1.loc[i, 'SS']
        alert_price = alert_data_1.loc[i, 'SS ALERT PRICE']
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> $%.2f' % (stock, alert_price)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> ￥%.2f' % (stock, alert_price)}
        send_price_notification(stock, payload, 'SS_1')

    # SS alert_price*(1+w)~alert_price*(1+2*w)
    alert_data_2 = alert_data.loc[(alert_data.price >= alert_data['SS ALERT PRICE'] * (1 + alert_data.w_value))&
                                  (alert_data.price <= alert_data['SS ALERT PRICE'] * (1 + 2*alert_data.w_value))
    , :].reset_index(drop=True)

    for i in range(alert_data_2.shape[0]):
        stock = alert_data_2.loc[i, 'SS']
        alert_price = alert_data_2.loc[i, 'SS ALERT PRICE'] * (1 + alert_data_2.loc[i, 'w_value'])
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> $%.2f**' % (stock, alert_price)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> ￥%.2f**' % (stock, alert_price)}
        send_price_notification(stock, payload, 'SS_2')

    # SS alert_price*(1+2*w)~
    alert_data_3 = alert_data.loc[
                                  (alert_data.price >= alert_data['SS ALERT PRICE'] * (1 + 2 * alert_data.w_value))
    , :].reset_index(drop=True)

    for i in range(alert_data_3.shape[0]):
        stock = alert_data_3.loc[i, 'SS']
        alert_price = alert_data_3.loc[i, 'SS ALERT PRICE'] * (1 + 2 * alert_data_3.loc[i, 'w_value'])
        if TZ == 'US':
            payload = {"value1": datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> $%.2f***' % (stock, alert_price)}
        elif TZ == 'CH':
            payload = {"value1": datetime.now(timezone('Asia/Shanghai')).strftime('%I:%M:%S%p'),
                       'value2': '%s =/> ￥%.2f***' % (stock, alert_price)}
        send_price_notification(stock, payload, 'SS_3')


def send_price_notification(stock, payload, category):
    # Get the frozen period for the specific stock category
    frozenperiod = globals()[stocks_class[stock] + '_FROZEN_TIME']

    # Check if the alert for this stock, category, and price type has not been sent recently
    if ((stock, 'price', category) not in alert_record.keys()) or \
            ((stock, 'price', category) in alert_record.keys() and time.time() - alert_record[
                (stock, 'price', category)] > frozenperiod):
        # Construct the URL for IFTTT webhook
        url = "https://maker.ifttt.com/trigger/notice_price_phone/with/key/" + IFTTT_api

        # Print the timestamp and the notification message
        print(datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'), payload["value2"])

        # Log the notification in a file
        with open(log_file_path, 'a+') as f:
            f.write(payload["value1"] + ' ' + payload["value2"] + '\n')

        # Send the POST request to the IFTTT webhook
        response = requests.request("POST", url, data=payload)

        # Update the alert record with the current timestamp
        alert_record[(stock, 'price', category)] = time.time()


def send_change_notification(stock, payload, category):
    # Get the frozen period for the specific stock category
    frozenperiod = globals()[stocks_class[stock] + '_FROZEN_TIME']

    # Check if the alert for this stock, category, and change type has not been sent recently
    if ((stock, 'change', category) not in alert_record.keys()) or \
            ((stock, 'change', category) in alert_record.keys() and time.time() - alert_record[
                (stock, 'change', category)] > frozenperiod):
        # Construct the URL for IFTTT webhook
        url = "https://maker.ifttt.com/trigger/notice_change_phone/with/key/" + IFTTT_api

        # Print the timestamp and the notification message
        print(datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'), payload["value2"])

        # Log the notification in a file
        with open(log_file_path, 'a+') as f:
            f.write(payload["value1"] + ' ' + payload["value2"] + '\n')

        # Send the POST request to the IFTTT webhook
        response = requests.request("POST", url, data=payload)

        # Update the alert record with the current timestamp
        alert_record[(stock, 'change', category)] = time.time()


def send_exception_notification(text):
    # Construct the URL for IFTTT webhook
    url = "https://maker.ifttt.com/trigger/notice_exception_phone/with/key/" + IFTTT_api

    # Define the payload with the exception message
    payload = {"value1": text}

    # Print the exception message and timestamp
    print("exception:%s" % (text), datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'))

    # Log the exception message along with timestamp in a file
    with open(log_file_path, 'a+') as f:
        f.write(payload["value1"] + datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p') + '\n')

    # Send the POST request to the IFTTT webhook
    response = requests.request("POST", url, data=payload)


class changerangeerror(Exception):
    pass
class stocknonexist(Exception):
    pass
def get_alert_information():
    # Define global variables to store alert information
    global us_alert_information
    global ch_fmp_alert_information
    global w_all_values,stocks_class

    # Read alert information for US market from Excel file
    us_alert = pd.read_excel('ALERT DATA INPUT.xlsx', sheet_name='FMP', header=None)
    us_alert.index = us_alert.iloc[:, 0]
    us_alert.drop(0, axis=1, inplace=True)
    us_alert = us_alert.T

    # Read alert information for CH FMP market from Excel file
    ch_fmp_alert = pd.read_excel('ALERT DATA INPUT.xlsx',sheet_name = 'CH FMP', header=None)
    ch_fmp_alert.index = ch_fmp_alert.iloc[:, 0]
    ch_fmp_alert.drop(0, axis=1, inplace=True)
    ch_fmp_alert = ch_fmp_alert.T

    # Read w values from Excel file
    w_values = pd.read_excel('ALERT DATA INPUT.xlsx', sheet_name='W Values', header=None)
    w_values.index = w_values.iloc[:, 0]
    w_values.drop(0, axis=1, inplace=True)
    w_values = w_values.T

    # Initialize dictionaries to store w values and stocks classification
    w_all_values = {}
    stocks_class = {}

    # Extract stocks and ETFs along with their corresponding w values
    stocks = w_values[['STOCK', 'W_STOCK']].dropna().reset_index(drop=True)
    etfs = w_values[['ETF', 'W_ETF']].dropna().reset_index(drop=True)

    # Populate w_all_values and stocks_class dictionaries
    for idx in range(stocks.shape[0]):
        w_all_values[stocks.loc[idx, 'STOCK']] = stocks.loc[idx, 'W_STOCK']
        stocks_class[stocks.loc[idx, 'STOCK']] = 'STOCK'
    for idx in range(etfs.shape[0]):
        w_all_values[etfs.loc[idx, 'ETF']] = etfs.loc[idx, 'W_ETF']
        stocks_class[etfs.loc[idx, 'ETF']] = 'ETF'

    # Convert w_all_values into a DataFrame
    w_all_values = pd.DataFrame(w_all_values, index=['w_value']).T.reset_index()

    # Assign alert information to global variables
    us_alert_information = us_alert
    ch_fmp_alert_information = ch_fmp_alert


def compute_sleep_time(now_time):
    # Check if it's a weekend (Saturday or Sunday)
    if now_time.weekday() in [5, 6]:
        # Find the next Monday and calculate the time until 9:29 AM
        first_weekday = now_time + timedelta(days=7 - now_time.weekday())
        return max(0, int((datetime(first_weekday.year, first_weekday.month, first_weekday.day, 9, 29, 0) - now_time.replace(tzinfo=None)).total_seconds()))
    else:
        # Check if it's within trading hours (9:29 AM to 4:00 PM)
        if '09:29' <= now_time.strftime("%H:%M") <= '16:00':
            return 0
        # If it's after market hours, calculate the time until 9:29 AM of the next day
        elif now_time.strftime("%H:%M") > '16:00':
            return max(0, int((datetime(now_time.year, now_time.month, now_time.day, 23, 59, 0) - now_time.replace(tzinfo=None)).total_seconds()) + 34200)
        # If it's before market hours, calculate the time until 9:29 AM
        else:
            return max(0, int((datetime(now_time.year, now_time.month, now_time.day, 9, 29, 0) - now_time.replace(tzinfo=None)).total_seconds()))


def get_us_stocks():
    # Get the list of US stock names from the alert information
    us_stocks_names = us_alert_information.loc[us_alert_information.loc[:, 'LB'].notnull(), 'LB'].tolist() + \
                      us_alert_information.loc[us_alert_information.loc[:, 'SS'].notnull(), 'SS'].tolist()

    # Construct the URL to fetch stock data
    url = ("https://financialmodelingprep.com/api/v3/quote/" + ','.join(us_stocks_names) + "?apikey=" + FMP_api)

    try:
        # Attempt to retrieve data from the URL
        us_data = pd.DataFrame(get_jsonparsed_data(url))
    except urllib.error.HTTPError as e:
        # Handle HTTPError (if any)
        print(e.__str__)
    except urllib.error.URLError as e:
        # Handle URLError (if any)
        print(e.__str__)

    # Check if all requested stocks are present in the data
    for i in us_stocks_names:
        if i not in us_data.loc[:, 'symbol'].tolist():
            raise stocknonexist('Stock %s does not exist' % i)

    # Select relevant columns and calculate 'change'
    us_data = us_data[['symbol', 'price', 'previousClose']]
    us_data.columns = ['stock', 'price', 'previousClose']
    us_data['change'] = us_data.price / us_data.previousClose - 1

    return us_data


def get_ch_fmp_stocks():
    # Get the list of CH FMP stock names from the alert information
    ch_fmp_stocks_name = ch_fmp_alert_information.loc[ch_fmp_alert_information.loc[:, 'LB'].notnull(), 'LB'].tolist() + \
                         ch_fmp_alert_information.loc[ch_fmp_alert_information.loc[:, 'SS'].notnull(), 'SS'].tolist()

    # Construct the URL to fetch stock data
    url = ("https://financialmodelingprep.com/api/v3/quote/" + ','.join(ch_fmp_stocks_name) + "?apikey=" + FMP_api)

    try:
        # Attempt to retrieve data from the URL
        ch_fmp_data = pd.DataFrame(get_jsonparsed_data(url))
    except urllib.error.HTTPError as e:
        # Handle HTTPError (if any)
        print(e.__str__)
    except urllib.error.URLError as e:
        # Handle URLError (if any)
        print(e.__str__)

    # Check if all requested stocks are present in the data
    for i in ch_fmp_stocks_name:
        if i not in ch_fmp_data.loc[:, 'symbol'].tolist():
            raise stocknonexist('Stock %s does not exist' % i)

    # Select relevant columns and calculate 'change'
    ch_fmp_data = ch_fmp_data[['symbol', 'price', 'previousClose']]
    ch_fmp_data.columns = ['stock', 'price', 'previousClose']
    ch_fmp_data['change'] = ch_fmp_data.price / ch_fmp_data.previousClose - 1

    return ch_fmp_data


def whole_us():
    while True:
        # Calculate the time to sleep before the next run based on the current time in New York timezone
        sleep_time = compute_sleep_time(datetime.now(timezone('America/New_York')))
        print('us stocks sleep:', sleep_time)

        # Sleep for the calculated time
        time.sleep(sleep_time)

        # Add an extra 1-second delay
        time.sleep(1)

        # Get the US stock data
        us_data = get_us_stocks()

        # Find price alerts for US stocks
        find_price_alert(us_data, 'US')

        # Find change alerts for US stocks
        find_change_alert(us_data, 'US')

        print('us_stock', datetime.now(timezone('America/New_York')))


def whole_ch_fmp():
    while True:
        # Calculate the time to sleep before the next run based on the current time in Shanghai timezone
        sleep_time = compute_sleep_time(datetime.now(timezone('Asia/Shanghai')))
        print('ch fmp stocks sleep:', sleep_time)

        # Sleep for the calculated time
        time.sleep(sleep_time)

        # Add an extra 1-second delay
        time.sleep(1)

        # Get the CH FMP stock data
        ch_data = get_ch_fmp_stocks()

        # Find price alerts for CH FMP stocks
        find_price_alert(ch_data, 'CH')

        # Find change alerts for CH FMP stocks
        find_change_alert(ch_data, 'CH')

        print('ch_fmp_stock', datetime.now(timezone('Asia/Shanghai')))

# Set default values and file paths
Default_IFTTT_api = ''
Default_FMP_api = ''
Default_frozen_time = 600
log_file_path = 'log_first.txt'

# Main execution block
if __name__ == "__main__":
    # Read hyperparameters from Excel
    hyper_parameter = pd.read_excel('ALERT DATA INPUT.xlsx', sheet_name='Parameter', index_col='NAME')

    # Initialize alert record
    alert_record = {}

    # Set global variables based on hyperparameters
    for na in ['STOCK_FROZEN_TIME', 'ETF_FROZEN_TIME']:
        globals()[na] = hyper_parameter.loc[na, 'VALUE']
        if pd.isna(globals()[na]):
            globals()[na] = Default_frozen_time
        else:
            globals()[na] = int(globals()[na])

    # Set IFTTT API key
    IFTTT_api = hyper_parameter.loc['IFTTT_API', 'VALUE']
    if pd.isna(IFTTT_api):
        IFTTT_api = Default_IFTTT_api
    else:
        IFTTT_api = str(IFTTT_api)

    # Set FMP API key
    FMP_api = hyper_parameter.loc['FMP_API', 'VALUE']
    if pd.isna(FMP_api):
        FMP_api = Default_FMP_api
    else:
        FMP_api = str(FMP_api)

    while True:
        try:
            # Get alert information from Excel
            get_alert_information()

            # Create and start threads for US and CH FMP stocks
            s1 = th.Thread(target=whole_us)
            s2 = th.Thread(target=whole_ch_fmp)

            for s in [s1, s2]:
                s.start()

            for s in [s1, s2]:
                s.join()

        # Handle file not found error
        except FileNotFoundError as e:
            print(str(e))
            send_exception_notification('FileName is Wrong:' + str(e))
            time.sleep(30)

        # Handle value error
        except ValueError as e:
            print(str(e))
            send_exception_notification(str(e)+' exit code!!')
            time.sleep(30)
            exit()

        # Handle non-existent stock error
        except stocknonexist as e:
            print(str(e))
            send_exception_notification(str(e))
            time.sleep(30)

        # Handle key error
        except KeyError as e:
            print(str(e))
            send_exception_notification(str(e)+' exit code!!')
            exit()

        # Handle other exceptions
        except Exception as e:
            print(str(e))
            send_exception_notification('Unknown problem:' + str(e))
            time.sleep(30)

