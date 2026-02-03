import sqlite3
import datetime
import os

DB_NAME = "attendance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid_uid TEXT NOT NULL,
            employee_name TEXT,
            timestamp TEXT NOT NULL,
            direction TEXT NOT NULL,
            synced BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def log_scan(rfid_uid, employee_name, direction):
    conn = get_db_connection()
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    c.execute('''
        INSERT INTO attendance (rfid_uid, employee_name, timestamp, direction, synced)
        VALUES (?, ?, ?, ?, 0)
    ''', (rfid_uid, employee_name, timestamp, direction))
    conn.commit()
    conn.close()
    return timestamp

def get_last_scan(rfid_uid):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT direction FROM attendance 
        WHERE rfid_uid = ? 
        ORDER BY id DESC 
        LIMIT 1
    ''', (rfid_uid,))
    result = c.fetchone()
    conn.close()
    return result

def get_unsynced_records():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM attendance WHERE synced = 0
    ''')
    records = c.fetchall()
    conn.close()
    return [dict(row) for row in records]

def mark_as_synced(record_ids):
    if not record_ids:
        return
    conn = get_db_connection()
    c = conn.cursor()
    # Use parameter substitution for the IN clause
    placeholders = ','.join('?' * len(record_ids))
    c.execute(f'''
        UPDATE attendance SET synced = 1 WHERE id IN ({placeholders})
    ''', record_ids)
    conn.commit()
    conn.close()

def get_daily_summary(date_str):
    """
    Returns a dictionary of summaries keyed by rfid_uid for a specific date (YYYY-MM-DD).
    Structure:
    {
        'rfid_uid': {
            'first_in': timestamp|None,
            'last_out': timestamp|None,
            'last_action': 'IN'|'OUT'
        }
    }
    """
    conn = get_db_connection()
    c = conn.cursor()
    # Filter by date substring (ISO8601 starts with YYYY-MM-DD)
    search_term = f"{date_str}%"
    c.execute('''
        SELECT rfid_uid, direction, timestamp FROM attendance 
        WHERE timestamp LIKE ? 
        ORDER BY timestamp ASC
    ''', (search_term,))
    rows = c.fetchall()
    conn.close()

    summary = {}
    for row in rows:
        uid = row['rfid_uid']
        direction = row['direction']
        ts = row['timestamp']
        
        if uid not in summary:
            summary[uid] = {
                'first_in': None,
                'last_out': None,
                'last_action': None
            }
        
        # Update State
        summary[uid]['last_action'] = direction
        
        # Determine First IN
        if direction == "IN" and summary[uid]['first_in'] is None:
            summary[uid]['first_in'] = ts
            
        # Determine Last OUT
        if direction == "OUT":
            summary[uid]['last_out'] = ts
            
    return summary

