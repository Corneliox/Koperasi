"""
Shared decorators for Koperasi Brimob
Includes error handling and logging decorators.
"""
import functools
import traceback
from app.utils.error_handler import log_custom_error

def handle_db_errors(func):
    """Decorator to catch and log database errors with user-friendly popups"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            original_error = str(e)
            user_msg = original_error
            
            # Translate common technical errors
            if "NOT NULL constraint failed" in original_error:
                field = original_error.split(".")[-1]
                user_msg = f"Gagal menyimpan: Kolom '{field}' wajib diisi!"
            elif "UNIQUE constraint failed" in original_error:
                field = original_error.split(".")[-1]
                user_msg = f"Gagal menyimpan: Data '{field}' sudah ada di sistem (Duplikat)!"
            elif "CHECK constraint failed" in original_error:
                user_msg = "Gagal menyimpan: Data yang dimasukkan tidak sesuai dengan kriteria sistem!"
            elif "foreign key constraint failed" in original_error:
                user_msg = "Gagal menyimpan: Data ini masih terhubung dengan data lain!"
            
            error_msg = f"Kesalahan Database: {user_msg}"
            details = traceback.format_exc()
            log_custom_error(error_msg, details)
            return {"success": False, "message": user_msg}
    return wrapper
