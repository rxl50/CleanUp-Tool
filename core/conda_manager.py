"""Anaconda environment management."""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.logger import logger
from utils.exceptions import OperationError
from utils.file_utils import get_directory_size
from core.safety_checker import SafetyChecker
from core.backup_manager import BackupManager


class CondaManager:
    """Manage Anaconda environments and operations."""
    
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.backup_manager = backup_manager
        self.safety_checker = SafetyChecker()
        self.conda_path = self._find_conda()
    
    def _find_conda(self) -> Optional[str]:
        """Find conda executable."""
        try:
            result = subprocess.run(
                ['conda', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'conda'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try common conda paths
        common_paths = [
            Path.home() / 'anaconda3' / 'Scripts' / 'conda.exe',
            Path.home() / 'miniconda3' / 'Scripts' / 'conda.exe',
            Path('C:/Anaconda3/Scripts/conda.exe'),
            Path('C:/Miniconda3/Scripts/conda.exe'),
        ]
        
        for path in common_paths:
            if path.exists():
                return str(path)
        
        logger.warning("Conda not found")
        return None
    
    def is_available(self) -> bool:
        """Check if conda is available."""
        return self.conda_path is not None
    
    def list_environments(self) -> List[Dict[str, Any]]:
        """
        List all conda environments.
        
        Returns:
            List of environment dictionaries
        """
        if not self.is_available():
            return []
        
        try:
            result = subprocess.run(
                [self.conda_path, 'env', 'list', '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Error listing environments: {result.stderr}")
                return []
            
            data = json.loads(result.stdout)
            environments = []
            
            # Get active environment
            active_env = self.get_active_environment()
            
            for env in data.get('envs', []):
                env_path = Path(env)
                env_name = env_path.name
                
                # Skip if it's the base environment path
                if env_name in ['base', 'root'] or 'base' in str(env_path):
                    env_name = 'base'
                
                # Calculate size
                try:
                    size = get_directory_size(env_path)
                except Exception as e:
                    logger.warning(f"Error calculating size for {env_name}: {e}")
                    size = 0
                
                is_active = (env_name == active_env)
                is_base = (env_name == 'base')
                
                environments.append({
                    'name': env_name,
                    'path': str(env_path),
                    'size': size,
                    'is_active': is_active,
                    'is_base': is_base,
                    'protected': is_active or is_base
                })
            
            return environments
            
        except FileNotFoundError:
            logger.error("Conda executable not found")
            return []
        except subprocess.TimeoutExpired:
            logger.error("Timeout listing conda environments")
            return []
        except Exception as e:
            logger.error(f"Error listing environments: {e}")
            return []
    
    def get_active_environment(self) -> Optional[str]:
        """Get name of active conda environment."""
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(
                [self.conda_path, 'info', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                active_prefix = data.get('active_prefix', '')
                if active_prefix:
                    return Path(active_prefix).name
        except FileNotFoundError:
            logger.warning("Conda executable not found")
        except Exception as e:
            logger.warning(f"Error getting active environment: {e}")
        
        return None
    
    def export_environment(self, env_name: str, output_file: Path) -> bool:
        """
        Export conda environment to YAML file.
        
        Args:
            env_name: Environment name
            output_file: Output file path
            
        Returns:
            True if successful
        """
        if not self.is_available():
            return False
        
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            result = subprocess.run(
                [self.conda_path, 'env', 'export', '--name', env_name, '--no-builds'],
                stdout=open(output_file, 'w', encoding='utf-8'),
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"Exported environment {env_name} to {output_file}")
                return True
            else:
                logger.error(f"Error exporting environment: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("Conda executable not found")
            return False
        except Exception as e:
            logger.error(f"Error exporting environment {env_name}: {e}")
            return False
    
    def remove_environment(self, env_name: str, create_backup: bool = True) -> bool:
        """
        Remove a conda environment.
        
        Args:
            env_name: Environment name
            create_backup: Whether to create backup first
            
        Returns:
            True if successful
        """
        if not self.is_available():
            raise OperationError("Conda is not available")
        
        # Input validation
        if not env_name or not env_name.strip():
            raise OperationError("Environment name cannot be empty")
        
        env_name = env_name.strip()
        
        # Check for invalid characters (conda environment names have restrictions)
        if any(char in env_name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            raise OperationError(f"Environment name contains invalid characters: {env_name}")
        
        # Safety checks
        active_env = self.get_active_environment()
        if env_name == active_env:
            raise OperationError(f"Cannot delete active environment: {env_name}")
        
        if env_name == 'base':
            raise OperationError("Cannot delete base environment")
        
        # Check if processes are running
        if self.safety_checker.check_conda_processes():
            raise OperationError("Conda processes are running. Please close them first.")
        
        # Create backup if requested
        restore_point_id = None
        if create_backup and self.backup_manager:
            try:
                items = [{
                    'type': 'conda_environment',
                    'name': env_name,
                    'path': '',  # Path will be determined from env list
                }]
                restore_point_id = self.backup_manager.create_restore_point('conda', items)
                logger.info(f"Created backup before deletion: {restore_point_id}")
            except Exception as e:
                if self.backup_manager.settings.get('backup_settings.mandatory_backup', True):
                    raise OperationError(f"Backup failed, operation cancelled: {e}")
                else:
                    logger.warning(f"Backup failed but not mandatory: {e}")
        
        # Remove environment
        try:
            result = subprocess.run(
                [self.conda_path, 'env', 'remove', '--name', env_name, '--yes'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"Removed conda environment: {env_name}")
                return True
            else:
                logger.error(f"Error removing environment: {result.stderr}")
                raise OperationError(f"Failed to remove environment: {result.stderr}")
                
        except FileNotFoundError:
            raise OperationError("Conda executable not found")
        except subprocess.TimeoutExpired:
            raise OperationError("Timeout removing environment")
        except Exception as e:
            logger.error(f"Error removing environment {env_name}: {e}")
            raise OperationError(f"Failed to remove environment: {e}")

