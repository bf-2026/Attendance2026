import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "attendance_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "attendance_logs")
