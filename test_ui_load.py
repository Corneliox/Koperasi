import customtkinter as ctk
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.ui.store_frame import StoreFrame
from app.ui.history_frame import HistoryFrame
from app.database.connection import init_database

def test_store_frame():
    print("Testing StoreFrame...")
    app = ctk.CTk()
    try:
        frame = StoreFrame(app, "SEMBAKO", "admin")
        print("StoreFrame initialized successfully.")
    except Exception as e:
        print(f"StoreFrame FAILED: {e}")
        import traceback
        traceback.print_exc()
    app.destroy()

def test_history_frame():
    print("\nTesting HistoryFrame...")
    app = ctk.CTk()
    try:
        frame = HistoryFrame(app, "SEMBAKO", "admin")
        print("HistoryFrame initialized successfully.")
    except Exception as e:
        print(f"HistoryFrame FAILED: {e}")
        import traceback
        traceback.print_exc()
    app.destroy()

if __name__ == "__main__":
    init_database()
    test_store_frame()
    test_history_frame()
