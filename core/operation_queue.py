"""Operation queue system for batch cleanup operations."""

from typing import List, Dict, Any, Callable, Optional
from enum import Enum
from datetime import datetime
from utils.logger import logger
from utils.exceptions import OperationError


class OperationStatus(Enum):
    """Operation status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Operation:
    """Represents a single cleanup operation."""
    
    def __init__(self, operation_id: str, operation_type: str, 
                 items: List[Dict[str, Any]], handler: Callable):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.items = items
        self.handler = handler
        self.status = OperationStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.result = None
    
    def execute(self) -> Any:
        """Execute the operation."""
        self.status = OperationStatus.IN_PROGRESS
        self.started_at = datetime.now()
        
        try:
            self.result = self.handler(self.items)
            self.status = OperationStatus.COMPLETED
            self.completed_at = datetime.now()
            logger.info(f"Operation {self.operation_id} completed successfully")
            return self.result
        except Exception as e:
            self.status = OperationStatus.FAILED
            self.error = str(e)
            self.completed_at = datetime.now()
            logger.error(f"Operation {self.operation_id} failed: {e}")
            raise OperationError(f"Operation failed: {e}")
    
    def cancel(self):
        """Cancel the operation."""
        if self.status == OperationStatus.PENDING:
            self.status = OperationStatus.CANCELLED
            self.completed_at = datetime.now()
            logger.info(f"Operation {self.operation_id} cancelled")
        else:
            logger.warning(f"Cannot cancel operation {self.operation_id} - status: {self.status}")


class OperationQueue:
    """Queue system for managing batch cleanup operations."""
    
    def __init__(self):
        self.queue: List[Operation] = []
        self.completed: List[Operation] = []
        self._next_id = 0
        self._lock = False
    
    def add_operation(self, operation_type: str, items: List[Dict[str, Any]], 
                     handler: Callable) -> str:
        """
        Add an operation to the queue.
        
        Args:
            operation_type: Type of operation (conda, pip, system, etc.)
            items: List of items to process
            handler: Function to handle the operation
            
        Returns:
            Operation ID
        """
        operation_id = f"OP_{self._next_id:06d}"
        self._next_id += 1
        
        operation = Operation(operation_id, operation_type, items, handler)
        self.queue.append(operation)
        
        logger.info(f"Added operation {operation_id} to queue: {operation_type}")
        return operation_id
    
    def execute_next(self) -> Optional[Any]:
        """
        Execute the next pending operation.
        
        Returns:
            Operation result or None if queue is empty
        """
        if self._lock:
            logger.warning("Queue is locked")
            return None
        
        if not self.queue:
            return None
        
        # Find next pending operation
        operation = None
        for op in self.queue:
            if op.status == OperationStatus.PENDING:
                operation = op
                break
        
        if not operation:
            return None
        
        try:
            self._lock = True
            result = operation.execute()
            self.queue.remove(operation)
            self.completed.append(operation)
            return result
        finally:
            self._lock = False
    
    def execute_all(self) -> List[Any]:
        """
        Execute all pending operations in sequence.
        
        Returns:
            List of operation results
        """
        results = []
        
        while self.queue:
            result = self.execute_next()
            if result is not None:
                results.append(result)
        
        return results
    
    def cancel_operation(self, operation_id: str) -> bool:
        """
        Cancel a pending operation.
        
        Args:
            operation_id: Operation ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        for operation in self.queue:
            if operation.operation_id == operation_id:
                operation.cancel()
                self.queue.remove(operation)
                self.completed.append(operation)
                return True
        
        return False
    
    def cancel_all(self):
        """Cancel all pending operations."""
        for operation in self.queue[:]:
            if operation.status == OperationStatus.PENDING:
                operation.cancel()
                self.queue.remove(operation)
                self.completed.append(operation)
    
    def get_operation(self, operation_id: str) -> Optional[Operation]:
        """Get operation by ID."""
        for operation in self.queue + self.completed:
            if operation.operation_id == operation_id:
                return operation
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        pending = sum(1 for op in self.queue if op.status == OperationStatus.PENDING)
        in_progress = sum(1 for op in self.queue if op.status == OperationStatus.IN_PROGRESS)
        completed = sum(1 for op in self.completed if op.status == OperationStatus.COMPLETED)
        failed = sum(1 for op in self.completed if op.status == OperationStatus.FAILED)
        
        return {
            'total_pending': pending,
            'in_progress': in_progress,
            'total_completed': completed,
            'total_failed': failed,
            'queue_length': len(self.queue)
        }
    
    def clear_completed(self, keep_recent: int = 10):
        """
        Clear completed operations, keeping recent ones.
        
        Args:
            keep_recent: Number of recent operations to keep
        """
        # Sort by completion time (newest first)
        self.completed.sort(key=lambda x: x.completed_at or datetime.min, reverse=True)
        
        # Keep only recent ones
        self.completed = self.completed[:keep_recent]
        logger.info(f"Cleared old completed operations, kept {len(self.completed)} recent")

