# py
import pandas as pd
import os
import configparser

# open the alert market
Markets = ['US']
# Markets = ['CH']
timezones = {'US':'America/New_York', 'CH':'Asia/Shanghai'}
read_in_file = 'ALERT DATA INPUT.xlsx'
analysis_result_directory = 'ALERT RESULT FOLDER'
if not os.path.exists(analysis_result_directory):
    os.makedirs(analysis_result_directory)


configargs = configparser.ConfigParser()
configargs.read('config.ini')
# read the data API
default_FMP_api = configargs['Credentials']['fmp_api']
default_IFTTT_api = configargs['Credentials']['ifttt_api']



# read the parameters
hyper_parameter = pd.read_excel(read_in_file, sheet_name='Parameter', index_col='name')
hyper_parameter_2 = pd.read_excel(read_in_file, sheet_name='Y', index_col='alert')
hyper_parameter_3 = pd.read_excel(read_in_file, sheet_name='N', index_col='alert')

# used to record all the alerts existing
alert_record = {}

# remember the stock class used for different frozen time
total_class = {}
for market in Markets:
    total_class[market + '_total_change_class'] = []
    total_class[market + '_total_price_class'] = []

df_analysis_result = {}

log_file_path = 'log_2nd.txt'

all_alerts_variables = {}


# Define frozen period, IFTTT API, and FMP API with fallbacks to defaults if not specified
frozenperiod = hyper_parameter.loc['frozen_time', 'value']
if pd.isna(frozenperiod):
    frozenperiod = 600
else:
    frozenperiod = int(frozenperiod)

IFTTT_api = hyper_parameter.loc['IFTTT_api', 'value']
if pd.isna(IFTTT_api):
    IFTTT_api = default_IFTTT_api
else:
    IFTTT_api = str(IFTTT_api)

FMP_api = hyper_parameter.loc['FMP_api', 'value']
if pd.isna(FMP_api):
    FMP_api = default_FMP_api
else:
    FMP_api = str(FMP_api)


# Initialize variables for each market and category (CHANGE, PRICE)
# For FMP stocks
for market in Markets:
    # initialize all the variables and assigning the parameters
    all_alerts_variables[market] = {}
    df_analysis_result[market] = {}
    for category in ['CHANGE', 'PRICE']:
        value = hyper_parameter.loc[market + ' FMP ' + category + '_alert_num', 'value']
        if pd.isna(value):
            all_alerts_variables[market][category + '_alert_num'] = 0
        else:
            all_alerts_variables[market][category + '_alert_num'] = int(value)

        for alert_i in range(value):
            all_alerts_variables[market][category + '_Y' + str(alert_i + 1)] = int(hyper_parameter_2.loc[market + ' FMP ' + category, 'Y' + str(alert_i + 1)])
            all_alerts_variables[market][category + '_N' + str(alert_i + 1)] = int(hyper_parameter_3.loc[market + ' FMP ' + category, 'N' + str(alert_i + 1)])
            # use two dataframe to record all the alerts and track the later change
            df_analysis_result[market][category + '_analysis_result_'+ str(alert_i + 1)] = [pd.DataFrame(columns = ['STOCK UP','TIME(t+n)',category+'(t+n)','TIME(t)',category+'(t)','Result']),
                                                                                            pd.DataFrame(columns = ['STOCK DOWN','TIME(t)',category+'(t)','TIME(t+n)',category+'(t+n)','Result'])]

        all_alerts_variables[market][category+'_sheet'] = pd.read_excel(read_in_file, sheet_name=market + ' FMP ' + category, index_col='stock')

