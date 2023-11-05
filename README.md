## Goal
Using python to moniter the given stock price change, alert when the threshold is reached. Collecting real-time data through FMP API and sending message by IFTTT API.

## Composition
1. stock_alert_first.py
* Retrieve stock names, thresholds, and API keys from the ALERT DATA INPUT.xlsx file. Proceed to fetch real-time data through the FMP API. Next, establish the alert criteria, which include monitoring stock price and percentage change. Then, scan for stocks that meet the specified criteria. If a match is found, instantly notify the user through the IFTTT API, enabling notifications on their mobile devices. The alert parameters can be adjusted based on the following categories:

* For stock price alerts (LB denotes upward stock and SS denotes downward stock):
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
2. link for first alert.py
I designed a user interface using tkinter to facilitate user control over the program running on a remote server. It includes functions:
* running monitoring code
* stopping monitoring code
* checking the update status of the ALERT DATA INPUT file
* verifying if a program is currently running
* replacing the ALERT DATA INPUT file.