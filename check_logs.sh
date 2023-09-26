
#!/bin/bash

ACTIVE_LOGS="./ACTIVE_LOGS"

# Function to get the latest directory under ACTIVE_LOGS
get_latest_log_dir() {
    # Find the latest directory based on creation time
    LATEST_DIR=$(find "$ACTIVE_LOGS" -maxdepth 1 -type d | sort -r | head -n 1)
    if [ ! -z "$LATEST_DIR" ]; then
        echo "$LATEST_DIR"
    else
        echo "No directories found under $ACTIVE_LOGS."
        exit 1
    fi
}

# Get the latest log directory
LATEST_DIR=$(get_latest_log_dir)

# Define log files to tail
CHAINLIT_OUTPUT_LOG="$LATEST_DIR/chainlit_output.log"
CHAINLIT_ERROR_LOG="$LATEST_DIR/chainlit_error.log"
FILEUPLOAD_OUTPUT_LOG="$LATEST_DIR/fileupload_output.log"
FILEUPLOAD_ERROR_LOG="$LATEST_DIR/fileupload_error.log"

# Tail log files
echo "Tailing log files from $LATEST_DIR..."
tail -f "$CHAINLIT_OUTPUT_LOG" &
tail -f "$CHAINLIT_ERROR_LOG" &
tail -f "$FILEUPLOAD_OUTPUT_LOG" &
tail -f "$FILEUPLOAD_ERROR_LOG" &

# Wait for all tail commands to exit
wait
