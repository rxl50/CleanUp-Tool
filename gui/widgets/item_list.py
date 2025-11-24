"""Reusable item list widget with checkboxes."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QCheckBox, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any
from gui.styles.theme import get_theme
from utils.size_formatter import format_size


class ItemList(QWidget):
    """List widget for displaying items with checkboxes."""
    
    # Signal emitted when selection changes
    selection_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.items = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme.get_color('surface')};
                border: 1px solid {self.theme.get_color('text_secondary')};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.list_widget)
    
    def add_item(self, item_id: str, name: str, size: int = 0, 
                description: str = "", checked: bool = False, 
                warning: bool = False) -> QListWidgetItem:
        """
        Add an item to the list.
        
        Args:
            item_id: Unique item identifier
            name: Item name
            size: Item size in bytes
            description: Item description
            checked: Whether item is checked by default
            warning: Whether to show warning indicator
            
        Returns:
            Created list widget item
        """
        # Create custom widget for list item
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(self.theme.get_spacing('medium'),
                                      self.theme.get_spacing('small'),
                                      self.theme.get_spacing('medium'),
                                      self.theme.get_spacing('small'))
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        checkbox.stateChanged.connect(lambda: self._on_selection_changed())
        item_layout.addWidget(checkbox)
        
        # Name label
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: {self.theme.get_color('text_primary')};
            font-size: {self.theme.get_font_size('body')}px;
            font-weight: bold;
        """)
        item_layout.addWidget(name_label)
        
        item_layout.addStretch()
        
        # Size label
        if size > 0:
            size_label = QLabel(format_size(size))
            size_label.setStyleSheet(f"""
                color: {self.theme.get_color('text_secondary')};
                font-size: {self.theme.get_font_size('caption')}px;
            """)
            item_layout.addWidget(size_label)
        
        # Warning indicator
        if warning:
            warning_label = QLabel("⚠️")
            warning_label.setToolTip("This item requires attention")
            item_layout.addWidget(warning_label)
        
        # Create list item
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)
        
        # Store item data
        self.items[item_id] = {
            'item': list_item,
            'widget': item_widget,
            'checkbox': checkbox,
            'name': name,
            'size': size,
            'description': description,
            'warning': warning
        }
        
        return list_item
    
    def get_selected_items(self) -> List[str]:
        """
        Get list of selected item IDs.
        
        Returns:
            List of selected item IDs
        """
        selected = []
        for item_id, item_data in self.items.items():
            if item_data['checkbox'].isChecked():
                selected.append(item_id)
        return selected
    
    def select_all(self):
        """Select all items."""
        for item_data in self.items.values():
            item_data['checkbox'].setChecked(True)
        self._on_selection_changed()
    
    def deselect_all(self):
        """Deselect all items."""
        for item_data in self.items.values():
            item_data['checkbox'].setChecked(False)
        self._on_selection_changed()
    
    def clear(self):
        """Clear all items."""
        self.items.clear()
        self.list_widget.clear()
    
    def _on_selection_changed(self):
        """Handle selection change."""
        selected = self.get_selected_items()
        self.selection_changed.emit(selected)

