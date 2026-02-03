import database
import os
import time
import shutil

# Setup clean test environment
TEST_DB = "test_attendance.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

# Monkey patch database.DB_NAME
original_db_name = database.DB_NAME
database.DB_NAME = TEST_DB

def run_verification():
    print("Running System Verification...")
    
    # 1. Test Init
    print("[1] Initializing Database...")
    database.init_db()
    if os.path.exists(TEST_DB):
        print(" -> PASS: Database created.")
    else:
        print(" -> FAIL: Database not created.")
        return

    # 2. Test Logging
    print("\n[2] Testing Logging...")
    uid = "TEST_USER_1"
    name = "Test User"
    
    # First Scan (IN)
    last_scan = database.get_last_scan(uid)
    direction = "IN"
    if last_scan and last_scan['direction'] == "IN":
        direction = "OUT"
    
    database.log_scan(uid, name, direction)
    print(f" -> Logged {direction} for {uid}")
    
    # Verify
    last = database.get_last_scan(uid)
    if last['direction'] == "IN":
        print(" -> PASS: Direction recorded as IN")
    else:
        print(f" -> FAIL: Expected IN, got {last['direction']}")

    # Second Scan (OUT)
    last_scan = database.get_last_scan(uid)
    direction = "IN"
    if last_scan and last_scan['direction'] == "IN":
        direction = "OUT"
    
    database.log_scan(uid, name, direction)
    print(f" -> Logged {direction} for {uid}")
    
    last = database.get_last_scan(uid)
    if last['direction'] == "OUT":
        print(" -> PASS: Direction toggled to OUT")
    else:
        print(f" -> FAIL: Expected OUT, got {last['direction']}")

    # 3. Test Sync status
    print("\n[3] Testing Sync Logic (Local)")
    unsynced = database.get_unsynced_records()
    print(f" -> Found {len(unsynced)} unsynced records.")
    if len(unsynced) == 2:
        print(" -> PASS: Correct number of unsynced records.")
    else:
        print(f" -> FAIL: Expected 2, got {len(unsynced)}")

    # Mark synced
    ids = [r['id'] for r in unsynced]
    database.mark_as_synced(ids)
    
    unsynced_after = database.get_unsynced_records()
    if len(unsynced_after) == 0:
        print(" -> PASS: Records marked as synced correctly.")
    else:
        print(f" -> FAIL: Still have {len(unsynced_after)} unsynced records.")

    # Cleanup
    database.DB_NAME = original_db_name
    # os.remove(TEST_DB) # Keep for inspection if needed
    print("\nVerification Complete.")

if __name__ == "__main__":
    run_verification()
