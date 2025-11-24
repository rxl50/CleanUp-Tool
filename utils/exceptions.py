"""Custom exceptions for CleanUp tool."""


class CleanUpError(Exception):
    """Base exception for all CleanUp errors."""
    pass


class BackupError(CleanUpError):
    """Exception raised when backup operations fail."""
    pass


class RestoreError(CleanUpError):
    """Exception raised when restore operations fail."""
    pass


class SafetyError(CleanUpError):
    """Exception raised when safety checks fail."""
    pass


class OperationError(CleanUpError):
    """Exception raised when cleanup operations fail."""
    pass


class ConfigurationError(CleanUpError):
    """Exception raised when configuration is invalid."""
    pass


class ProcessError(CleanUpError):
    """Exception raised when process detection fails."""
    pass

