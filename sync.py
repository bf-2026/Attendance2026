import threading
import time
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError, InvalidURI
import config
import database

class SyncEngine:
    def __init__(self, interval=10):
        self.interval = interval
        self.running = False
        self.thread = None
        self.client = None
        self.collection = None
        self.status = "Stopped"
        self._connect()

    def _connect(self):
        try:
            if not config.MONGODB_URI or "mongodb+srv://" not in config.MONGODB_URI:
                # print("Warning: MONGODB_URI not set or invalid. Sync will remain offline.")
                self.status = "Offline (No Config)"
                return

            self.client = pymongo.MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            db = self.client[config.DB_NAME]
            self.collection = db[config.COLLECTION_NAME]
            # Trigger a connection check
            self.client.server_info()
            self.status = "Connected"
        except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError, InvalidURI) as e:
            self.status = "Offline (Connection Failed)"
            # print(f"Sync Init Failed: {e}") # Silent fail on init to avoid spam, retry in loop

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_loop(self):
        while self.running:
            try:
                self.sync_data()
            except Exception as e:
                self.status = f"Error: {str(e)}"
            time.sleep(self.interval)

    def sync_data(self):
        # Reconnect if needed
        if "Offline" in self.status or self.collection is None:
             self._connect()
             if "Offline" in self.status:
                 return # Still offline, retry next loop

        records = database.get_unsynced_records()
        if not records:
            self.status = "Idle (Synced)"
            return

        self.status = f"Syncing {len(records)} records..."
        
        # Prepare for bulk insert or individual inserts
        # For simplicity and ID mapping, we'll do:
        # 1. Insert to Mongo
        # 2. On success of batch, update local
        
        to_insert = []
        ids_to_update = []
        
        for record in records:
            doc = record.copy()
            # Remove local sqlite ID from mongo doc or rename it? 
            # Usually better to drop it or rename to 'local_id'
            doc['local_id'] = doc.pop('id')
            # Remove 'synced' field as it's redundant in cloud
            doc.pop('synced', None)
            to_insert.append(doc)
            ids_to_update.append(record['id'])

        if to_insert:
            try:
                self.collection.insert_many(to_insert)
                database.mark_as_synced(ids_to_update)
                self.status = f"Synced {len(records)} records"
            except (ConnectionFailure, ServerSelectionTimeoutError):
                self.status = "Offline (Sync Failed)"
            except Exception as e:
                self.status = f"Sync Error: {str(e)}"

if __name__ == "__main__":
    # Test
    sync = SyncEngine(interval=2)
    sync.start()
    try:
        while True:
            print(f"Status: {sync.status}")
            time.sleep(2)
    except KeyboardInterrupt:
        sync.stop()
