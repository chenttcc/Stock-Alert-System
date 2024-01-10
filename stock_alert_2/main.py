import pandas as pd
from utility_functions import send_change_notification, send_price_notification, send_exception_notification
import warnings
import config
from main_execution import MarketThread
import time
from errors import stocknonexist
import numpy as np
from datetime import datetime, timedelta
from pytz import utc, timezone

warnings.filterwarnings("ignore")

import signal
import sys
import os
import glob

def keep_latest_files(directory_path, file_extension, num_files_to_keep):
    # Get the list of Excel files in the directory
    excel_files = glob.glob(os.path.join(directory_path, f'*.{file_extension}'))

    # Sort the files based on creation time
    sorted_excel_files = sorted(excel_files, key=os.path.getctime, reverse=True)

    # Keep the latest four files
    files_to_keep = sorted_excel_files[:num_files_to_keep]

    # Delete the older files
    for file in sorted_excel_files[num_files_to_keep:]:
        os.remove(file)
        print(f"Deleted file: {file}")

# Everytime the alert system is closed, compute and output all the alerted stocks
def cleanup_function(signum, frame):
    # Your cleanup code or any function you want to run before closing

    # Specify the directory path, file extension, and the number of files to keep
    file_extension = 'xlsx'
    num_files_to_keep = 4

    # Call the function to keep the latest four Excel files
    keep_latest_files(config.analysis_result_directory, file_extension, num_files_to_keep)

    now_time = datetime.now(timezone('America/New_York')).strftime('%I_%M_%S%p')
    # Create ExcelWriter object
    writer = pd.ExcelWriter(config.analysis_result_directory+'/ALERT RESULT ANALYSIS_'+now_time+'.xlsx', engine='xlsxwriter')

    for s in all_threads:
        change_analysis = pd.DataFrame()
        price_analysis = pd.DataFrame()

        for alert_i in range(s.change_alert_num):
            alert_i_change_up, alert_i_change_down = config.df_analysis_result[s.name]['CHANGE_analysis_result_' + str(alert_i + 1)]
            # ['STOCK UP', 'TIME(t+n)', 'CHANGE(t+n)', 'TIME(t)', 'CHANGE(t)', 'Result']

            alert_i_change_up['Result'] = alert_i_change_up['CHANGE(t)'] - alert_i_change_up['CHANGE(t+n)']
            alert_i_change_up = alert_i_change_up.dropna()

            alert_i_change_down['Result'] = alert_i_change_down['CHANGE(t+n)'] - alert_i_change_down['CHANGE(t)']
            alert_i_change_down = alert_i_change_down.dropna()

            average_value_up, average_value_down = alert_i_change_up['Result'].mean(), alert_i_change_down['Result'].mean()
            alert_i_change_up = alert_i_change_up.append(
                pd.Series({'Result': average_value_up, 'STOCK UP': 'AVERAGE'}, name=len(alert_i_change_up)))
            alert_i_change_down = alert_i_change_down.append(
                pd.Series({'Result': average_value_down, 'STOCK DOWN': 'AVERAGE'}, name=len(alert_i_change_down)))

            alert_i_change_up[['CHANGE(t+n)', 'CHANGE(t)', 'Result']] = alert_i_change_up[
                ['CHANGE(t+n)', 'CHANGE(t)', 'Result']].apply(lambda x: x * 100).applymap(lambda x: '{:.2f}%'.format(x) if pd.notnull(x) else np.nan)
            alert_i_change_down[['CHANGE(t)', 'CHANGE(t+n)', 'Result']] = alert_i_change_down[
                ['CHANGE(t)', 'CHANGE(t+n)', 'Result']].apply(lambda x: x * 100).applymap(lambda x: '{:.2f}%'.format(x) if pd.notnull(x) else np.nan)


            result_df_alert_i = pd.concat([alert_i_change_up, alert_i_change_down], axis=1)

            interbal_name = pd.DataFrame(result_df_alert_i.columns).T
            result_df_alert_i.columns = list(range(0, result_df_alert_i.shape[1]))
            result_df_alert_i = pd.concat(
                [pd.DataFrame(['ALERT['+str(alert_i+1)+']'] + [np.nan] * 11).T, interbal_name, result_df_alert_i], axis=0,
                ignore_index=True)

            change_analysis = pd.concat([change_analysis,result_df_alert_i], axis = 1)


        for alert_i in range(s.price_alert_num):
            alert_i_price_up, alert_i_price_down = config.df_analysis_result[s.name][
                'PRICE_analysis_result_' + str(alert_i + 1)]
            # ['STOCK UP', 'TIME(t+n)', 'PRICE(t+n)', 'TIME(t)', 'PRICE(t)', 'Result']


            alert_i_price_up['Result'] = alert_i_price_up['PRICE(t)']/alert_i_price_up['PRICE(t+n)'] - 1
            alert_i_price_up = alert_i_price_up.dropna()
            alert_i_price_up[['PRICE(t+n)', 'PRICE(t)']] = alert_i_price_up[
                ['PRICE(t+n)', 'PRICE(t)']].round(2)

            alert_i_price_down['Result'] = alert_i_price_down['PRICE(t+n)']/alert_i_price_down['PRICE(t)'] - 1
            alert_i_price_down = alert_i_price_down.dropna()
            alert_i_price_down[['PRICE(t)', 'PRICE(t+n)']] = alert_i_price_down[
                ['PRICE(t)', 'PRICE(t+n)']].round(2)

            average_value_up, average_value_down = alert_i_price_up['Result'].mean(), alert_i_price_down[
                'Result'].mean()
            alert_i_price_up = alert_i_price_up.append(
                pd.Series({'Result': average_value_up, 'STOCK UP': 'AVERAGE'}, name=len(alert_i_price_up)))
            alert_i_price_down = alert_i_price_down.append(
                pd.Series({'Result': average_value_down, 'STOCK DOWN': 'AVERAGE'}, name=len(alert_i_price_down)))

            alert_i_price_up['Result'] = alert_i_price_up['Result'].apply(lambda x: x * 100).apply(lambda x: '{:.2f}%'.format(x) if pd.notnull(x)  else np.nan)
            alert_i_price_down['Result'] = alert_i_price_down['Result'].apply(lambda x: x * 100).apply(lambda x: '{:.2f}%'.format(x) if pd.notnull(x)  else np.nan)

            result_df_alert_i = pd.concat([alert_i_price_up, alert_i_price_down], axis=1)

            interbal_name = pd.DataFrame(result_df_alert_i.columns).T
            result_df_alert_i.columns = list(range(0, result_df_alert_i.shape[1]))
            result_df_alert_i = pd.concat(
                [pd.DataFrame(['ALERT['+str(alert_i+1)+']'] + [np.nan] * 11).T, interbal_name, result_df_alert_i], axis=0,
                ignore_index=True)

            price_analysis = pd.concat([price_analysis, result_df_alert_i], axis=1)

        if change_analysis.shape[0] > 0:
            change_analysis.to_excel(writer, sheet_name=s.name+' CHANGE RESULT', index=False, header=False)
        if price_analysis.shape[0] > 0:
            price_analysis.to_excel(writer, sheet_name=s.name+' PRICE RESULT', index=False, header=False)
        # Close writer
    writer.close()


    print("Cleaning up before closing...")
    os._exit(1)

# Register the cleanup function for SIGTERM

if __name__ == "__main__":

    signal.signal(signal.SIGTERM, cleanup_function)

    while True:
        try:
            all_threads = []
            for market in config.Markets:
                all_threads.append(MarketThread(market,config.timezones[market],config.all_alerts_variables[market]))


            for s in all_threads:
                s.start()


            for s in all_threads:
                s.join()

        except FileNotFoundError as e:
            print(str(e))
            send_exception_notification('FileName is Wrong:' + str(e))
            time.sleep(30)

        except ValueError as e:
            print(str(e))
            send_exception_notification(str(e)+' exit code!!')
            time.sleep(30)
            exit()
        except stocknonexist as e:
            print(str(e))
            send_exception_notification(str(e))
            time.sleep(30)
        except KeyError as e:
            print(str(e))
            send_exception_notification(str(e)+' exit code!!')
            exit()
        except Exception as e:
            print(str(e))
            send_exception_notification('Unknown problem:' + str(e))
            time.sleep(30)
