"""
Diagnostic Protocol for Koperasi Brimob
Checks all core functionalities and provides a detailed log report.
"""
import os
import sys
import platform
import logging
import traceback
import sqlite3
import datetime

# Setup diagnostic logging
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

DIAG_LOG_PATH = os.path.join(LOG_DIR, "diagnostics.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(DIAG_LOG_PATH, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Diagnostics")

def run_diagnostics():
    logger.info("=" * 50)
    logger.info("KOPERASI BRIMOB - SYSTEM DIAGNOSTIC PROTOCOL")
    logger.info("=" * 50)
    
    results = {
        "System Info": False,
        "Dependencies": False,
        "Module Imports": False,
        "Database Connection": False,
        "File Permissions": False,
        "UI Framework": False
    }

    # 1. System Info
    try:
        logger.info("[1/6] Gathering System Information...")
        logger.info(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
        logger.info(f"Python: {sys.version}")
        logger.info(f"WorkDir: {os.getcwd()}")
        results["System Info"] = True
    except Exception as e:
        logger.error(f"Error gathering system info: {e}")

    # 2. Dependencies
    try:
        logger.info("[2/6] Checking Critical Dependencies...")
        import customtkinter
        import PIL
        import openpyxl
        logger.info(f"CustomTkinter version: {customtkinter.__version__}")
        logger.info("Critical dependencies found.")
        results["Dependencies"] = True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")

    # 3. Module Imports
    try:
        logger.info("[3/6] Checking Internal Modules...")
        from app.database.connection import init_database, get_db_path
        from app.utils.audit_log import log_audit
        from app.utils.error_handler import setup_global_error_handler
        from app.modules import warehouse, members, loans, transactions
        logger.info("All internal modules imported successfully.")
        results["Module Imports"] = True
    except Exception as e:
        logger.error(f"Module import failed: {e}")
        logger.error(traceback.format_exc())

    # 4. Database Connection
    try:
        logger.info("[4/6] Testing Database Connection...")
        from app.database.connection import get_connection, init_database, DB_PATH
        logger.info(f"Database path: {DB_PATH}")
        
        # Test initialization
        init_database()
        
        # Test connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        logger.info(f"Found {len(table_names)} tables: {', '.join(table_names)}")
        
        # Check for core tables
        core_tables = ['warehouse', 'members', 'transactions', 'loans', 'users', 'audit_log_immutable']
        missing = [t for t in core_tables if t not in table_names]
        
        if not missing:
            logger.info("All core tables are present.")
            results["Database Connection"] = True
        else:
            logger.error(f"Missing core tables: {', '.join(missing)}")
        
        conn.close()
    except Exception as e:
        logger.error(f"Database diagnostic failed: {e}")
        logger.error(traceback.format_exc())

    # 5. File Permissions
    try:
        logger.info("[5/6] Checking File System Permissions...")
        test_file = os.path.join(LOG_DIR, "perm_test.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        logger.info("Write permissions in logs directory: OK")
        
        # Check database directory permissions
        db_dir = os.path.dirname(DB_PATH)
        if os.access(db_dir, os.W_OK):
            logger.info(f"Write permissions in DB directory ({db_dir}): OK")
            results["File Permissions"] = True
        else:
            logger.error(f"No write permission in DB directory: {db_dir}")
    except Exception as e:
        logger.error(f"File permission check failed: {e}")

    # 6. UI Framework
    try:
        logger.info("[6/6] Checking UI Framework Initialization...")
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw() # Don't show the window
        logger.info("CustomTkinter root initialization: OK")
        root.destroy()
        results["UI Framework"] = True
    except Exception as e:
        logger.info(f"UI Framework check (headless?): {e}")
        # Not strictly failing if in terminal environment
        results["UI Framework"] = "WARNING (Headless?)"

    # Summary
    logger.info("=" * 50)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 50)
    all_passed = True
    for test, status in results.items():
        status_str = "PASS" if status is True else ("FAIL" if status is False else str(status))
        logger.info(f"{test:<25}: {status_str}")
        if status is False:
            all_passed = False
    
    logger.info("=" * 50)
    if all_passed:
        logger.info("RESULT: SYSTEM HEALTHY")
    else:
        logger.info("RESULT: ISSUES DETECTED - Check logs/diagnostics.log")
    logger.info("=" * 50)
    
    if not all_passed and sys.stdin.isatty():
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_diagnostics()
