"""Main application class for CleanUp."""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
from utils.logger import logger
from config.settings import get_settings


class CleanUpApp(QApplication):
    """Main application class."""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("CleanUp")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("CleanUp Tool")
        
        # Load settings
        self.settings = get_settings()
        
        # Set application style
        self._setup_style()
        
        # Create main window
        self.main_window = MainWindow()
        self.main_window.show()
        
        logger.info("CleanUp application started")
    
    def _setup_style(self):
        """Setup application style and theme."""
        # Set style sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)

