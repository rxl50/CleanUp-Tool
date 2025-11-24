"""Icon resources for the application."""

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize


class Icons:
    """Icon management for the application."""
    
    # Icon paths (using Unicode symbols as fallback)
    ICONS = {
        'home': '🏠',
        'conda': '🐍',
        'pip': '📦',
        'system': '💻',
        'browser': '🌐',
        'dev_tools': '⚙️',
        'files': '📁',
        'duplicates': '🔍',
        'restore': '↩️',
        'settings': '⚙️',
        'help': '❓',
        'delete': '🗑️',
        'clean': '✨',
        'backup': '💾',
        'warning': '⚠️',
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️',
    }
    
    @staticmethod
    def get_icon(name: str, size: int = 24) -> QIcon:
        """
        Get icon by name.
        
        Args:
            name: Icon name
            size: Icon size in pixels
            
        Returns:
            QIcon object
        """
        # For now, return empty icon (can be enhanced with actual icon files)
        # In a full implementation, you would load icon files here
        return QIcon()
    
    @staticmethod
    def get_icon_text(name: str) -> str:
        """
        Get icon as text (emoji/unicode).
        
        Args:
            name: Icon name
            
        Returns:
            Icon text/emoji
        """
        return Icons.ICONS.get(name, '📄')

