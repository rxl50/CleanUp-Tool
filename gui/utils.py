"""GUI utility functions."""

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt
from typing import Optional
from utils.size_formatter import format_size


def show_message(parent: Optional[QWidget], title: str, message: str, 
                icon: QMessageBox.Icon = QMessageBox.Information):
    """
    Show a message box.
    
    Args:
        parent: Parent widget
        title: Message title
        message: Message text
        icon: Message icon
    """
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def show_error(parent: Optional[QWidget], title: str, message: str):
    """Show an error message."""
    show_message(parent, title, message, QMessageBox.Critical)


def show_warning(parent: Optional[QWidget], title: str, message: str):
    """Show a warning message."""
    show_message(parent, title, message, QMessageBox.Warning)


def show_success(parent: Optional[QWidget], title: str, message: str):
    """Show a success message."""
    show_message(parent, title, message, QMessageBox.Information)


def format_size_for_display(size_bytes: int) -> str:
    """
    Format size for display in GUI.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    return format_size(size_bytes, precision=1)

