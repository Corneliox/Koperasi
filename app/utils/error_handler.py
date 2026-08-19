"""
Global Error and Crash Handler for Koperasi Brimob
Provides structured logging, detailed exception handling, and informative notifications.
"""
import sys
import os
import traceback
import logging
import datetime
import tkinter.messagebox
from typing import Type, Optional
from types import TracebackType

# Configure standard logging to file
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

CRASH_LOG_PATH = os.path.join(LOG_DIR, "crash_reports.log")

# Setup logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(CRASH_LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Optional[TracebackType]):
    """
    Global exception handler for unhandled exceptions.
    Logs the error and shows a popup to the user.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Generate detailed error message
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Log the crash
    logging.error("Unhandled Exception:\n%s", error_msg)
    
    # Also try to log to audit_log database if possible
    try:
        from app.utils.audit_log import log_audit
        log_audit(
            user="SYSTEM",
            action_category="SYSTEM",
            action_type="CRASH",
            details=f"CRASH DETECTED: {str(exc_value)}",
            level="DANGER"
        )
    except Exception as e:
        logging.error("Failed to log crash to database: %s", str(e))

    # Create an informative crash report file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(LOG_DIR, f"crash_report_{timestamp}.txt")
    
    try:
        with open(report_file, "w", encoding='utf-8') as f:
            f.write("=== KOPERASI CRASH REPORT ===\n")
            f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write("-" * 40 + "\n")
            f.write("ERROR DETAILS:\n")
            f.write(error_msg)
            f.write("-" * 40 + "\n")
            f.write("Environment Variables (Partial):\n")
            for key in ['OS', 'PROCESSOR_IDENTIFIER', 'USERNAME']:
                if key in os.environ:
                    f.write(f"{key}: {os.environ[key]}\n")
    except Exception as e:
        logging.error("Failed to write detailed crash report file: %s", str(e))

    # Show popup notification
    show_error_popup(exc_value, report_file)

def show_error_popup(exc_value: BaseException, report_file: str):
    """Show an informative popup about the error"""
    try:
        title = "❌ Terjadi Kesalahan Fatal"
        message = (
            f"Aplikasi mengalami kesalahan yang tidak terduga dan harus ditutup.\n\n"
            f"Detail Error: {str(exc_value)}\n\n"
            f"Laporan kerusakan telah disimpan di:\n{report_file}\n\n"
            "Silakan kirimkan file ini ke tim teknis untuk perbaikan."
        )
        
        # Use tkinter messagebox since customtkinter might be what crashed
        root = tkinter.Tk()
        root.withdraw()
        tkinter.messagebox.showerror(title, message)
        root.destroy()
    except Exception as e:
        # Fallback if even tkinter fails
        print(f"CRITICAL ERROR in popup handler: {e}")
        print(f"Original error was: {exc_value}")

def setup_global_error_handler():
    """Initialize the global exception hook"""
    sys.excepthook = handle_exception
    print("Global error handler initialized. All crashes will be logged and notified.")

def log_custom_error(message: str, details: str = None):
    """Utility to log a caught error with popup but without crashing the app"""
    logging.error(f"Handled Error: {message}\nDetails: {details}")
    try:
        from app.utils.audit_log import log_audit
        log_audit(
            user="SYSTEM",
            action_category="SYSTEM",
            action_type="ERROR",
            details=f"{message} | {details}",
            level="ERROR"
        )
    except:
        pass
    
    try:
        if tkinter._default_root is not None and tkinter._default_root.winfo_exists():
            tkinter.messagebox.showerror("Error", f"{message}\n\n{details if details else ''}")
    except Exception:
        pass

def clean_numeric(value: str) -> float:
    """Helper to safely convert UI strings (with dots/commas) to float"""
    if not value:
        return 0.0
    try:
        # Remove common currency separators
        sanitized = str(value).replace(',', '').replace(' ', '')
        # Handle cases with multiple dots if any
        if sanitized.count('.') > 1:
            parts = sanitized.split('.')
            sanitized = "".join(parts[:-1]) + "." + parts[-1]
        return float(sanitized)
    except (ValueError, TypeError):
        return 0.0
