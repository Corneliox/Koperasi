"""
Global Error and Crash Handler for Sistem Koperasi
Provides structured logging, detailed exception handling, and informative notifications.
"""
import sys
import os
import glob
import traceback
import logging
import logging.handlers
import datetime
import tkinter.messagebox
from typing import Type, Optional
from types import TracebackType


def get_log_dir() -> str:
    """Get writable log directory with fallback to AppData or temp directory"""
    try:
        if getattr(sys, 'frozen', False):
            app_data = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
            log_dir = os.path.join(app_data, "Koperasi", "logs")
        else:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    except Exception:
        import tempfile
        log_dir = os.path.join(tempfile.gettempdir(), "Koperasi_logs")
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            pass
        return log_dir


LOG_DIR = get_log_dir()
CRASH_LOG_PATH = os.path.join(LOG_DIR, "crash_reports.log")

# Setup logging with rotation
logger = logging.getLogger("koperasi")
logger.setLevel(logging.ERROR)
if not logger.handlers:
    try:
        rfh = logging.handlers.RotatingFileHandler(
            CRASH_LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    except Exception:
        pass


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
    logger.error("Unhandled Exception:\n%s", error_msg)
    
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
        logger.error("Failed to log crash to database: %s", str(e))

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
                    
        # Clean up old crash report files (keep at most 15 latest)
        try:
            old_reports = sorted(glob.glob(os.path.join(LOG_DIR, "crash_report_*.txt")))
            if len(old_reports) > 15:
                for old_f in old_reports[:-15]:
                    os.remove(old_f)
        except Exception:
            pass
    except Exception as e:
        logger.error("Failed to write detailed crash report file: %s", str(e))

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
    logger.error(f"Handled Error: {message}\nDetails: {details}")
    try:
        from app.utils.audit_log import log_audit
        log_audit(
            user="SYSTEM",
            action_category="SYSTEM",
            action_type="ERROR",
            details=f"{message} | {details}",
            level="ERROR"
        )
    except Exception:
        pass
    
    try:
        if tkinter._default_root is not None and tkinter._default_root.winfo_exists():
            tkinter.messagebox.showerror("Error", f"{message}\n\n{details if details else ''}")
    except Exception:
        pass


def clean_numeric(value) -> float:
    """
    Helper to safely convert UI strings (Indonesian currency or plain numbers) to float.
    Handles:
    - "50.000" -> 50000.0 (Indonesian thousands separator)
    - "1.500.000" -> 1500000.0
    - "50,5" or "50.5" -> 50.5 (Decimals)
    - "Rp 150.000,00" -> 150000.0
    - Negative values, spaces, none, int, float
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
        
    val_str = str(value).strip()
    if not val_str:
        return 0.0
        
    # Remove prefix like "Rp", "rp", "IDR", spaces
    for prefix in ["Rp.", "rp.", "Rp", "rp", "IDR", "idr"]:
        if val_str.startswith(prefix):
            val_str = val_str[len(prefix):].strip()
            
    val_str = val_str.replace(" ", "")
    if not val_str:
        return 0.0
        
    is_negative = val_str.startswith("-")
    if is_negative:
        val_str = val_str[1:].strip()
        
    try:
        has_dot = '.' in val_str
        has_comma = ',' in val_str
        
        if has_dot and has_comma:
            # e.g., "1.500.000,50" -> dot is thousand, comma is decimal
            if val_str.rfind(',') > val_str.rfind('.'):
                val_str = val_str.replace('.', '').replace(',', '.')
            else:
                val_str = val_str.replace(',', '')
        elif has_comma and not has_dot:
            # e.g., "50,5"
            val_str = val_str.replace(',', '.')
        elif has_dot and not has_comma:
            parts = val_str.split('.')
            if len(parts) > 2:
                # Multiple dots: thousand separators: "1.000.000"
                val_str = "".join(parts)
            elif len(parts) == 2:
                # Single dot: if 3 digits after dot, treat as thousands separator (Rupiah context)
                # except if explicitly small fractional like 0.500 or 0.123
                if len(parts[1]) == 3 and not (len(parts[0]) == 1 and parts[0] == '0'):
                    val_str = parts[0] + parts[1]
                else:
                    val_str = val_str
                    
        result = float(val_str)
        return -result if is_negative else result
    except (ValueError, TypeError):
        return 0.0
