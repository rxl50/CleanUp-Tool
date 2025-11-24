"""Navigation sidebar component."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from gui.styles.theme import get_theme
from gui.styles.icons import Icons


class Sidebar(QWidget):
    """Navigation sidebar with menu items."""
    
    # Signal emitted when a tab is selected
    tab_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.current_tab = 'home'
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.theme.get_spacing('medium'),
                                 self.theme.get_spacing('medium'),
                                 self.theme.get_spacing('medium'),
                                 self.theme.get_spacing('medium'))
        layout.setSpacing(self.theme.get_spacing('small'))
        
        # Navigation items
        self.tabs = [
            ('home', 'Home', Icons.get_icon_text('home')),
            ('conda', 'Anaconda', Icons.get_icon_text('conda')),
            ('pip', 'Pip Cache', Icons.get_icon_text('pip')),
            ('system', 'System', Icons.get_icon_text('system')),
            ('browser', 'Browser', Icons.get_icon_text('browser')),
            ('dev_tools', 'Dev Tools', Icons.get_icon_text('dev_tools')),
            ('files', 'Files', Icons.get_icon_text('files')),
            ('duplicates', 'Duplicates', Icons.get_icon_text('duplicates')),
            ('restore', 'Restore Points', Icons.get_icon_text('restore')),
        ]
        
        self.buttons = {}
        
        for tab_id, label, icon in self.tabs:
            btn = QPushButton(f"{icon} {label}")
            btn.setCheckable(True)
            btn.setStyleSheet(self._get_button_style())
            btn.clicked.connect(lambda checked, t=tab_id: self._on_tab_clicked(t))
            layout.addWidget(btn)
            self.buttons[tab_id] = btn
        
        layout.addStretch()
        
        # Help button at bottom
        help_btn = QPushButton(Icons.get_icon_text('help') + " Help")
        help_btn.setStyleSheet(self._get_button_style())
        help_btn.clicked.connect(self._on_help_clicked)
        layout.addWidget(help_btn)
    
    def _get_button_style(self) -> str:
        """Get style for sidebar buttons."""
        return f"""
            QPushButton {{
                text-align: left;
                padding: {self.theme.get_spacing('medium')}px;
                border-radius: 4px;
                background-color: {self.theme.get_color('surface')};
                color: {self.theme.get_color('text_primary')};
                font-size: {self.theme.get_font_size('body')}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.get_color('primary')};
                color: white;
            }}
            QPushButton:checked {{
                background-color: {self.theme.get_color('primary')};
                color: white;
                font-weight: bold;
            }}
        """
    
    def _on_tab_clicked(self, tab_id: str):
        """Handle tab button click."""
        # Update button states
        for btn_id, btn in self.buttons.items():
            btn.setChecked(btn_id == tab_id)
        
        self.current_tab = tab_id
        self.tab_selected.emit(tab_id)
    
    def _on_help_clicked(self):
        """Handle help button click."""
        if self.parent():
            self.parent().show_help()
    
    def set_active_tab(self, tab_id: str):
        """Set active tab programmatically."""
        self._on_tab_clicked(tab_id)

