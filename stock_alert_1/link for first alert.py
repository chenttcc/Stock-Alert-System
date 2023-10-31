import paramiko
import os
from tkmacosx import Button
import tkinter as tk
import re
from datetime import datetime,timedelta
import time

remote_server_ip = ''
remote_server_port = ''
remote_server_username = ''
remote_server_password = ''


# open the alert file on the remote server
def open_alert():
    try:
        # Establish an SSH connection
        ssh = paramiko.SSHClient()
        # connect to the remote server
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=remote_server_ip, port=remote_server_port, username=remote_server_password, password=remote_server_password)

        # open terminal
        invoke = ssh.invoke_shell()

        # find the directory
        invoke.send("cd alert_system\n")

        # open virtual environment
        invoke.send("source stock/bin/activate\n")

        # run the alert file on the backend
        invoke.send("nohup python3 -u 'stock_alert_first.py' > test.log 2>&1 &\n")
        invoke.send("exit \n")

        # Collect results from the shell session
        results = ''
        while True:
            result = invoke.recv(1024).decode('utf-8')
            results += result.strip()
            if results[-6:] in 'logout':
                break

        # Close the SSH connection
        ssh.close()
    except Exception as e:
        # If an exception occurs, display the error message
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(e))
    else:
        # If successful, clear the original text and print success message with timestamp
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, datetime.now().strftime('%I:%M:%S%p') + ' open done')

# closing all the running code of this alert
def close_alert():
    try:
        # Establish an SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        ssh.connect(hostname=remote_server_ip, port=remote_server_port, username=remote_server_password, password=remote_server_password)

        # Open a shell session
        invoke = ssh.invoke_shell()

        # Send command to find and kill the process
        invoke.send(
            "ps -ef | grep 'python3 -u stock_alert_first.py'| grep -v grep | awk '{print $2}' | xargs kill -9\n")
        # Send command to exit the shell session
        invoke.send("exit \n")
        # Collect results from the shell session
        results = ''
        while True:
            result = invoke.recv(1024).decode('utf-8')
            results += result.strip()
            if results[-6:] in 'logout':
                break
        # Close the SSH connection
        ssh.close()
    except Exception as e:
        # If an exception occurs, display the error message
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(e))
    else:
        # If successful, clear the original text and print success message with timestamp
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, datetime.now().strftime('%I:%M:%S%p') + ' close done')

# replace the ALERT INFORMATION on remote server
def send_file():
    try:
        # Establish an SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the remote server
        ssh.connect(hostname=remote_server_ip, port=remote_server_port, username=remote_server_password, password=remote_server_password)
        # Open an SFTP session
        sftp = ssh.open_sftp()
        # Upload the file from the local system to the remote server
        sftp.put("ALERT DATA INPUT.xlsx", "/root/alert_system/ALERT DATA INPUT.xlsx")
        # Close the SFTP session
        sftp.close()
        # Close the SSH connection
        ssh.close()
    except Exception as e:
        # If an exception occurs, display the error message
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(e))
    else:
        # If successful, clear the original text and print success message with timestamp
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, datetime.now().strftime('%I:%M:%S%p')+' send done')


# check how many codes running on the remote server
def check_situation():
    try:
        # Establish an SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        ssh.connect(hostname=remote_server_ip, port=remote_server_port, username=remote_server_password, password=remote_server_password)

        # Execute a command on the remote server
        stdin, stdout, stderr = ssh.exec_command("ps aux|grep 'python3 -u stock_alert_first.py'", get_pty=True)

        # Read the output of the command
        result = stdout.read().decode('utf-8')

        # Split the result into individual lines
        all_result = result.split('\r\n')

        # Initialize a counter for running processes
        running_process = 0

        # Loop through each line of the result
        for i in all_result:
            # Use regular expression to check for lines containing the process we're interested in
            if re.search(r'\d{1,2}:\d{1,2} python3 -u stock_alert_first.py', i):
                running_process += 1

        # Close the SSH connection
        ssh.close()
    except Exception as e:
        # If an exception occurs, display the error message
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(e))
    else:
        # If successful, clear the original text and print the number of running processes with a timestamp
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END,
                           datetime.now().strftime('%I:%M:%S%p') + ' %d processes are running' % running_process)

# chech whether the remote ALERT INFORMATION file replaced
def check_file_update():
    try:
        # Establish an SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        ssh.connect(hostname=remote_server_ip, port=remote_server_port, username=remote_server_password, password=remote_server_password)

        # Execute a command on the remote server to get file status
        stdin, stdout, stderr = ssh.exec_command("cd alert_system;stat 'ALERT DATA INPUT.xlsx'", get_pty=True)

        # Read the output of the command
        result = stdout.read().decode('utf-8')

        # Split the result into individual lines
        all_result = result.split('\r\n')

        # Loop through each line of the result
        for i in all_result:
            # Use regular expression to find modification time
            r = re.findall(re.compile('Modify: (.*)'), i)
            if len(r) > 0:
                r = r[0]
                # Convert the modification time to a more readable format
                t = (datetime.fromisoformat(r) - timedelta(hours=4)).strftime('%m-%d %I:%M:%S%p')

        # Close the SSH connection
        ssh.close()
    except Exception as e:
        # If an exception occurs, display the error message
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(e))
    else:
        # If successful, clear the original text and print the last modification time with a timestamp
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, datetime.now().strftime('%I:%M:%S%p') + '\nLast modifying time:%s' % t)


# get the lastest record log the alert code
def get_log():
    try:
        # Establish an SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        ssh.connect(hostname=remote_server_ip, port=remote_server_port, username=remote_server_password, password=remote_server_password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Download the log file from the remote server to the local system
        sftp.get("/root/alert_system/test.log", 'test.log')

        # Close the SFTP session
        sftp.close()

        # Close the SSH connection
        ssh.close()
    except Exception as e:
        # If an exception occurs, display the error message
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(e))
    else:
        # If successful, clear the original text and print success message with timestamp
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, datetime.now().strftime('%I:%M:%S%p')+' get log done')


if __name__ == "__main__" :
    # Set window dimensions
    w = 350
    h = 450

    # Create a Tkinter window
    root = tk.Tk()
    root.geometry("%dx%d" % (w, h))

    # Get screen dimensions
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()

    # Calculate window position
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # Set window title
    root.title('First Alert')

    # Create buttons and associate them with functions
    Button(root, text="Open Alert", command=open_alert).grid(row=0, column=1, padx=10, pady=10)
    Button(root, text="Replace Alert File", command=send_file).grid(row=0, column=2, padx=10, pady=10)
    Button(root, text="Close Alert", command=close_alert).grid(row=0, column=3, padx=10, pady=10)
    Button(root, text="Check Process", command=check_situation).grid(row=1, column=1, padx=10, pady=10)
    Button(root, text="Check File Update", command=check_file_update).grid(row=1, column=2, padx=10, pady=10)
    Button(root, text="Get Latest Log", command=get_log).grid(row=1, column=3, padx=10, pady=10)

    # Create a text widget for displaying results
    result_text = tk.Text(root, height=10, width=40)
    result_text.grid(row=2, column=1, columnspan=3, pady=10)

    # Start the Tkinter event loop
    root.mainloop()

