"""Restore point management and restoration operations."""

import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.logger import logger
from utils.exceptions import RestoreError
from utils.file_utils import ensure_directory
from core.backup_manager import BackupManager


class RestoreManager:
    """Manage restore operations from backup restore points."""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.restore_points_dir = backup_manager.restore_points_dir
        self.metadata = backup_manager.metadata
    
    def list_restore_points(self) -> List[Dict[str, Any]]:
        """
        List all available restore points.
        
        Returns:
            List of restore point dictionaries sorted by timestamp (newest first)
        """
        restore_points = self.metadata.get('restore_points', [])
        
        # Sort by timestamp (newest first)
        restore_points.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
        
        return restore_points
    
    def get_restore_point_details(self, restore_point_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a restore point.
        
        Args:
            restore_point_id: Restore point ID
            
        Returns:
            Restore point details or None if not found
        """
        restore_point_dir = self.restore_points_dir / restore_point_id
        zip_path = restore_point_dir.with_suffix('.zip')
        
        # Check if compressed
        temp_dir = None
        if zip_path.exists():
            # Extract temporarily to read metadata
            temp_dir = restore_point_dir.parent / f"{restore_point_id}_temp"
            try:
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                meta_file = temp_dir / restore_point_id / "metadata.json"
            except Exception as e:
                logger.error(f"Error extracting restore point: {e}")
                if temp_dir and temp_dir.exists():
                    shutil.rmtree(temp_dir)
                return None
        else:
            meta_file = restore_point_dir / "metadata.json"
        
        if not meta_file.exists():
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
            return None
        
        try:
            # Read metadata before cleanup
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata
        except Exception as e:
            logger.error(f"Error reading restore point details: {e}")
            return None
        finally:
            # Cleanup temp directory after reading
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Error cleaning up temp directory: {e}")
    
    def restore_conda_environment(self, restore_point_id: str, env_name: str, 
                                  target_name: Optional[str] = None) -> bool:
        """
        Restore a conda environment from backup.
        
        Args:
            restore_point_id: Restore point ID
            env_name: Original environment name
            target_name: Target environment name (default: original name)
            
        Returns:
            True if successful
        """
        if target_name is None:
            target_name = env_name
        
        restore_point_dir = self.restore_points_dir / restore_point_id
        zip_path = restore_point_dir.with_suffix('.zip')
        
        # Extract if compressed
        extract_dir = None
        if zip_path.exists():
            extract_dir = restore_point_dir.parent / f"{restore_point_id}_temp"
            try:
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.extractall(extract_dir)
                restore_point_dir = extract_dir / restore_point_id
            except Exception as e:
                logger.error(f"Error extracting restore point: {e}")
                if extract_dir and extract_dir.exists():
                    shutil.rmtree(extract_dir)
                raise RestoreError(f"Failed to extract restore point: {e}")
        
        try:
            # Find environment file
            env_file = restore_point_dir / "conda_envs" / f"{env_name}.yml"
            
            if not env_file.exists():
                raise RestoreError(f"Environment file not found: {env_file}")
            
            # Create environment from file
            result = subprocess.run(
                ['conda', 'env', 'create', '--name', target_name, '--file', str(env_file)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"Restored conda environment: {target_name}")
                return True
            else:
                logger.error(f"Failed to restore environment: {result.stderr}")
                raise RestoreError(f"Failed to create environment: {result.stderr}")
        
        finally:
            # Cleanup temp extraction after all operations complete
            if extract_dir and extract_dir.exists():
                try:
                    shutil.rmtree(extract_dir)
                except Exception as e:
                    logger.warning(f"Error cleaning up temp directory: {e}")
    
    def restore_files(self, restore_point_id: str, file_paths: Optional[List[str]] = None,
                     target_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Restore files from backup.
        
        Args:
            restore_point_id: Restore point ID
            file_paths: Specific files to restore (None = restore all)
            target_dir: Target directory for restoration (None = original location)
            
        Returns:
            Dictionary with restoration results
        """
        details = self.get_restore_point_details(restore_point_id)
        if not details:
            raise RestoreError(f"Restore point not found: {restore_point_id}")
        
        results = {
            'restored': [],
            'failed': [],
            'skipped': []
        }
        
        restore_point_dir = self.restore_points_dir / restore_point_id
        zip_path = restore_point_dir.with_suffix('.zip')
        
        # Extract if compressed
        extract_dir = None
        if zip_path.exists():
            extract_dir = restore_point_dir.parent / f"{restore_point_id}_temp"
            try:
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.extractall(extract_dir)
                restore_point_dir = extract_dir / restore_point_id
            except Exception as e:
                logger.error(f"Error extracting restore point: {e}")
                if extract_dir and extract_dir.exists():
                    shutil.rmtree(extract_dir)
                raise RestoreError(f"Failed to extract restore point: {e}")
        
        try:
            items = details.get('items', [])
            
            for item in items:
                original_path = item.get('original_path', '')
                
                # Filter by file_paths if specified
                if file_paths and original_path not in file_paths:
                    continue
                
                item_type = item.get('type', 'file')
                
                if item_type == 'conda_environment':
                    # Skip conda environments (use restore_conda_environment)
                    results['skipped'].append(original_path)
                    continue
                
                # For files/directories, we only have metadata
                # Actual file restoration would require full backup (not just metadata)
                # This is a limitation - we can only restore conda environments fully
                logger.warning(f"Cannot fully restore file from metadata: {original_path}")
                results['skipped'].append(original_path)
        
        finally:
            # Cleanup temp extraction after all operations complete
            if extract_dir and extract_dir.exists():
                try:
                    shutil.rmtree(extract_dir)
                except Exception as e:
                    logger.warning(f"Error cleaning up temp directory: {e}")
        
        return results
    
    def compare_restore_points(self, restore_point_id1: str, restore_point_id2: str) -> Dict[str, Any]:
        """
        Compare two restore points.
        
        Args:
            restore_point_id1: First restore point ID
            restore_point_id2: Second restore point ID
            
        Returns:
            Comparison results
        """
        details1 = self.get_restore_point_details(restore_point_id1)
        details2 = self.get_restore_point_details(restore_point_id2)
        
        if not details1 or not details2:
            raise RestoreError("One or both restore points not found")
        
        items1 = {item.get('original_path'): item for item in details1.get('items', [])}
        items2 = {item.get('original_path'): item for item in details2.get('items', [])}
        
        only_in_1 = set(items1.keys()) - set(items2.keys())
        only_in_2 = set(items2.keys()) - set(items1.keys())
        in_both = set(items1.keys()) & set(items2.keys())
        
        return {
            'restore_point1': restore_point_id1,
            'restore_point2': restore_point_id2,
            'only_in_1': list(only_in_1),
            'only_in_2': list(only_in_2),
            'in_both': list(in_both),
            'total_items_1': len(items1),
            'total_items_2': len(items2)
        }
    
    def delete_restore_point(self, restore_point_id: str):
        """Delete a restore point."""
        self.backup_manager.delete_restore_point(restore_point_id)

