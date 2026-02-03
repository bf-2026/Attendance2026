# Pi-RFID Attendance System (Cloud Sync Edition)

A Python-based attendance tracking system designed for Raspberry Pi (or any PC). It captures employee attendance via RFID (simulated with keyboard input), logs data locally to SQLite for reliability, and synchronizes records to a MongoDB Atlas cloud database in the background.

## 🚀 Features

- **Hybrid Architecture**: Works offline with local SQLite storage and syncs to Cloud (MongoDB) when online.
- **Smart Toggling**: Automatically determines if a scan is 'IN' or 'OUT' based on the employee's last status.
- **Simulated RFID**: Accepts keyboard input to simulate RFID tag scans (great for testing without hardware).
- **Background Sync**: Dedicated thread handles cloud synchronization without blocking the UI.
- **Debouncing**: Prevents accidental double-scans within a configurable timeframe.
- **Terminal Dashboard**: Real-time CLI interface showing daily summaries and sync status.

## 📂 Project Structure

- `main.py`: The entry point. Handles the UI and user input loop.
- `database.py`: Manages SQLite database operations (logging, fetching history).
- `sync.py`: Background runner that pushes unsynced records to MongoDB.
- `config.py`: Loads environment variables.
- `verify_system.py`: A self-test script to validate logic without running the full app.

## 🛠️ Prerequisites

- Python 3.8+
- A MongoDB Atlas account (for cloud sync)

## 📦 Installation

1. **Clone the repository** (or navigate to the project folder)
   ```bash
   cd Attendance2026
   ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    Create a `.env` file in the root directory with your MongoDB credentials:
    ```env
    MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
    DB_NAME=attendance_system
    COLLECTION_NAME=logs
    ```

## 🖥️ Usage

### Running the System
Start the main application:
```bash
python main.py
```
- The dashboard will appear.
- **To Scan**: Type an Employee ID (e.g., `1001`, `1002`) and press **ENTER**.
- The system will log the scan and update the "Status" on the screen.

### Running Tests
To verify the database logic and sync marking mechanisms without the UI:
```bash
python verify_system.py
```

## 👥 Employees (Demo IDs)
The system is pre-configured with these demo IDs for testing:
- `1001`: Alice Johnson
- `1002`: Bob Smith
- `1003`: Charlie Brown
- `1004`: Diana Prince

## 🛡️ License
Open Source.

## 🚀 Deployment on Raspberry Pi

This project includes a **One-Click Setup Script** to automate the entire installation process on a Raspberry Pi.

### 1. Automated Setup (Recommended)
This script will update the system, install dependencies, pull the latest code, and configure auto-start/auto-updates.

1.  **Preparation**: Copy the project files to your Raspberry Pi (or clone the repo).
2.  **Run the Script**:
    ```bash
    chmod +x setup_pi.sh
    ./setup_pi.sh
    ```
3.  **Completion**: The Pi will reboot automatically. Upon restart, the Attendance System will launch.

*Note: If the folder is not a git repository (e.g., copied via USB), the script will automatically initialize it and link it to the official repository to enable future updates.*

### 2. Manual Setup (Alternative)
If you prefer to configure it manually:

1.  **Permissions**:
    ```bash
    chmod +x launcher.sh autoupdate_watchdog.sh
    ```
2.  **Auto-Start**:
    Add the following to your `~/.bashrc`:
    ```bash
    /path/to/attendance-system/launcher.sh
    ```
3.  **Auto-Update**:
    Add the following to your `crontab -e`:
    ```bash
    * * * * * cd /path/to/attendance-system && ./autoupdate_watchdog.sh >> /tmp/attendance_update.log 2>&1
    ```
