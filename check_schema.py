import sqlite3
import os

db_path = "backend/openpaw_v2.db"
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='conversations'")
    print(cursor.fetchone()[0])
    conn.close()
