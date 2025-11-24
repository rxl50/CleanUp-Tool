"""Restore points management tab."""

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer
from gui.tabs.base_tab import BaseTab
from gui.utils import show_error, show_success, format_size_for_display
from core.restore_manager import RestoreManager
from core.backup_manager import BackupManager
from utils.async_worker import AsyncWorker
from datetime import datetime


class RestoreTab(BaseTab):
    """Tab for managing restore points."""
    
    def __init__(self, parent=None):
        super().__init__("Restore Points", parent)
        self.backup_manager = BackupManager()
        self.restore_manager = RestoreManager(self.backup_manager)
        self.async_worker = AsyncWorker()
        self.restore_points = []
        self.init_content()
    
    def init_content(self):
        """Initialize tab content."""
        info = QLabel("Restore points allow you to recover deleted items. Select a restore point to view details or restore.")
        info.setWordWrap(True)
        self.content_layout.addWidget(info)
        
        self.list_widget = QListWidget()
        self.content_layout.addWidget(self.list_widget)
        
        buttons_layout = QVBoxLayout()
        
        self.view_btn = QPushButton("View Details")
        self.view_btn.setEnabled(False)
        self.view_btn.clicked.connect(self._on_view)
        buttons_layout.addWidget(self.view_btn)
        
        self.restore_btn = QPushButton("Restore")
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self._on_restore)
        buttons_layout.addWidget(self.restore_btn)
        
        self.delete_btn = QPushButton("Delete Restore Point")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._on_delete)
        buttons_layout.addWidget(self.delete_btn)
        
        self.content_layout.addLayout(buttons_layout)
    
    def scan(self):
        """Load restore points."""
        self.update_status("Loading restore points...")
        self.scan_btn.setEnabled(False)
        
        def load_points():
            return self.restore_manager.list_restore_points()
        
        def on_complete(points):
            QTimer.singleShot(0, lambda: self._safe_update_scan_complete(points))
        
        def on_error(error):
            QTimer.singleShot(0, lambda: self._safe_update_scan_error(error))
        
        self.async_worker.execute(load_points, callback=on_complete, error_callback=on_error)
    
    def _safe_update_scan_complete(self, points):
        """Thread-safe UI update after scan completes."""
        self.restore_points = points
        self._update_ui()
        self.scan_btn.setEnabled(True)
        self.update_status(f"Found {len(points)} restore points")
    
    def _safe_update_scan_error(self, error):
        """Thread-safe UI update after scan error."""
        show_error(self, "Error", str(error))
        self.scan_btn.setEnabled(True)
    
    def _update_ui(self):
        """Update UI with restore points."""
        self.list_widget.clear()
        
        for point in self.restore_points:
            timestamp = point.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                time_str = timestamp
            
            size = format_size_for_display(point.get('total_size_bytes', 0))
            item_text = f"{point.get('id', 'Unknown')} - {time_str} - {size}"
            
            item = QListWidgetItem(item_text)
            item.setData(256, point.get('id'))  # Store ID in user role
            self.list_widget.addItem(item)
        
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """Handle selection change."""
        selected = self.list_widget.selectedItems()
        has_selection = len(selected) > 0
        self.view_btn.setEnabled(has_selection)
        self.restore_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def _on_view(self):
        """View restore point details."""
        selected = self.list_widget.selectedItems()
        if not selected:
            return
        
        point_id = selected[0].data(256)
        details = self.restore_manager.get_restore_point_details(point_id)
        
        if details:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Restore Point Details")
            msg.setText(f"Restore Point: {point_id}")
            msg.setInformativeText(
                f"Type: {details.get('operation_type', 'Unknown')}\n"
                f"Items: {details.get('items_backed_up', {}).get('total_count', 0)}\n"
                f"Size: {format_size_for_display(details.get('items_backed_up', {}).get('total_size_bytes', 0))}"
            )
            msg.exec_()
    
    def _on_restore(self):
        """Restore from restore point."""
        selected = self.list_widget.selectedItems()
        if not selected:
            return
        
        point_id = selected[0].data(256)
        show_error(self, "Not Implemented", "Restore functionality will be implemented in future version.")
    
    def _on_delete(self):
        """Delete restore point."""
        selected = self.list_widget.selectedItems()
        if not selected:
            return
        
        point_id = selected[0].data(256)
        
        reply = QMessageBox.question(
            self, "Confirm", f"Delete restore point {point_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.restore_manager.delete_restore_point(point_id)
                show_success(self, "Deleted", "Restore point deleted")
                self.scan()
            except Exception as e:
                show_error(self, "Error", str(e))
    
    def preview(self):
        """Preview not applicable for restore tab."""
        pass
    
    def get_selected_items(self):
        """Get selected restore points."""
        selected = self.list_widget.selectedItems()
        return [item.data(256) for item in selected]

