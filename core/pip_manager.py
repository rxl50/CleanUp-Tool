"""Pip cache management."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import logger
from utils.exceptions import OperationError
from utils.file_utils import get_directory_size
from core.safety_checker import SafetyChecker
from core.backup_manager import BackupManager


class PipManager:
    """Manage pip cache operations."""
    
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.backup_manager = backup_manager
        self.safety_checker = SafetyChecker()
        self.pip_path = self._find_pip()
    
    def _find_pip(self) -> Optional[str]:
        """Find pip executable."""
        try:
            result = subprocess.run(
                ['pip', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'pip'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try python -m pip
        try:
            result = subprocess.run(
                ['python', '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'python -m pip'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        logger.warning("Pip not found")
        return None
    
    def is_available(self) -> bool:
        """Check if pip is available."""
        return self.pip_path is not None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get pip cache information.
        
        Returns:
            Dictionary with cache info
        """
        if not self.is_available():
            return {'available': False}
        
        try:
            result = subprocess.run(
                self.pip_path.split() + ['cache', 'info'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"Error getting cache info: {result.stderr}")
                return {'available': True, 'size': 0, 'location': ''}
            
            # Parse output
            info = {'available': True, 'size': 0, 'location': ''}
            
            for line in result.stdout.split('\n'):
                if 'Location:' in line:
                    info['location'] = line.split('Location:')[1].strip()
                elif 'Size:' in line:
                    size_str = line.split('Size:')[1].strip()
                    # Try to parse size (format: "123.4 MB")
                    try:
                        # Simple parsing - can be enhanced
                        parts = size_str.split()
                        if len(parts) >= 2:
                            value = float(parts[0])
                            unit = parts[1].upper()
                            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
                            info['size'] = int(value * multipliers.get(unit, 1))
                    except (ValueError, IndexError, KeyError):
                        # Ignore parsing errors, will use directory size calculation instead
                        pass
            
            # If location found, calculate actual size
            if info['location']:
                cache_path = Path(info['location'])
                if cache_path.exists():
                    try:
                        info['size'] = get_directory_size(cache_path)
                    except Exception as e:
                        logger.warning(f"Error calculating cache size: {e}")
            
            return info
            
        except FileNotFoundError:
            logger.error("Pip executable not found")
            return {'available': False, 'size': 0, 'location': ''}
        except subprocess.TimeoutExpired:
            logger.error("Timeout getting pip cache info")
            return {'available': True, 'size': 0, 'location': ''}
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {'available': True, 'size': 0, 'location': ''}
    
    def list_cached_packages(self) -> List[str]:
        """
        List packages in pip cache.
        
        Returns:
            List of package names
        """
        if not self.is_available():
            return []
        
        try:
            result = subprocess.run(
                self.pip_path.split() + ['cache', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Error listing cache: {result.stderr}")
                return []
            
            # Parse package names from output
            packages = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('Package'):
                    # Extract package name (first part before version)
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
            
            return list(set(packages))  # Remove duplicates
            
        except FileNotFoundError:
            logger.error("Pip executable not found")
            return []
        except subprocess.TimeoutExpired:
            logger.error("Timeout listing pip cache")
            return []
        except Exception as e:
            logger.error(f"Error listing cache: {e}")
            return []
    
    def purge_cache(self, create_backup: bool = True) -> bool:
        """
        Purge entire pip cache.
        
        Args:
            create_backup: Whether to create backup first
            
        Returns:
            True if successful
        """
        if not self.is_available():
            raise OperationError("Pip is not available")
        
        # Check if processes are running
        if self.safety_checker.check_pip_processes():
            raise OperationError("Pip processes are running. Please close them first.")
        
        # Get cache info before deletion
        cache_info = self.get_cache_info()
        
        # Create backup if requested
        restore_point_id = None
        if create_backup and self.backup_manager:
            try:
                # Store cache info
                items = [{
                    'type': 'pip_cache',
                    'name': 'pip_cache',
                    'path': cache_info.get('location', ''),
                    'info': cache_info
                }]
                restore_point_id = self.backup_manager.create_restore_point('pip', items)
                logger.info(f"Created backup before cache purge: {restore_point_id}")
            except Exception as e:
                if self.backup_manager.settings.get('backup_settings.mandatory_backup', True):
                    raise OperationError(f"Backup failed, operation cancelled: {e}")
                else:
                    logger.warning(f"Backup failed but not mandatory: {e}")
        
        # Purge cache
        try:
            result = subprocess.run(
                self.pip_path.split() + ['cache', 'purge'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("Purged pip cache")
                return True
            else:
                logger.error(f"Error purging cache: {result.stderr}")
                raise OperationError(f"Failed to purge cache: {result.stderr}")
                
        except FileNotFoundError:
            raise OperationError("Pip executable not found")
        except subprocess.TimeoutExpired:
            raise OperationError("Timeout purging cache")
        except Exception as e:
            logger.error(f"Error purging cache: {e}")
            raise OperationError(f"Failed to purge cache: {e}")
    
    def remove_package(self, package_name: str) -> bool:
        """
        Remove a specific package from cache.
        
        Args:
            package_name: Package name to remove
            
        Returns:
            True if successful
        """
        if not self.is_available():
            raise OperationError("Pip is not available")
        
        # Input validation
        if not package_name or not package_name.strip():
            raise OperationError("Package name cannot be empty")
        
        package_name = package_name.strip()
        
        try:
            result = subprocess.run(
                self.pip_path.split() + ['cache', 'remove', package_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"Removed package from cache: {package_name}")
                return True
            else:
                logger.warning(f"Error removing package: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("Pip executable not found")
            return False
        except Exception as e:
            logger.error(f"Error removing package {package_name}: {e}")
            return False

