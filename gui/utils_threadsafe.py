"""Thread-safe GUI update utilities."""

from PyQt5.QtCore import QTimer, QMetaObject, Qt, Q_ARG
from typing import Callable, Any


def safe_gui_update(callback: Callable, *args, **kwargs):
    """
    Safely update GUI from any thread by posting to main thread.
    
    Args:
        callback: Function to call on main thread
        *args: Positional arguments for callback
        **kwargs: Keyword arguments for callback
    """
    # Use QTimer.singleShot to post to main thread event loop
    def execute():
        try:
            callback(*args, **kwargs)
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Error in GUI callback: {e}")
    
    QTimer.singleShot(0, execute)


def safe_gui_method_call(obj: Any, method_name: str, *args):
    """
    Safely call a method on a QObject from any thread.
    
    Args:
        obj: QObject instance
        method_name: Name of method to call
        *args: Arguments for method
    """
    if hasattr(obj, method_name):
        method = getattr(obj, method_name)
        QMetaObject.invokeMethod(
            obj,
            method_name,
            Qt.QueuedConnection,
            *[Q_ARG(type(arg), arg) for arg in args]
        )

