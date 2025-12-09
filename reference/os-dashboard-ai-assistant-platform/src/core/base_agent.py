"""
Core Base Agent - Foundation for all AI Assistant capabilities
Provides the fundamental architecture for autonomous workflow execution
"""

import asyncio
import logging
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Represents a single task in the workflow"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0
    
    def mark_started(self):
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()
    
    def mark_completed(self, result: Any = None):
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result
        self.progress = 100.0
    
    def mark_failed(self, error: str):
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = time.time()

class BaseAgent(ABC):
    """
    Base Agent class providing core functionality for autonomous workflows
    """
    
    def __init__(self, name: str, max_workers: int = 10):
        self.name = name
        self.max_workers = max_workers
        self.logger = self._setup_logger()
        self.task_queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Workflow state management
        self.workflow_state = {}
        self.context = {}
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger(f"agent.{self.name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def add_event_handler(self, event: str, handler: Callable):
        """Add event handler for workflow events"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def emit_event(self, event: str, data: Any = None):
        """Emit an event to all registered handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event}: {e}")
    
    def add_task(self, task: Task) -> str:
        """Add a task to the execution queue"""
        self.task_queue.put((task.priority.value * -1, task.created_at, task))
        self.logger.info(f"Task added: {task.name} (ID: {task.id})")
        self.emit_event("task_added", task)
        return task.id
    
    def create_task(self, name: str, description: str = "", priority: Priority = Priority.MEDIUM,
                   dependencies: List[str] = None, metadata: Dict[str, Any] = None) -> Task:
        """Create a new task"""
        task = Task(
            name=name,
            description=description,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        return task
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].status
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        return None
    
    def get_task_result(self, task_id: str) -> Any:
        """Get the result of a completed task"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].result
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED
                self.logger.info(f"Task cancelled: {task.name}")
                self.emit_event("task_cancelled", task)
                return True
        return False
    
    def wait_for_dependencies(self, task: Task) -> bool:
        """Check if all dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
            if self.completed_tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def execute_workflow(self, tasks: List[Task]) -> Dict[str, Any]:
        """Execute a complete workflow with dependency management"""
        self.logger.info(f"Starting workflow execution with {len(tasks)} tasks")
        
        # Add all tasks to queue
        for task in tasks:
            self.add_task(task)
        
        # Start processing
        self.running = True
        results = {}
        
        try:
            while self.running and (not self.task_queue.empty() or self.active_tasks):
                # Process ready tasks
                ready_tasks = []
                temp_queue = []
                
                # Check queue for ready tasks
                while not self.task_queue.empty():
                    priority, created_at, task = self.task_queue.get()
                    if self.wait_for_dependencies(task):
                        ready_tasks.append(task)
                    else:
                        temp_queue.append((priority, created_at, task))
                
                # Put non-ready tasks back
                for item in temp_queue:
                    self.task_queue.put(item)
                
                # Execute ready tasks
                if ready_tasks:
                    futures = []
                    for task in ready_tasks:
                        if len(self.active_tasks) < self.max_workers:
                            self.active_tasks[task.id] = task
                            task.mark_started()
                            future = self.executor.submit(self._execute_task, task)
                            futures.append((task.id, future))
                    
                    # Wait for completion
                    for task_id, future in futures:
                        try:
                            result = future.result(timeout=300)  # 5 minute timeout
                            task = self.active_tasks[task_id]
                            task.mark_completed(result)
                            results[task_id] = result
                            self.completed_tasks[task_id] = task
                            del self.active_tasks[task_id]
                            self.emit_event("task_completed", task)
                        except Exception as e:
                            task = self.active_tasks[task_id]
                            task.mark_failed(str(e))
                            self.completed_tasks[task_id] = task
                            del self.active_tasks[task_id]
                            self.emit_event("task_failed", task)
                            self.logger.error(f"Task failed: {task.name} - {e}")
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        
        finally:
            self.running = False
        
        self.logger.info("Workflow execution completed")
        return results
    
    def _execute_task(self, task: Task) -> Any:
        """Execute a single task - to be implemented by subclasses"""
        try:
            self.logger.info(f"Executing task: {task.name}")
            result = self.execute_task(task)
            self.logger.info(f"Task completed: {task.name}")
            return result
        except Exception as e:
            self.logger.error(f"Task execution failed: {task.name} - {e}")
            raise
    
    @abstractmethod
    def execute_task(self, task: Task) -> Any:
        """Execute a specific task - must be implemented by subclasses"""
        pass
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get statistics about the current workflow"""
        total_tasks = len(self.active_tasks) + len(self.completed_tasks)
        completed = len([t for t in self.completed_tasks.values() if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in self.completed_tasks.values() if t.status == TaskStatus.FAILED])
        
        return {
            "total_tasks": total_tasks,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": completed,
            "failed_tasks": failed,
            "success_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def shutdown(self):
        """Shutdown the agent and cleanup resources"""
        self.running = False
        self.executor.shutdown(wait=True)
        self.logger.info(f"Agent {self.name} shutdown completed")

class WorkflowBuilder:
    """Builder class for creating complex workflows"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.task_map: Dict[str, Task] = {}
    
    def add_task(self, name: str, description: str = "", priority: Priority = Priority.MEDIUM,
                dependencies: List[str] = None, metadata: Dict[str, Any] = None) -> 'WorkflowBuilder':
        """Add a task to the workflow"""
        task = Task(
            name=name,
            description=description,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        self.tasks.append(task)
        self.task_map[task.id] = task
        return self
    
    def add_dependency(self, task_name: str, depends_on: str) -> 'WorkflowBuilder':
        """Add a dependency between tasks"""
        task = next((t for t in self.tasks if t.name == task_name), None)
        dep_task = next((t for t in self.tasks if t.name == depends_on), None)
        
        if task and dep_task:
            if dep_task.id not in task.dependencies:
                task.dependencies.append(dep_task.id)
        
        return self
    
    def build(self) -> List[Task]:
        """Build and return the workflow"""
        return self.tasks.copy()

# Example usage and testing
if __name__ == "__main__":
    # This would be used by other modules
    pass