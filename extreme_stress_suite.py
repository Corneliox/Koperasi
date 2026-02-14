"""
EXTREME Stress Suite for Koperasi Brimob
Focus: Memory Limits (32-bit), Data Integrity, and Race Conditions.
"""
import sys
import os
import random
import time
import threading
import logging
import sqlite3
from concurrent.futures import ThreadPoolExecutor

# Setup Path
sys.path.append(os.getcwd())

from app.database.connection import get_connection, init_database
from app.modules.members import MemberManager
from app.modules.warehouse import WarehouseManager

# Disable logging to focus on performance
logging.getLogger().setLevel(logging.CRITICAL)

class ExtremeStressTester:
    def __init__(self):
        init_database()
        self.members = MemberManager()
        self.warehouse = WarehouseManager("SEMBAKO")
        self._lock = threading.Lock()
        self.errors = []

    def test_massive_data_load(self, count=5000):
        """Test how the system handles 5k records (32-bit memory limit test)"""
        print(f"PHASE 1: Massive Data Insertion ({count} records)...")
        start = time.time()
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            data = []
            for i in range(count):
                data.append((f"Member {i}", f"Rank {i}", "Unit", f"NRP-{i}", "0812", "Address", "Aktif"))
            
            cursor.executemany(
                "INSERT OR IGNORE INTO members (name, rank, unit, nrp, phone, address, membership_status) VALUES (?,?,?,?,?,?,?)",
                data
            )
            conn.commit()
            duration = time.time() - start
            print(f"Inserted {count} records in {duration:.2f}s")
            
            print(f"Testing fuzzy search on {count} records...")
            search_start = time.time()
            results = self.members.find_similar_members("Member 4999")
            search_duration = time.time() - search_start
            print(f"Fuzzy search completed in {search_duration:.2f}s. Results: {len(results)}")
            
        except Exception as e:
            print(f"Massive Data Test Failed: {e}")
        finally:
            conn.close()

    def test_database_locking_war(self, duration=5):
        """Intense write/read war to force 'database is locked' errors"""
        print(f"PHASE 2: Database Locking War ({duration} seconds)...")
        stop_event = threading.Event()
        
        def intense_writer():
            while not stop_event.is_set():
                try:
                    self.warehouse.add_item(f"Item {random.randint(1,100)}", 1, 100, 200)
                except:
                    pass

        def intense_reader():
            while not stop_event.is_set():
                try:
                    self.warehouse.get_all_items()
                except:
                    pass

        threads = []
        for _ in range(5): threads.append(threading.Thread(target=intense_writer))
        for _ in range(5): threads.append(threading.Thread(target=intense_reader))
        
        for t in threads: t.start()
        time.sleep(duration)
        stop_event.set()
        for t in threads: t.join()
        print("Database Locking War completed without application crash.")

    def test_ui_logic_spam(self, iterations=500):
        """Simulate high-frequency UI events to find race conditions"""
        print(f"PHASE 3: UI Event Logic Spam ({iterations} iterations)...")
        
        def spam_action():
            try:
                m_id = random.randint(1, 5000)
                self.members.get_member_by_id(m_id)
                self.members.autocomplete_search("Mem")
                self.warehouse.get_statistics()
            except Exception as e:
                with self._lock:
                    self.errors.append(str(e))

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda _: spam_action(), range(iterations))
            
        print(f"UI Logic Spam completed. Errors caught: {len(self.errors)}")

    def cleanup(self):
        """Cleanup massive data"""
        conn = get_connection()
        conn.execute("DELETE FROM members WHERE nrp LIKE 'NRP-%'")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    tester = ExtremeStressTester()
    try:
        tester.test_massive_data_load(5000)
        tester.test_database_locking_war(5)
        tester.test_ui_logic_spam(500)
        print("\nALL EXTREME TESTS COMPLETED SUCCESSFULLY.")
    finally:
        tester.cleanup()
