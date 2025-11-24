"""Backup system for cleanup operations."""

import json
import shutil
import subprocess
import zipfile
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.logger import logger
from utils.exceptions import BackupError
from utils.file_utils import get_file_info, ensure_directory
from config.settings import get_settings


class BackupManager:
    """Manage backups and restore points."""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        ensure_directory(self.backup_dir)
        
        self.restore_points_dir = self.backup_dir / "restore_points"
        ensure_directory(self.restore_points_dir)
        
        self.metadata_file = self.backup_dir / "metadata.json"
        self.settings = get_settings()
        
        # Load or create metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load backup metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {'restore_points': [], 'settings': {}}
        else:
            return {
                'restore_points': [],
                'settings': {
                    'retention_days': self.settings.get('backup_settings.retention_days', 30),
                    'max_restore_points': self.settings.get('backup_settings.max_restore_points', 50),
                    'auto_cleanup': self.settings.get('backup_settings.auto_cleanup', True)
                }
            }
    
    def _save_metadata(self):
        """Save backup metadata."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise BackupError(f"Failed to save backup metadata: {e}")
    
    def create_restore_point(self, operation_type: str, items: List[Dict[str, Any]]) -> str:
        """
        Create a restore point before deletion.
        
        Args:
            operation_type: Type of operation (conda, pip, system, etc.)
            items: List of items to backup (each with 'type', 'path', 'info')
            
        Returns:
            Restore point ID
        """
        # Generate unique restore point ID (timestamp + UUID to prevent collisions)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
        restore_point_id = f"RP_{timestamp}_{unique_id}"
        
        # Ensure directory doesn't already exist (very unlikely but check anyway)
        restore_point_dir = self.restore_points_dir / restore_point_id
        counter = 1
        while restore_point_dir.exists():
            restore_point_id = f"RP_{timestamp}_{unique_id}_{counter}"
            restore_point_dir = self.restore_points_dir / restore_point_id
            counter += 1
        
        ensure_directory(restore_point_dir)
        
        # Create restore point structure
        restore_point_data = {
            'id': restore_point_id,
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'items_backed_up': {
                'total_count': len(items),
                'total_size_bytes': 0
            },
            'backup_location': str(restore_point_dir),
            'status': 'in_progress',
            'items': []
        }
        
        total_size = 0
        
        try:
            # Backup each item
            for item in items:
                item_backup = self._backup_item(item, restore_point_dir)
                restore_point_data['items'].append(item_backup)
                total_size += item_backup.get('size_bytes', 0)
            
            restore_point_data['items_backed_up']['total_size_bytes'] = total_size
            restore_point_data['status'] = 'complete'
            
            # Save restore point metadata
            restore_point_meta_file = restore_point_dir / "metadata.json"
            with open(restore_point_meta_file, 'w', encoding='utf-8') as f:
                json.dump(restore_point_data, f, indent=2, default=str)
            
            # Add to main metadata
            self.metadata['restore_points'].append({
                'id': restore_point_id,
                'timestamp': restore_point_data['timestamp'],
                'operation_type': operation_type,
                'items_count': len(items),
                'total_size_bytes': total_size,
                'backup_location': str(restore_point_dir),
                'status': 'complete'
            })
            
            # Compress if enabled
            if self.settings.get('backup_settings.compress_backups', True):
                self._compress_restore_point(restore_point_dir)
            
            # Verify backup
            if self.settings.get('backup_settings.verify_backups', True):
                if not self.verify_backup(restore_point_id):
                    raise BackupError(f"Backup verification failed for {restore_point_id}")
            
            # Cleanup old restore points
            if self.settings.get('backup_settings.auto_cleanup', True):
                self.cleanup_old_restore_points()
            
            self._save_metadata()
            logger.info(f"Created restore point: {restore_point_id}")
            
            return restore_point_id
            
        except Exception as e:
            restore_point_data['status'] = 'failed'
            restore_point_data['error'] = str(e)
            logger.error(f"Error creating restore point: {e}")
            raise BackupError(f"Failed to create restore point: {e}")
    
    def _backup_item(self, item: Dict[str, Any], restore_point_dir: Path) -> Dict[str, Any]:
        """
        Backup a single item.
        
        Args:
            item: Item to backup (must have 'type' and 'path')
            restore_point_dir: Directory for restore point
            
        Returns:
            Backup information dictionary
        """
        item_type = item.get('type', 'file')
        item_path_str = item.get('path', '')
        
        # Validate path
        if not item_path_str:
            backup_info = {
                'type': item_type,
                'original_path': '',
                'backed_up': False,
                'size_bytes': 0,
                'error': 'Empty path provided'
            }
            return backup_info
        
        item_path = Path(item_path_str)
        
        backup_info = {
            'type': item_type,
            'original_path': str(item_path),
            'backed_up': False,
            'size_bytes': 0
        }
        
        try:
            if item_type == 'conda_environment':
                # Export conda environment
                env_name = item.get('name', '')
                env_file = restore_point_dir / "conda_envs" / f"{env_name}.yml"
                ensure_directory(env_file.parent)
                
                # Run conda env export
                result = subprocess.run(
                    ['conda', 'env', 'export', '--name', env_name, '--no-builds'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    backup_info['backed_up'] = True
                    backup_info['backup_file'] = str(env_file)
                    backup_info['size_bytes'] = env_file.stat().st_size
                else:
                    logger.warning(f"Failed to export conda environment {env_name}")
                    backup_info['error'] = result.stderr
            
            elif item_type == 'file' or item_type == 'directory':
                # Store file metadata
                if item_path.exists():
                    file_info = get_file_info(item_path)
                    backup_info.update(file_info)
                    backup_info['backed_up'] = True
                    
                    # Store metadata
                    metadata_file = restore_point_dir / "file_metadata" / f"{item_path.name}.json"
                    ensure_directory(metadata_file.parent)
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(file_info, f, indent=2, default=str)
                    backup_info['backup_file'] = str(metadata_file)
            
            else:
                # Generic metadata backup
                backup_info['metadata'] = item.get('info', {})
                backup_info['backed_up'] = True
        
        except Exception as e:
            logger.error(f"Error backing up item {item_path}: {e}")
            backup_info['error'] = str(e)
        
        return backup_info
    
    def _compress_restore_point(self, restore_point_dir: Path):
        """Compress restore point to save space."""
        zip_path = restore_point_dir.with_suffix('.zip')
        
        try:
            # Create zip file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in restore_point_dir.rglob('*'):
                    if file.is_file():
                        zipf.write(file, file.relative_to(restore_point_dir))
            
            # Verify zip file was created and is valid
            if not zip_path.exists():
                raise BackupError("Zip file was not created")
            
            # Test zip file integrity
            try:
                with zipfile.ZipFile(zip_path, 'r') as test_zip:
                    test_zip.testzip()
            except zipfile.BadZipFile:
                raise BackupError("Created zip file is corrupted")
            
            # Only delete original directory after successful compression and verification
            shutil.rmtree(restore_point_dir)
            logger.debug(f"Compressed restore point: {zip_path}")
            
        except Exception as e:
            # If compression failed, ensure we don't lose data
            if zip_path.exists():
                try:
                    zip_path.unlink()  # Remove corrupted zip
                except Exception:
                    pass
            logger.warning(f"Failed to compress restore point: {e}")
            # Original directory is preserved, so restore point is still usable
    
    def verify_backup(self, restore_point_id: str) -> bool:
        """
        Verify backup integrity.
        
        Args:
            restore_point_id: Restore point ID to verify
            
        Returns:
            True if backup is valid
        """
        restore_point_dir = self.restore_points_dir / restore_point_id
        
        # Check if compressed
        zip_path = restore_point_dir.with_suffix('.zip')
        if zip_path.exists():
            # Verify zip file
            try:
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.testzip()
                return True
            except Exception as e:
                logger.error(f"Backup verification failed: {e}")
                return False
        
        # Check if directory exists and has metadata
        if restore_point_dir.exists():
            meta_file = restore_point_dir / "metadata.json"
            return meta_file.exists()
        
        return False
    
    def get_backup_size(self, restore_point_id: str) -> int:
        """Get size of a restore point in bytes."""
        restore_point_dir = self.restore_points_dir / restore_point_id
        zip_path = restore_point_dir.with_suffix('.zip')
        
        if zip_path.exists():
            return zip_path.stat().st_size
        elif restore_point_dir.exists():
            total = 0
            for file in restore_point_dir.rglob('*'):
                if file.is_file():
                    total += file.stat().st_size
            return total
        
        return 0
    
    def cleanup_old_restore_points(self):
        """Remove old restore points based on retention policy."""
        retention_days = self.settings.get('backup_settings.retention_days', 30)
        max_points = self.settings.get('backup_settings.max_restore_points', 50)
        
        cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)
        
        # Filter old restore points
        valid_points = []
        for point in self.metadata.get('restore_points', []):
            try:
                point_time = datetime.fromisoformat(point['timestamp']).timestamp()
                if point_time > cutoff_date:
                    valid_points.append(point)
            except (ValueError, KeyError):
                continue
        
        # Limit to max restore points
        if len(valid_points) > max_points:
            # Sort by timestamp (oldest first)
            valid_points.sort(key=lambda x: x.get('timestamp', ''))
            valid_points = valid_points[-max_points:]
        
        # Remove old restore points
        removed_count = 0
        for point in self.metadata.get('restore_points', []):
            if point not in valid_points:
                restore_point_id = point['id']
                self.delete_restore_point(restore_point_id)
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old restore points")
            self._save_metadata()
    
    def delete_restore_point(self, restore_point_id: str):
        """Delete a restore point."""
        restore_point_dir = self.restore_points_dir / restore_point_id
        zip_path = restore_point_dir.with_suffix('.zip')
        
        try:
            if zip_path.exists():
                zip_path.unlink()
            elif restore_point_dir.exists():
                shutil.rmtree(restore_point_dir)
            
            # Remove from metadata
            self.metadata['restore_points'] = [
                p for p in self.metadata.get('restore_points', [])
                if p.get('id') != restore_point_id
            ]
            self._save_metadata()
            logger.info(f"Deleted restore point: {restore_point_id}")
        except Exception as e:
            logger.error(f"Error deleting restore point {restore_point_id}: {e}")
            raise BackupError(f"Failed to delete restore point: {e}")

