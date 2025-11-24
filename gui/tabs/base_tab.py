"""Base class for all tabs."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal
from gui.styles.theme import get_theme
from gui.styles.icons import Icons
from utils.logger import logger


class BaseTab(QWidget):
    """Base class for all cleanup tabs."""
    
    # Signal emitted when cleanup is requested
    cleanup_requested = pyqtSignal(list)
    
    def __init__(self, tab_name: str, parent=None):
        super().__init__(parent)
        self.tab_name = tab_name
        self.theme = get_theme()
        self.items = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize base UI structure."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.theme.get_spacing('large'),
                                 self.theme.get_spacing('large'),
                                 self.theme.get_spacing('large'),
                                 self.theme.get_spacing('large'))
        layout.setSpacing(self.theme.get_spacing('medium'))
        
        # Title
        self.title_label = QLabel(self.tab_name)
        self.title_label.setStyleSheet(f"""
            font-size: {self.theme.get_font_size('h2')}px;
            font-weight: bold;
            color: {self.theme.get_color('text_primary')};
        """)
        layout.addWidget(self.title_label)
        
        # Content area (to be filled by subclasses)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.scan_btn = QPushButton(Icons.get_icon_text('info') + " Scan")
        self.scan_btn.clicked.connect(self._on_scan)
        buttons_layout.addWidget(self.scan_btn)
        
        self.preview_btn = QPushButton(Icons.get_icon_text('info') + " Preview")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self._on_preview)
        buttons_layout.addWidget(self.preview_btn)
        
        self.cleanup_btn = QPushButton(Icons.get_icon_text('clean') + " Clean")
        self.cleanup_btn.setEnabled(False)
        self.cleanup_btn.clicked.connect(self._on_cleanup)
        buttons_layout.addWidget(self.cleanup_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_scan(self):
        """Handle scan button click. Override in subclasses."""
        logger.info(f"Scan requested for {self.tab_name}")
        self.scan()
    
    def _on_preview(self):
        """Handle preview button click. Override in subclasses."""
        logger.info(f"Preview requested for {self.tab_name}")
        self.preview()
    
    def _on_cleanup(self):
        """Handle cleanup button click. Override in subclasses."""
        logger.info(f"Cleanup requested for {self.tab_name}")
        selected = self.get_selected_items()
        if selected:
            self.cleanup_requested.emit(selected)
    
    def scan(self):
        """
        Scan for items to clean. Override in subclasses.
        
        This method should:
        1. Scan for cleanup opportunities
        2. Populate the items list
        3. Update the UI
        4. Enable preview/cleanup buttons
        """
        pass
    
    def preview(self):
        """
        Preview cleanup operations. Override in subclasses.
        
        This method should:
        1. Show what will be deleted
        2. Display space savings
        3. Show warnings if any
        """
        pass
    
    def get_selected_items(self) -> list:
        """
        Get selected items for cleanup. Override in subclasses.
        
        Returns:
            List of selected item IDs
        """
        return []
    
    def update_status(self, message: str):
        """
        Update status message.
        
        Args:
            message: Status message
        """
        # Find main window in parent hierarchy
        from gui.main_window import MainWindow
        parent = self.parent()
        while parent:
            if isinstance(parent, MainWindow):
                parent.status_bar.set_message(message)
                break
            parent = parent.parent()

