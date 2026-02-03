import sys
import time
import datetime
import database
import sync
import os

# Configuration
DEBOUNCE_SECONDS = 5
EMPLOYEE_CACHE = {
    "1001": "Alice Johnson",
    "1002": "Bob Smith",
    "1003": "Charlie Brown",
    "1004": "Diana Prince"
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("Initializing System...")
    database.init_db()
    
    # Initialize Sync Engine
    sync_engine = sync.SyncEngine(interval=10)
    sync_engine.start()
    
    scan_cooldowns = {} # {rfid_uid: last_scan_time_float}
    
    print("="*40)
    print("  Pi-RFID Attendance System Ready")
    print("  Type an ID and press ENTER to scan")
    print("  (Ctrl+C to quit)")
    print("="*40)
    
    try:
        while True:
            # 1. Render Dashboard
            clear_screen()
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            summary = database.get_daily_summary(today)
            
            print(f"\n[ Sync Status: {sync_engine.status} ]  Date: {today}\n")
            print(f"{'ID':<6} | {'Name':<20} | {'First In':<10} | {'Last Out':<10} | {'Status':<6}")
            print("-" * 65)
            
            sorted_uids = sorted(EMPLOYEE_CACHE.keys())
            for uid in sorted_uids:
                name = EMPLOYEE_CACHE[uid]
                data = summary.get(uid, {})
                
                # Format Times
                first_in = data.get('first_in')
                last_out = data.get('last_out')
                status = data.get('last_action', '--')
                
                f_in = first_in.split('T')[1][:8] if first_in else "--:--:--"
                l_out = last_out.split('T')[1][:8] if last_out else "--:--:--"
                
                print(f"{uid:<6} | {name:<20} | {f_in:<10} | {l_out:<10} | {status:<6}")
                
            print("-" * 65)
            print("\nType ID and press ENTER to scan > ", end="", flush=True)

            rfid_uid = input().strip()
            
            if not rfid_uid:
                continue
                
            now = time.time()
            
            # Debounce Check
            if rfid_uid in scan_cooldowns:
                if now - scan_cooldowns[rfid_uid] < DEBOUNCE_SECONDS:
                    # Flash warning briefly
                    print(f"\n(!) Cooldown active for {rfid_uid}. Please wait.")
                    time.sleep(1.5)
                    continue
            
            scan_cooldowns[rfid_uid] = now
            
            # Lookup Employee
            name = EMPLOYEE_CACHE.get(rfid_uid)
            if not name:
                name = "Unknown Employee"
                # Optionally add to cache nicely if we want to show them in table dynamically
                # But for now, we only show fixed cache in table or all from summary? 
                # Let's add them to cache temporarily for display if unknown
                EMPLOYEE_CACHE[rfid_uid] = name

            # Determine Direction
            last_record = database.get_last_scan(rfid_uid)
            direction = "IN"
            if last_record and last_record['direction'] == "IN":
                direction = "OUT"
            
            # Log to DB
            database.log_scan(rfid_uid, name, direction)
            
            # The loop repeats, which calls clear_screen() and re-renders the table with new data.
            
    except KeyboardInterrupt:
        print("\nStopping system...")
        sync_engine.stop()
        print("Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
