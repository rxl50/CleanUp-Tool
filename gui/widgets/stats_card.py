"""Statistics card widget."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from gui.styles.theme import get_theme


class StatsCard(QWidget):
    """Card widget for displaying statistics."""
    
    def __init__(self, title: str, value: str = "", parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.title = title
        self.value = value
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.theme.get_spacing('large'),
                                 self.theme.get_spacing('medium'),
                                 self.theme.get_spacing('large'),
                                 self.theme.get_spacing('medium'))
        layout.setSpacing(self.theme.get_spacing('small'))
        
        # Set card style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.get_color('surface')};
                border-radius: 8px;
                border: 1px solid {self.theme.get_color('text_secondary')};
            }}
        """)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            color: {self.theme.get_color('text_secondary')};
            font-size: {self.theme.get_font_size('caption')}px;
        """)
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"""
            color: {self.theme.get_color('text_primary')};
            font-size: {self.theme.get_font_size('h3')}px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        """
        Update the value displayed.
        
        Args:
            value: New value to display
        """
        self.value = value
        self.value_label.setText(value)

