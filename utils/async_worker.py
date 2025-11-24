"""Async operation handler for non-blocking operations."""

import threading
from typing import Callable, Any, Optional
from queue import Queue, Empty
from utils.logger import logger


class AsyncWorker:
    """Handle async operations in background threads."""
    
    def __init__(self):
        self.threads = []
        self.results = {}
        self.callbacks = {}
        self._next_id = 0
        self._lock = threading.Lock()
    
    def execute(self, func: Callable, *args, callback: Optional[Callable] = None, 
                error_callback: Optional[Callable] = None, **kwargs) -> int:
        """
        Execute a function in a background thread.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            callback: Callback function called with result on success
            error_callback: Callback function called with exception on error
            **kwargs: Keyword arguments for function
            
        Returns:
            Operation ID
        """
        with self._lock:
            op_id = self._next_id
            self._next_id += 1
        
        def worker():
            try:
                result = func(*args, **kwargs)
                self.results[op_id] = result
                if callback:
                    # Check if we're in a PyQt5 context
                    try:
                        from PyQt5.QtCore import QTimer
                        # Use QTimer to post callback to main thread
                        QTimer.singleShot(0, lambda: callback(result))
                    except ImportError:
                        # Not in PyQt5 context, call directly
                        callback(result)
            except Exception as e:
                logger.error(f"Error in async operation {op_id}: {e}")
                self.results[op_id] = None
                if error_callback:
                    try:
                        from PyQt5.QtCore import QTimer
                        QTimer.singleShot(0, lambda: error_callback(e))
                    except ImportError:
                        error_callback(e)
            finally:
                # Clean up thread reference after completion
                with self._lock:
                    if thread in self.threads:
                        # Thread will be removed in next cleanup call
                        pass
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        with self._lock:
            self.threads.append(thread)
            # Periodic cleanup of completed threads
            if len(self.threads) > 50:
                self.cleanup()
        
        return op_id
    
    def get_result(self, op_id: int, timeout: Optional[float] = None) -> Any:
        """
        Get result from async operation.
        
        Args:
            op_id: Operation ID
            timeout: Maximum time to wait (None = wait indefinitely)
            
        Returns:
            Operation result or None if not available
        """
        # Wait for thread to complete
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=timeout)
        
        return self.results.get(op_id)
    
    def is_complete(self, op_id: int) -> bool:
        """Check if operation is complete."""
        return op_id in self.results
    
    def cleanup(self):
        """Clean up completed threads."""
        with self._lock:
            # Remove completed threads
            self.threads = [t for t in self.threads if t.is_alive()]
            # Clean up old results (keep last 100)
            if len(self.results) > 100:
                # Remove oldest results
                keys_to_remove = sorted(self.results.keys())[:-100]
                for key in keys_to_remove:
                    self.results.pop(key, None)


class ProgressWorker(AsyncWorker):
    """Async worker with progress tracking."""
    
    def __init__(self):
        super().__init__()
        self.progress = {}
        self.progress_callbacks = {}
    
    def execute_with_progress(self, func: Callable, *args, 
                             progress_callback: Optional[Callable] = None,
                             callback: Optional[Callable] = None,
                             error_callback: Optional[Callable] = None,
                             **kwargs) -> int:
        """
        Execute function with progress tracking.
        
        Args:
            func: Function that accepts progress_queue parameter
            *args: Positional arguments
            progress_callback: Called with (current, total, message) updates
            callback: Called on completion
            error_callback: Called on error
            **kwargs: Keyword arguments
            
        Returns:
            Operation ID
        """
        with self._lock:
            op_id = self._next_id
            self._next_id += 1
        
        progress_queue = Queue()
        self.progress[op_id] = {'current': 0, 'total': 0, 'message': ''}
        
        def progress_monitor():
            """Monitor progress queue and update callbacks."""
            while True:
                try:
                    update = progress_queue.get(timeout=0.1)
                    if update is None:  # Sentinel value for completion
                        break
                    
                    current, total, message = update
                    self.progress[op_id] = {
                        'current': current,
                        'total': total,
                        'message': message
                    }
                    
                    if progress_callback:
                        progress_callback(current, total, message)
                except Empty:
                    continue
        
        def worker():
            try:
                # Start progress monitor
                monitor_thread = threading.Thread(target=progress_monitor, daemon=True)
                monitor_thread.start()
                
                # Execute function with progress queue
                result = func(*args, progress_queue=progress_queue, **kwargs)
                
                # Signal completion
                progress_queue.put(None)
                monitor_thread.join(timeout=1)
                
                self.results[op_id] = result
                if callback:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in progress operation {op_id}: {e}")
                self.results[op_id] = None
                if error_callback:
                    error_callback(e)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        self.threads.append(thread)
        
        return op_id
    
    def get_progress(self, op_id: int) -> dict:
        """Get current progress for operation."""
        return self.progress.get(op_id, {'current': 0, 'total': 0, 'message': ''})

