"""Anaconda cleanup tab."""

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from gui.tabs.base_tab import BaseTab
from gui.widgets.item_list import ItemList
from gui.styles.theme import get_theme
from gui.styles.icons import Icons
from PyQt5.QtCore import QTimer
from gui.utils import show_error, show_success, format_size_for_display
from core.conda_manager import CondaManager
from core.backup_manager import BackupManager
from utils.logger import logger
from utils.async_worker import AsyncWorker


class AnacondaTab(BaseTab):
    """Tab for Anaconda environment cleanup."""
    
    def __init__(self, parent=None):
        super().__init__("Anaconda Cleanup", parent)
        self.backup_manager = BackupManager()
        self.conda_manager = CondaManager(self.backup_manager)
        self.async_worker = AsyncWorker()
        self.environments = []
        self.init_content()
    
    def init_content(self):
        """Initialize tab content."""
        # Info label
        info_label = QLabel(
            "Select conda environments to remove. Active and base environments are protected."
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
        
        # Item list
        self.item_list = ItemList(self)
        self.item_list.selection_changed.connect(self._on_selection_changed)
        self.content_layout.addWidget(self.item_list)
        
        # Summary label
        self.summary_label = QLabel("No items selected")
        self.summary_label.setStyleSheet(f"""
            color: {self.theme.get_color('text_secondary')};
            font-size: {self.theme.get_font_size('body')}px;
        """)
        self.content_layout.addWidget(self.summary_label)
    
    def scan(self):
        """Scan for conda environments."""
        if not self.conda_manager.is_available():
            show_error(self, "Conda Not Available", 
                      "Conda is not installed or not found in PATH.")
            return
        
        self.update_status("Scanning conda environments...")
        self.scan_btn.setEnabled(False)
        
        # Scan in background
        def scan_environments():
            return self.conda_manager.list_environments()
        
        def on_complete(environments):
            # Post to main thread for GUI updates
            QTimer.singleShot(0, lambda: self._safe_update_scan_complete(environments))
        
        def on_error(error):
            # Post to main thread for GUI updates
            QTimer.singleShot(0, lambda: self._safe_update_scan_error(error))
        
        self.async_worker.execute(scan_environments, callback=on_complete, error_callback=on_error)
    
    def _update_ui(self):
        """Update UI with scanned environments."""
        self.item_list.clear()
        
        total_size = 0
        safe_count = 0
        
        for env in self.environments:
            # Skip protected environments
            if env['protected']:
                continue
            
            # Add to list
            warning = False
            checked = True  # Pre-select safe environments
            
            self.item_list.add_item(
                item_id=env['name'],
                name=env['name'],
                size=env['size'],
                description=f"Path: {env['path']}",
                checked=checked,
                warning=warning
            )
            
            total_size += env['size']
            safe_count += 1
        
        # Update summary
        if safe_count > 0:
            self.summary_label.setText(
                f"{safe_count} environment(s) selected, "
                f"total size: {format_size_for_display(total_size)}"
            )
            self.preview_btn.setEnabled(True)
            self.cleanup_btn.setEnabled(True)
        else:
            self.summary_label.setText("No safe environments found to clean")
            self.preview_btn.setEnabled(False)
            self.cleanup_btn.setEnabled(False)
    
    def _on_selection_changed(self, selected: list):
        """Handle selection change."""
        total_size = 0
        for env in self.environments:
            if env['name'] in selected:
                total_size += env['size']
        
        if selected:
            self.summary_label.setText(
                f"{len(selected)} environment(s) selected, "
                f"total size: {format_size_for_display(total_size)}"
            )
            self.preview_btn.setEnabled(True)
            self.cleanup_btn.setEnabled(True)
        else:
            self.summary_label.setText("No items selected")
            self.preview_btn.setEnabled(False)
            self.cleanup_btn.setEnabled(False)
    
    def preview(self):
        """Preview cleanup operations."""
        selected = self.get_selected_items()
        if not selected:
            show_error(self, "No Selection", "Please select environments to clean.")
            return
        
        # Calculate total size
        total_size = 0
        env_names = []
        for env in self.environments:
            if env['name'] in selected:
                total_size += env['size']
                env_names.append(env['name'])
        
        # Show preview dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Cleanup Preview")
        msg.setText(f"Will remove {len(selected)} environment(s):")
        msg.setDetailedText("\n".join(f"  • {name}" for name in env_names))
        msg.setInformativeText(f"Total space to free: {format_size_for_display(total_size)}")
        msg.exec_()
    
    def get_selected_items(self) -> list:
        """Get selected environment names."""
        return self.item_list.get_selected_items()
    
    def _on_cleanup(self):
        """Handle cleanup button click."""
        selected = self.get_selected_items()
        if not selected:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove {len(selected)} environment(s)?\n\n"
            "A backup will be created before deletion.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Perform cleanup
        self.update_status("Removing environments...")
        self.cleanup_btn.setEnabled(False)
        
        def cleanup_environments():
            results = {'success': [], 'failed': []}
            for env_name in selected:
                try:
                    self.conda_manager.remove_environment(env_name, create_backup=True)
                    results['success'].append(env_name)
                except Exception as e:
                    logger.error(f"Error removing {env_name}: {e}")
                    results['failed'].append((env_name, str(e)))
            return results
        
        def on_complete(results):
            # Post to main thread for GUI updates
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_complete(results))
        
        def on_error(error):
            # Post to main thread for GUI updates
            QTimer.singleShot(0, lambda: self._safe_update_cleanup_error(error))
        
        self.async_worker.execute(cleanup_environments, callback=on_complete, error_callback=on_error)
    
    def _safe_update_cleanup_complete(self, results):
        """Thread-safe UI update after cleanup completes."""
        success_count = len(results['success'])
        failed_count = len(results['failed'])
        
        if success_count > 0:
            show_success(self, "Cleanup Complete", 
                       f"Successfully removed {success_count} environment(s).")
            # Rescan to update list
            self.scan()
        
        if failed_count > 0:
            error_msg = "\n".join(f"{name}: {error}" for name, error in results['failed'])
            show_error(self, "Some Deletions Failed", error_msg)
        
        self.cleanup_btn.setEnabled(True)
        self.update_status("Cleanup complete")
    
    def _safe_update_cleanup_error(self, error):
        """Thread-safe UI update after cleanup error."""
        show_error(self, "Cleanup Error", f"Error during cleanup: {error}")
        self.cleanup_btn.setEnabled(True)
        self.update_status("Cleanup failed")
    
    def _safe_update_scan_complete(self, environments):
        """Thread-safe UI update after scan completes."""
        self.environments = environments
        self._update_ui()
        self.scan_btn.setEnabled(True)
        self.update_status(f"Found {len(environments)} environments")
    
    def _safe_update_scan_error(self, error):
        """Thread-safe UI update after scan error."""
        show_error(self, "Scan Error", f"Error scanning environments: {error}")
        self.scan_btn.setEnabled(True)
        self.update_status("Scan failed")

