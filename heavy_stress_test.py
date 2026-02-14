"""
HEAVY Stress Test for Koperasi Brimob
Simulates high load, concurrent access, and extreme data edge cases.
"""
import sys
import os
import threading
import random
import time
import logging
from concurrent.futures import ThreadPoolExecutor

# Ensure app modules can be imported
sys.path.append(os.getcwd())

from app.database.connection import init_database
from app.modules.warehouse import WarehouseManager
from app.modules.members import MemberManager
from app.modules.loans import LoanManager

# Silence standard logging
logging.getLogger('app.utils.audit_log').setLevel(logging.CRITICAL)

class HeavyStressTester:
    def __init__(self):
        init_database()
        self.warehouse = WarehouseManager("TAKTIKAL")
        self.members = MemberManager()
        self.loans = LoanManager()
        self.errors = []
        self.success_count = 0
        self.fail_count = 0
        self._lock = threading.Lock()

    def random_string(self, length=10):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(chars) for _ in range(length))

    def simulate_user_action(self, user_id):
        actions = ['add_item', 'add_member', 'create_loan', 'sell_item', 'query']
        action = random.choice(actions)
        
        try:
            if action == 'add_item':
                self.warehouse.add_item(
                    name=random.choice([None, "", self.random_string(50)]),
                    stock=random.choice([None, -99, 999999999]),
                    buy_price=random.choice([0.01, 1000000.0]),
                    sell_price=random.choice([None, -1, 0])
                )
            elif action == 'add_member':
                self.members.add_member(
                    name=self.random_string(20),
                    nrp=random.choice([None, self.random_string(10)])
                )
            elif action == 'create_loan':
                self.loans.create_loan(
                    member_id=random.randint(1, 10),
                    amount=random.choice([None, 0, -50000, 1000000.0]),
                    interest_rate=random.choice([0, 10, -1]),
                    duration_months=random.choice([0, 12, -12])
                )
            elif action == 'sell_item':
                self.warehouse.sell_item(
                    item_id=random.randint(1, 10),
                    qty=random.randint(-10, 100)
                )
            elif action == 'query':
                self.members.autocomplete_search(self.random_string(2))
            
            with self._lock:
                self.success_count += 1
        except Exception as e:
            with self._lock:
                self.errors.append(f"CRASH in {action}: {str(e)}")
                self.fail_count += 1

    def run_heavy_test(self, total_tasks=1000, workers=20):
        print(f"Starting HEAVY STRESS TEST: {total_tasks} tasks with {workers} workers...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(self.simulate_user_action, range(total_tasks))
            
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*50)
        print("📊 HEAVY STRESS TEST RESULTS")
        print("="*50)
        print(f"Total Tasks Executed : {total_tasks}")
        print(f"Time Taken           : {duration:.2f} seconds")
        print(f"Handled/Successful   : {self.success_count}")
        print(f"Actual Crashes       : {self.fail_count}")
        
        crash_prob = (self.fail_count / total_tasks) * 100
        print(f"Crash Probability    : {crash_prob:.2f}%")
        
        if crash_prob < 5:
            print("\n✅ STATUS: RESILIENT (Meets < 5% requirement)")
        else:
            print("\n❌ STATUS: VULNERABLE")
        print("="*50)

if __name__ == "__main__":
    tester = HeavyStressTester()
    tester.run_heavy_test()
