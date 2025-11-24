"""Utility functions for formatting file sizes."""


def format_size(size_bytes: int, precision: int = 2) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        precision: Number of decimal places
        
    Returns:
        Formatted size string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.{precision}f} {units[unit_index]}"


def parse_size(size_str: str) -> int:
    """
    Parse human-readable size string to bytes.
    
    Args:
        size_str: Size string (e.g., "1.5 GB", "500 MB")
        
    Returns:
        Size in bytes
    """
    size_str = size_str.strip().upper()
    
    # Extract number and unit
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
    
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)].strip())
                return int(number * multiplier)
            except ValueError:
                raise ValueError(f"Invalid size format: {size_str}")
    
    # Try to parse as plain number (assume bytes)
    try:
        return int(float(size_str))
    except ValueError:
        raise ValueError(f"Invalid size format: {size_str}")

