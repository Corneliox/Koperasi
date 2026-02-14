"""
Stress Test Logic for Koperasi Brimob
Verifies resilience against invalid inputs and edge cases.
"""
import sys
import os
import unittest
import logging

# Ensure app modules can be imported
sys.path.append(os.getcwd())

from app.database.connection import init_database
from app.modules.warehouse import WarehouseManager
from app.modules.members import MemberManager
from app.modules.loans import LoanManager
from app.modules.transactions import TransactionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StressTest")

class TestKoperasiResilience(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Initialize DB once"""
        init_database()
        
    def setUp(self):
        self.warehouse = WarehouseManager("SEMBAKO")
        self.members = MemberManager()
        self.loans = LoanManager()
        self.transactions = TransactionManager("SEMBAKO")

    def test_warehouse_invalid_inputs(self):
        """Test warehouse operations with bad data"""
        logger.info("Testing Warehouse with invalid inputs...")
        
        # Test add_item with None/Empty
        try:
            # Should be handled by decorator or DB constraints
            self.warehouse.add_item(None, -1, "abc", None) 
        except Exception as e:
            logger.error(f"Warehouse crash detected: {e}")
            self.fail("Warehouse crashed on invalid add_item")

        # Test calculation with invalid types
        try:
            self.warehouse.sell_item("invalid_id", "many")
        except Exception as e:
             logger.error(f"Warehouse crash detected: {e}")
             self.fail("Warehouse crashed on invalid sell_item")

    def test_member_fuzzing(self):
        """Test member operations with fuzz data"""
        logger.info("Testing Members with fuzz data...")
        
        fuzz_strings = ["", "   ", "Robert'); DROP TABLE members;--", "🌟emoji🌟", "\0null"]
        
        for s in fuzz_strings:
            try:
                self.members.add_member(s, s, s, s)
                self.members.autocomplete_search(s)
            except Exception as e:
                self.fail(f"Member crashed on input '{s}': {e}")

    def test_loan_calculations(self):
        """Test loan simulation with edge cases"""
        logger.info("Testing Loan calculations...")
        
        scenarios = [
            (0, 10, 12),      # Zero amount
            (-1000, 10, 12),  # Negative amount
            (1000000, -5, 12),# Negative interest
            (1000000, 10, 0), # Zero duration (Div by zero risk)
            (None, None, None)# None types
        ]
        
        for amt, rate, dur in scenarios:
            try:
                # The simulation method might raise error if not guarded
                # But we wrapped create_loan, let's check simulate_loan logic inside
                # (simulate_loan isn't wrapped in decorator in my previous edit, 
                # but create_loan calls it. Let's call create_loan directly)
                self.loans.create_loan(1, amt, rate, dur)
            except Exception as e:
                # If create_loan is decorated, it should catch this and return None or dict
                # It should NOT raise exception to here.
                self.fail(f"Loan create crashed on ({amt}, {rate}, {dur}): {e}")

    def test_transaction_queries(self):
        """Test transaction queries with invalid dates"""
        logger.info("Testing Transaction queries...")
        
        try:
            self.transactions.get_transactions(start_date="invalid-date", end_date=12345)
        except Exception as e:
            self.fail(f"Transaction query crashed: {e}")

if __name__ == "__main__":
    unittest.main()
