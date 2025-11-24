"""Status bar component."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from gui.styles.theme import get_theme


class StatusBar(QWidget):
    """Status bar showing progress and messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(self.theme.get_spacing('medium'),
                                 self.theme.get_spacing('small'),
                                 self.theme.get_spacing('medium'),
                                 self.theme.get_spacing('small'))
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            color: {self.theme.get_color('text_secondary')};
            font-size: {self.theme.get_font_size('caption')}px;
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        layout.addWidget(self.progress_bar)
    
    def set_message(self, message: str):
        """
        Set status message.
        
        Args:
            message: Status message text
        """
        self.status_label.setText(message)
    
    def show_progress(self, current: int, total: int, message: str = ""):
        """
        Show progress bar.
        
        Args:
            current: Current progress value
            total: Total progress value
            message: Optional progress message
        """
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        if message:
            self.status_label.setText(message)
    
    def hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

