"""
Shared decorators for Koperasi Brimob
Includes error handling and logging decorators.
"""
import functools
import traceback
from app.utils.error_handler import log_custom_error

def handle_db_errors(func):
    """Decorator to catch and log database errors with popups"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            details = traceback.format_exc()
            log_custom_error(error_msg, details)
            return None
    return wrapper
