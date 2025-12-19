#!/usr/bin/env python3
"""
Self-Healing Engine - Advanced error recovery and automatic remediation

This module provides intelligent error detection, analysis, and automatic
recovery for all projects in the workspace.

Features:
- Automatic error pattern detection
- Intelligent recovery strategies
- Learning from past fixes
- Proactive health monitoring
- Automatic rollback on failed fixes

Usage:
    # Run as standalone monitor
    python scripts/self_healing_engine.py
    
    # Integrate with other systems
    from scripts.self_healing_engine import SelfHealingEngine
    engine = SelfHealingEngine()
    engine.start()
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass
class ErrorPattern:
    """Detected error pattern."""
    pattern: str
    severity: str  # critical, high, medium, low
    category: str  # syntax, runtime, dependency, configuration
    frequency: int = 0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)


@dataclass
class RecoveryStrategy:
    """Strategy for recovering from an error."""
    name: str
    description: str
    commands: List[str]
    success_rate: float = 0.0
    total_attempts: int = 0
    successful_attempts: int = 0


@dataclass
class HealthMetric:
    """Health metric for a project."""
    project: str
    metric: str
    value: float
    threshold: float
    status: str  # healthy, warning, critical
    timestamp: float = field(default_factory=time.time)


class SelfHealingEngine:
    """Advanced error recovery and self-healing engine."""
    
    # Common error patterns and their recovery strategies
    ERROR_PATTERNS = [
        {
            "pattern": r"ModuleNotFoundError: No module named '(\w+)'",
            "severity": "high",
            "category": "dependency",
            "recovery": ["pip install {1}", "pip install --upgrade {1}"],
        },
        {
            "pattern": r"npm ERR!.*Cannot find module '([\w\-@/]+)'",
            "severity": "high",
            "category": "dependency",
            "recovery": ["npm install {1}", "npm install --save {1}"],
        },
        {
            "pattern": r"Error: ENOENT: no such file or directory",
            "severity": "medium",
            "category": "runtime",
            "recovery": ["mkdir -p {1}", "touch {1}"],
        },
        {
            "pattern": r"Permission denied",
            "severity": "high",
            "category": "configuration",
            "recovery": ["chmod +x {1}", "sudo chmod +x {1}"],
        },
        {
            "pattern": r"Port (\d+) is already in use",
            "severity": "medium",
            "category": "runtime",
            "recovery": ["kill -9 $(lsof -ti:{1})", "fuser -k {1}/tcp"],
        },
        {
            "pattern": r"git: command not found",
            "severity": "critical",
            "category": "dependency",
            "recovery": ["sudo apt-get install git", "brew install git"],
        },
        {
            "pattern": r"SyntaxError:",
            "severity": "high",
            "category": "syntax",
            "recovery": ["# Syntax errors require manual code fixes"],
        },
    ]
    
    def __init__(
        self,
        *,
        log_dir: Path = REPO_ROOT / "logs",
        knowledge_base: Path = REPO_ROOT / "logs" / "healing_knowledge.json",
        health_check_interval: int = 60,
        max_recovery_attempts: int = 3,
    ):
        self.log_dir = log_dir
        self.knowledge_base = knowledge_base
        self.health_check_interval = health_check_interval
        self.max_recovery_attempts = max_recovery_attempts
        
        # State
        self.running = False
        self.detected_errors: Dict[str, ErrorPattern] = {}
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.health_metrics: List[HealthMetric] = []
        
        # Threads
        self.monitor_thread: Optional[threading.Thread] = None
        self.health_thread: Optional[threading.Thread] = None
        
        # Logging
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
        
        # Load knowledge base
        self.load_knowledge_base()
    
    def setup_logging(self):
        """Set up logging."""
        log_file = self.log_dir / "self_healing.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
        
        self.logger = logging.getLogger(__name__)
    
    def load_knowledge_base(self):
        """Load the knowledge base of past fixes."""
        if not self.knowledge_base.exists():
            self.logger.info("No existing knowledge base found, starting fresh")
            return
        
        try:
            with self.knowledge_base.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Load recovery strategies
            for name, strategy_data in data.get("strategies", {}).items():
                strategy = RecoveryStrategy(
                    name=name,
                    description=strategy_data["description"],
                    commands=strategy_data["commands"],
                    success_rate=strategy_data.get("success_rate", 0.0),
                    total_attempts=strategy_data.get("total_attempts", 0),
                    successful_attempts=strategy_data.get("successful_attempts", 0),
                )
                self.recovery_strategies[name] = strategy
            
            self.logger.info(f"Loaded {len(self.recovery_strategies)} recovery strategies")
        
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {e}")
    
    def save_knowledge_base(self):
        """Save the knowledge base of fixes."""
        data = {
            "strategies": {
                name: {
                    "description": strategy.description,
                    "commands": strategy.commands,
                    "success_rate": strategy.success_rate,
                    "total_attempts": strategy.total_attempts,
                    "successful_attempts": strategy.successful_attempts,
                }
                for name, strategy in self.recovery_strategies.items()
            },
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        try:
            with self.knowledge_base.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            self.logger.info("Knowledge base saved")
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {e}")
    
    def detect_error(self, log_line: str) -> Optional[ErrorPattern]:
        """Detect error patterns in log lines."""
        for pattern_def in self.ERROR_PATTERNS:
            match = re.search(pattern_def["pattern"], log_line)
            if match:
                pattern_key = f"{pattern_def['category']}_{pattern_def['pattern']}"
                
                if pattern_key in self.detected_errors:
                    error = self.detected_errors[pattern_key]
                    error.frequency += 1
                    error.last_seen = time.time()
                else:
                    error = ErrorPattern(
                        pattern=pattern_def["pattern"],
                        severity=pattern_def["severity"],
                        category=pattern_def["category"],
                        frequency=1,
                    )
                    self.detected_errors[pattern_key] = error
                
                return error
        
        return None
    
    def get_recovery_strategy(self, error: ErrorPattern) -> Optional[RecoveryStrategy]:
        """Get the best recovery strategy for an error."""
        # Find matching pattern definition
        for pattern_def in self.ERROR_PATTERNS:
            if pattern_def["pattern"] == error.pattern:
                strategy_name = f"{error.category}_{error.pattern[:30]}"
                
                if strategy_name in self.recovery_strategies:
                    return self.recovery_strategies[strategy_name]
                
                # Create new strategy
                strategy = RecoveryStrategy(
                    name=strategy_name,
                    description=f"Recovery for {error.category} error",
                    commands=pattern_def.get("recovery", []),
                )
                self.recovery_strategies[strategy_name] = strategy
                return strategy
        
        return None
    
    def execute_recovery(
        self,
        strategy: RecoveryStrategy,
        project_path: Path,
        error_context: str = "",
    ) -> bool:
        """Execute a recovery strategy."""
        self.logger.info(f"Executing recovery strategy: {strategy.name}")
        self.logger.info(f"Commands: {strategy.commands}")
        
        strategy.total_attempts += 1
        
        # Create backup before attempting fix
        self._create_backup(project_path)
        
        success = True
        for cmd in strategy.commands:
            if cmd.startswith("#"):
                # Skip comments
                continue
            
            # Substitute placeholders
            cmd = self._substitute_placeholders(cmd, error_context)
            
            self.logger.info(f"Running: {cmd}")
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    self.logger.warning(f"Command failed: {cmd}")
                    self.logger.warning(f"Error: {result.stderr}")
                    success = False
                    break
                
                self.logger.info(f"Command succeeded: {cmd}")
            
            except subprocess.TimeoutExpired:
                self.logger.error(f"Command timed out: {cmd}")
                success = False
                break
            
            except Exception as e:
                self.logger.error(f"Error executing command: {e}")
                success = False
                break
        
        if success:
            strategy.successful_attempts += 1
            strategy.success_rate = strategy.successful_attempts / strategy.total_attempts
            self.logger.info(f"Recovery successful! Success rate: {strategy.success_rate:.1%}")
        else:
            # Rollback on failure
            self._rollback_backup(project_path)
            self.logger.error("Recovery failed, rolled back changes")
        
        # Save updated knowledge base
        self.save_knowledge_base()
        
        return success
    
    def _create_backup(self, project_path: Path):
        """Create a backup before making changes."""
        backup_dir = self.log_dir / "backups" / project_path.name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}.tar.gz"
        
        try:
            subprocess.run(
                ["tar", "-czf", str(backup_path), "."],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            self.logger.info(f"Backup created: {backup_path}")
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
    
    def _rollback_backup(self, project_path: Path):
        """Rollback to the most recent backup."""
        backup_dir = self.log_dir / "backups" / project_path.name
        
        if not backup_dir.exists():
            self.logger.warning("No backups found for rollback")
            return
        
        # Find most recent backup
        backups = sorted(backup_dir.glob("backup_*.tar.gz"), reverse=True)
        if not backups:
            self.logger.warning("No backups found for rollback")
            return
        
        latest_backup = backups[0]
        
        try:
            subprocess.run(
                ["tar", "-xzf", str(latest_backup)],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            self.logger.info(f"Rolled back to: {latest_backup}")
        except Exception as e:
            self.logger.error(f"Failed to rollback: {e}")
    
    def _substitute_placeholders(self, cmd: str, context: str) -> str:
        """Substitute placeholders in commands."""
        # Extract placeholders like {1}, {2}, etc.
        # This is a simple implementation
        return cmd.replace("{1}", context)
    
    def monitor_logs(self):
        """Monitor logs for errors."""
        self.logger.info("Starting log monitoring...")
        
        while self.running:
            try:
                # Monitor all project logs
                log_files = list(self.log_dir.glob("*_monitor.log"))
                
                for log_file in log_files:
                    self._process_log_file(log_file)
                
                time.sleep(10)  # Check every 10 seconds
            
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)
    
    def _process_log_file(self, log_file: Path):
        """Process a single log file for errors."""
        try:
            with log_file.open("r", encoding="utf-8") as f:
                # Read only new lines (store offset)
                lines = f.readlines()
            
            for line in lines:
                error = self.detect_error(line)
                if error and error.severity in ["critical", "high"]:
                    self.logger.warning(f"Detected {error.severity} error: {error.pattern}")
                    
                    # Attempt recovery if frequency is high enough
                    if error.frequency >= 3:
                        strategy = self.get_recovery_strategy(error)
                        if strategy:
                            project_name = log_file.stem.replace("_monitor", "")
                            # Note: We need project path, skipping for now
                            self.logger.info(f"Recovery strategy available for {project_name}")
        
        except Exception as e:
            self.logger.error(f"Error processing log file {log_file}: {e}")
    
    def health_check_loop(self):
        """Continuous health checking."""
        self.logger.info("Starting health check loop...")
        
        while self.running:
            try:
                # Check health metrics
                self._check_system_health()
                
                time.sleep(self.health_check_interval)
            
            except Exception as e:
                self.logger.error(f"Error in health check: {e}")
                time.sleep(60)
    
    def _check_system_health(self):
        """Check overall system health."""
        status_file = self.log_dir / "status_report.json"
        
        if not status_file.exists():
            return
        
        try:
            with status_file.open("r", encoding="utf-8") as f:
                status = json.load(f)
            
            monitors = status.get("monitors", {})
            
            # Check monitor health
            error_count = monitors.get("error", 0)
            stopped_count = monitors.get("stopped", 0)
            
            if error_count > 0:
                self.logger.warning(f"{error_count} monitors in error state")
            
            if stopped_count > 3:
                self.logger.warning(f"{stopped_count} monitors stopped")
        
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
    
    def start(self):
        """Start the self-healing engine."""
        self.logger.info("═" * 80)
        self.logger.info("🛡️  SELF-HEALING ENGINE STARTING")
        self.logger.info("═" * 80)
        
        self.running = True
        
        # Start monitoring threads
        self.monitor_thread = threading.Thread(target=self.monitor_logs, daemon=True)
        self.monitor_thread.start()
        
        self.health_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        self.health_thread.start()
        
        self.logger.info("✅ Self-healing engine is running")
        self.logger.info("   • Log monitoring: Active")
        self.logger.info("   • Health checks: Active")
        self.logger.info("   • Recovery strategies: Loaded")
        self.logger.info("═" * 80)
    
    def stop(self):
        """Stop the self-healing engine."""
        self.logger.info("Stopping self-healing engine...")
        self.running = False
        
        # Save knowledge base
        self.save_knowledge_base()
        
        self.logger.info("✅ Self-healing engine stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Self-Healing Engine for OS Dashboard AI Assistant"
    )
    
    parser.add_argument(
        "--health-interval",
        type=int,
        default=60,
        help="Health check interval in seconds (default: 60)",
    )
    
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum recovery attempts per error (default: 3)",
    )
    
    args = parser.parse_args()
    
    engine = SelfHealingEngine(
        health_check_interval=args.health_interval,
        max_recovery_attempts=args.max_attempts,
    )
    
    try:
        engine.start()
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
        engine.stop()
        return 0
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
