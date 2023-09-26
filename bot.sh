#!/bin/bash

# Directory to store the active logs
ACTIVE_LOGS="./ACTIVE_LOGS"

# Function to get the PID of running chainlit process
get_pid() {
    CHAINLIT_PID=$(pgrep -f "chainlit run deploy.py -w")
}

# Function to kill running chainlit process
kill_process() {
    if [ ! -z "$CHAINLIT_PID" ]; then
        kill $CHAINLIT_PID
        echo "Stopped running chainlit process (PID: $CHAINLIT_PID)"
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

# Get the PID of any running chainlit process
get_pid

# If chainlit process is running, stop it
kill_process

# Create log directory with date and seconds format
create_log_dir

# Check if "chainlit" command is available
if ! command -v chainlit &> /dev/null
then
    echo "chainlit command not found. Please install it first."
    exit 1
fi

# Start the chainlit process in the background and direct logs to the LOG_DIR directory
nohup chainlit run deploy.py -w > "$LOG_DIR/chainlit_output.log" 2> "$LOG_DIR/chainlit_error.log" &

# Get the PID of the last background process (chainlit process in this case)
CHAINLIT_PID=$!

# Print the PID so you can use it to manage the processes (like killing them later if necessary)
echo "Chainlit process started with PID: $CHAINLIT_PID"

# Print a message indicating where the logs can be found
echo "Chainlit output is being logged to '$LOG_DIR/chainlit_output.log' and errors to '$LOG_DIR/chainlit_error.log'."

# Define the current date, time, and username
CURRENT_DATE_TIME=$(date "+%Y-%m-%d %H:%M:%S")
USERNAME=$(whoami)

# Define the entry for overwriting lines and for appending as a table row
ENTRY="### Application Start Log\n- Application Start Date and Time: $CURRENT_DATE_TIME\n- Username: $USERNAME\n- Log Store: $LOG_DIR"
TABLE_ENTRY="| $CURRENT_DATE_TIME | $USERNAME | $LOG_DIR |"

# Overwrite lines 3-6 in the chainlit.md file
sed -i "3,6c\\
$ENTRY
" ./chainlit.md

# Append the data as a new row in the table at the end of the chainlit.md file
echo -e "$TABLE_ENTRY" >> ./chainlit.md

# Exit the script
exit 0
