"""Pip cache cleanup tab."""

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from gui.tabs.base_tab import BaseTab
from gui.styles.theme import get_theme
from gui.styles.icons import Icons
from gui.utils import show_error, show_success, format_size_for_display
from core.pip_manager import PipManager
from core.backup_manager import BackupManager
from utils.logger import logger
from utils.async_worker import AsyncWorker


class PipTab(BaseTab):
    """Tab for pip cache cleanup."""
    
    def __init__(self, parent=None):
        super().__init__("Pip Cache Cleanup", parent)
        self.backup_manager = BackupManager()
        self.pip_manager = PipManager(self.backup_manager)
        self.async_worker = AsyncWorker()
        self.cache_info = {}
        self.init_content()
    
    def init_content(self):
        """Initialize tab content."""
        # Info label
        info_label = QLabel(
            "Clean pip cache to free up disk space. This will remove all cached packages."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"""
            color: {self.theme.get_color('text_secondary')};
            font-size: {self.theme.get_font_size('body')}px;
            padding: {self.theme.get_spacing('medium')}px;
            background-color: {self.theme.get_color('surface')};
            border-radius: 4px;
        """)
        self.content_layout.addWidget(info_label)
        
        # Cache info display
        self.info_widget = QLabel("Click 'Scan' to check pip cache")
        self.info_widget.setStyleSheet(f"""
            color: {self.theme.get_color('text_primary')};
            font-size: {self.theme.get_font_size('body')}px;
            padding: {self.theme.get_spacing('large')}px;
            background-color: {self.theme.get_color('surface')};
            border-radius: 4px;
        """)
        self.content_layout.addWidget(self.info_widget)
        
        self.content_layout.addStretch()
    
    def scan(self):
        """Scan pip cache."""
        if not self.pip_manager.is_available():
            show_error(self, "Pip Not Available", 
                      "Pip is not installed or not found in PATH.")
            return
        
        self.update_status("Scanning pip cache...")
        self.scan_btn.setEnabled(False)
        
        # Scan in background
        def scan_cache():
            return self.pip_manager.get_cache_info()
        
        def on_complete(info):
            QTimer.singleShot(0, lambda: self._safe_update_scan_complete(info))
        
        def on_error(error):
            QTimer.singleShot(0, lambda: self._safe_update_scan_error(error))
        
        self.async_worker.execute(scan_cache, callback=on_complete, error_callback=on_error)
    
    def _update_ui(self):
        """Update UI with cache info."""
        if not self.cache_info.get('available', False):
            self.info_widget.setText("Pip is not available")
            self.preview_btn.setEnabled(False)
            self.cleanup_btn.setEnabled(False)
            return
        
        size = self.cache_info.get('size', 0)
        location = self.cache_info.get('location', 'Unknown')
        
        if size > 0:
            info_text = (
                f"<b>Cache Size:</b> {format_size_for_display(size)}<br>"
                f"<b>Location:</b> {location}<br><br>"
                f"Click 'Preview' to see details or 'Clean' to remove cache."
            )
            self.preview_btn.setEnabled(True)
            self.cleanup_btn.setEnabled(True)
        else:
            info_text = "Pip cache is empty or not found."
            self.preview_btn.setEnabled(False)
            self.cleanup_btn.setEnabled(False)
        
        self.info_widget.setText(info_text)
    
    def preview(self):
        """Preview cache cleanup."""
        size = self.cache_info.get('size', 0)
        location = self.cache_info.get('location', 'Unknown')
        
        if size == 0:
            show_error(self, "Empty Cache", "Pip cache is empty.")
            return
        
        # Show preview
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Cache Cleanup Preview")
        msg.setText("Will purge entire pip cache")
        msg.setInformativeText(
            f"Cache size: {format_size_for_display(size)}\n"
            f"Location: {location}\n\n"
            "A backup will be created before deletion."
        )
        msg.exec_()
    
    def get_selected_items(self) -> list:
        """Get selected items (always returns cache if available)."""
        if self.cache_info.get('size', 0) > 0:
            return ['pip_cache']
        return []
    
    def _on_cleanup(self):
        """Handle cleanup button click."""
        size = self.cache_info.get('size', 0)
        if size == 0:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Cache Purge",
            f"Are you sure you want to purge the pip cache?\n\n"
            f"Cache size: {format_size_for_display(size)}\n\n"
            "A backup will be created before deletion.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Perform cleanup
        self.update_status("Purging pip cache...")
        self.cleanup_btn.setEnabled(False)
        
        def purge_cache():
            return self.pip_manager.purge_cache(create_backup=True)
        
        def on_complete(success):
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_complete(success, size))
        
        def on_error(error):
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_error(error))
        
        self.async_worker.execute(purge_cache, callback=on_complete, error_callback=on_error)
    
    def _safe_update_scan_complete(self, info):
        """Thread-safe UI update after scan completes."""
        self.cache_info = info
        self._update_ui()
        self.scan_btn.setEnabled(True)
        self.update_status("Scan complete")
    
    def _safe_update_scan_error(self, error):
        """Thread-safe UI update after scan error."""
        show_error(self, "Scan Error", f"Error scanning pip cache: {error}")
        self.scan_btn.setEnabled(True)
        self.update_status("Scan failed")
    
    def _safe_update_cleanup_complete(self, success, size):
        """Thread-safe UI update after cleanup completes."""
        if success:
            show_success(self, "Cache Purged", 
                       f"Successfully freed {format_size_for_display(size)} of disk space.")
            # Rescan to update info
            self.scan()
        else:
            show_error(self, "Purge Failed", "Failed to purge pip cache.")
        
        self.cleanup_btn.setEnabled(True)
        self.update_status("Cleanup complete")
    
    def _safe_update_cleanup_error(self, error):
        """Thread-safe UI update after cleanup error."""
        show_error(self, "Purge Error", f"Error purging cache: {error}")
        self.cleanup_btn.setEnabled(True)
        self.update_status("Cleanup failed")

