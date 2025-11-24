"""File operation utilities."""

import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import send2trash

from utils.logger import logger
from utils.exceptions import OperationError


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get comprehensive information about a file or directory.
    
    Args:
        file_path: Path to file or directory
        
    Returns:
        Dictionary with file information
    """
    try:
        stat = file_path.stat()
        
        info = {
            'path': str(file_path),
            'name': file_path.name,
            'size': stat.st_size if file_path.is_file() else get_directory_size(file_path),
            'is_file': file_path.is_file(),
            'is_dir': file_path.is_dir(),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'accessed': datetime.fromtimestamp(stat.st_atime),
            'permissions': oct(stat.st_mode)[-3:],
        }
        
        # Add hash for files
        if file_path.is_file():
            info['hash'] = calculate_file_hash(file_path)
        
        return info
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        raise OperationError(f"Failed to get file info: {e}")


def get_directory_size(directory: Path) -> int:
    """
    Calculate total size of a directory.
    
    Args:
        directory: Path to directory
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    try:
        for item in directory.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except (OSError, PermissionError):
                    # Skip files we can't access
                    pass
    except (OSError, PermissionError) as e:
        logger.warning(f"Error calculating directory size for {directory}: {e}")
    
    return total_size


def calculate_file_hash(file_path: Path, algorithm: str = 'md5', chunk_size: int = 8192) -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('md5', 'sha256')
        chunk_size: Chunk size for reading large files
        
    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        raise OperationError(f"Failed to calculate file hash: {e}")


def safe_delete(file_path: Path, use_trash: bool = True) -> bool:
    """
    Safely delete a file or directory (moves to recycle bin by default).
    
    Args:
        file_path: Path to file or directory
        use_trash: If True, move to recycle bin; if False, permanently delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if use_trash:
            send2trash.send2trash(str(file_path))
            logger.info(f"Moved to recycle bin: {file_path}")
        else:
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
            logger.info(f"Permanently deleted: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting {file_path}: {e}")
        raise OperationError(f"Failed to delete {file_path}: {e}")


def ensure_directory(directory: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory
        
    Returns:
        Path object of the directory
    """
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def copy_file_metadata(source: Path, dest: Path) -> bool:
    """
    Copy file metadata (timestamps, permissions) from source to destination.
    
    Args:
        source: Source file path
        dest: Destination file path
        
    Returns:
        True if successful
    """
    try:
        source_stat = source.stat()
        
        # Copy timestamps
        os.utime(dest, (source_stat.st_atime, source_stat.st_mtime))
        
        # Copy permissions (if possible)
        try:
            os.chmod(dest, source_stat.st_mode)
        except (OSError, PermissionError):
            # Permissions might not be copyable on all systems
            pass
        
        return True
    except Exception as e:
        logger.warning(f"Could not copy metadata from {source} to {dest}: {e}")
        return False

