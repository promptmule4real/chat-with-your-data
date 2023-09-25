#!/bin/bash

# Directory to store the active logs
ACTIVE_LOGS="./ACTIVE_LOGS"

# Function to get the PID of running processes
get_pids() {
    DATAMANAGER_PID=$(pgrep -f "python3 dataManager.py")
}

# Function to kill running processes
kill_processes() {
    if [ ! -z "$DATAMANAGER_PID" ]; then
        kill $DATAMANAGER_PID
        echo "Stopped running dataManager.py process (PID: $DATAMANAGER_PID)"
    fi
}

# Function to create log directory with date and seconds format
create_log_dir() {
    LOG_DIR="$ACTIVE_LOGS/$(date +%F)_$(date +%s)"
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
    fi
    echo "Logs will be created in $LOG_DIR."
}

# Get the PIDs of any running processes
get_pids

# If either process is running, stop them
kill_processes

# Create log directory with date and seconds format
create_log_dir

# Start the dataManager.py process in the background and direct logs to the LOG_DIR directory
nohup python3 dataManager.py > "$LOG_DIR/fileupload_output.log" 2> "$LOG_DIR/fileupload_error.log" &

# Get the PID of the last background process (dataManager.py process in this case)
DATAMANAGER_PID=$!

# Print the PID so you can use it to manage the processes (like killing them later if necessary)
echo "dataManager process started with PID: $DATAMANAGER_PID"

# Print a message indicating where the logs can be found
echo "dataManager output is being logged to '$LOG_DIR/fileupload_output.log' and errors to '$LOG_DIR/fileupload_error.log'."

# Define the current date, time, and username
CURRENT_DATE_TIME=$(date "+%Y-%m-%d %H:%M:%S")
USERNAME=$(whoami)

# Define the entry for overwriting lines and for appending as a table row
ENTRY="### Application Start Log\n- Application Start Date and Time: $CURRENT_DATE_TIME\n- Username: $USERNAME\n- Log Store: $LOG_DIR"
TABLE_ENTRY="| $CURRENT_DATE_TIME | $USERNAME | $LOG_DIR |"

# Append the data as a new row in the table at the end of the relevant markdown file (replace yourMarkdown.md with actual file name)
echo -e "$TABLE_ENTRY" >> ./yourMarkdown.md

# Exit the script
exit 0
