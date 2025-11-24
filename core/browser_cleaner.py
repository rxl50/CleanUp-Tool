"""Browser cache cleanup."""

import os
from pathlib import Path
from typing import List, Dict, Any
from utils.logger import logger
from utils.exceptions import OperationError
from utils.file_utils import get_directory_size
from core.safety_checker import SafetyChecker
from core.backup_manager import BackupManager


class BrowserCleaner:
    """Clean browser cache files."""
    
    def __init__(self, backup_manager: BackupManager = None):
        self.backup_manager = backup_manager
        self.safety_checker = SafetyChecker()
    
    def get_browser_caches(self) -> List[Dict[str, Any]]:
        """
        Get list of browser cache locations.
        
        Returns:
            List of browser cache dictionaries
        """
        caches = []
        local_appdata = Path(os.environ.get('LOCALAPPDATA', ''))
        appdata = Path(os.environ.get('APPDATA', ''))
        
        # Chrome
        chrome_cache = local_appdata / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Cache'
        if chrome_cache.exists():
            size = get_directory_size(chrome_cache)
            caches.append({
                'name': 'Chrome',
                'path': chrome_cache,
                'size': size,
                'type': 'chrome'
            })
        
        # Firefox
        firefox_profiles = appdata / 'Mozilla' / 'Firefox' / 'Profiles'
        if firefox_profiles.exists():
            total_size = 0
            for profile in firefox_profiles.iterdir():
                if profile.is_dir():
                    cache_dir = profile / 'cache2'
                    if cache_dir.exists():
                        total_size += get_directory_size(cache_dir)
            
            if total_size > 0:
                caches.append({
                    'name': 'Firefox',
                    'path': firefox_profiles,
                    'size': total_size,
                    'type': 'firefox'
                })
        
        # Edge
        edge_cache = local_appdata / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Cache'
        if edge_cache.exists():
            size = get_directory_size(edge_cache)
            caches.append({
                'name': 'Microsoft Edge',
                'path': edge_cache,
                'size': size,
                'type': 'edge'
            })
        
        # Opera
        opera_cache = local_appdata / 'Opera Software' / 'Opera Stable' / 'Cache'
        if opera_cache.exists():
            size = get_directory_size(opera_cache)
            caches.append({
                'name': 'Opera',
                'path': opera_cache,
                'size': size,
                'type': 'opera'
            })
        
        return caches
    
    def clean_browser_cache(self, browser_type: str, create_backup: bool = True) -> bool:
        """
        Clean browser cache.
        
        Args:
            browser_type: Browser type (chrome, firefox, edge, opera)
            create_backup: Whether to create backup first
            
        Returns:
            True if successful
        """
        caches = self.get_browser_caches()
        browser_cache = next((c for c in caches if c['type'] == browser_type), None)
        
        if not browser_cache:
            return False
        
        cache_path = browser_cache['path']
        
        # Create backup if requested
        restore_point_id = None
        if create_backup and self.backup_manager:
            try:
                backup_items = [{
                    'type': 'directory',
                    'path': str(cache_path),
                    'info': browser_cache
                }]
                restore_point_id = self.backup_manager.create_restore_point('browser', backup_items)
                logger.info(f"Created backup before cache cleanup: {restore_point_id}")
            except Exception as e:
                if self.backup_manager.settings.get('backup_settings.mandatory_backup', True):
                    raise OperationError(f"Backup failed, operation cancelled: {e}")
                else:
                    logger.warning(f"Backup failed but not mandatory: {e}")
        
        # Delete cache
        try:
            import shutil
            if cache_path.is_dir():
                shutil.rmtree(cache_path)
                # Recreate empty directory
                cache_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cleaned {browser_cache['name']} cache")
            return True
        except Exception as e:
            logger.error(f"Error cleaning {browser_cache['name']} cache: {e}")
            raise OperationError(f"Failed to clean cache: {e}")

