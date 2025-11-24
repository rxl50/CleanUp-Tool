"""System temporary files cleanup."""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
from utils.logger import logger
from utils.exceptions import OperationError
from utils.file_utils import get_directory_size, get_file_info
from core.safety_checker import SafetyChecker
from core.backup_manager import BackupManager


class SystemCleaner:
    """Clean system temporary files."""
    
    def __init__(self, backup_manager: BackupManager = None):
        self.backup_manager = backup_manager
        self.safety_checker = SafetyChecker()
    
    def get_temp_locations(self) -> List[Dict[str, Any]]:
        """
        Get list of temporary file locations.
        
        Returns:
            List of temp location dictionaries
        """
        locations = []
        
        # Windows temp directories
        if os.name == 'nt':
            # User temp
            user_temp = Path(os.environ.get('TEMP', os.environ.get('TMP', '')))
            if user_temp.exists():
                locations.append({
                    'name': 'User Temp',
                    'path': user_temp,
                    'type': 'directory'
                })
            
            # System temp
            system_temp = Path(os.environ.get('SystemRoot', 'C:\\Windows')) / 'Temp'
            if system_temp.exists():
                locations.append({
                    'name': 'System Temp',
                    'path': system_temp,
                    'type': 'directory'
                })
            
            # Windows Update cache
            update_cache = Path(os.environ.get('SystemRoot', 'C:\\Windows')) / 'SoftwareDistribution' / 'Download'
            if update_cache.exists():
                locations.append({
                    'name': 'Windows Update Cache',
                    'path': update_cache,
                    'type': 'directory'
                })
            
            # Thumbnail cache
            thumbnail_cache = Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'Windows' / 'Explorer'
            if thumbnail_cache.exists():
                locations.append({
                    'name': 'Thumbnail Cache',
                    'path': thumbnail_cache,
                    'type': 'directory'
                })
            
            # Prefetch
            prefetch = Path('C:\\Windows\\Prefetch')
            if prefetch.exists():
                locations.append({
                    'name': 'Prefetch Files',
                    'path': prefetch,
                    'type': 'directory'
                })
        
        return locations
    
    def scan_temp_files(self, min_age_days: int = 30) -> List[Dict[str, Any]]:
        """
        Scan for temporary files to clean.
        
        Args:
            min_age_days: Minimum age in days for files to be considered for deletion
            
        Returns:
            List of file/directory info dictionaries
        """
        files_to_clean = []
        cutoff_date = datetime.now() - timedelta(days=min_age_days)
        
        locations = self.get_temp_locations()
        
        for location in locations:
            path = location['path']
            
            if not path.exists():
                continue
            
            try:
                # Scan directory
                for item in path.rglob('*'):
                    try:
                        if item.is_file():
                            # Check file age
                            mtime = datetime.fromtimestamp(item.stat().st_mtime)
                            if mtime < cutoff_date:
                                file_info = get_file_info(item)
                                file_info['location_name'] = location['name']
                                files_to_clean.append(file_info)
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Error accessing {item}: {e}")
                        continue
            except Exception as e:
                logger.error(f"Error scanning {path}: {e}")
        
        return files_to_clean
    
    def get_location_size(self, location_path: Path) -> int:
        """Get total size of a location."""
        try:
            return get_directory_size(location_path)
        except Exception as e:
            logger.warning(f"Error calculating size for {location_path}: {e}")
            return 0
    
    def clean_temp_files(self, files: List[Dict[str, Any]], create_backup: bool = True) -> Dict[str, Any]:
        """
        Clean temporary files.
        
        Args:
            files: List of file info dictionaries to delete
            create_backup: Whether to create backup first
            
        Returns:
            Dictionary with cleanup results
        """
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        # Create backup if requested
        restore_point_id = None
        if create_backup and self.backup_manager and files:
            try:
                backup_items = []
                for f in files:
                    # Validate path
                    file_path = f.get('path', '')
                    if file_path:
                        # Convert to string if it's a Path object
                        if isinstance(file_path, Path):
                            file_path = str(file_path)
                        backup_items.append({
                            'type': 'file',
                            'path': file_path,
                            'info': f
                        })
                
                if backup_items:
                    restore_point_id = self.backup_manager.create_restore_point('system', backup_items)
                    logger.info(f"Created backup before cleanup: {restore_point_id}")
            except Exception as e:
                if self.backup_manager.settings.get('backup_settings.mandatory_backup', True):
                    raise OperationError(f"Backup failed, operation cancelled: {e}")
                else:
                    logger.warning(f"Backup failed but not mandatory: {e}")
        
        # Delete files
        from utils.file_utils import safe_delete
        
        for file_info in files:
            file_path = Path(file_info['path'])
            try:
                if file_path.exists():
                    safe_delete(file_path, use_trash=True)
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"File not found: {file_path}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error deleting {file_path}: {e}")
                logger.error(f"Error deleting {file_path}: {e}")
        
        return results

