#!/bin/bash

# Configuration
BRANCH="main"
APP_PROCESS_NAME="main.py"

# Fetch latest info
git fetch origin

# Get hash of local and remote
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/$BRANCH)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "Update detected!"
    echo "Local:  $LOCAL"
    echo "Remote: $REMOTE"
    
    # Kill the running python process
    # The launcher.sh loop will catch this exit and restart the app,
    # pulling the new code in the process.
    echo "Stopping running application to trigger update..."
    pkill -f $APP_PROCESS_NAME
    
    echo "Update trigger sent."
else
    echo "System is up to date."
fi
