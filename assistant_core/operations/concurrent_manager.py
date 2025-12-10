"""
Concurrent Operations Manager
Parallel processing, batch operations, and background task management
"""

import asyncio
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
import time
import logging
import queue
import json
from datetime import datetime
import uuid
import signal
import os
from contextlib import contextmanager


@dataclass
class ConcurrentTask:
    """Represents a task for concurrent execution"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    function: Callable = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 1  # Higher number = higher priority
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed, cancelled


@dataclass
class BatchOperation:
    """Represents a batch of related operations"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    tasks: List[ConcurrentTask] = field(default_factory=list)
    batch_size: int = 10
    parallel_limit: int = 5
    fail_fast: bool = False
    progress_callback: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)
    status: str = "pending"


class ConcurrentOperationsManager:
    """
    Advanced concurrent operations manager with multiple execution strategies
    """

    def __init__(self, max_workers: int = None, max_processes: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.max_processes = max_processes or os.cpu_count() or 1
        self.logger = logging.getLogger(__name__)

        # Executors
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=self.max_processes)

        # Task management
        self.active_tasks: Dict[str, ConcurrentTask] = {}
        self.completed_tasks: Dict[str, ConcurrentTask] = {}
        self.task_queue = queue.PriorityQueue()

        # Batch operations
        self.active_batches: Dict[str, BatchOperation] = {}

        # Background processing
        self.background_processor = None
        self.shutdown_event = threading.Event()

        # Performance monitoring
        self.performance_stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
        }

        self._start_background_processor()

    def _start_background_processor(self):
        """Start background task processor"""

        def process_tasks():
            while not self.shutdown_event.is_set():
                try:
                    # Get task from queue with timeout
                    try:
                        priority, timestamp, task = self.task_queue.get(timeout=1.0)
                    except queue.Empty:
                        continue

                    # Execute task
                    self._execute_task_background(task)

                except Exception as e:
                    self.logger.error(f"Error in background processor: {e}")

        self.background_processor = threading.Thread(target=process_tasks, daemon=True)
        self.background_processor.start()

    def submit_task(self, task: ConcurrentTask, execution_mode: str = "thread") -> str:
        """
        Submit a task for concurrent execution

        Args:
            task: The task to execute
            execution_mode: 'thread', 'process', or 'async'
        """
        task.status = "pending"
        self.active_tasks[task.id] = task

        if execution_mode == "immediate":
            # Execute immediately in thread pool
            future = self.thread_executor.submit(self._execute_task_wrapper, task)
            task.future = future
        else:
            # Add to queue for background processing
            priority_score = -task.priority  # Negative for max heap behavior
            self.task_queue.put((priority_score, task.created_at, task))

        self.logger.info(f"Task submitted: {task.name} (ID: {task.id})")
        return task.id

    def _execute_task_wrapper(self, task: ConcurrentTask) -> Any:
        """Wrapper for task execution with error handling and timing"""
        task.started_at = time.time()
        task.status = "running"

        try:
            # Execute with timeout if specified
            if task.timeout:
                result = self._execute_with_timeout(task)
            else:
                result = task.function(*task.args, **task.kwargs)

            task.result = result
            task.status = "completed"
            task.completed_at = time.time()

            # Update performance stats
            execution_time = task.completed_at - task.started_at
            self.performance_stats["tasks_completed"] += 1
            self.performance_stats["total_execution_time"] += execution_time
            self.performance_stats["average_execution_time"] = (
                self.performance_stats["total_execution_time"]
                / self.performance_stats["tasks_completed"]
            )

            self.logger.info(f"Task completed: {task.name} ({execution_time:.2f}s)")
            return result

        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            task.completed_at = time.time()

            self.performance_stats["tasks_failed"] += 1

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = "pending"
                self.logger.warning(
                    f"Task failed, retrying ({task.retry_count}/{task.max_retries}): {task.name}"
                )

                # Re-submit for retry
                priority_score = -task.priority
                self.task_queue.put((priority_score, time.time(), task))
                return None
            else:
                self.logger.error(f"Task failed permanently: {task.name} - {e}")
                raise

        finally:
            # Move to completed tasks
            if task.status in ["completed", "failed"]:
                self.completed_tasks[task.id] = task
                if task.id in self.active_tasks:
                    del self.active_tasks[task.id]

    def _execute_task_background(self, task: ConcurrentTask):
        """Execute task in background thread"""
        try:
            future = self.thread_executor.submit(self._execute_task_wrapper, task)
            task.future = future
        except Exception as e:
            self.logger.error(f"Error submitting background task: {e}")
            task.status = "failed"
            task.error = str(e)

    def _execute_with_timeout(self, task: ConcurrentTask) -> Any:
        """Execute task with timeout"""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(
                f"Task {task.name} timed out after {task.timeout} seconds"
            )

        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(task.timeout))

        try:
            result = task.function(*task.args, **task.kwargs)
            signal.alarm(0)  # Cancel timeout
            return result
        finally:
            signal.signal(signal.SIGALRM, old_handler)

    def create_batch_operation(
        self,
        name: str,
        tasks: List[ConcurrentTask],
        batch_size: int = 10,
        parallel_limit: int = 5,
        fail_fast: bool = False,
    ) -> str:
        """
        Create a batch operation for processing multiple related tasks
        """
        batch = BatchOperation(
            name=name,
            tasks=tasks,
            batch_size=batch_size,
            parallel_limit=parallel_limit,
            fail_fast=fail_fast,
        )

        self.active_batches[batch.id] = batch
        self.logger.info(f"Batch operation created: {name} with {len(tasks)} tasks")

        return batch.id

    async def execute_batch_async(self, batch_id: str) -> Dict[str, Any]:
        """
        Execute batch operation asynchronously
        """
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch {batch_id} not found")

        batch = self.active_batches[batch_id]
        batch.status = "running"

        results = {}
        failed_tasks = []

        try:
            # Process tasks in batches
            for i in range(0, len(batch.tasks), batch.batch_size):
                batch_tasks = batch.tasks[i : i + batch.batch_size]

                # Execute batch with parallel limit
                semaphore = asyncio.Semaphore(batch.parallel_limit)

                async def execute_task_async(task):
                    async with semaphore:
                        loop = asyncio.get_event_loop()
                        try:
                            result = await loop.run_in_executor(
                                self.thread_executor, self._execute_task_wrapper, task
                            )
                            return task.id, result
                        except Exception as e:
                            failed_tasks.append(task.id)
                            if batch.fail_fast:
                                raise
                            return task.id, None

                # Execute batch tasks
                batch_futures = [execute_task_async(task) for task in batch_tasks]
                batch_results = await asyncio.gather(
                    *batch_futures, return_exceptions=True
                )

                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        if batch.fail_fast:
                            raise result
                        continue

                    task_id, task_result = result
                    results[task_id] = task_result

                # Progress callback
                if batch.progress_callback:
                    progress = min(i + batch.batch_size, len(batch.tasks)) / len(
                        batch.tasks
                    )
                    batch.progress_callback(progress, len(results), len(failed_tasks))

            batch.status = "completed"

        except Exception as e:
            batch.status = "failed"
            self.logger.error(f"Batch operation failed: {batch.name} - {e}")
            raise

        finally:
            # Cleanup
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]

        return {
            "batch_id": batch_id,
            "total_tasks": len(batch.tasks),
            "successful_tasks": len(results),
            "failed_tasks": len(failed_tasks),
            "results": results,
            "failed_task_ids": failed_tasks,
        }

    def execute_batch_sync(self, batch_id: str) -> Dict[str, Any]:
        """
        Execute batch operation synchronously
        """
        return asyncio.run(self.execute_batch_async(batch_id))

    def parallel_map(
        self,
        function: Callable,
        items: List[Any],
        max_workers: int = None,
        execution_mode: str = "thread",
    ) -> List[Any]:
        """
        Parallel map operation with configurable execution mode
        """
        max_workers = max_workers or self.max_workers

        if execution_mode == "thread":
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(function, item) for item in items]
                results = [future.result() for future in as_completed(futures)]

        elif execution_mode == "process":
            with ProcessPoolExecutor(
                max_workers=min(max_workers, self.max_processes)
            ) as executor:
                results = list(executor.map(function, items))

        else:
            raise ValueError(f"Unsupported execution mode: {execution_mode}")

        return results

    def parallel_search(
        self,
        search_queries: List[str],
        search_function: Callable,
        max_concurrent: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute multiple search queries in parallel
        """
        tasks = []

        for i, query in enumerate(search_queries):
            task = ConcurrentTask(
                name=f"search_query_{i}",
                function=search_function,
                args=(query,),
                priority=1,
            )
            tasks.append(task)

        # Create and execute batch
        batch_id = self.create_batch_operation(
            name="parallel_search", tasks=tasks, parallel_limit=max_concurrent
        )

        return self.execute_batch_sync(batch_id)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
        else:
            return {"status": "not_found"}

        return {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "execution_time": (
                (task.completed_at or time.time()) - task.started_at
                if task.started_at
                else None
            ),
            "retry_count": task.retry_count,
            "error": task.error,
        }

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]

            if hasattr(task, "future") and task.future:
                cancelled = task.future.cancel()
                if cancelled:
                    task.status = "cancelled"
                    self.completed_tasks[task_id] = task
                    del self.active_tasks[task_id]
                    return True

            # If not yet started, mark as cancelled
            if task.status == "pending":
                task.status = "cancelled"
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]
                return True

        return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.performance_stats,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "queue_size": self.task_queue.qsize(),
            "active_batches": len(self.active_batches),
            "thread_pool_size": self.max_workers,
            "process_pool_size": self.max_processes,
        }

    def optimize_performance(self) -> Dict[str, Any]:
        """
        Analyze performance and suggest optimizations
        """
        stats = self.get_performance_stats()
        suggestions = []

        # Analyze task completion rate
        total_tasks = stats["tasks_completed"] + stats["tasks_failed"]
        if total_tasks > 0:
            failure_rate = stats["tasks_failed"] / total_tasks
            if failure_rate > 0.1:  # More than 10% failure rate
                suggestions.append(
                    "High task failure rate detected. Consider reviewing task error handling."
                )

        # Analyze execution time
        if stats["average_execution_time"] > 30:  # More than 30 seconds average
            suggestions.append(
                "High average execution time. Consider breaking down tasks or increasing parallelism."
            )

        # Analyze queue size
        if stats["queue_size"] > 100:
            suggestions.append(
                "Large task queue detected. Consider increasing worker pool size."
            )

        # Analyze resource utilization
        if stats["active_tasks"] < self.max_workers * 0.5:
            suggestions.append(
                "Low resource utilization. Consider increasing task submission rate."
            )

        return {
            "current_stats": stats,
            "suggestions": suggestions,
            "recommended_workers": min(self.max_workers * 2, 64)
            if stats["queue_size"] > 50
            else self.max_workers,
        }

    @contextmanager
    def performance_monitor(self, operation_name: str):
        """Context manager for monitoring operation performance"""
        start_time = time.time()
        initial_stats = self.get_performance_stats().copy()

        try:
            yield
        finally:
            end_time = time.time()
            final_stats = self.get_performance_stats()

            # Calculate operation metrics
            operation_time = end_time - start_time
            tasks_processed = (
                final_stats["tasks_completed"] - initial_stats["tasks_completed"]
            )

            self.logger.info(f"Operation '{operation_name}' completed:")
            self.logger.info(f"  Duration: {operation_time:.2f}s")
            self.logger.info(f"  Tasks processed: {tasks_processed}")
            self.logger.info(
                f"  Throughput: {tasks_processed/operation_time:.2f} tasks/sec"
            )

    def shutdown(self, wait: bool = True):
        """Shutdown the concurrent operations manager"""
        self.logger.info("Shutting down concurrent operations manager...")

        # Signal shutdown
        self.shutdown_event.set()

        # Cancel all pending tasks
        for task_id in list(self.active_tasks.keys()):
            self.cancel_task(task_id)

        # Shutdown executors
        self.thread_executor.shutdown(wait=wait)
        self.process_executor.shutdown(wait=wait)

        # Wait for background processor
        if self.background_processor and self.background_processor.is_alive():
            self.background_processor.join(timeout=5.0)

        self.logger.info("Concurrent operations manager shutdown complete")


class TaskScheduler:
    """
    Advanced task scheduler with cron-like functionality
    """

    def __init__(self, concurrent_manager: ConcurrentOperationsManager):
        self.concurrent_manager = concurrent_manager
        self.scheduled_tasks = {}
        self.scheduler_thread = None
        self.running = False
        self.logger = logging.getLogger(__name__)

    def schedule_task(
        self, task: ConcurrentTask, schedule: str, start_time: datetime = None
    ) -> str:
        """
        Schedule a task with cron-like syntax

        Args:
            task: Task to schedule
            schedule: Cron-like schedule string (e.g., "0 */5 * * *" for every 5 minutes)
            start_time: When to start scheduling (default: now)
        """
        schedule_id = str(uuid.uuid4())

        self.scheduled_tasks[schedule_id] = {
            "task": task,
            "schedule": schedule,
            "start_time": start_time or datetime.now(),
            "last_run": None,
            "next_run": self._calculate_next_run(schedule, start_time),
            "run_count": 0,
        }

        self.logger.info(f"Task scheduled: {task.name} with schedule {schedule}")
        return schedule_id

    def _calculate_next_run(
        self, schedule: str, from_time: datetime = None
    ) -> datetime:
        """Calculate next run time based on cron schedule"""
        # Simplified cron parser - in production, use a proper cron library
        from_time = from_time or datetime.now()

        # For demo purposes, simple interval parsing
        if schedule.startswith("*/"):
            interval = int(schedule[2:])
            return from_time.replace(second=0, microsecond=0) + datetime.timedelta(
                minutes=interval
            )

        # Default to 1 hour
        return from_time + datetime.timedelta(hours=1)

    def start_scheduler(self):
        """Start the task scheduler"""
        if self.running:
            return

        self.running = True

        def scheduler_loop():
            while self.running:
                try:
                    current_time = datetime.now()

                    for schedule_id, schedule_info in list(
                        self.scheduled_tasks.items()
                    ):
                        if current_time >= schedule_info["next_run"]:
                            # Execute scheduled task
                            task = schedule_info["task"]

                            # Create new task instance for execution
                            execution_task = ConcurrentTask(
                                name=f"{task.name}_scheduled_{schedule_info['run_count']}",
                                function=task.function,
                                args=task.args,
                                kwargs=task.kwargs,
                                priority=task.priority,
                            )

                            # Submit for execution
                            self.concurrent_manager.submit_task(execution_task)

                            # Update schedule info
                            schedule_info["last_run"] = current_time
                            schedule_info["run_count"] += 1
                            schedule_info["next_run"] = self._calculate_next_run(
                                schedule_info["schedule"], current_time
                            )

                    time.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    self.logger.error(f"Error in scheduler loop: {e}")
                    time.sleep(60)  # Wait longer on error

        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Task scheduler started")

    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
        self.logger.info("Task scheduler stopped")

    def unschedule_task(self, schedule_id: str) -> bool:
        """Remove a scheduled task"""
        if schedule_id in self.scheduled_tasks:
            del self.scheduled_tasks[schedule_id]
            self.logger.info(f"Task unscheduled: {schedule_id}")
            return True
        return False

    def get_scheduled_tasks(self) -> Dict[str, Any]:
        """Get information about all scheduled tasks"""
        return {
            schedule_id: {
                "task_name": info["task"].name,
                "schedule": info["schedule"],
                "next_run": info["next_run"].isoformat(),
                "last_run": info["last_run"].isoformat() if info["last_run"] else None,
                "run_count": info["run_count"],
            }
            for schedule_id, info in self.scheduled_tasks.items()
        }


# Example usage and utility functions
def example_search_function(query: str) -> Dict[str, Any]:
    """Example search function for testing"""
    import random

    time.sleep(random.uniform(0.5, 2.0))  # Simulate network delay

    return {
        "query": query,
        "results": [f"Result {i} for {query}" for i in range(random.randint(1, 5))],
        "timestamp": time.time(),
    }


def example_data_processing(data: List[Any]) -> Dict[str, Any]:
    """Example data processing function"""
    time.sleep(0.1)  # Simulate processing time

    return {
        "processed_count": len(data),
        "sum": sum(x for x in data if isinstance(x, (int, float))),
        "timestamp": time.time(),
    }


# Example usage
if __name__ == "__main__":
    # Initialize concurrent manager
    manager = ConcurrentOperationsManager(max_workers=10)

    # Example 1: Parallel search queries
    search_queries = ["AI technology", "machine learning", "data science", "automation"]

    with manager.performance_monitor("parallel_search"):
        search_results = manager.parallel_search(
            search_queries, example_search_function, max_concurrent=3
        )

    print(f"Search completed: {search_results['successful_tasks']} successful")

    # Example 2: Batch data processing
    data_batches = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]

    processing_tasks = [
        ConcurrentTask(
            name=f"process_batch_{i}",
            function=example_data_processing,
            args=(batch,),
            priority=1,
        )
        for i, batch in enumerate(data_batches)
    ]

    batch_id = manager.create_batch_operation(
        name="data_processing_batch", tasks=processing_tasks, parallel_limit=2
    )

    batch_results = manager.execute_batch_sync(batch_id)
    print(f"Batch processing completed: {batch_results['successful_tasks']} tasks")

    # Performance stats
    stats = manager.get_performance_stats()
    print(
        f"Performance: {stats['tasks_completed']} completed, avg time: {stats['average_execution_time']:.2f}s"
    )

    # Cleanup
    manager.shutdown()
