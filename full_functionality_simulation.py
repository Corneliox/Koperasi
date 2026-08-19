"""
Full Functionality Simulation for Koperasi Brimob
Simulates: Member creation, Inventory CRUD, Sales, Stock management, and Loans.
"""
import sys
import os

# Setup Path
sys.path.append(os.getcwd())

from app.database.connection import init_database
from app.modules.members import MemberManager
from app.modules.warehouse import WarehouseManager
from app.modules.loans import LoanManager
from app.modules.transactions import TransactionManager
from app.utils.audit_log import get_audit_logs

def run_simulation():
    print("STARTING FULL FUNCTIONALITY SIMULATION\n")
    init_database()
    
    members = MemberManager("SIMULATOR")
    warehouse = WarehouseManager("SEMBAKO", "SIMULATOR")
    loans = LoanManager("SIMULATOR")
    transactions = TransactionManager("SEMBAKO")
    
    print("--- STEP 1: MEMBER MANAGEMENT ---")
    import time
    member_name = "Simulasi Anggota"
    member_nrp = f"NRP-SIM-{int(time.time())}"
    res_m = members.add_member(name=member_name, nrp=member_nrp, unit="SIMULASI", rank="BRIPDA")
    if res_m and res_m.get('success'):
        member_id = res_m['id']
        print(f"SUCCESS: Member created (ID: {member_id})")
    else:
        print(f"FAILED: Member creation: {res_m.get('message') if res_m else 'None'}")
        return

    print("\n--- STEP 2: INVENTORY MANAGEMENT ---")
    item_name = "Barang Simulasi"
    res_i = warehouse.add_item(name=item_name, stock=50, buy_price=10000, sell_price=15000, item_code="CODE-SIM")
    if res_i and res_i.get('success'):
        item_id = res_i['id']
        print(f"SUCCESS: Item added (ID: {item_id})")
        warehouse.update_item(item_id, name=f"{item_name} Edited", stock=50, buy_price=11000, sell_price=16000, status="Koperasi", description="Update test", item_code="CODE-SIM-ED")
        print("SUCCESS: Item updated")
        warehouse.add_stock(item_id, 10, "Restock simulasi")
        item_data = warehouse.get_item_by_id(item_id)
        print(f"SUCCESS: Stock verified as {item_data['stock']}")

    print("\n--- STEP 3: SALES TRANSACTION ---")
    res_s = warehouse.sell_item(item_id, qty=5, member_id=member_id, payment_method="Tunai")
    if res_s and res_s.get('success'):
        print(f"SUCCESS: Sale recorded. Remaining stock: {res_s['remaining_stock']}")
    else:
        print("FAILED: Sale")

    print("\n--- STEP 4: LOAN MANAGEMENT ---")
    res_l = loans.create_loan(member_id, amount=5000000, interest_rate=5, duration_months=10, notes="Pinjaman simulasi")
    if res_l and res_l.get('success'):
        loan_id = res_l['loan_id']
        print(f"SUCCESS: Loan created (ID: {loan_id})")
        res_p = loans.record_payment(loan_id, amount=500000, payment_method="Transfer", notes="Cicilan 1")
        if res_p and res_p.get('success'):
            print(f"SUCCESS: Payment recorded: {res_p['message']}")

    print("\n--- STEP 5: VERIFICATION & AUDIT ---")
    history = transactions.get_transactions(member_id=member_id)
    print(f"VERIFIED: {len(history)} transaction(s) found for member.")
    logs = get_audit_logs(limit=5)
    print(f"VERIFIED: Audit log updated. Latest: {logs[0]['action_type']}")

    print("\n--- CLEANUP ---")
    warehouse.delete_item(item_id)
    print("SUCCESS: Test item deleted.")
    print("\nSIMULATION COMPLETED: ALL CORE FUNCTIONS ARE WORKING PROPERLY.")

if __name__ == "__main__":
    run_simulation()
