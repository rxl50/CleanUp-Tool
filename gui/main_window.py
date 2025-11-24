"""Main window for CleanUp application."""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
import shutil
from pathlib import Path

from gui.components.header import Header
from gui.components.sidebar import Sidebar
from gui.components.status_bar import StatusBar
from gui.components.dashboard import Dashboard
from gui.tabs.base_tab import BaseTab
from gui.styles.theme import get_theme
from utils.logger import logger
from config.settings import get_settings


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.theme = get_theme()
        self.init_ui()
        self.update_disk_space()
    
    def init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("CleanUp Tool")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.tab_selected.connect(self._on_tab_selected)
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        self.header = Header(self)
        self.header._on_settings_clicked = self.show_settings
        content_layout.addWidget(self.header)
        
        # Stacked widget for tabs
        self.stacked_widget = QStackedWidget()
        
        # Dashboard (home)
        self.dashboard = Dashboard(self)
        self.stacked_widget.addWidget(self.dashboard)
        
        # Add tabs
        self.tabs = {}
        
        # Anaconda tab
        from gui.tabs.anaconda_tab import AnacondaTab
        conda_tab = AnacondaTab(self)
        conda_tab.cleanup_requested.connect(self._on_cleanup_requested)
        self.tabs['conda'] = conda_tab
        self.stacked_widget.addWidget(conda_tab)
        
        # Pip tab
        from gui.tabs.pip_tab import PipTab
        pip_tab = PipTab(self)
        pip_tab.cleanup_requested.connect(self._on_cleanup_requested)
        self.tabs['pip'] = pip_tab
        self.stacked_widget.addWidget(pip_tab)
        
        # System tab
        from gui.tabs.system_tab import SystemTab
        system_tab = SystemTab(self)
        system_tab.cleanup_requested.connect(self._on_cleanup_requested)
        self.tabs['system'] = system_tab
        self.stacked_widget.addWidget(system_tab)
        
        # Browser tab
        from gui.tabs.browser_tab import BrowserTab
        browser_tab = BrowserTab(self)
        browser_tab.cleanup_requested.connect(self._on_cleanup_requested)
        self.tabs['browser'] = browser_tab
        self.stacked_widget.addWidget(browser_tab)
        
        # Placeholder tabs (will be implemented in future phases)
        tab_names = ['dev_tools', 'files', 'duplicates']
        for tab_name in tab_names:
            tab = BaseTab(tab_name.replace('_', ' ').title(), self)
            tab.cleanup_requested.connect(self._on_cleanup_requested)
            self.tabs[tab_name] = tab
            self.stacked_widget.addWidget(tab)
        
        # Restore tab
        from gui.tabs.restore_tab import RestoreTab
        restore_tab = RestoreTab(self)
        restore_tab.cleanup_requested.connect(self._on_cleanup_requested)
        self.tabs['restore'] = restore_tab
        self.stacked_widget.addWidget(restore_tab)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Status bar
        self.status_bar = StatusBar(self)
        content_layout.addWidget(self.status_bar)
        
        main_layout.addWidget(content_widget)
        
        # Apply theme
        self.setStyleSheet(self.theme.get_stylesheet())
    
    def _on_tab_selected(self, tab_id: str):
        """Handle tab selection."""
        logger.info(f"Tab selected: {tab_id}")
        
        # Map tab IDs to indices
        tab_map = {
            'home': 0,
            'conda': 1,
            'pip': 2,
            'system': 3,
            'browser': 4,
            'dev_tools': 5,
            'files': 6,
            'duplicates': 7,
            'restore': 8
        }
        
        index = tab_map.get(tab_id, 0)
        self.stacked_widget.setCurrentIndex(index)
    
    def _on_cleanup_requested(self, items: list):
        """Handle cleanup request from a tab."""
        logger.info(f"Cleanup requested for {len(items)} items")
        self.status_bar.set_message(f"Cleanup requested for {len(items)} items")
    
    def update_disk_space(self):
        """Update disk space display."""
        try:
            # Get disk usage for C: drive (Windows)
            total, used, free = shutil.disk_usage("C:\\")
            self.header.update_disk_space(used, total)
            self.dashboard.update_disk_space(used, total)
        except Exception as e:
            logger.error(f"Error getting disk space: {e}")
            self.header.update_disk_space(0, 0)
            self.dashboard.update_disk_space(0, 0)
    
    def show_settings(self):
        """Show settings dialog."""
        logger.info("Settings dialog requested")
        # Will be implemented in Phase 7
        self.status_bar.set_message("Settings dialog (to be implemented)")
    
    def show_help(self):
        """Show help dialog."""
        logger.info("Help dialog requested")
        # Will be implemented in Phase 7
        self.status_bar.set_message("Help dialog (to be implemented)")
    
    def perform_quick_clean(self):
        """Perform quick clean of safe items."""
        logger.info("Quick clean requested")
        # Will be implemented in Phase 3+
        self.status_bar.set_message("Quick clean (to be implemented)")
    
    def scan_all_categories(self):
        """Scan all categories for cleanup opportunities."""
        logger.info("Scan all requested")
        # Will be implemented in Phase 3+
        self.status_bar.set_message("Scanning all categories (to be implemented)")

