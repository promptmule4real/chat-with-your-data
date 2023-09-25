#!/bin/bash

# SSH to the remote host
ssh -i ~/.ssh/id_rsa.pem azureuser@172.178.80.213

# Change to the cs directory
cd cs

# List contents in reverse order
ls -r

# Create a file named criticalfiles using Vim
vim criticalfiles

# Navigate up one directory level
cd ..

# Create a directory named cs
mkdir cs

# Initialize a Git repository in the cs directory
cd cs
git init

# Clone the GitHub repository into the cs directory
git clone https://github.com/promptmule4real/chat-with-your-data.git

# Create symbolic links
ln -s chat-with-your-data/deploy.py deploy.py
ln -s chat-with-your-data/chainlit.md chainlit.md
ln -s chat-with-your-data/startup.sh startup.sh
ln -s chat-with-your-data/requirements.txt requirements.txt
ln -s chat-with-your-data/dataManager.py dataManager.py

# Create additional directories
mkdir ACTIVE_LOGS
mkdir LLM

# Copy files from cs/LLM to cs/LLM
cp ../cs/LLM/* LLM

# List contents of the cs directory
ls

# Exit the SSH session
exit
