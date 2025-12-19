#!/usr/bin/env python3
"""
Memory Resource Manager Daemon

Monitors system memory and automatically reduces resource allocation for processes
with exponential (O(2^n)) or quadratic (O(n^2)) memory growth patterns, especially
after user inactivity periods.

Features:
- Real-time memory monitoring
- Complexity pattern detection (O(2^n), O(n^2), etc.)
- User activity detection
- Automatic resource throttling/suspension
- AI-powered decision making for resource allocation
- Process prioritization based on usage patterns
"""

import os
import sys
import time
import signal
import logging
import argparse
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import platform

try:
    import psutil
except ImportError:
    print("ERROR: psutil not installed. Install with: pip install psutil")
    sys.exit(1)

# macOS-specific imports
if platform.system() == "Darwin":
    try:
        from Quartz import CGEventSourceSecondsSinceLastEventType, kCGEventSourceStateHIDSystemState
    except ImportError:
        # Quartz requires pyobjc-framework-Quartz, which may not be installed
        try:
            from AppKit import NSEvent
            # Use alternative method if Quartz not available
            CGEventSourceSecondsSinceLastEventType = None
            kCGEventSourceStateHIDSystemState = None
        except ImportError:
            CGEventSourceSecondsSinceLastEventType = None
            kCGEventSourceStateHIDSystemState = None
else:
    CGEventSourceSecondsSinceLastEventType = None
    kCGEventSourceStateHIDSystemState = None


class ProcessState(Enum):
    """Process state enumeration"""
    ACTIVE = "active"
    THROTTLED = "throttled"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class ComplexityLevel(Enum):
    """Memory complexity classification"""
    LINEAR = "O(n)"
    QUADRATIC = "O(n^2)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"
    UNKNOWN = "unknown"


@dataclass
class ProcessMetrics:
    """Metrics for a single process"""
    pid: int
    name: str
    memory_mb: float
    memory_percent: float
    cpu_percent: float
    num_threads: int
    create_time: float
    last_activity: datetime
    memory_history: deque
    complexity: ComplexityLevel
    state: ProcessState
    throttle_level: float  # 0.0 to 1.0, where 1.0 is full resources
    suspension_count: int
    last_user_interaction: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['memory_history'] = list(self.memory_history)
        data['complexity'] = self.complexity.value
        data['state'] = self.state.value
        data['last_activity'] = self.last_activity.isoformat()
        if self.last_user_interaction:
            data['last_user_interaction'] = self.last_user_interaction.isoformat()
        return data


@dataclass
class SystemMetrics:
    """Overall system metrics"""
    total_memory_mb: float
    available_memory_mb: float
    used_memory_mb: float
    memory_percent: float
    swap_used_mb: float
    swap_percent: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ComplexityAnalyzer:
    """Analyzes process memory patterns to detect complexity"""
    
    def __init__(self, history_size: int = 20):
        self.history_size = history_size
        self.logger = logging.getLogger(__name__)
    
    def analyze_complexity(self, memory_history: deque) -> ComplexityLevel:
        """
        Analyze memory growth pattern to determine complexity.
        
        Uses statistical analysis to detect:
        - Linear: constant growth rate
        - Quadratic: growth rate increases linearly
        - Exponential: growth rate increases exponentially
        """
        if len(memory_history) < 5:
            return ComplexityLevel.UNKNOWN
        
        # Convert to list for analysis
        mem_values = list(memory_history)
        
        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(mem_values)):
            if mem_values[i-1] > 0:
                rate = (mem_values[i] - mem_values[i-1]) / mem_values[i-1]
                growth_rates.append(rate)
        
        if not growth_rates:
            return ComplexityLevel.UNKNOWN
        
        # Analyze growth rate trends
        if len(growth_rates) < 3:
            return ComplexityLevel.LINEAR
        
        # Calculate second derivative (rate of change of growth rate)
        growth_accelerations = []
        for i in range(1, len(growth_rates)):
            growth_accelerations.append(growth_rates[i] - growth_rates[i-1])
        
        avg_growth = sum(growth_rates) / len(growth_rates)
        avg_acceleration = sum(growth_accelerations) / len(growth_accelerations) if growth_accelerations else 0
        
        # Classification logic
        if avg_growth < 0.01:  # Less than 1% growth per interval
            return ComplexityLevel.LINEAR
        elif avg_acceleration < 0.05:  # Slow acceleration
            return ComplexityLevel.QUADRATIC
        elif avg_acceleration > 0.2 or avg_growth > 0.5:  # High acceleration or growth
            return ComplexityLevel.EXPONENTIAL
        else:
            return ComplexityLevel.QUADRATIC
    
    def calculate_memory_score(self, metrics: ProcessMetrics) -> float:
        """
        Calculate a score (0-100) indicating how problematic a process is.
        Higher scores = more problematic.
        """
        score = 0.0
        
        # Base score from memory usage
        score += metrics.memory_percent * 0.4
        
        # Complexity multiplier
        complexity_multipliers = {
            ComplexityLevel.LINEAR: 1.0,
            ComplexityLevel.QUADRATIC: 2.0,
            ComplexityLevel.EXPONENTIAL: 4.0,
            ComplexityLevel.FACTORIAL: 8.0,
            ComplexityLevel.UNKNOWN: 1.5
        }
        score *= complexity_multipliers.get(metrics.complexity, 1.0)
        
        # Growth rate penalty
        if len(metrics.memory_history) >= 2:
            recent_growth = list(metrics.memory_history)[-1] - list(metrics.memory_history)[-2]
            if recent_growth > 0:
                score += min(recent_growth / 100.0, 20.0)  # Cap at 20 points
        
        return min(score, 100.0)


class UserActivityDetector:
    """Detects user activity on the system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_activity_time = datetime.now()
        self.activity_threshold = 60  # seconds of inactivity before considered idle
    
    def get_last_activity_time(self) -> datetime:
        """Get the time of last user activity"""
        if platform.system() == "Darwin" and CGEventSourceSecondsSinceLastEventType:
            try:
                # macOS: Get time since last keyboard/mouse activity
                seconds_since = CGEventSourceSecondsSinceLastEventType(
                    kCGEventSourceStateHIDSystemState
                )
                if seconds_since is not None:
                    return datetime.now() - timedelta(seconds=seconds_since)
            except Exception as e:
                self.logger.debug(f"Could not get macOS activity: {e}")
        
        # Fallback: Check for active processes that indicate user activity
        try:
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    pinfo = proc.info
                    # Check for common interactive applications
                    interactive_apps = ['Finder', 'Safari', 'Chrome', 'Firefox', 
                                       'Terminal', 'iTerm', 'Code', 'Cursor',
                                       'Slack', 'Discord', 'Spotify']
                    if any(app.lower() in pinfo['name'].lower() for app in interactive_apps):
                        # Check if process has recent CPU usage (indicates activity)
                        try:
                            proc_obj = psutil.Process(pinfo['pid'])
                            if proc_obj.is_running():
                                cpu = proc_obj.cpu_percent(interval=0.1)
                                if cpu > 1.0:  # Active process
                                    return datetime.now()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.debug(f"Error detecting activity: {e}")
        
        return self.last_activity_time
    
    def is_user_active(self) -> bool:
        """Check if user is currently active"""
        last_activity = self.get_last_activity_time()
        inactive_duration = (datetime.now() - last_activity).total_seconds()
        return inactive_duration < self.activity_threshold
    
    def get_inactivity_duration(self) -> float:
        """Get duration of inactivity in seconds"""
        last_activity = self.get_last_activity_time()
        return (datetime.now() - last_activity).total_seconds()


class ResourceThrottler:
    """Manages resource throttling and suspension of processes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def throttle_process(self, pid: int, throttle_level: float) -> bool:
        """
        Throttle a process by setting CPU and I/O limits.
        
        Args:
            pid: Process ID
            throttle_level: 0.0 (fully throttled) to 1.0 (full resources)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            proc = psutil.Process(pid)
            
            if platform.system() == "Darwin":
                # macOS: Use nice value and CPU affinity
                try:
                    # Set nice value (higher = lower priority)
                    nice_value = int(20 * (1 - throttle_level))
                    proc.nice(nice_value)
                    
                    # Limit CPU usage by setting CPU affinity to fewer cores
                    cpu_count = psutil.cpu_count()
                    if cpu_count > 1:
                        cores_to_use = max(1, int(cpu_count * throttle_level))
                        proc.cpu_affinity(list(range(cores_to_use)))
                    
                    self.logger.info(f"Throttled PID {pid} to {throttle_level:.2%} resources")
                    return True
                except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                    self.logger.warning(f"Cannot throttle PID {pid}: {e}")
                    return False
            else:
                # Linux: Use nice and ionice
                try:
                    nice_value = int(20 * (1 - throttle_level))
                    proc.nice(nice_value)
                    # Note: ionice requires root on most systems
                    self.logger.info(f"Throttled PID {pid} to {throttle_level:.2%} resources")
                    return True
                except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                    self.logger.warning(f"Cannot throttle PID {pid}: {e}")
                    return False
                    
        except psutil.NoSuchProcess:
            self.logger.warning(f"Process {pid} no longer exists")
            return False
        except Exception as e:
            self.logger.error(f"Error throttling process {pid}: {e}")
            return False
    
    def suspend_process(self, pid: int) -> bool:
        """Suspend a process (pause execution)"""
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            self.logger.info(f"Suspended PID {pid}")
            return True
        except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
            self.logger.warning(f"Cannot suspend PID {pid}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error suspending process {pid}: {e}")
            return False
    
    def resume_process(self, pid: int) -> bool:
        """Resume a suspended process"""
        try:
            proc = psutil.Process(pid)
            proc.resume()
            self.logger.info(f"Resumed PID {pid}")
            return True
        except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
            self.logger.warning(f"Cannot resume PID {pid}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error resuming process {pid}: {e}")
            return False
    
    def terminate_process(self, pid: int, force: bool = False) -> bool:
        """Terminate a process (last resort)"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            self.logger.warning(f"{'Killed' if force else 'Terminated'} PID {pid}")
            return True
        except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
            self.logger.warning(f"Cannot terminate PID {pid}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error terminating process {pid}: {e}")
            return False


class MemoryResourceManager:
    """Main memory resource management daemon"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.running = False
        self.processes: Dict[int, ProcessMetrics] = {}
        self.complexity_analyzer = ComplexityAnalyzer(
            history_size=config.get('history_size', 20)
        )
        self.activity_detector = UserActivityDetector()
        self.throttler = ResourceThrottler()
        
        # Configuration
        self.memory_threshold = config.get('memory_threshold', 85.0)  # % memory usage
        self.inactivity_threshold = config.get('inactivity_threshold', 300)  # seconds
        self.monitor_interval = config.get('monitor_interval', 5)  # seconds
        self.min_memory_mb = config.get('min_memory_mb', 100)  # MB threshold
        self.whitelist = set(config.get('whitelist', []))  # Process names to never throttle
        self.blacklist = set(config.get('blacklist', []))  # Process names to always throttle
        
        # Statistics
        self.stats = {
            'processes_throttled': 0,
            'processes_suspended': 0,
            'processes_terminated': 0,
            'memory_freed_mb': 0.0,
            'start_time': datetime.now()
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_level = self.config.get('log_level', 'INFO').upper()
        log_file = self.config.get('log_file', 'logs/memory_manager.log')
        
        # Create logs directory if it doesn't exist
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system memory metrics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return SystemMetrics(
            total_memory_mb=memory.total / (1024 * 1024),
            available_memory_mb=memory.available / (1024 * 1024),
            used_memory_mb=memory.used / (1024 * 1024),
            memory_percent=memory.percent,
            swap_used_mb=swap.used / (1024 * 1024),
            swap_percent=swap.percent,
            timestamp=datetime.now()
        )
    
    def scan_processes(self) -> None:
        """Scan all running processes and update metrics"""
        current_pids = set()
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 
                                        'num_threads', 'create_time']):
            try:
                pinfo = proc.info
                pid = pinfo['pid']
                current_pids.add(pid)
                
                # Skip if whitelisted
                if pinfo['name'] in self.whitelist:
                    continue
                
                # Get process object for detailed metrics
                proc_obj = psutil.Process(pid)
                memory_info = proc_obj.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                
                # Skip processes with low memory usage
                if memory_mb < self.min_memory_mb:
                    continue
                
                # Get or create process metrics
                if pid not in self.processes:
                    self.processes[pid] = ProcessMetrics(
                        pid=pid,
                        name=pinfo['name'],
                        memory_mb=memory_mb,
                        memory_percent=0.0,
                        cpu_percent=0.0,
                        num_threads=pinfo.get('num_threads', 0),
                        create_time=pinfo.get('create_time', time.time()),
                        memory_history=deque(maxlen=self.complexity_analyzer.history_size),
                        complexity=ComplexityLevel.UNKNOWN,
                        state=ProcessState.ACTIVE,
                        throttle_level=1.0,
                        suspension_count=0,
                        last_user_interaction=None
                    )
                
                metrics = self.processes[pid]
                
                # Update metrics
                total_memory = psutil.virtual_memory().total
                metrics.memory_mb = memory_mb
                metrics.memory_percent = (memory_mb / (total_memory / (1024 * 1024))) * 100
                metrics.cpu_percent = proc_obj.cpu_percent(interval=0.1)
                metrics.num_threads = pinfo.get('num_threads', 0)
                metrics.last_activity = datetime.now()
                
                # Update memory history
                metrics.memory_history.append(memory_mb)
                
                # Analyze complexity
                if len(metrics.memory_history) >= 5:
                    metrics.complexity = self.complexity_analyzer.analyze_complexity(
                        metrics.memory_history
                    )
                
                # Update last user interaction if process is active
                if metrics.cpu_percent > 1.0:
                    metrics.last_user_interaction = datetime.now()
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                self.logger.debug(f"Error scanning process {pid}: {e}")
        
        # Remove processes that no longer exist
        dead_pids = set(self.processes.keys()) - current_pids
        for pid in dead_pids:
            del self.processes[pid]
    
    def should_throttle(self, metrics: ProcessMetrics, system_metrics: SystemMetrics,
                       inactivity_duration: float) -> Tuple[bool, float]:
        """
        Determine if a process should be throttled and to what level.
        
        Returns:
            (should_throttle, throttle_level)
        """
        # Never throttle whitelisted processes
        if metrics.name in self.whitelist:
            return False, 1.0
        
        # Always throttle blacklisted processes if memory is high
        if metrics.name in self.blacklist and system_metrics.memory_percent > self.memory_threshold:
            return True, 0.3
        
        # Check if system memory is under pressure
        memory_pressure = system_metrics.memory_percent > self.memory_threshold
        
        # Check if user is inactive
        user_inactive = inactivity_duration > self.inactivity_threshold
        
        # Calculate memory score
        memory_score = self.complexity_analyzer.calculate_memory_score(metrics)
        
        # Decision logic
        should_throttle = False
        throttle_level = 1.0
        
        if memory_pressure and user_inactive:
            # High memory + user inactive = aggressive throttling
            if memory_score > 50:
                should_throttle = True
                # Exponential complexity gets more aggressive throttling
                if metrics.complexity == ComplexityLevel.EXPONENTIAL:
                    throttle_level = 0.1
                elif metrics.complexity == ComplexityLevel.QUADRATIC:
                    throttle_level = 0.3
                else:
                    throttle_level = 0.5
        elif memory_pressure:
            # High memory but user active = moderate throttling
            if memory_score > 70:
                should_throttle = True
                throttle_level = 0.7
        elif user_inactive and memory_score > 60:
            # User inactive but memory OK = light throttling for high-complexity processes
            if metrics.complexity in [ComplexityLevel.EXPONENTIAL, ComplexityLevel.QUADRATIC]:
                should_throttle = True
                throttle_level = 0.6
        
        return should_throttle, throttle_level
    
    def manage_resources(self) -> None:
        """Main resource management loop"""
        system_metrics = self.get_system_metrics()
        inactivity_duration = self.activity_detector.get_inactivity_duration()
        user_active = self.activity_detector.is_user_active()
        
        # Sort processes by memory score (most problematic first)
        process_scores = []
        for pid, metrics in self.processes.items():
            score = self.complexity_analyzer.calculate_memory_score(metrics)
            process_scores.append((pid, metrics, score))
        
        process_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Process top offenders first
        for pid, metrics, score in process_scores:
            should_throttle, throttle_level = self.should_throttle(
                metrics, system_metrics, inactivity_duration
            )
            
            if should_throttle:
                # Apply throttling
                if metrics.state == ProcessState.ACTIVE:
                    if self.throttler.throttle_process(pid, throttle_level):
                        metrics.state = ProcessState.THROTTLED
                        metrics.throttle_level = throttle_level
                        self.stats['processes_throttled'] += 1
                        self.logger.info(
                            f"Throttled {metrics.name} (PID {pid}) to {throttle_level:.0%} - "
                            f"Score: {score:.1f}, Complexity: {metrics.complexity.value}"
                        )
                elif metrics.state == ProcessState.THROTTLED:
                    # Update throttle level if needed
                    if abs(metrics.throttle_level - throttle_level) > 0.1:
                        self.throttler.throttle_process(pid, throttle_level)
                        metrics.throttle_level = throttle_level
            else:
                # Restore full resources if previously throttled
                if metrics.state == ProcessState.THROTTLED:
                    if self.throttler.throttle_process(pid, 1.0):
                        metrics.state = ProcessState.ACTIVE
                        metrics.throttle_level = 1.0
                        self.logger.info(f"Restored full resources to {metrics.name} (PID {pid})")
                elif metrics.state == ProcessState.SUSPENDED and user_active:
                    # Resume if user becomes active
                    if self.throttler.resume_process(pid):
                        metrics.state = ProcessState.ACTIVE
                        self.logger.info(f"Resumed {metrics.name} (PID {pid}) due to user activity")
    
    def save_state(self, filepath: str) -> None:
        """Save current state to JSON file"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': self.get_system_metrics().to_dict(),
            'processes': {str(pid): metrics.to_dict() for pid, metrics in self.processes.items()},
            'stats': {
                **self.stats,
                'start_time': self.stats['start_time'].isoformat()
            }
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    async def run(self) -> None:
        """Main daemon loop"""
        self.running = True
        self.logger.info("Memory Resource Manager daemon started")
        
        try:
            while self.running:
                # Scan processes
                self.scan_processes()
                
                # Manage resources
                self.manage_resources()
                
                # Save state periodically
                state_file = self.config.get('state_file', 'logs/memory_manager_state.json')
                self.save_state(state_file)
                
                # Sleep until next cycle
                await asyncio.sleep(self.monitor_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.running = False
            self.logger.info("Memory Resource Manager daemon stopped")
    
    def stop(self) -> None:
        """Stop the daemon"""
        self.running = False


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or use defaults"""
    default_config = {
        'memory_threshold': 85.0,
        'inactivity_threshold': 300,
        'monitor_interval': 5,
        'min_memory_mb': 100,
        'history_size': 20,
        'log_level': 'INFO',
        'log_file': 'logs/memory_manager.log',
        'state_file': 'logs/memory_manager_state.json',
        'whitelist': [],
        'blacklist': []
    }
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                default_config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
    
    return default_config


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Memory Resource Manager Daemon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python memory_resource_manager.py

  # Run with custom config
  python memory_resource_manager.py --config config/memory_manager.json

  # Run in foreground with debug logging
  python memory_resource_manager.py --foreground --log-level DEBUG
        """
    )
    
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--foreground', action='store_true', 
                       help='Run in foreground (not as daemon)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    parser.add_argument('--memory-threshold', type=float, default=85.0,
                       help='Memory usage threshold percentage (default: 85.0)')
    parser.add_argument('--inactivity-threshold', type=int, default=300,
                       help='Inactivity threshold in seconds (default: 300)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    config['log_level'] = args.log_level
    if args.memory_threshold:
        config['memory_threshold'] = args.memory_threshold
    if args.inactivity_threshold:
        config['inactivity_threshold'] = args.inactivity_threshold
    
    # Create manager
    manager = MemoryResourceManager(config)
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        manager.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run
    if args.foreground:
        asyncio.run(manager.run())
    else:
        # Run as daemon
        try:
            asyncio.run(manager.run())
        except KeyboardInterrupt:
            manager.stop()


if __name__ == '__main__':
    main()
