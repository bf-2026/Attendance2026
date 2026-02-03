The Prompt
Role: Senior IoT Python Developer

Task: Develop a Raspberry Pi-based Attendance System based on the following specifications.

1. Core Functionality
Input Mechanism: Create a script that listens for keyboard-style input (simulating an RFID reader) where a user enters a numeric ID and presses "Enter".

Local Logging: Every scan must be saved to a local SQLite3 database (attendance.db).

Logic: Automatically toggle the direction ('IN' or 'OUT') based on the last entry for that specific rfid_uid. If no previous record exists, default to 'IN'.

2. Database & Schema
Implement the local SQLite3 schema:

id (Primary Key), rfid_uid (Text), employee_name (Text), timestamp (ISO8601), direction (Text), and synced (Boolean, default 0).

3. Synchronization Engine
Develop a background sync process (using threading or a separate schedule) that looks for records where synced=0.

Push these records to a MongoDB Atlas cluster using pymongo.

Upon a successful cloud write, update the local record to synced=1.

4. Technical Constraints & UI
Security: Use python-dotenv for MongoDB URI and API credentials.

UI: Provide a simple terminal application to display the employees and their scans and a "Sync Status" indicator.

Code Style: Modular design. Separate the database operations, the input listener, and the sync logic into distinct functions or classes.

5. Error Handling
Handle "Offline Mode": If the MongoDB connection fails, the app should continue to log locally without crashing.

💡 Pro-Tips for Implementation
When you run this prompt, you might want to consider these architectural nuances:

The "Keyboard" Trap: Most RFID USB readers act as HID (Human Interface Devices).

Debouncing: RFID cards can sometimes trigger multiple reads if held near the scanner. Ensure your code has a "cooldown" (e.g., 5 seconds) before the same ID can be scanned again.

## 🚀 Project Overview

**Name:** Pi-RFID Attendance System (Cloud Sync Edition)
**Hardware:** Raspberry Pi
**Primary Goal:** Capture employee attendance locally and synchronize data to a cloud database for remote monitoring and reporting.

---

## 🏗 System Architecture

### 1. Hardware Layer

* **Processing:** Raspberry Pi (Python 3.x).

### 2. Data Layer

* **Local DB:** SQLite3 (`attendance.db`).
* *Purpose:* Low-latency logging, offline persistence.


* **Cloud DB:** MongoDB Atlas
* *Purpose:* Centralized reporting, multi-device aggregation.



### 3. Sync Logic

* **Pattern:** Transactional Queue.
* **Mechanism:** Periodic background process checking for `synced=0` flags.

---

## 📊 Database Schema (Local)

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary Key (Auto-increment) |
| `rfid_uid` | TEXT | Unique ID from the RFID tag |
| `employee_name` | TEXT | Linked name (cached locally) |
| `timestamp` | DATETIME | ISO8601 string of scan time |
| `direction` | TEXT | 'IN' or 'OUT' |
| **`synced`** | **BOOLEAN** | **0 for local only, 1 for pushed to cloud** |

---

## 💻 Technical Requirements

### Dependencies

* `sqlite3` (Local storage)
* `requests` (API communication)

---

## 📝 Usage Notes for AI

* **Coding Style:** Clean, modular Python with docstrings.
* **Error Handling:** Graceful failure if the Cloud API is unreachable.
* **Security:** Never hardcode API keys; use `python-dotenv`.
