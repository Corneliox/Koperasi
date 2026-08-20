"""
Shared decorators for Sistem Koperasi
Includes error handling and logging decorators.
"""
import functools
import traceback
from app.utils.error_handler import log_custom_error

def handle_db_errors(func):
    """
    Decorator to catch and log database errors with user-friendly popups.
    Returns:
    - dict {'success': False, 'message': ...} if func returns dict or mutates
    - list [] if func return type annotation is list
    - int 0 if func return type annotation is int
    - None for others
    """
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
            
            # Check return annotation for type safety
            ret_type = func.__annotations__.get('return', None)
            if ret_type is list:
                return []
            elif ret_type is int:
                return 0
            elif ret_type is None:
                return None
            return {"success": False, "message": user_msg}
    return wrapper
