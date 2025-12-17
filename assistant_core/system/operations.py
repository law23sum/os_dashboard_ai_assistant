"""
System-Level Operations Controller
Full Linux environment control, process management, and network services
"""

import os
import platform
import subprocess

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - fallback when psutil missing
    from utils.psutil_stub import psutil  # type: ignore
import threading
import time
import signal
import socket
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json
import tempfile
import shutil
import zipfile
import tarfile
from pathlib import Path
import requests
import yaml


@dataclass
class ProcessInfo:
    """Information about a running process"""

    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    create_time: float
    cmdline: List[str]


@dataclass
class ServiceConfig:
    """Configuration for a network service"""

    name: str
    port: int
    host: str = "0.0.0.0"
    protocol: str = "http"
    auto_start: bool = True
    environment: Dict[str, str] = None
    working_directory: str = None


class SystemOperationsController:
    """
    Advanced system operations controller with full Linux environment control
    """

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_processes = {}
        self.exposed_ports = {}
        self.background_tasks = {}

    def execute_command(
        self,
        command: Union[str, List[str]],
        working_dir: str = None,
        environment: Dict[str, str] = None,
        timeout: int = None,
        capture_output: bool = True,
        shell: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute system command with advanced options
        """
        try:
            # Prepare environment
            env = os.environ.copy()
            if environment:
                env.update(environment)

            # Execute command
            start_time = time.time()

            if isinstance(command, list):
                shell = False

            result = subprocess.run(
                command,
                cwd=working_dir,
                env=env,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                shell=shell,
            )

            execution_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "execution_time": execution_time,
                "command": command,
            }

        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "error": "Command timed out",
                "timeout": timeout,
                "command": command,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    def execute_background_command(
        self,
        command: Union[str, List[str]],
        task_name: str,
        working_dir: str = None,
        environment: Dict[str, str] = None,
        log_file: str = None,
    ) -> str:
        """
        Execute command in background and return task ID
        """
        task_id = f"{task_name}_{int(time.time())}"

        def run_background_task():
            try:
                # Prepare environment
                env = os.environ.copy()
                if environment:
                    env.update(environment)

                # Setup logging
                stdout_file = log_file or f"/tmp/{task_id}.log"
                stderr_file = f"/tmp/{task_id}_error.log"

                with open(stdout_file, "w") as stdout_f, open(
                    stderr_file, "w"
                ) as stderr_f:
                    process = subprocess.Popen(
                        command,
                        cwd=working_dir,
                        env=env,
                        stdout=stdout_f,
                        stderr=stderr_f,
                        shell=isinstance(command, str),
                    )

                    self.running_processes[task_id] = {
                        "process": process,
                        "start_time": time.time(),
                        "command": command,
                        "log_file": stdout_file,
                        "error_file": stderr_file,
                    }

                    # Wait for completion
                    process.wait()

                    # Update status
                    if task_id in self.running_processes:
                        self.running_processes[task_id]["end_time"] = time.time()
                        self.running_processes[task_id][
                            "returncode"
                        ] = process.returncode

            except Exception as e:
                self.logger.error(f"Background task {task_id} failed: {e}")
                if task_id in self.running_processes:
                    self.running_processes[task_id]["error"] = str(e)

        # Start background task
        future = self.executor.submit(run_background_task)
        self.background_tasks[task_id] = future

        self.logger.info(f"Started background task: {task_id}")
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of background task"""
        if task_id not in self.running_processes:
            return {"status": "not_found"}

        task_info = self.running_processes[task_id]
        process = task_info["process"]

        status = {
            "task_id": task_id,
            "command": task_info["command"],
            "start_time": task_info["start_time"],
            "log_file": task_info["log_file"],
            "error_file": task_info["error_file"],
        }

        if process.poll() is None:
            status["status"] = "running"
            status["pid"] = process.pid
        else:
            status["status"] = "completed"
            status["returncode"] = process.returncode
            status["end_time"] = task_info.get("end_time", time.time())

        if "error" in task_info:
            status["error"] = task_info["error"]

        return status

    def kill_task(self, task_id: str, force: bool = False) -> bool:
        """Kill background task"""
        if task_id not in self.running_processes:
            return False

        try:
            process = self.running_processes[task_id]["process"]

            if process.poll() is None:  # Process is still running
                if force:
                    process.kill()
                else:
                    process.terminate()

                # Wait for process to end
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if not force:
                        process.kill()
                        process.wait()

            self.logger.info(f"Task {task_id} terminated")
            return True

        except Exception as e:
            self.logger.error(f"Error killing task {task_id}: {e}")
            return False

    def install_package(
        self, package_name: str, package_manager: str = "auto"
    ) -> Dict[str, Any]:
        """
        Install system package using appropriate package manager
        """
        # Detect package manager if auto
        if package_manager == "auto":
            if shutil.which("apt-get"):
                package_manager = "apt"
            elif shutil.which("yum"):
                package_manager = "yum"
            elif shutil.which("dnf"):
                package_manager = "dnf"
            elif shutil.which("pacman"):
                package_manager = "pacman"
            else:
                return {"success": False, "error": "No supported package manager found"}

        # Build install command
        commands = {
            "apt": ["sudo", "apt-get", "install", "-y", package_name],
            "yum": ["sudo", "yum", "install", "-y", package_name],
            "dnf": ["sudo", "dnf", "install", "-y", package_name],
            "pacman": ["sudo", "pacman", "-S", "--noconfirm", package_name],
            "pip": ["pip", "install", package_name],
            "npm": ["npm", "install", "-g", package_name],
        }

        if package_manager not in commands:
            return {
                "success": False,
                "error": f"Unsupported package manager: {package_manager}",
            }

        command = commands[package_manager]

        # Update package list for apt
        if package_manager == "apt":
            update_result = self.execute_command(["sudo", "apt-get", "update"])
            if not update_result["success"]:
                self.logger.warning("Failed to update package list")

        # Install package
        result = self.execute_command(command, timeout=300)  # 5 minute timeout

        if result["success"]:
            self.logger.info(f"Successfully installed package: {package_name}")
        else:
            self.logger.error(
                f"Failed to install package {package_name}: {result.get('stderr', '')}"
            )

        return result

    def expose_port(
        self, port: int, service_name: str = None, protocol: str = "tcp"
    ) -> Dict[str, Any]:
        """
        Expose port to public internet (simulated)
        """
        try:
            # Check if port is available
            if not self._is_port_available(port):
                return {"success": False, "error": f"Port {port} is already in use"}

            # Generate public URL (simulated)
            public_url = f"https://{port}-sandbox.example.com"

            self.exposed_ports[port] = {
                "service_name": service_name or f"service_{port}",
                "protocol": protocol,
                "public_url": public_url,
                "exposed_at": time.time(),
            }

            self.logger.info(f"Port {port} exposed at {public_url}")

            return {
                "success": True,
                "port": port,
                "public_url": public_url,
                "protocol": protocol,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return True
        except OSError:
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU information
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "total_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "current_frequency": psutil.cpu_freq().current
                if psutil.cpu_freq()
                else None,
                "cpu_usage": psutil.cpu_percent(interval=1),
            }

            # Memory information
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percentage": memory.percent,
            }

            # Disk information
            disk = psutil.disk_usage("/")
            disk_info = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percentage": (disk.used / disk.total) * 100,
            }

            # Network information
            network_info = {}
            for interface, addrs in psutil.net_if_addrs().items():
                network_info[interface] = []
                for addr in addrs:
                    network_info[interface].append(
                        {
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        }
                    )

            # Process information
            processes = []
            for proc in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "status",
                    "cpu_percent",
                    "memory_percent",
                    "create_time",
                    "cmdline",
                ]
            ):
                try:
                    processes.append(ProcessInfo(**proc.info))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "network": network_info,
                "processes": processes[:20],  # Top 20 processes
                "uptime": time.time() - psutil.boot_time(),
                "exposed_ports": self.exposed_ports,
                "running_tasks": len(self.running_processes),
            }

        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}

    def manage_file_permissions(
        self, file_path: str, permissions: str, recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Manage file permissions with advanced options
        """
        try:
            command = ["chmod"]

            if recursive:
                command.append("-R")

            command.extend([permissions, file_path])

            result = self.execute_command(command)

            if result["success"]:
                self.logger.info(f"Permissions changed for {file_path}: {permissions}")

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_archive(
        self,
        source_path: str,
        archive_path: str,
        archive_type: str = "zip",
        compression_level: int = 6,
    ) -> Dict[str, Any]:
        """
        Create compressed archives with various formats
        """
        try:
            source_path = Path(source_path)
            archive_path = Path(archive_path)

            if archive_type.lower() == "zip":
                with zipfile.ZipFile(
                    archive_path,
                    "w",
                    zipfile.ZIP_DEFLATED,
                    compresslevel=compression_level,
                ) as zipf:
                    if source_path.is_file():
                        zipf.write(source_path, source_path.name)
                    else:
                        for file_path in source_path.rglob("*"):
                            if file_path.is_file():
                                arcname = file_path.relative_to(source_path.parent)
                                zipf.write(file_path, arcname)

            elif archive_type.lower() in ["tar", "tar.gz", "tgz"]:
                mode = "w:gz" if archive_type.lower() in ["tar.gz", "tgz"] else "w"
                with tarfile.open(archive_path, mode) as tarf:
                    tarf.add(source_path, arcname=source_path.name)

            else:
                return {
                    "success": False,
                    "error": f"Unsupported archive type: {archive_type}",
                }

            archive_size = archive_path.stat().st_size

            return {
                "success": True,
                "archive_path": str(archive_path),
                "archive_size": archive_size,
                "compression_ratio": archive_size
                / self._get_directory_size(source_path),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def extract_archive(
        self, archive_path: str, extract_to: str = None
    ) -> Dict[str, Any]:
        """
        Extract compressed archives
        """
        try:
            archive_path = Path(archive_path)
            extract_to = Path(extract_to) if extract_to else archive_path.parent

            if not archive_path.exists():
                return {"success": False, "error": f"Archive not found: {archive_path}"}

            # Determine archive type
            if archive_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(archive_path, "r") as zipf:
                    zipf.extractall(extract_to)
                    extracted_files = zipf.namelist()

            elif archive_path.suffix.lower() in [".tar", ".gz", ".tgz"]:
                with tarfile.open(archive_path, "r:*") as tarf:
                    tarf.extractall(extract_to)
                    extracted_files = tarf.getnames()

            else:
                return {
                    "success": False,
                    "error": f"Unsupported archive format: {archive_path.suffix}",
                }

            return {
                "success": True,
                "extract_path": str(extract_to),
                "extracted_files": extracted_files,
                "file_count": len(extracted_files),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory"""
        if path.is_file():
            return path.stat().st_size

        total_size = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

    def monitor_system_resources(
        self, duration: int = 60, interval: int = 5
    ) -> Dict[str, Any]:
        """
        Monitor system resources over time
        """
        monitoring_data = {
            "cpu_usage": [],
            "memory_usage": [],
            "disk_io": [],
            "network_io": [],
            "timestamps": [],
        }

        start_time = time.time()

        # Initial network and disk IO counters
        initial_net_io = psutil.net_io_counters()
        initial_disk_io = psutil.disk_io_counters()

        while time.time() - start_time < duration:
            timestamp = time.time()

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk IO
            current_disk_io = psutil.disk_io_counters()
            disk_io_data = {
                "read_bytes": current_disk_io.read_bytes - initial_disk_io.read_bytes,
                "write_bytes": current_disk_io.write_bytes
                - initial_disk_io.write_bytes,
            }

            # Network IO
            current_net_io = psutil.net_io_counters()
            net_io_data = {
                "bytes_sent": current_net_io.bytes_sent - initial_net_io.bytes_sent,
                "bytes_recv": current_net_io.bytes_recv - initial_net_io.bytes_recv,
            }

            # Store data
            monitoring_data["timestamps"].append(timestamp)
            monitoring_data["cpu_usage"].append(cpu_percent)
            monitoring_data["memory_usage"].append(memory.percent)
            monitoring_data["disk_io"].append(disk_io_data)
            monitoring_data["network_io"].append(net_io_data)

            time.sleep(interval)

        return monitoring_data

    def memory_thread_resilience_plan(self) -> Dict[str, Any]:
        """
        Produce a structured plan for recovering from memory pressure and thread oversubscription.

        The plan is tuned for macOS hosts (as detected in the field) and mirrors the remediation
        steps we typically hand to operators via the CLI playbook. Commands are grouped so the UI
        can render them as runbook cards without guessing context.
        """

        os_family = platform.system().lower()
        arch = platform.machine()
        logical = psutil.cpu_count(logical=True) or 0
        physical = psutil.cpu_count(logical=False) or logical or 0

        plan = {
            "os_family": os_family,
            "architecture": arch,
            "logical_cores": logical,
            "physical_cores": physical,
            "recommended_thread_cap": max(physical, 1),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "spec_refs": ["11.8", "14.3", "17.2"],
            "steps": [
                {
                    "title": "Baseline telemetry snapshot",
                    "objective": "Capture memory pressure, swap usage, and the top offenders before applying fixes.",
                    "commands": [
                        {
                            "command": "vm_stat",
                            "description": "Snapshot virtual memory stats (free, active, compressed pages).",
                        },
                        {
                            "command": "sysctl vm.swapusage",
                            "description": "Record current swap consumption.",
                        },
                        {
                            "command": "sudo memory_pressure -l warn",
                            "description": "Stream memory pressure; stop once readings stabilize.",
                            "requires_sudo": True,
                        },
                        {
                            "command": "ps aux | sort -nrk 6 | head -n 10",
                            "description": "List the top RSS consumers to target first.",
                        },
                    ],
                    "verification": [
                        "Store the output in ~/logs/memwatch before tuning so you can prove improvement.",
                        "Flag any process that consistently consumes >20% of RAM for follow-up fixes.",
                    ],
                },
                {
                    "title": "Kernel memory tuning (adaptive, reversible)",
                    "objective": "Reduce swap churn and hold more working set in compressed RAM before eviction.",
                    "commands": [
                        {
                            "command": "sudo sysctl vm.compressor_threshold=8",
                            "description": "Keep more pages compressed before swapping.",
                            "requires_sudo": True,
                        },
                        {
                            "command": "sudo sysctl vm.page_free_min=4000",
                            "description": "Trigger earlier free-page replenishment to avoid stalls.",
                            "requires_sudo": True,
                        },
                        {
                            "command": "sudo sysctl vm.vm_compressor_mode=4",
                            "description": "Favor skip-swap mode, trading CPU for fewer disk writes.",
                            "requires_sudo": True,
                        },
                        {
                            "command": "sudo defaults write /Library/Preferences/com.apple.dynamic_pager ReduceSwapUsage -bool true",
                            "description": "Bias the pager toward compression; reboot to fully apply.",
                            "requires_sudo": True,
                        },
                    ],
                    "verification": [
                        "Re-run `sysctl vm.page_free_min vm.vm_compressor_mode vm.compressor_threshold` to confirm the values held.",
                        "If latency-sensitive jobs regress, roll back the knobs with the default values (typically 0 or 2).",
                    ],
                },
                {
                    "title": "Thread pool sizing and priority hygiene",
                    "objective": "Cap worker pools to available cores and demote background noise.",
                    "commands": [
                        {
                            "command": "sysctl -n hw.physicalcpu",
                            "description": "Use as the baseline for CPU-bound pool sizing.",
                        },
                        {
                            "command": "sysctl -n hw.logicalcpu",
                            "description": "Track the SMT ceiling for IO-heavy jobs.",
                        },
                        {
                            "command": "export OMP_NUM_THREADS=$(sysctl -n hw.physicalcpu)",
                            "description": "Keep OpenMP workloads at physical core count.",
                        },
                        {
                            "command": "export UV_THREADPOOL_SIZE=$(sysctl -n hw.physicalcpu)",
                            "description": "Prevent libuv (Node.js) from growing unbounded.",
                        },
                        {
                            "command": "taskpolicy -l <PID>",
                            "description": "Inspect QoS for a suspect process (replace <PID> with the real process id).",
                        },
                        {
                            "command": "sudo taskpolicy -s BG <PID>",
                            "description": "Push noisy background workers into lower QoS so the UI stays responsive.",
                            "requires_sudo": True,
                        },
                    ],
                    "verification": [
                        "After exports, restart shells or supervisors so workloads inherit the caps.",
                        "Confirm thread counts with `ps -axo pid,thcount,rss,comm | sort -nrk2,3 | head`.",
                    ],
                },
                {
                    "title": "Automation helpers (optional but recommended)",
                    "objective": "Stand up lightweight scripts that operators can trigger during incidents.",
                    "commands": [
                        {
                            "command": (
                                "cat <<'EOF' > ~/bin/trim_memory.sh\n"
                                "#!/bin/zsh\n"
                                "ps -axo pid,rss,comm | sort -nrk2 | head -n 5\n"
                                "sudo memory_pressure -l warn\n"
                                "sudo purge\n"
                                "vm_stat\n"
                                "EOF\n"
                                "chmod +x ~/bin/trim_memory.sh"
                            ),
                            "description": "Create a quick triage script to capture offenders and flush caches.",
                            "requires_sudo": True,
                        },
                        {
                            "command": (
                                "cat <<'EOF' > ~/bin/thread_guard.sh\n"
                                "#!/bin/zsh\n"
                                "limit=800\n"
                                "for pid in $(ps -axo pid); do\n"
                                "  threads=$(ps -M $pid 2>/dev/null | wc -l | tr -d ' ')\n"
                                "  if [[ $threads -gt $limit ]]; then\n"
                                "    sudo renice +15 -p $pid >/dev/null 2>&1\n"
                                "  fi\n"
                                "done\n"
                                "EOF\n"
                                "chmod +x ~/bin/thread_guard.sh"
                            ),
                            "description": "Install a guard that soft-renices runaway thread factories.",
                            "requires_sudo": True,
                        },
                        {
                            "command": (
                                "cat <<'EOF' > ~/Library/LaunchAgents/com.local.memory_guard.plist\n"
                                "<?xml version='1.0' encoding='UTF-8'?>\n"
                                "<!DOCTYPE plist PUBLIC '-//Apple//DTD PLIST 1.0//EN' "
                                "'http://www.apple.com/DTDs/PropertyList-1.0.dtd'>\n"
                                "<plist version='1.0'><dict>\n"
                                "  <key>Label</key><string>com.local.memory_guard</string>\n"
                                "  <key>ProgramArguments</key><array>"
                                "<string>/bin/zsh</string><string>-lc</string>"
                                "<string>~/bin/trim_memory.sh</string></array>\n"
                                "  <key>StartInterval</key><integer>300</integer>\n"
                                "  <key>RunAtLoad</key><true/>\n"
                                "</dict></plist>\n"
                                "EOF\n"
                                "launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.local.memory_guard.plist"
                            ),
                            "description": "Schedule periodic trims so memory pressure gets logged and relieved automatically.",
                            "requires_sudo": True,
                        },
                    ],
                    "verification": [
                        "Check `launchctl print gui/$UID/com.local.memory_guard` for a healthy state.",
                        "Keep scripts under source control so Evidence Packs capture every change.",
                    ],
                },
                {
                    "title": "Persistence and post-change validation",
                    "objective": "Repeat checks to prove memory pressure drops and ensure limits persist after reboot.",
                    "commands": [
                        {
                            "command": "sudo launchctl limit maxproc 2048 4096",
                            "description": "Enforce sane process caps immediately.",
                            "requires_sudo": True,
                        },
                        {
                            "command": "sudo launchctl limit maxfiles 10240 40960",
                            "description": "Prevent descriptor exhaustion during thrash recovery.",
                            "requires_sudo": True,
                        },
                        {
                            "command": "sudo launchctl config system maxproc 2048 4096",
                            "description": "Persist process caps across boots (reboot required).",
                            "requires_sudo": True,
                        },
                        {
                            "command": "sudo launchctl config system maxfiles 10240 40960",
                            "description": "Persist file descriptor caps across boots.",
                            "requires_sudo": True,
                        },
                        {
                            "command": "sysctl vm.page_free_min vm.vm_compressor_mode vm.compressor_threshold",
                            "description": "Confirm the tuned values survived until a reboot applies configs.",
                        },
                        {
                            "command": "launchctl limit",
                            "description": "Snapshot the final limits for the incident report.",
                        },
                        {
                            "command": "memory_pressure -l warn | head -n 3",
                            "description": "Verify the system-wide pressure returns to Normal.",
                        },
                    ],
                    "verification": [
                        "Archive a final `vm_stat` + `sysctl vm.swapusage` reading to compare with the baseline.",
                        "After the next reboot, rerun the validation trio to ensure persistence.",
                    ],
                },
            ],
            "follow_up": [
                "Reboot during a maintenance window so launchd configs and dynamic_pager settings apply cleanly.",
                "Attach the before/after telemetry to the incident ticket for audit readiness.",
                "Track any processes repeatedly reniced by thread_guard and assign owners to fix leaks at the source.",
            ],
        }

        return plan

    def cleanup_resources(self):
        """Cleanup system resources"""
        # Kill all background tasks
        for task_id in list(self.running_processes.keys()):
            self.kill_task(task_id, force=True)

        # Shutdown executor
        self.executor.shutdown(wait=True)

        self.logger.info("System operations controller cleaned up")


# Network service manager
class NetworkServiceManager:
    """
    Manage network services and port exposure
    """

    def __init__(self, system_controller: SystemOperationsController):
        self.system_controller = system_controller
        self.services = {}
        self.logger = logging.getLogger(__name__)

    def start_service(self, config: ServiceConfig) -> Dict[str, Any]:
        """Start a network service"""
        try:
            # Check if port is available
            if not self.system_controller._is_port_available(config.port):
                return {
                    "success": False,
                    "error": f"Port {config.port} is already in use",
                }

            # Start service (this would be service-specific implementation)
            service_info = {
                "name": config.name,
                "port": config.port,
                "host": config.host,
                "protocol": config.protocol,
                "status": "running",
                "start_time": time.time(),
            }

            self.services[config.name] = service_info

            # Expose port if needed
            if config.auto_start:
                expose_result = self.system_controller.expose_port(
                    config.port, config.name, config.protocol
                )
                service_info["public_url"] = expose_result.get("public_url")

            self.logger.info(f"Service {config.name} started on port {config.port}")

            return {"success": True, "service": service_info}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_service(self, service_name: str) -> Dict[str, Any]:
        """Stop a network service"""
        if service_name not in self.services:
            return {"success": False, "error": f"Service {service_name} not found"}

        try:
            service_info = self.services[service_name]
            service_info["status"] = "stopped"
            service_info["stop_time"] = time.time()

            self.logger.info(f"Service {service_name} stopped")

            return {"success": True, "service": service_info}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a service"""
        if service_name not in self.services:
            return {"status": "not_found"}

        return self.services[service_name]

    def list_services(self) -> Dict[str, Any]:
        """List all managed services"""
        return {
            "services": list(self.services.values()),
            "total_services": len(self.services),
            "running_services": len(
                [s for s in self.services.values() if s["status"] == "running"]
            ),
        }


# Example usage
if __name__ == "__main__":
    # Initialize system controller
    controller = SystemOperationsController()

    # Execute a command
    result = controller.execute_command("ls -la")
    print(f"Command result: {result}")

    # Start background task
    task_id = controller.execute_background_command("sleep 10", "test_task")
    print(f"Started background task: {task_id}")

    # Get system info
    sys_info = controller.get_system_info()
    print(f"System info: {sys_info}")

    # Cleanup
    controller.cleanup_resources()
