"""Browser cleanup tab."""

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import QTimer
from gui.tabs.base_tab import BaseTab
from gui.widgets.item_list import ItemList
from gui.utils import show_error, show_success, format_size_for_display
from core.browser_cleaner import BrowserCleaner
from core.backup_manager import BackupManager
from utils.async_worker import AsyncWorker


class BrowserTab(BaseTab):
    """Tab for browser cache cleanup."""
    
    def __init__(self, parent=None):
        super().__init__("Browser Cleanup", parent)
        self.backup_manager = BackupManager()
        self.browser_cleaner = BrowserCleaner(self.backup_manager)
        self.async_worker = AsyncWorker()
        self.browsers = []
        self.init_content()
    
    def init_content(self):
        """Initialize tab content."""
        info = QLabel("Select browsers to clean cache")
        info.setWordWrap(True)
        self.content_layout.addWidget(info)
        
        self.item_list = ItemList(self)
        self.item_list.selection_changed.connect(self._on_selection_changed)
        self.content_layout.addWidget(self.item_list)
        
        self.summary_label = QLabel("No browsers selected")
        self.content_layout.addWidget(self.summary_label)
    
    def scan(self):
        """Scan for browser caches."""
        self.update_status("Scanning browsers...")
        self.scan_btn.setEnabled(False)
        
        def scan_browsers():
            return self.browser_cleaner.get_browser_caches()
        
        def on_complete(browsers):
            QTimer.singleShot(0, lambda: self._safe_update_scan_complete(browsers))
        
        def on_error(error):
            QTimer.singleShot(0, lambda: self._safe_update_scan_error(error))
        
        self.async_worker.execute(scan_browsers, callback=on_complete, error_callback=on_error)
    
    def _update_ui(self):
        """Update UI."""
        self.item_list.clear()
        total_size = 0
        
        for browser in self.browsers:
            self.item_list.add_item(
                item_id=browser['type'],
                name=browser['name'],
                size=browser['size'],
                checked=True
            )
            total_size += browser['size']
        
        self.summary_label.setText(f"{len(self.browsers)} browsers, {format_size_for_display(total_size)}")
        self.preview_btn.setEnabled(len(self.browsers) > 0)
        self.cleanup_btn.setEnabled(len(self.browsers) > 0)
    
    def _on_selection_changed(self, selected):
        """Handle selection change."""
        total_size = sum(b['size'] for b in self.browsers if b['type'] in selected)
        self.summary_label.setText(f"{len(selected)} selected, {format_size_for_display(total_size)}")
    
    def preview(self):
        """Preview cleanup."""
        selected = self.get_selected_items()
        browsers = [b for b in self.browsers if b['type'] in selected]
        total_size = sum(b['size'] for b in browsers)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Preview")
        msg.setText(f"Will clean {len(browsers)} browser cache(s)")
        msg.setInformativeText(f"Space to free: {format_size_for_display(total_size)}")
        msg.exec_()
    
    def get_selected_items(self):
        """Get selected browsers."""
        return self.item_list.get_selected_items()
    
    def _on_cleanup(self):
        """Handle cleanup."""
        selected = self.get_selected_items()
        if not selected:
            return
        
        reply = QMessageBox.question(
            self, "Confirm", f"Clean {len(selected)} browser cache(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.update_status("Cleaning caches...")
        self.cleanup_btn.setEnabled(False)
        
        def cleanup():
            results = {'success': [], 'failed': []}
            for browser_type in selected:
                try:
                    if self.browser_cleaner.clean_browser_cache(browser_type, create_backup=True):
                        results['success'].append(browser_type)
                    else:
                        results['failed'].append(browser_type)
                except Exception as e:
                    results['failed'].append((browser_type, str(e)))
            return results
        
        def on_complete(results):
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_complete(results))
        
        def on_error(error):
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_error(error))
        
        self.async_worker.execute(cleanup, callback=on_complete, error_callback=on_error)
    
    def _safe_update_scan_complete(self, browsers):
        """Thread-safe UI update after scan completes."""
        self.browsers = browsers
        self._update_ui()
        self.scan_btn.setEnabled(True)
        self.update_status(f"Found {len(browsers)} browsers")
    
    def _safe_update_scan_error(self, error):
        """Thread-safe UI update after scan error."""
        show_error(self, "Error", str(error))
        self.scan_btn.setEnabled(True)
    
    def _safe_update_cleanup_complete(self, results):
        """Thread-safe UI update after cleanup completes."""
        if results['success']:
            show_success(self, "Complete", f"Cleaned {len(results['success'])} cache(s)")
            self.scan()
        if results['failed']:
            show_error(self, "Some Failed", str(results['failed']))
        self.cleanup_btn.setEnabled(True)
    
    def _safe_update_cleanup_error(self, error):
        """Thread-safe UI update after cleanup error."""
        show_error(self, "Error", str(error))
        self.cleanup_btn.setEnabled(True)

