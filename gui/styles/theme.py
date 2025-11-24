"""UI theme definitions."""

import json
from pathlib import Path
from typing import Dict, Any
from config.settings import get_settings


class Theme:
    """Manage UI theme and styling."""
    
    def __init__(self):
        self.settings = get_settings()
        self.ui_config_path = Path("config/ui_config.json")
        self.theme_config = self._load_theme_config()
        self.current_theme = self.settings.get('ui_settings.theme', 'light')
    
    def _load_theme_config(self) -> Dict[str, Any]:
        """Load theme configuration from file."""
        try:
            if self.ui_config_path.exists():
                with open(self.ui_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading theme config: {e}")
        
        # Return default theme
        return {
            "theme": {
                "light": {
                    "background": "#FFFFFF",
                    "surface": "#F5F5F5",
                    "primary": "#2196F3",
                    "secondary": "#FF9800",
                    "success": "#4CAF50",
                    "warning": "#FFC107",
                    "error": "#F44336",
                    "text_primary": "#212121",
                    "text_secondary": "#757575"
                },
                "dark": {
                    "background": "#121212",
                    "surface": "#1E1E1E",
                    "primary": "#64B5F6",
                    "secondary": "#FFB74D",
                    "success": "#81C784",
                    "warning": "#FFD54F",
                    "error": "#E57373",
                    "text_primary": "#FFFFFF",
                    "text_secondary": "#B0B0B0"
                }
            },
            "spacing": {
                "unit": 8,
                "small": 4,
                "medium": 8,
                "large": 16,
                "xlarge": 24
            },
            "typography": {
                "font_family": "Segoe UI, Arial, sans-serif",
                "sizes": {
                    "h1": 32,
                    "h2": 24,
                    "h3": 20,
                    "body": 14,
                    "caption": 12
                }
            }
        }
    
    def get_color(self, color_name: str) -> str:
        """
        Get color value from current theme.
        
        Args:
            color_name: Color name (background, primary, etc.)
            
        Returns:
            Hex color code
        """
        theme_colors = self.theme_config.get('theme', {}).get(self.current_theme, {})
        return theme_colors.get(color_name, "#000000")
    
    def get_spacing(self, size: str = 'medium') -> int:
        """
        Get spacing value.
        
        Args:
            size: Spacing size (small, medium, large, xlarge)
            
        Returns:
            Spacing in pixels
        """
        spacing = self.theme_config.get('spacing', {})
        return spacing.get(size, spacing.get('unit', 8))
    
    def get_font_size(self, size: str = 'body') -> int:
        """
        Get font size.
        
        Args:
            size: Font size (h1, h2, h3, body, caption)
            
        Returns:
            Font size in pixels
        """
        sizes = self.theme_config.get('typography', {}).get('sizes', {})
        return sizes.get(size, 14)
    
    def get_font_family(self) -> str:
        """Get font family."""
        return self.theme_config.get('typography', {}).get('font_family', 'Arial')
    
    def set_theme(self, theme_name: str):
        """
        Set current theme.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        if theme_name in ['light', 'dark']:
            self.current_theme = theme_name
            self.settings.set('ui_settings.theme', theme_name)
    
    def get_stylesheet(self) -> str:
        """Get complete stylesheet for current theme."""
        bg = self.get_color('background')
        surface = self.get_color('surface')
        primary = self.get_color('primary')
        text_primary = self.get_color('text_primary')
        text_secondary = self.get_color('text_secondary')
        
        return f"""
            QMainWindow {{
                background-color: {bg};
                color: {text_primary};
            }}
            QWidget {{
                background-color: {bg};
                color: {text_primary};
                font-family: {self.get_font_family()};
            }}
            QPushButton {{
                background-color: {primary};
                color: white;
                border: none;
                padding: {self.get_spacing('medium')}px {self.get_spacing('large')}px;
                border-radius: 4px;
                font-weight: bold;
                font-size: {self.get_font_size('body')}px;
            }}
            QPushButton:hover {{
                background-color: {primary};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {primary};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {surface};
                color: {text_secondary};
            }}
            QLineEdit, QTextEdit {{
                background-color: {surface};
                border: 1px solid {text_secondary};
                border-radius: 4px;
                padding: {self.get_spacing('small')}px;
            }}
            QListWidget, QTreeWidget {{
                background-color: {surface};
                border: 1px solid {text_secondary};
                border-radius: 4px;
            }}
        """


# Global theme instance
_theme_instance = None


def get_theme() -> Theme:
    """Get global theme instance."""
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = Theme()
    return _theme_instance

