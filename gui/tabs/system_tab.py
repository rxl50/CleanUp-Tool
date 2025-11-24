"""System cleanup tab."""

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QSpinBox, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer
from gui.tabs.base_tab import BaseTab
from gui.widgets.item_list import ItemList
from gui.utils import show_error, show_success, format_size_for_display
from core.system_cleaner import SystemCleaner
from core.backup_manager import BackupManager
from utils.async_worker import AsyncWorker


class SystemTab(BaseTab):
    """Tab for system temp files cleanup."""
    
    def __init__(self, parent=None):
        super().__init__("System Cleanup", parent)
        self.backup_manager = BackupManager()
        self.system_cleaner = SystemCleaner(self.backup_manager)
        self.async_worker = AsyncWorker()
        self.temp_files = []
        self.init_content()
    
    def init_content(self):
        """Initialize tab content."""
        # Age filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Minimum file age (days):"))
        self.age_spinbox = QSpinBox()
        self.age_spinbox.setMinimum(1)
        self.age_spinbox.setMaximum(365)
        self.age_spinbox.setValue(30)
        filter_layout.addWidget(self.age_spinbox)
        filter_layout.addStretch()
        self.content_layout.addLayout(filter_layout)
        
        # Item list
        self.item_list = ItemList(self)
        self.item_list.selection_changed.connect(self._on_selection_changed)
        self.content_layout.addWidget(self.item_list)
        
        # Summary
        self.summary_label = QLabel("No items selected")
        self.content_layout.addWidget(self.summary_label)
    
    def scan(self):
        """Scan for temp files."""
        min_age = self.age_spinbox.value()
        self.update_status(f"Scanning temp files (min age: {min_age} days)...")
        self.scan_btn.setEnabled(False)
        
        def scan_files():
            return self.system_cleaner.scan_temp_files(min_age_days=min_age)
        
        def on_complete(files):
            QTimer.singleShot(0, lambda: self._safe_update_scan_complete(files))
        
        def on_error(error):
            QTimer.singleShot(0, lambda: self._safe_update_scan_error(error))
        
        self.async_worker.execute(scan_files, callback=on_complete, error_callback=on_error)
    
    def _update_ui(self):
        """Update UI with scanned files."""
        self.item_list.clear()
        total_size = 0
        
        for file_info in self.temp_files[:100]:  # Limit display
            self.item_list.add_item(
                item_id=file_info['path'],
                name=file_info['name'],
                size=file_info['size'],
                checked=True
            )
            total_size += file_info['size']
        
        self.summary_label.setText(f"{len(self.temp_files)} files, {format_size_for_display(total_size)}")
        self.preview_btn.setEnabled(len(self.temp_files) > 0)
        self.cleanup_btn.setEnabled(len(self.temp_files) > 0)
    
    def _on_selection_changed(self, selected):
        """Handle selection change."""
        total_size = sum(f['size'] for f in self.temp_files if f['path'] in selected)
        self.summary_label.setText(f"{len(selected)} selected, {format_size_for_display(total_size)}")
    
    def preview(self):
        """Preview cleanup."""
        selected = self.get_selected_items()
        total_size = sum(f['size'] for f in self.temp_files if f['path'] in selected)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Cleanup Preview")
        msg.setText(f"Will delete {len(selected)} file(s)")
        msg.setInformativeText(f"Space to free: {format_size_for_display(total_size)}")
        msg.exec_()
    
    def get_selected_items(self):
        """Get selected files."""
        return self.item_list.get_selected_items()
    
    def _on_cleanup(self):
        """Handle cleanup."""
        selected = self.get_selected_items()
        if not selected:
            return
        
        files_to_delete = [f for f in self.temp_files if f['path'] in selected]
        
        reply = QMessageBox.question(
            self, "Confirm", f"Delete {len(files_to_delete)} files?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.update_status("Cleaning files...")
        self.cleanup_btn.setEnabled(False)
        
        def cleanup():
            return self.system_cleaner.clean_temp_files(files_to_delete, create_backup=True)
        
        def on_complete(results):
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_complete(results))
        
        def on_error(error):
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_error(error))
        
        self.async_worker.execute(cleanup, callback=on_complete, error_callback=on_error)
    
    def _safe_update_scan_complete(self, files):
        """Thread-safe UI update after scan completes."""
        self.temp_files = files
        self._update_ui()
        self.scan_btn.setEnabled(True)
        self.update_status(f"Found {len(files)} files")
    
    def _safe_update_scan_error(self, error):
        """Thread-safe UI update after scan error."""
        show_error(self, "Scan Error", f"Error scanning: {error}")
        self.scan_btn.setEnabled(True)
    
    def _safe_update_cleanup_complete(self, results):
        """Thread-safe UI update after cleanup completes."""
        show_success(self, "Complete", f"Deleted {results['success']} files")
        self.scan()
        self.cleanup_btn.setEnabled(True)
    
    def _safe_update_cleanup_error(self, error):
        """Thread-safe UI update after cleanup error."""
        show_error(self, "Error", str(error))
        self.cleanup_btn.setEnabled(True)

