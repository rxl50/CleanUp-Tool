"""Header component for main window."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from gui.styles.theme import get_theme
from gui.styles.icons import Icons


class Header(QWidget):
    """Application header with title and disk space indicator."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(self.theme.get_spacing('large'), 
                                 self.theme.get_spacing('medium'),
                                 self.theme.get_spacing('large'),
                                 self.theme.get_spacing('medium'))
        
        # Title
        title_label = QLabel("CleanUp Tool")
        title_label.setStyleSheet(f"""
            font-size: {self.theme.get_font_size('h2')}px;
            font-weight: bold;
            color: {self.theme.get_color('text_primary')};
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Disk space indicator
        self.disk_space_label = QLabel("Disk Space: Calculating...")
        self.disk_space_label.setStyleSheet(f"""
            color: {self.theme.get_color('text_secondary')};
            font-size: {self.theme.get_font_size('body')}px;
        """)
        layout.addWidget(self.disk_space_label)
        
        # Settings button
        settings_btn = QPushButton(Icons.get_icon_text('settings') + " Settings")
        settings_btn.setToolTip("Open settings")
        settings_btn.clicked.connect(self._on_settings_clicked)
        layout.addWidget(settings_btn)
    
    def update_disk_space(self, used: int, total: int):
        """
        Update disk space display.
        
        Args:
            used: Used space in bytes
            total: Total space in bytes
        """
        from utils.size_formatter import format_size
        used_str = format_size(used)
        total_str = format_size(total)
        percent = (used / total * 100) if total > 0 else 0
        
        self.disk_space_label.setText(
            f"Disk Space: {used_str} / {total_str} ({percent:.1f}%)"
        )
    
    def _on_settings_clicked(self):
        """Handle settings button click."""
        # This will be connected to main window's settings dialog
        if self.parent():
            self.parent().show_settings()

