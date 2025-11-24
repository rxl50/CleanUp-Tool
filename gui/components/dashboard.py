"""Dashboard/home view component."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from gui.styles.theme import get_theme
from gui.widgets.stats_card import StatsCard
from utils.size_formatter import format_size


class Dashboard(QWidget):
    """Dashboard showing overview and quick actions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.theme.get_spacing('large'),
                                 self.theme.get_spacing('large'),
                                 self.theme.get_spacing('large'),
                                 self.theme.get_spacing('large'))
        layout.setSpacing(self.theme.get_spacing('large'))
        
        # Title
        title = QLabel("Welcome to CleanUp Tool")
        title.setStyleSheet(f"""
            font-size: {self.theme.get_font_size('h1')}px;
            font-weight: bold;
            color: {self.theme.get_color('text_primary')};
        """)
        layout.addWidget(title)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(self.theme.get_spacing('medium'))
        
        self.disk_space_card = StatsCard("Disk Space", "Calculating...", self)
        self.cleanup_savings_card = StatsCard("Potential Savings", "0 B", self)
        self.restore_points_card = StatsCard("Restore Points", "0", self)
        
        stats_layout.addWidget(self.disk_space_card)
        stats_layout.addWidget(self.cleanup_savings_card)
        stats_layout.addWidget(self.restore_points_card)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet(f"""
            font-size: {self.theme.get_font_size('h3')}px;
            font-weight: bold;
            color: {self.theme.get_color('text_primary')};
            margin-top: {self.theme.get_spacing('large')}px;
        """)
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(self.theme.get_spacing('medium'))
        
        self.quick_clean_btn = QPushButton("Quick Clean")
        self.quick_clean_btn.setToolTip("Clean safe items automatically")
        self.quick_clean_btn.clicked.connect(self._on_quick_clean)
        actions_layout.addWidget(self.quick_clean_btn)
        
        self.scan_btn = QPushButton("Scan All")
        self.scan_btn.setToolTip("Scan all categories for cleanup opportunities")
        self.scan_btn.clicked.connect(self._on_scan_all)
        actions_layout.addWidget(self.scan_btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
    
    def update_disk_space(self, used: int, total: int):
        """Update disk space display."""
        used_str = format_size(used)
        total_str = format_size(total)
        percent = (used / total * 100) if total > 0 else 0
        self.disk_space_card.set_value(f"{used_str} / {total_str} ({percent:.1f}%)")
    
    def update_savings(self, savings: int):
        """Update potential savings."""
        self.cleanup_savings_card.set_value(format_size(savings))
    
    def update_restore_points(self, count: int):
        """Update restore points count."""
        self.restore_points_card.set_value(str(count))
    
    def _on_quick_clean(self):
        """Handle quick clean button click."""
        if self.parent():
            self.parent().perform_quick_clean()
    
    def _on_scan_all(self):
        """Handle scan all button click."""
        if self.parent():
            self.parent().scan_all_categories()

