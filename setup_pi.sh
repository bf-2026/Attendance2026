#!/bin/bash

echo "=========================================="
echo "   Raspberry Pi Attendance System Setup   "
echo "=========================================="

# 1. Update System
echo "[1/5] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# 2. Install Dependencies
echo "[2/5] Installing dependencies (git, python3-venv)..."
sudo apt install -y git python3-venv python3-pip

# 3. Setup Project Code
echo "[3/5] Setting up Project Code..."

# Check if we are in a git repo
if [ -d ".git" ]; then
    echo "  - Git repository detected. Pulling changes..."
    git pull origin main || echo "  - Warning: Git pull failed. Continuing..."
else
    REPO_URL="https://github.com/bf-2026/Attendance2026.git"
    echo "  - Not a git repository."
    echo "  - Initializing from default: $REPO_URL"
    
    echo "  - Initializing git..."
    git init -b main
    git remote add origin "$REPO_URL"
    
    echo "  - Fetching code..."
    git fetch origin
    
    echo "  - Resetting to match remote..."
    git reset --hard origin/main
    git branch --set-upstream-to=origin/main main
fi

# 4. Set Permissions
echo "[4/5] Setting executable permissions..."
chmod +x launcher.sh autoupdate_watchdog.sh

# 5. Configure Auto-Start
echo "[5/5] Configuring auto-start..."

# Path to the current directory
APP_DIR=$(pwd)
LAUNCHER_PATH="$APP_DIR/launcher.sh"
WATCHDOG_PATH="$APP_DIR/autoupdate_watchdog.sh"

# 5a. Add to .bashrc for auto-start on login
BASHRC="$HOME/.bashrc"
if grep -q "Attendance System" "$BASHRC"; then
    echo "  - Auto-start already configured in .bashrc"
else
    echo "  - Adding auto-start to $BASHRC"
    echo "" >> "$BASHRC"
    echo "# Auto-start Attendance System" >> "$BASHRC"
    echo "$LAUNCHER_PATH" >> "$BASHRC"
fi

# 5b. Add Cron Job for Watchdog (every minute)
# We use a temporary file to manipulate the crontab
CRON_CMD="* * * * * cd $APP_DIR && ./autoupdate_watchdog.sh >> /tmp/attendance_update.log 2>&1"
CRON_FILE="/tmp/cron_dump"

crontab -l 2>/dev/null > "$CRON_FILE" || true

if grep -q "autoupdate_watchdog.sh" "$CRON_FILE"; then
    echo "  - Watchdog cron job already exists"
else
    echo "  - Adding watchdog cron job"
    echo "$CRON_CMD" >> "$CRON_FILE"
    crontab "$CRON_FILE"
fi
rm "$CRON_FILE"

echo "=========================================="
echo "   Setup Complete!"
echo "   Rebooting in 5 seconds..."
echo "=========================================="
sleep 5
sudo reboot
