# CopyBot User Manual

Welcome to **CopyBot** – a simplified method to set up and interact with the chatbot application.

## Table of Contents
- [Application Details](#application-details)
- [Getting Started](#1-getting-started)
- [Execution Details](#2-execution-details)
- [Managing Processes](#3-managing-processes)
- [Viewing Logs](#4-viewing-logs)
- [Requirements](#5-requirements)
- [Ending Your Session](#6-ending-your-session)
- [Tips for an Optimal Experience](#tips-for-an-optimal-experience)

---

## 1. Getting Started

This guide is intended to help you run the **CopyBot** application and manage its processes.

## 2. Execution Details

To start the application:

1. Navigate to the root directory of the project.
2. Run the script using the following command:
   ```bash
   ./startup.sh
   ```

## 3. Managing Processes

The script will first check for any existing processes (`chainlit` and `dataManager.py`) and will stop them before starting fresh instances. This ensures that there are no conflicts with previously running applications.

The `chainlit` process and `dataManager.py` script will then be run in the background. The script will display the PIDs (Process IDs) for both processes for your reference.

## 4. Viewing Logs

Logs for both processes are stored in a dedicated `ACTIVE_LOGS` directory. Inside, individual log directories are named by the current date and timestamp.

The output and error logs for both `chainlit` and `dataManager.py` can be found within these directories, named as follows:

- `chainlit_output.log` and `chainlit_error.log`
- `fileupload_output.log` and `fileupload_error.log`

To monitor the logs in real-time, you can use commands like `tail -f`:

```bash
tail -f ACTIVE_LOGS/[YOUR_TIMESTAMP]/chainlit_output.log
```

Replace `[YOUR_TIMESTAMP]` with the specific directory timestamp.

## 5. Requirements

Before executing the script, ensure you have the necessary dependencies installed:

1. The `chainlit` command must be available in your shell.
2. Python3 should be installed.
3. All the Python libraries mentioned in the `requirements.txt` file should be installed. As this file is already a part of the repository, you can set it up using:
   ```bash
   pip install -r requirements.txt
   ```

## 6. Ending Your Session

When you wish to stop the processes:

1. Use the provided PIDs by the script to kill the processes.
   ```bash
   kill [CHAINLIT_PID]
   kill [DATAMANAGER_PID]
   ```
---

### CopyBot Chat Data Manager Guide

The **CopyBot Chat Data Manager** is a user-friendly web portal that facilitates the management of chat data files and embeddings. With a sleek design and easy-to-follow instructions, this guide will walk you through its primary functionalities.

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
To start chatting, use the provided link: [http://promptstitution.com:8000/](http://promptstitution.com:8000/).

#### **Technical Details**:
- **Frontend**: The platform utilizes the Materialize CSS framework to ensure a responsive and modern design.
- **Backend**: (Not provided, but likely a server framework that processes the form submissions and manages the files.)

#### **Wrap Up**:
Thank you for choosing **CopyBot**. Always ensure that you keep your keys confidential and follow the outlined steps for a smooth experience.

---
