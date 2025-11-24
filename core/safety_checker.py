"""Safety validation framework for cleanup operations."""

import os
import psutil
from pathlib import Path
from typing import List, Dict, Set, Optional
from utils.logger import logger
from utils.exceptions import SafetyError, ProcessError
from config.settings import get_settings


class SafetyChecker:
    """Validate operations for safety before execution."""
    
    def __init__(self):
        self.settings = get_settings()
        self.protected_dirs = self._get_protected_directories()
        self.running_processes = set()
    
    def _get_protected_directories(self) -> Set[Path]:
        """Get list of protected system directories."""
        protected = set()
        
        # Windows system directories
        if os.name == 'nt':
            system_drive = Path(os.environ.get('SystemDrive', 'C:'))
            protected.update([
                system_drive / 'Windows',
                system_drive / 'Program Files',
                system_drive / 'Program Files (x86)',
                system_drive / 'ProgramData',
            ])
        
        return protected
    
    def check_process_running(self, process_names: List[str]) -> bool:
        """
        Check if any of the specified processes are running.
        
        Args:
            process_names: List of process names to check
            
        Returns:
            True if any process is running
        """
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(name.lower() in proc_name for name in process_names):
                        self.running_processes.add(proc_name)
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            logger.error(f"Error checking processes: {e}")
            raise ProcessError(f"Failed to check running processes: {e}")
    
    def check_conda_processes(self) -> bool:
        """Check if conda-related processes are running."""
        return self.check_process_running(['conda', 'anaconda', 'python'])
    
    def check_pip_processes(self) -> bool:
        """Check if pip processes are running."""
        return self.check_process_running(['pip', 'python'])
    
    def check_npm_processes(self) -> bool:
        """Check if npm/node processes are running."""
        return self.check_process_running(['npm', 'node', 'yarn'])
    
    def check_docker_processes(self) -> bool:
        """Check if Docker processes are running."""
        return self.check_process_running(['docker', 'dockerd'])
    
    def is_protected_directory(self, path: Path) -> bool:
        """
        Check if a directory is protected.
        
        Args:
            path: Path to check
            
        Returns:
            True if directory is protected
        """
        path = Path(path).resolve()
        
        # Check against protected directories
        for protected in self.protected_dirs:
            try:
                if path.is_relative_to(protected):
                    return True
            except (AttributeError, ValueError):
                # Python < 3.9 compatibility
                try:
                    if str(path).startswith(str(protected)):
                        return True
                except (TypeError, OSError):
                    # Ignore conversion errors
                    pass
        
        return False
    
    def is_system_file(self, path: Path) -> bool:
        """
        Check if a file is a system file.
        
        Args:
            path: Path to check
            
        Returns:
            True if file is a system file
        """
        # Check if in protected directory
        if self.is_protected_directory(path.parent):
            return True
        
        # Check for system file attributes (Windows)
        if os.name == 'nt':
            try:
                import win32api
                import win32con
                attrs = win32api.GetFileAttributes(str(path))
                if attrs & win32con.FILE_ATTRIBUTE_SYSTEM:
                    return True
            except ImportError:
                # win32api not available, skip attribute check
                pass
        
        return False
    
    def validate_delete_operation(self, paths: List[Path], operation_type: str = "general") -> Dict[str, Any]:
        """
        Validate a delete operation for safety.
        
        Args:
            paths: List of paths to delete
            operation_type: Type of operation (conda, pip, system, etc.)
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'safe': True,
            'warnings': [],
            'errors': [],
            'blocked_paths': []
        }
        
        for path in paths:
            path = Path(path).resolve()
            
            # Check if path exists
            if not path.exists():
                results['warnings'].append(f"Path does not exist: {path}")
                continue
            
            # Check for protected directories
            if self.is_protected_directory(path):
                results['safe'] = False
                results['errors'].append(f"Protected directory: {path}")
                results['blocked_paths'].append(path)
                continue
            
            # Check for system files
            if path.is_file() and self.is_system_file(path):
                results['safe'] = False
                results['errors'].append(f"System file: {path}")
                results['blocked_paths'].append(path)
                continue
            
            # Operation-specific checks
            if operation_type == "conda":
                if self.check_conda_processes():
                    results['safe'] = False
                    results['errors'].append("Conda processes are running. Please close them first.")
            
            elif operation_type == "pip":
                if self.check_pip_processes():
                    results['safe'] = False
                    results['errors'].append("Pip processes are running. Please close them first.")
            
            elif operation_type == "npm":
                if self.check_npm_processes():
                    results['safe'] = False
                    results['errors'].append("NPM/Node processes are running. Please close them first.")
            
            elif operation_type == "docker":
                if self.check_docker_processes():
                    results['safe'] = False
                    results['errors'].append("Docker processes are running. Please close them first.")
        
        return results
    
    def can_proceed(self, validation_results: Dict[str, Any]) -> bool:
        """
        Determine if operation can proceed based on validation results.
        
        Args:
            validation_results: Results from validate_delete_operation
            
        Returns:
            True if operation can proceed
        """
        # Cannot proceed if there are errors
        if validation_results['errors']:
            return False
        
        # Can proceed if safe or only warnings
        return validation_results['safe'] or not validation_results['blocked_paths']
    
    def get_safety_level(self, category: str) -> str:
        """
        Get safety level for a category.
        
        Args:
            category: Category name (user_data, caches, temp_files, environments)
            
        Returns:
            Safety level (very_safe, moderate, user_choice)
        """
        return self.settings.get(f'safety_levels.{category}', 'moderate')
    
    def is_protected_item(self, item_type: str, item_name: str) -> bool:
        """
        Check if an item is protected.
        
        Args:
            item_type: Type of item (conda_base, active_env, etc.)
            item_name: Name of the item
            
        Returns:
            True if item is protected
        """
        protected = self.settings.get('protected_items', {})
        
        if item_type == 'conda_base' and item_name == 'base':
            return protected.get('conda_base', True)
        
        if item_type == 'active_env':
            return protected.get('active_env', True)
        
        return False

