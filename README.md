# Goal
Using python to moniter the given stock price change, alert when the threshold is reached. Collecting real-time data through FMP API and sending message by IFTTT API.

## stock_alert_first
Retrieve stock names, thresholds, and API keys from the ALERT DATA INPUT.xlsx file. Proceed to fetch real-time data through the FMP API. Next, establish the alert criteria, which include monitoring stock price and percentage change. Then, scan for stocks that meet the specified criteria. If a match is found, instantly notify the user through the IFTTT API, enabling notifications on their mobile devices. The alert parameters can be adjusted based on the following categories:

### 1. Criteria 
For stock price alerts (LB denotes upward stock and SS denotes downward stock):
  - LB:
    - Price between p and p*(1+w)
    - Price between p*(1+w) and p*(1+2w)
    - Price greater than or equal to p*(1+2w)
  - SS:
    - Price between p and p*(1-w)
    - Price between p*(1-w) and p*(1-2w)
    - Price less than or equal to p*(1-2w)

* For stock price change alerts (LB denotes upward stock and SS denotes downward stock):
  - LB:
    - Change between c and c*(1+w)
    - Change between c*(1+w) and c*(1+2w)
    - Change greater than or equal to c*(1+2w)
  - SS:
    - Change between c and c*(1-w)
    - Change between c*(1-w) and c*(1-2w)
    - Change less than or equal to c*(1-2w). 
### 2. link for first alert.py
I designed a user interface using tkinter to facilitate user control over the program running on a remote server. It includes functions:
* running monitoring code
* stopping monitoring code
* checking the update status of the ALERT DATA INPUT file
* verifying if a program is currently running
* replacing the ALERT DATA INPUT file.


## stock_alert_second
The Python directory in this project contains scripts and modules for implementing a real-time stock alert system. The system monitors stock changes and prices, generating alerts based on predefined criteria. Below is an overview of the main functions and how they are realized.
* The alert system operates in two monitoring periods, when a stock triggers the criteria of the first monitoring period, the system initiates the second period of observation. Only when both periods meet their respective thresholds does the system generate alerts, signaling potential significant changes in stock behavior. 
* This approach is particularly valuable for identifying stocks that maintain longer-term trends, whether they are upward or downward. 
* The system serves as a tool for recording post-alert stock behavior, facilitating the assessment of the accuracy of the alert time points. 
* Users can adjust criteria, durations, and post-alert periods for both monitoring periods. 
* The system's scalability enables it to seamlessly extend its monitoring capabilities across multiple trade markets, enhancing its applicability and adaptability to diverse trading environments(trading time).



### 1. **Configuration (`config.py`):**
   - Defines configuration parameters such as markets, timezones, API keys, and alert data input.
   - Reads API keys from a configuration file (`config.ini`).
   - Loads parameters from an Excel file (`ALERT DATA INPUT.xlsx`).
   - Manages alert records and classifies stocks based on frozen time.

### 2. **Data Retrieval (`data_retrieval.py`):**
   - Retrieves real-time stock data using the Financial Modeling Prep API.
   - Handles HTTP errors and ensures the existence of stocks.
   - Converts data into suitable formats for further analysis.

### 3. **Error Handling (`errors.py`):**
   - Defines custom exceptions (`stocknonexist`, `inputerror`) for error handling in the application.

### 4. **Main Execution (`main.py`):**
   - Orchestrates the execution of market threads and manages cleanup functions.
   - Handles file management to keep the latest analysis results.
   - Utilizes multi-threading for parallel processing of multiple markets.

### 5. **Main Execution (`main_execution.py`):**
   - Implements the `MarketThread` class for each market to run threaded tasks.
   - Computes sleep time based on market hours.
   - Retrieves stock data and performs alert checks for both price and change.

### 6. **Utility Functions (`utility_functions.py`):**
   - Sends various types of notifications (change, price, exception) using the IFTTT service.
   - Logs notifications and exceptions to a log file.

### 7. **Alert Classes (`alert_classes.py`):**
   - Defines classes (`CheckIsAlertChange`, `CheckIsAlertPrice`) for checking if an alert condition is met.
   - Contains methods for processing alerts based on predefined parameters.

### 8. **Alert Processing (`alert_processing.py`):**
   - Implements functions (`find_change_alert`, `find_price_alert`) for processing change and price alerts.
   - Adds new data to the analysis results for tracking.
