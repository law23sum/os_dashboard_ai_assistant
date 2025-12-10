"""Driver Architecture & System Execution Layer.

Implements the driver taxonomy, OS drivers, package managers, SaaS drivers,
execution scheduler, and driver registry as outlined in Section 5 of the Canon
Technical Specification for the OS Dashboard AI Assistant.
"""

from __future__ import annotations

import asyncio
import logging
import os
import platform
import shutil
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 5.1 Driver Taxonomy & Design Principles
# ---------------------------------------------------------------------------
class DriverCategory(Enum):
    OS = "os"
    HARDWARE = "hardware"
    SOFTWARE_SAAS = "software_saas"
    DATA = "data"
    WORKFLOW = "workflow"
    GOVERNANCE = "governance"
    RESEARCH_SIMULATION = "research_simulation"


class DriverStatus(Enum):
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    READY = "ready"
    EXECUTING = "executing"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ExecutionPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DriverCapability:
    name: str
    description: str
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriverManifest:
    name: str
    version: str
    category: DriverCategory
    description: str
    capabilities: List[DriverCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    supported_platforms: List[str] = field(default_factory=list)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    security_requirements: Dict[str, Any] = field(default_factory=dict)
    configuration_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriverExecution:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    driver_id: str = ""
    capability: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: str = "running"
    result: Optional[Any] = None
    error: Optional[str] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    execution_context: Dict[str, Any] = field(default_factory=dict)


class BaseDriver:
    """Base class for all drivers."""

    def __init__(self, manifest: DriverManifest, config: Optional[Dict[str, Any]] = None):
        self.id = str(uuid.uuid4())
        self.manifest = manifest
        self.config = config or {}
        self.status = DriverStatus.INACTIVE
        self.created_at = datetime.now(timezone.utc)
        self.last_execution: Optional[DriverExecution] = None
        self.execution_history: List[DriverExecution] = []

    async def initialize(self) -> bool:
        raise NotImplementedError

    async def execute(
        self, capability: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        raise NotImplementedError

    async def cleanup(self) -> None:
        raise NotImplementedError

    async def start(self) -> None:
        if self.status != DriverStatus.INACTIVE:
            return
        self.status = DriverStatus.INITIALIZING
        try:
            if await self.initialize():
                self.status = DriverStatus.READY
                logger.info("Driver %s initialized", self.manifest.name)
            else:
                self.status = DriverStatus.ERROR
                logger.error("Driver %s initialization failed", self.manifest.name)
        except Exception as exc:  # pragma: no cover - defensive
            self.status = DriverStatus.ERROR
            logger.exception("Error starting driver %s", self.manifest.name)
            raise exc

    async def stop(self) -> None:
        try:
            await self.cleanup()
        finally:
            self.status = DriverStatus.INACTIVE
            logger.info("Driver %s stopped", self.manifest.name)

    def can_execute(self, capability: str) -> bool:
        return any(cap.name == capability for cap in self.manifest.capabilities)

    def get_capability(self, name: str) -> Optional[DriverCapability]:
        return next((cap for cap in self.manifest.capabilities if cap.name == name), None)


# ---------------------------------------------------------------------------
# 5.2 OS Drivers
# ---------------------------------------------------------------------------
class OSDriver(BaseDriver):
    def __init__(self, manifest: DriverManifest, config: Optional[Dict[str, Any]] = None):
        super().__init__(manifest, config)
        self.platform = platform.system().lower()

    async def initialize(self) -> bool:
        return not self.manifest.supported_platforms or self.platform in self.manifest.supported_platforms


class FilesystemDriver(OSDriver):
    def __init__(self):
        manifest = DriverManifest(
            name="filesystem",
            version="1.0.0",
            category=DriverCategory.OS,
            description="Filesystem operations driver",
            capabilities=[
                DriverCapability("read_file", "Read file contents", ["string"], ["string", "bytes"]),
                DriverCapability("write_file", "Write file contents", ["string", "bytes"], ["boolean"]),
                DriverCapability("list_directory", "List directory contents", ["string"], ["list"]),
                DriverCapability("create_directory", "Create directory", ["string"], ["boolean"]),
                DriverCapability("delete_path", "Delete file or directory", ["string"], ["boolean"]),
            ],
            supported_platforms=["windows", "linux", "darwin"],
        )
        super().__init__(manifest)

    async def execute(
        self, capability: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        execution = DriverExecution(
            driver_id=self.id,
            capability=capability,
            parameters=parameters,
            execution_context=context or {},
        )
        try:
            self.status = DriverStatus.EXECUTING
            if capability == "read_file":
                result = await self._read_file(parameters.get("path", ""))
            elif capability == "write_file":
                result = await self._write_file(parameters.get("path", ""), parameters.get("content", ""))
            elif capability == "list_directory":
                result = await self._list_directory(parameters.get("path", "."))
            elif capability == "create_directory":
                result = await self._create_directory(parameters.get("path", ""))
            elif capability == "delete_path":
                result = await self._delete_path(parameters.get("path", ""))
            else:
                raise ValueError(f"Unknown capability: {capability}")
            execution.result = result
            execution.status = "completed"
            self.status = DriverStatus.READY
        except Exception as exc:
            execution.error = str(exc)
            execution.status = "error"
            self.status = DriverStatus.ERROR
            logger.exception("Filesystem driver error")
            raise
        finally:
            execution.completed_at = datetime.now(timezone.utc)
            self.last_execution = execution
            self.execution_history.append(execution)
        return execution.result

    async def _read_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()

    async def _write_file(self, path: str, content: str) -> bool:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return True

    async def _list_directory(self, path: str) -> List[str]:
        return os.listdir(path)

    async def _create_directory(self, path: str) -> bool:
        os.makedirs(path, exist_ok=True)
        return True

    async def _delete_path(self, path: str) -> bool:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True

    async def cleanup(self) -> None:
        return None


class ProcessDriver(OSDriver):
    def __init__(self):
        manifest = DriverManifest(
            name="process",
            version="1.0.0",
            category=DriverCategory.OS,
            description="Process management driver",
            capabilities=[
                DriverCapability("execute_command", "Execute system command", ["string", "list"], ["dict"]),
                DriverCapability("list_processes", "List running processes", [], ["list"]),
                DriverCapability("kill_process", "Kill process by PID", ["int"], ["boolean"]),
            ],
            supported_platforms=["windows", "linux", "darwin"],
        )
        super().__init__(manifest)

    async def execute(
        self, capability: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        execution = DriverExecution(
            driver_id=self.id,
            capability=capability,
            parameters=parameters,
            execution_context=context or {},
        )
        try:
            self.status = DriverStatus.EXECUTING
            if capability == "execute_command":
                result = await self._execute_command(
                    parameters.get("command", ""),
                    parameters.get("args", []),
                    parameters.get("cwd"),
                    parameters.get("env"),
                )
            elif capability == "list_processes":
                result = await self._list_processes()
            elif capability == "kill_process":
                result = await self._kill_process(parameters.get("pid", 0))
            else:
                raise ValueError(f"Unknown capability: {capability}")
            execution.result = result
            execution.status = "completed"
            self.status = DriverStatus.READY
        except Exception as exc:
            execution.error = str(exc)
            execution.status = "error"
            self.status = DriverStatus.ERROR
            logger.exception("Process driver error")
            raise
        finally:
            execution.completed_at = datetime.now(timezone.utc)
            self.last_execution = execution
            self.execution_history.append(execution)
        return execution.result

    async def _execute_command(
        self, command: str, args: Optional[List[str]] = None, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        cmd = [command] + (args or [])
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        stdout, stderr = await process.communicate()
        return {
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8", errors="ignore"),
            "stderr": stderr.decode("utf-8", errors="ignore"),
            "command": cmd,
        }

    async def _list_processes(self) -> List[Dict[str, Any]]:
        if self.platform == "windows":
            result = await self._execute_command("tasklist", ["/fo", "csv"])
        else:
            result = await self._execute_command("ps", ["aux"])
        processes: List[Dict[str, Any]] = []
        if result["returncode"] == 0:
            lines = result["stdout"].strip().split("\n")
            for line in lines[1:]:
                processes.append({"info": line})
        return processes

    async def _kill_process(self, pid: int) -> bool:
        if self.platform == "windows":
            result = await self._execute_command("taskkill", ["/PID", str(pid), "/F"])
        else:
            result = await self._execute_command("kill", [str(pid)])
        return result["returncode"] == 0

    async def cleanup(self) -> None:
        return None


# ---------------------------------------------------------------------------
# 5.4 Package & Environment Management Drivers
# ---------------------------------------------------------------------------
class PackageManagerDriver(BaseDriver):
    def __init__(self, manifest: DriverManifest, config: Optional[Dict[str, Any]] = None):
        super().__init__(manifest, config)
        self.package_manager = manifest.name

    async def initialize(self) -> bool:
        try:
            result = await self._execute_pm_command(["--version"])
            return result["returncode"] == 0
        except Exception:
            return False

    async def _execute_pm_command(self, args: List[str]) -> Dict[str, Any]:
        cmd = [self.package_manager] + args
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return {
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8", errors="ignore"),
            "stderr": stderr.decode("utf-8", errors="ignore"),
            "command": cmd,
        }


class PipDriver(PackageManagerDriver):
    def __init__(self):
        manifest = DriverManifest(
            name="pip",
            version="1.0.0",
            category=DriverCategory.OS,
            description="Python pip package manager",
            capabilities=[
                DriverCapability("install_package", "Install Python package", ["string"], ["dict"]),
                DriverCapability("uninstall_package", "Uninstall Python package", ["string"], ["dict"]),
                DriverCapability("list_packages", "List installed packages", [], ["list"]),
                DriverCapability("upgrade_package", "Upgrade Python package", ["string"], ["dict"]),
            ],
            supported_platforms=["windows", "linux", "darwin"],
        )
        super().__init__(manifest)

    async def execute(
        self, capability: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        execution = DriverExecution(
            driver_id=self.id,
            capability=capability,
            parameters=parameters,
            execution_context=context or {},
        )
        try:
            self.status = DriverStatus.EXECUTING
            if capability == "install_package":
                result = await self._execute_pm_command(["install", parameters.get("package", "")])
            elif capability == "uninstall_package":
                result = await self._execute_pm_command(["uninstall", parameters.get("package", ""), "-y"])
            elif capability == "list_packages":
                result = await self._execute_pm_command(["list"])
                packages = []
                if result["returncode"] == 0:
                    for line in result["stdout"].splitlines()[2:]:
                        line = line.strip()
                        if line:
                            packages.append(line.split()[0])
                execution.result = packages
                execution.status = "completed"
                self.status = DriverStatus.READY
                return packages
            elif capability == "upgrade_package":
                result = await self._execute_pm_command(["install", "--upgrade", parameters.get("package", "")])
            else:
                raise ValueError(f"Unknown capability: {capability}")
            execution.result = result
            execution.status = "completed"
            self.status = DriverStatus.READY
        except Exception as exc:
            execution.error = str(exc)
            execution.status = "error"
            self.status = DriverStatus.ERROR
            logger.exception("Pip driver error")
            raise
        finally:
            execution.completed_at = datetime.now(timezone.utc)
            self.last_execution = execution
            self.execution_history.append(execution)
        return execution.result

    async def cleanup(self) -> None:
        return None


# ---------------------------------------------------------------------------
# 5.6 Software & SaaS Drivers
# ---------------------------------------------------------------------------
class GitDriver(BaseDriver):
    def __init__(self):
        manifest = DriverManifest(
            name="git",
            version="1.0.0",
            category=DriverCategory.SOFTWARE_SAAS,
            description="Git version control system driver",
            capabilities=[
                DriverCapability("clone_repository", "Clone git repository", ["string"], ["dict"]),
                DriverCapability("commit_changes", "Commit changes to repository", ["string"], ["dict"]),
                DriverCapability("push_changes", "Push changes to remote", ["string"], ["dict"]),
                DriverCapability("pull_changes", "Pull changes from remote", ["string"], ["dict"]),
                DriverCapability("get_status", "Get repository status", ["string"], ["dict"]),
            ],
            supported_platforms=["windows", "linux", "darwin"],
        )
        super().__init__(manifest)

    async def initialize(self) -> bool:
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False

    async def execute(
        self, capability: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        execution = DriverExecution(
            driver_id=self.id,
            capability=capability,
            parameters=parameters,
            execution_context=context or {},
        )
        try:
            self.status = DriverStatus.EXECUTING
            if capability == "clone_repository":
                result = await self._execute_git_command(["clone", parameters.get("url", ""), parameters.get("path", "")])
            elif capability == "commit_changes":
                result = await self._commit_changes(parameters.get("path", "."), parameters.get("message", ""))
            elif capability == "push_changes":
                result = await self._execute_git_command(["push"], cwd=parameters.get("path", "."))
            elif capability == "pull_changes":
                result = await self._execute_git_command(["pull"], cwd=parameters.get("path", "."))
            elif capability == "get_status":
                result = await self._execute_git_command(["status", "--porcelain"], cwd=parameters.get("path", "."))
            else:
                raise ValueError(f"Unknown capability: {capability}")
            execution.result = result
            execution.status = "completed"
            self.status = DriverStatus.READY
        except Exception as exc:
            execution.error = str(exc)
            execution.status = "error"
            self.status = DriverStatus.ERROR
            logger.exception("Git driver error")
            raise
        finally:
            execution.completed_at = datetime.now(timezone.utc)
            self.last_execution = execution
            self.execution_history.append(execution)
        return execution.result

    async def _execute_git_command(self, args: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        process = await asyncio.create_subprocess_exec(
            "git",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        stdout, stderr = await process.communicate()
        return {
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8", errors="ignore"),
            "stderr": stderr.decode("utf-8", errors="ignore"),
            "command": ["git", *args],
        }

    async def _commit_changes(self, path: str, message: str) -> Dict[str, Any]:
        add_result = await self._execute_git_command(["add", "."], cwd=path)
        if add_result["returncode"] != 0:
            return add_result
        return await self._execute_git_command(["commit", "-m", message], cwd=path)

    async def cleanup(self) -> None:
        return None


# ---------------------------------------------------------------------------
# 5.12 Driver Scheduling, Prioritization, Backpressure & Admission Control
# ---------------------------------------------------------------------------
@dataclass
class DriverExecutionRequest:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    driver_id: str = ""
    capability: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    context: Dict[str, Any] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    timeout: Optional[int] = None


class DriverScheduler:
    def __init__(self, max_concurrent_executions: int = 10):
        self.drivers: Dict[str, BaseDriver] = {}
        self.execution_queue: List[DriverExecutionRequest] = []
        self.active_executions: Dict[str, DriverExecution] = {}
        self.max_concurrent_executions = max_concurrent_executions
        self.scheduler_running = False
        self._scheduler_task: Optional[asyncio.Task] = None

    def register_driver(self, driver: BaseDriver) -> None:
        self.drivers[driver.id] = driver
        logger.info("Scheduler registered driver %s", driver.manifest.name)

    async def start_scheduler(self) -> None:
        if self.scheduler_running:
            return
        self.scheduler_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Driver scheduler started")

    async def stop_scheduler(self) -> None:
        self.scheduler_running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Driver scheduler stopped")

    async def submit_request(self, request: DriverExecutionRequest) -> str:
        if len(self.execution_queue) > 1000:
            raise RuntimeError("Execution queue is full")
        if request.driver_id not in self.drivers:
            raise ValueError(f"Driver {request.driver_id} not found")
        driver = self.drivers[request.driver_id]
        if not driver.can_execute(request.capability):
            raise ValueError(f"Driver {driver.manifest.name} cannot execute {request.capability}")
        self._insert_by_priority(request)
        return request.id

    def _insert_by_priority(self, request: DriverExecutionRequest) -> None:
        ordering = {
            ExecutionPriority.CRITICAL: 0,
            ExecutionPriority.HIGH: 1,
            ExecutionPriority.NORMAL: 2,
            ExecutionPriority.LOW: 3,
        }
        request_priority = ordering[request.priority]
        insert_index = len(self.execution_queue)
        for idx, queued in enumerate(self.execution_queue):
            if ordering[queued.priority] > request_priority:
                insert_index = idx
                break
        self.execution_queue.insert(insert_index, request)

    async def _scheduler_loop(self) -> None:
        while self.scheduler_running:
            if (
                len(self.active_executions) < self.max_concurrent_executions
                and self.execution_queue
            ):
                request = self.execution_queue.pop(0)
                await self._execute_request(request)
            await self._cleanup_completed_executions()
            await asyncio.sleep(0.1)

    async def _execute_request(self, request: DriverExecutionRequest) -> None:
        driver = self.drivers[request.driver_id]
        asyncio.create_task(self._execute_with_timeout(driver, request))
        self.active_executions[request.id] = DriverExecution(
            id=request.id,
            driver_id=request.driver_id,
            capability=request.capability,
            parameters=request.parameters,
            execution_context=request.context,
        )

    async def _execute_with_timeout(self, driver: BaseDriver, request: DriverExecutionRequest) -> None:
        try:
            if request.timeout:
                result = await asyncio.wait_for(
                    driver.execute(request.capability, request.parameters, request.context),
                    timeout=request.timeout,
                )
            else:
                result = await driver.execute(request.capability, request.parameters, request.context)
            execution = self.active_executions.get(request.id)
            if execution:
                execution.result = result
                execution.status = "completed"
                execution.completed_at = datetime.now(timezone.utc)
        except asyncio.TimeoutError:
            execution = self.active_executions.get(request.id)
            if execution:
                execution.error = "Execution timeout"
                execution.status = "timeout"
                execution.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            execution = self.active_executions.get(request.id)
            if execution:
                execution.error = str(exc)
                execution.status = "error"
                execution.completed_at = datetime.now(timezone.utc)

    async def _cleanup_completed_executions(self) -> None:
        completed = [eid for eid, exe in self.active_executions.items() if exe.status in {"completed", "error", "timeout"}]
        for eid in completed:
            del self.active_executions[eid]

    def get_queue_status(self) -> Dict[str, Any]:
        return {
            "queue_length": len(self.execution_queue),
            "active_executions": len(self.active_executions),
            "max_concurrent": self.max_concurrent_executions,
            "scheduler_running": self.scheduler_running,
            "registered_drivers": len(self.drivers),
        }


# ---------------------------------------------------------------------------
# Driver Registry and Management
# ---------------------------------------------------------------------------
class DriverRegistry:
    def __init__(self):
        self.drivers: Dict[str, BaseDriver] = {}
        self.driver_manifests: Dict[str, DriverManifest] = {}
        self.scheduler = DriverScheduler()
        self.initialized = False

    async def initialize(self) -> None:
        if self.initialized:
            return
        await self._register_default_drivers()
        await self.scheduler.start_scheduler()
        self.initialized = True
        logger.info("Driver registry initialized")

    async def _register_default_drivers(self) -> None:
        for driver in [FilesystemDriver(), ProcessDriver(), PipDriver(), GitDriver()]:
            await self.register_driver(driver)

    async def register_driver(self, driver: BaseDriver) -> None:
        await driver.start()
        if driver.status == DriverStatus.READY:
            self.drivers[driver.id] = driver
            self.driver_manifests[driver.id] = driver.manifest
            self.scheduler.register_driver(driver)
            logger.info("Registered driver: %s", driver.manifest.name)
        else:
            logger.error("Failed to register driver: %s", driver.manifest.name)

    async def unregister_driver(self, driver_id: str) -> None:
        driver = self.drivers.get(driver_id)
        if not driver:
            return
        await driver.stop()
        self.drivers.pop(driver_id, None)
        self.driver_manifests.pop(driver_id, None)
        logger.info("Unregistered driver: %s", driver.manifest.name)

    async def execute_capability(
        self,
        driver_name: str,
        capability: str,
        parameters: Dict[str, Any],
        priority: ExecutionPriority = ExecutionPriority.NORMAL,
    ) -> str:
        driver_id = next((did for did, drv in self.drivers.items() if drv.manifest.name == driver_name), None)
        if not driver_id:
            raise ValueError(f"Driver {driver_name} not found")
        request = DriverExecutionRequest(
            driver_id=driver_id,
            capability=capability,
            parameters=parameters,
            priority=priority,
        )
        return await self.scheduler.submit_request(request)

    def get_available_drivers(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for driver_id, driver in self.drivers.items():
            items.append(
                {
                    "id": driver_id,
                    "name": driver.manifest.name,
                    "category": driver.manifest.category.value,
                    "version": driver.manifest.version,
                    "status": driver.status.value,
                    "capabilities": [cap.name for cap in driver.manifest.capabilities],
                }
            )
        return items

    def get_driver_status(self) -> Dict[str, Any]:
        return {
            "initialized": self.initialized,
            "registered_drivers": len(self.drivers),
            "scheduler_status": self.scheduler.get_queue_status(),
            "drivers": self.get_available_drivers(),
        }

    async def shutdown(self) -> None:
        await self.scheduler.stop_scheduler()
        for driver in list(self.drivers.values()):
            await driver.stop()
        self.drivers.clear()
        self.driver_manifests.clear()
        self.initialized = False
        logger.info("Driver registry shutdown")


__all__ = [
    "BaseDriver",
    "DriverCategory",
    "DriverStatus",
    "DriverManifest",
    "DriverCapability",
    "DriverExecution",
    "DriverExecutionRequest",
    "ExecutionPriority",
    "OSDriver",
    "FilesystemDriver",
    "ProcessDriver",
    "PackageManagerDriver",
    "PipDriver",
    "GitDriver",
    "DriverScheduler",
    "DriverRegistry",
]
