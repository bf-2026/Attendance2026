#!/bin/bash

# Configuration
BRANCH="main"
SCRIPT="main.py"
VENV_DIR="venv"

echo "Starting Attendance System Launcher..."

while true; do
    echo "----------------------------------------"
    echo "Checking for updates..."
    
    # 1. Pull latest code
    git fetch origin
    git reset --hard origin/$BRANCH
    
    # 2. Check/Activate Virtual Environment
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv $VENV_DIR
    fi
    source $VENV_DIR/bin/activate
    
    # 3. Install Dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt > /dev/null
    fi
    
    # 4. Run Application
    echo "Launching $SCRIPT..."
    python $SCRIPT
    
    # 5. Handle Exit
    EXIT_CODE=$?
    echo "Application stopped with exit code $EXIT_CODE."
    
    if [ $EXIT_CODE -eq 130 ]; then
        # Ctrl+C was likely pressed intentionally if caught by shell (though python handles it too)
        echo "Launcher stopped by user."
        break
    fi
    
    echo "Restarting in 5 seconds..."
    sleep 5
done
