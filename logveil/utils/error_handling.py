"""
Error handling utilities for LogVeil.
Provides helper functions for consistent error logging.
"""

from typing import Callable
import traceback
from logveil.utils.logging import logger

def log_exception(func: Callable):
    """
    Decorator to log exceptions raised by the decorated function.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}")
            logger.debug(traceback.format_exc())
            raise
    return wrapper