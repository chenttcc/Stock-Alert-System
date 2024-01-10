import warnings
from datetime import datetime, timedelta
from pytz import utc, timezone
import time
import config
import requests

warnings.filterwarnings("ignore")


def send_change_notification(stock, past_nc,past_cf,now_change,now_cf,direction,timezone_ct,alert_i):

        url = "https://maker.ifttt.com/trigger/change_sec/with/key/" + config.IFTTT_api
        if direction == 'up':
            text_in = '[%d] %s %s %.2f%% (%.2f%%), to %s %.2f%% (%.2f%%)'%(alert_i+1, stock,'/',past_cf*100,past_nc*100,
                                                                      '/',now_cf*100,now_change*100)
        else:
            text_in = '[%d] %s %s %.2f%% (%.2f%%), to %s %.2f%% (%.2f%%)'%(alert_i+1,stock,'\\',past_cf*100,past_nc*100,
                                                                      '\\',now_cf*100,now_change*100)

        payload = {"value1": datetime.now(timezone(timezone_ct)).strftime('%I:%M:%S%p'), "value2": text_in}
        print(datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
              text_in)
        with open(config.log_file_path, 'a+') as f:
            f.write(payload["value1"] + ' ' + payload["value2"] + '\n')
        response = requests.request("POST", url, data=payload)
        config.alert_record[(stock, 'change')] = datetime.now(timezone('America/New_York'))

def send_price_notification(stock, past_np,past_pf,now_price,now_pf,direction,timezone_ct,alert_i,money_sign):

        url = "https://maker.ifttt.com/trigger/price_sec/with/key/" + config.IFTTT_api

        if direction == 'up':
            text_in = '[%d] %s %s %.2f%% (%s%.2f), to %s %.2f%% (%s%.2f)'%(alert_i+1, stock,'/',past_pf*100, money_sign,past_np,
                                                                     '/',now_pf*100, money_sign,now_price)
        else:
            text_in = '[%d] %s %s %.2f%% (%s%.2f), to %s %.2f%% (%s%.2f)'%(alert_i+1, stock,'\\',past_pf*100, money_sign,past_np,
                                                                      '\\',now_pf*100, money_sign,now_price)

        payload = {"value1": datetime.now(timezone(timezone_ct)).strftime('%I:%M:%S%p'), "value2": text_in}
        print(datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'),
              text_in)
        with open(config.log_file_path, 'a+') as f:
            f.write(payload["value1"] + ' ' + payload["value2"] + '\n')
        response = requests.request("POST", url, data=payload)
        config.alert_record[(stock, 'price')] = datetime.now(timezone('America/New_York'))

def send_exception_notification(text):
    url = "https://maker.ifttt.com/trigger/notice_exception_phone/with/key/" + config.IFTTT_api
    payload = {"value1": 'second_alert '+text}
    print("exception:%s )"%('second_alert '+text), datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p'))
    with open(config.log_file_path, 'a+') as f:
        f.write(payload["value1"] + datetime.now(timezone('America/New_York')).strftime('%I:%M:%S%p')+'\n')
    response = requests.request("POST", url, data=payload)