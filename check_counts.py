import sqlite3
import os

db_path = "koperasi_brimob.db"
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM members")
        members_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM warehouse")
        warehouse_count = cursor.fetchone()[0]
        
        print(f"Root Database: {db_path}")
        print(f"Members Count: {members_count}")
        print(f"Warehouse Count: {warehouse_count}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
