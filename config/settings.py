"""Configuration management for CleanUp tool."""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from utils.logger import logger
from utils.exceptions import ConfigurationError


class Settings:
    """Manage application settings and configuration."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.defaults_file = self.config_dir / "defaults.json"
        self.user_settings_file = self.config_dir / "user_settings.json"
        
        # Load defaults
        self._defaults = self._load_json(self.defaults_file)
        
        # Load user settings (override defaults)
        self._user_settings = {}
        if self.user_settings_file.exists():
            self._user_settings = self._load_json(self.user_settings_file)
        else:
            # Initialize with defaults
            self._user_settings = self._defaults.copy()
            self.save()
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file {file_path}: {e}")
            return {}
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving config file {file_path}: {e}")
            raise ConfigurationError(f"Failed to save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get setting value using dot notation (e.g., 'backup_settings.retention_days').
        
        Args:
            key: Setting key (supports nested keys with dots)
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self._user_settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set setting value using dot notation.
        
        Args:
            key: Setting key (supports nested keys with dots)
            value: Value to set
        """
        keys = key.split('.')
        config = self._user_settings
        
        # Navigate/create nested structure
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
        self.save()
    
    def save(self):
        """Save current settings to user settings file."""
        self._save_json(self.user_settings_file, self._user_settings)
        logger.debug("Settings saved")
    
    def reset(self, key: Optional[str] = None):
        """
        Reset setting(s) to defaults.
        
        Args:
            key: Specific key to reset (None = reset all)
        """
        if key is None:
            self._user_settings = self._defaults.copy()
        else:
            keys = key.split('.')
            default_value = self._defaults
            for k in keys:
                if isinstance(default_value, dict) and k in default_value:
                    default_value = default_value[k]
                else:
                    logger.warning(f"Default not found for key: {key}")
                    return
            
            self.set(key, default_value)
        
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._user_settings.copy()
    
    def update(self, updates: Dict[str, Any]):
        """
        Update multiple settings at once.
        
        Args:
            updates: Dictionary of setting updates
        """
        def deep_update(base: dict, updates: dict):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(self._user_settings, updates)
        self.save()


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

