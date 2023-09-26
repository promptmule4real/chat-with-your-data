# ChatSnap User Manual

Welcome to **ChatSnap** – a simplified method to set up and interact with the chatbot application.

## Table of Contents
- [Application Details](#application-details)
- [Getting Started](#1-getting-started)
- [Managing Processes](#2-managing-processes)
- [Viewing Logs](#3-viewing-logs)
- [Requirements](#4-requirements)
- [Ending Your Session](#5-ending-your-session)

---

## Application Details

This repository contains two scripts, `go.sh` and `bot.sh`, which are part of the ChatSnap application. The first script, `go.sh`, manages data uploads and logging, while the second script, `bot.sh`, interacts with a chatbot.

## 1. Getting Started

This guide is intended to help you run the ChatSnap application and manage its processes.

## 2. Managing Processes

The scripts (`go.sh` and `bot.sh`) will first check for any existing processes (`chainlit` and `dataManager.py`) and will stop them before starting fresh instances. This ensures that there are no conflicts with previously running applications.

The `chainlit` process and `dataManager.py` script will then be run in the background. The scripts display the PIDs (Process IDs) for both processes for your reference.

## 3. Viewing Logs

Logs for both processes are stored in a dedicated `ACTIVE_LOGS` directory. Inside, individual log directories are named by the current date and timestamp.

The output and error logs for both `chainlit` and `dataManager.py` can be found within these directories, named as follows:

- `chainlit_output.log` and `chainlit_error.log` for `bot.sh`
- `fileupload_output.log` and `fileupload_error.log` for `go.sh`

To monitor the logs in real-time, you can use commands like `tail -f`:

```bash
tail -f ACTIVE_LOGS/[YOUR_TIMESTAMP]/chainlit_output.log
```

Replace `[YOUR_TIMESTAMP]` with the specific directory timestamp.

## 4. Requirements

Before executing the scripts, ensure you have the necessary dependencies installed:

1. The `chainlit` command must be available in your shell.
2. Python3 should be installed.
3. All the Python libraries mentioned in the `requirements.txt` file should be installed. As this file is already a part of the repository, you can set it up using:

   ```bash
   pip install -r requirements.txt
   ```

## 5. Ending Your Session

When you wish to stop the processes:

1. Use the provided PIDs by the scripts to kill the processes.
   ```bash
   kill [CHAINLIT_PID]
   kill [DATAMANAGER_PID]
   ```
   
---

### ChatSnap Manager Guide

The **ChatSnap Manager** is a user-friendly web portal that facilitates the management of chat data files and embeddings. With a sleek design and easy-to-follow instructions, this guide will walk you through its primary functionalities.

#### **Uploading Files**
1. **Navigate to the Files Upload Card**: This card has a section where you can provide your unique `Upload Key`.
2. **Select Files for Upload**: Click on the "Select a PDF file" input box to browse and select your desired PDF files.
3. **File Constraints**: Ensure that:
   - Each uploaded file is a PDF.
   - The total size of all selected files doesn't exceed 16MB.
4. **Initiate Upload**: Click the "Upload" button. As the upload progresses, you'll observe the operation's progress percentage.

#### **Processing Embeddings**
1. **Go to the Process Embeddings Card**: This card requests your `Process Key`.
2. **Start Processing**: After entering the key, click the "Process Directory" button. This operation may take a while, depending on the data volume. 

#### **Deleting Files**
1. **Head to the Delete Files Card**: Here, you'll provide a `Delete Key`. For security reasons, this key is masked by default but can be viewed by clicking the "Show" text next to the input box.
2. **Choose Files to Delete**: A list of all available files will be displayed with checkboxes. Select the ones you want to remove.
3. **Confirm Deletion**: Click the "Delete Selected" button. You'll be prompted to confirm your choice as this action is irreversible.

#### **Destroying Embeddings**
1. **Access the Destroy Embeddings Card**: This card requires a special `Delete Embeddings Key`.
2. **Begin Destruction**: After providing the key, click the "Destroy Embeddings" button. You'll receive a prompt for confirmation as this action will delete the entire directory, making recovery impossible.

#### **Visual Feedback**:
- **Error Messages**: If there's an issue (e.g., files exceeding the 16MB limit), an error message will be displayed in red.
- **Success Messages**: Successful operations will result in green-colored success messages.
- **Progress Bar**: While uploading or processing, a progress bar displays the percentage of completion.

#### **Starting a Chat**:
To start chatting, use the provided link: [http://app.chatsnap.me](http://app.chatsnap.me).

#### **Technical Details**:
- **Frontend**: The platform utilizes the Materialize CSS framework to ensure a responsive and modern design.
- **Backend**: (Not provided, but likely a server framework that processes the form submissions and manages the files.)

#### **Wrap Up**:
Thank you for choosing **ChatSnap**. Always ensure that you keep your keys confidential and follow the outlined steps for a smooth experience.

---
