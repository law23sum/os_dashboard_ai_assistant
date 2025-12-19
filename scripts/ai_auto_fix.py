#!/usr/bin/env python3
"""Watch backend/frontend logs and let the AI auto-patch regressions and improve code.

Comprehensive Features:
- Detects ALL HTTP errors (4xx, 5xx) and API issues
- Detects warnings and deprecations
- Detects performance issues and bottlenecks
- Proactively analyzes logs for improvement opportunities
- Suggests code quality improvements, refactoring, and optimizations
- Analyzes FastAPI router structure to understand routing issues
- Automatically fixes missing API endpoints and routing problems
- Monitors performance metrics and suggests optimizations
- Identifies code smells and improvement opportunities
- Automatically detects backend/frontend binaries (web + desktop) and tails their logs
- Watches both browser (Vite) and desktop (Electron) log directories with no manual configuration

Usage:
    # Basic usage - watches for errors and improvements
    python scripts/ai_auto_fix.py --backend "python -m uvicorn backend_api.main:app --reload" --frontend "npm run dev:web"
    
    # Only fix errors, disable proactive improvements
    python scripts/ai_auto_fix.py --backend "python main.py" --no-improvements
    
    # Aggressive performance monitoring (flag anything >500ms)
    python scripts/ai_auto_fix.py --backend "python main.py" --performance-threshold-ms 500
    
    # Frequent improvement checks (every 60 seconds)
    python scripts/ai_auto_fix.py --backend "python main.py" --improvement-interval 60

    # Passive mode: just tail existing log directories and auto-fix when they change
    python scripts/ai_auto_fix.py --logs-only --log-dir logs --log-dir frontend/logs
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - dotenv is optional
    load_dotenv = None

if load_dotenv:
    load_dotenv(REPO_ROOT / ".env")  # type: ignore[arg-type]

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil optional
    from utils.psutil_stub import psutil  # type: ignore

try:
    from assistant_core.ai import generate_ai_reply, openai_available  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - optional deps missing
    _MISSING_AI_DEP = exc.name or str(exc)
    _AI_DISABLED_MESSAGE = (
        "AI auto-fix helpers are unavailable because dependency "
        f"`{_MISSING_AI_DEP}` is missing. Install optional packages with "
        "`python -m pip install -r requirements.txt` to enable automated fixes."
    )

    def generate_ai_reply(*args, **kwargs):
        """Fallback stub when assistant_core.ai cannot be imported."""
        return None, _AI_DISABLED_MESSAGE, None

    def openai_available() -> bool:
        return False

    print(f"[auto-fix] {_AI_DISABLED_MESSAGE}")

from assistant_core.db import (  # type: ignore
    ChatMessage,
    init_db,
    load_openai_api_key,
    save_openai_api_key,
)


@dataclass
class ProcessSpec:
    name: str
    command: List[str]


@dataclass
class TestSpec:
    name: str
    command: List[str]


@dataclass(frozen=True)
class BinarySignature:
    """Definition of a process/binary that should trigger log monitoring."""

    label: str
    keywords: List[str]
    log_dirs: List[Path]


DEFAULT_LOG_DIRS = [
    REPO_ROOT / "logs",
    REPO_ROOT / "frontend" / "logs",
    REPO_ROOT / "frontend" / "dist-electron" / "logs",
]

DEFAULT_AUTOFIX_TESTS: List[tuple[str, List[str]]] = [
    ("desktop-launcher", [sys.executable, "-m", "pytest", "-q", "tests/test_desktop_launcher.py"]),
    (
        "desktop-port-guard",
        ["node", "--test", "frontend/scripts/__tests__/dev-desktop-utils.test.mjs"],
    ),
]


class LineBuffer:
    """Keep a rolling buffer of log lines per component."""

    def __init__(self, max_lines: int = 400) -> None:
        self.lines: Deque[str] = deque(maxlen=max_lines)
        self.lock = threading.Lock()

    def push(self, line: str) -> None:
        with self.lock:
            self.lines.append(line.rstrip("\n"))

    def snapshot(self, limit: Optional[int] = None) -> str:
        with self.lock:
            data = list(self.lines)
        if limit is not None:
            data = data[-limit:]
        return "\n".join(data)


class ProcessRunner:
    """Launch a long-running command and stream logs to the orchestrator."""

    def __init__(
        self,
        spec: ProcessSpec,
        line_callback,
        exit_callback,
        cwd: Path = REPO_ROOT,
    ) -> None:
        self.spec = spec
        self.line_callback = line_callback
        self.exit_callback = exit_callback
        self.cwd = cwd
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.emit_exit_events = True

    def start(self) -> None:
        if self.process:
            raise RuntimeError(f"{self.spec.name} already running")
        self.process = subprocess.Popen(
            self.spec.command,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        self.emit_exit_events = True
        self.thread = threading.Thread(target=self._pump, daemon=True)
        self.thread.start()

    def _pump(self) -> None:
        assert self.process is not None
        assert self.process.stdout is not None
        for raw in self.process.stdout:
            if raw is None:
                break
            self.line_callback(self.spec.name, raw)
        self.process.wait()
        code = self.process.returncode
        if self.emit_exit_events and code not in (0, None):
            self.exit_callback(self.spec.name, code)

    def stop(self) -> None:
        if not self.process:
            return
        self.emit_exit_events = False
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        self.process = None
        self.thread = None


class AIFixer:
    """Use the repo's AI helper to propose + apply patches until logs are clean."""

    PATCH_RE = re.compile(r"```(?:patch|diff)\s+([\s\S]*?)```", re.MULTILINE)

    def __init__(
        self,
        *,
        persona: str = "AIC",
        diff_limit: int = 400,
        repo_root: Path = REPO_ROOT,
        max_ai_retries: int = 3,
        retry_backoff_seconds: int = 5,
    ) -> None:
        self.persona = persona
        self.diff_limit = diff_limit
        self.repo_root = repo_root
        self.history: List[ChatMessage] = []
        self.max_ai_retries = max(1, max_ai_retries)
        self.retry_backoff_seconds = max(1, retry_backoff_seconds)

    def _request_ai_patch(self, *, temperature: float, max_tokens: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Call ``generate_ai_reply`` with retries so transient OpenAI errors don't abort the run.
        Returns (reply, error_message).
        """
        last_error: Optional[str] = None
        for attempt in range(1, self.max_ai_retries + 1):
            reply: Optional[str] = None
            error: Optional[str] = None
            try:
                reply, error, _ = generate_ai_reply(
                    self.history,
                    persona=self.persona,
                    append_prompt=False,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as exc:  # pragma: no cover - defensive guard
                error = f"Unhandled AI client error: {exc}"

            if error:
                last_error = error
                wait = self.retry_backoff_seconds * attempt
                print(f"⚠️  AI attempt {attempt}/{self.max_ai_retries} failed: {error}. Retrying in {wait}s...")
                time.sleep(wait)
                continue

            if reply:
                return reply, None

        return None, last_error

    def try_fix(self, component: str, log_excerpt: str, iteration: int, event_type: str = "error") -> bool:
        if not openai_available():
            print(
                "❌ OpenAI client is not configured. Provide --openai-key once (or set OPENAI_API_KEY) "
                "and it will be stored in assistant_hub.db for future runs."
            )
            return False

        status = self._run_text(["git", "status", "-sb"])
        diffstat = self._run_text(["git", "diff", "--stat=120,80"])
        diff = self._trim_diff(self._run_text(["git", "diff"]))
        
        # Extract HTTP error patterns from logs for better context
        http_errors = self._extract_http_errors(log_excerpt)
        http_warnings = self._extract_http_warnings(log_excerpt)
        performance_issues = self._extract_performance_issues(log_excerpt)
        router_info = self._analyze_routers()
        code_quality_issues = self._analyze_code_quality()

        # Build context-aware prompt based on event type
        if event_type == "error" or event_type.startswith("http_"):
            issue_desc = "reported an error"
            goal_focus = "eliminates the runtime error"
        elif event_type == "warning":
            issue_desc = "reported warnings that should be addressed"
            goal_focus = "resolves the warnings and improves code quality"
        elif event_type == "performance":
            issue_desc = "showed performance issues"
            goal_focus = "optimizes performance and reduces latency"
        elif event_type == "improvement_opportunity":
            issue_desc = "shows opportunities for improvement"
            goal_focus = "improves code quality, performance, maintainability, and follows best practices"
        else:
            issue_desc = "needs attention"
            goal_focus = "improves the codebase"

        prompt = (
            "You are the autonomous maintainer for the OS Dashboard AI Assistant. "
            "Backend and frontend dev servers are running and the following component "
            f"{issue_desc}.\n\n"
            f"Component: {component}\n"
            f"Event Type: {event_type}\n"
            f"Iteration: {iteration}\n\n"
            "Recent logs:\n```\n"
            f"{log_excerpt.strip()}\n"
            "```\n\n"
        )
        
        if http_errors:
            prompt += (
                "Detected HTTP errors:\n```\n"
                f"{http_errors}\n"
                "```\n\n"
            )
        
        if http_warnings:
            prompt += (
                "Detected HTTP warnings/4xx responses:\n```\n"
                f"{http_warnings}\n"
                "```\n\n"
            )
        
        if performance_issues:
            prompt += (
                "Detected performance issues:\n```\n"
                f"{performance_issues}\n"
                "```\n\n"
            )
        
        if router_info:
            prompt += (
                "Current FastAPI router structure:\n```\n"
                f"{router_info}\n"
                "```\n\n"
            )
        
        if code_quality_issues:
            prompt += (
                "Code quality analysis:\n```\n"
                f"{code_quality_issues}\n"
                "```\n\n"
            )
        
        prompt += (
            "Git status:\n```\n"
            f"{status.strip() or '(clean)'}\n"
            "```\n\n"
            "Diffstat:\n```\n"
            f"{diffstat.strip() or '(no staged changes)'}\n"
            "```\n\n"
            "Unified diff (trimmed):\n```\n"
            f"{diff.strip() or '(no local diff)'}\n"
            "```\n\n"
            f"Goal: generate source changes that {goal_focus}.\n\n"
        )
        
        # Add specific guidance based on event type
        if event_type.startswith("http_"):
            prompt += (
                "For HTTP errors, check if:\n"
                "1. The endpoint exists in the router file\n"
                "2. The router is properly included in main.py with the correct prefix\n"
                "3. The HTTP method (GET/POST/PUT/DELETE) matches the endpoint definition\n"
                "4. The route path matches what's being requested\n"
                "5. Request/response models match the endpoint signature\n"
                "6. CORS or authentication middleware isn't blocking requests\n\n"
            )
        
        if event_type == "performance":
            prompt += (
                "For performance issues, consider:\n"
                "1. Adding database query optimization (indexes, query optimization)\n"
                "2. Implementing caching where appropriate\n"
                "3. Adding connection pooling\n"
                "4. Optimizing algorithms or data structures\n"
                "5. Adding async/await where synchronous operations block\n"
                "6. Implementing pagination for large datasets\n"
                "7. Adding request timeouts and circuit breakers\n\n"
            )
        
        if event_type == "improvement_opportunity" or event_type == "warning":
            prompt += (
                "For code improvements, consider:\n"
                "1. Refactoring duplicate code\n"
                "2. Improving error handling and logging\n"
                "3. Adding type hints and documentation\n"
                "4. Following Python/FastAPI best practices\n"
                "5. Improving code organization and structure\n"
                "6. Adding input validation and sanitization\n"
                "7. Improving security (SQL injection, XSS prevention)\n"
                "8. Adding unit tests or improving test coverage\n"
                "9. Optimizing imports and dependencies\n"
                "10. Following DRY (Don't Repeat Yourself) principles\n\n"
            )
        
        prompt += (
            "For FastAPI applications:\n"
            "- Routes are defined with @router.get(), @router.post(), etc.\n"
            "- Routers are included with app.include_router(router, prefix='/api/...')\n"
            "- Check backend_api/main.py for router registrations\n"
            "- Check backend_api/routers/*.py for route definitions\n\n"
            "Return a short reasoning paragraph followed by the full unified diff wrapped inside "
            "a single ```patch block. The diff must apply cleanly with `git apply --whitespace=fix`. "
            "Make improvements even if there are no critical errors - focus on code quality, "
            "performance, maintainability, and best practices."
        )

        user_msg = ChatMessage(
            id=len(self.history) + 1,
            persona=self.persona,
            role="user",
            kind="chat",
            content=prompt,
        )
        self.history.append(user_msg)
        reply, error = self._request_ai_patch(temperature=0.1, max_tokens=1800)
        if error:
            print(f"❌ AI call failed after retries: {error}")
            return False

        assistant_msg = ChatMessage(
            id=len(self.history) + 1,
            persona=self.persona,
            role="assistant",
            kind="chat",
            content=reply,
        )
        self.history.append(assistant_msg)

        patches = self._extract_patches(reply)
        if not patches:
            print("⚠️  AI response did not include a ```patch block. Full reply:\n")
            print(reply)
            return False

        try:
            for idx, patch in enumerate(patches, start=1):
                self._apply_patch(patch, idx)
        except RuntimeError as exc:
            print(f"❌ Failed to apply AI patch: {exc}")
            return False

        print("✅ Patch applied. Re-running monitored processes...")
        return True

    def _trim_diff(self, diff: str) -> str:
        if not diff or not self.diff_limit:
            return diff
        lines = diff.splitlines()
        if len(lines) <= self.diff_limit:
            return diff
        head = max(10, self.diff_limit // 4)
        tail = self.diff_limit - head
        trimmed = lines[:head] + ["... (diff truncated) ..."] + lines[-tail:]
        return "\n".join(trimmed)

    def _run_text(self, cmd: List[str]) -> str:
        proc = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
        return proc.stdout

    def _extract_patches(self, reply: str) -> List[str]:
        matches = self.PATCH_RE.findall(reply)
        return [block.strip() for block in matches if block.strip()]

    def _apply_patch(self, patch: str, idx: int) -> None:
        proc = subprocess.run(
            ["git", "apply", "--whitespace=fix"],
            input=patch,
            text=True,
            cwd=self.repo_root,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"patch #{idx} failed")
    
    def _extract_http_errors(self, log_excerpt: str) -> str:
        """Extract HTTP error patterns from logs."""
        http_error_pattern = re.compile(
            r'("(?:GET|POST|PUT|DELETE|PATCH|OPTIONS)\s+([^"]+)\s+HTTP/[^"]+)"\s+(\d{3})\s+([^\n]+)',
            re.IGNORECASE
        )
        errors = []
        for match in http_error_pattern.finditer(log_excerpt):
            method_path, path, status, message = match.groups()
            status_code = int(status)
            if status_code >= 400:
                errors.append(f"{method_path} -> {status_code} {message.strip()}")
        return "\n".join(errors) if errors else ""
    
    def _extract_http_warnings(self, log_excerpt: str) -> str:
        """Extract HTTP 4xx responses that might indicate issues."""
        http_pattern = re.compile(
            r'("(?:GET|POST|PUT|DELETE|PATCH|OPTIONS)\s+([^"]+)\s+HTTP/[^"]+)"\s+(\d{3})',
            re.IGNORECASE
        )
        warnings = []
        for match in http_pattern.finditer(log_excerpt):
            method_path, path, status = match.groups()
            status_code = int(status)
            # 4xx are client errors, might indicate API usage issues or missing endpoints
            if 400 <= status_code < 500:
                warnings.append(f"{method_path} -> {status_code} (client error)")
        return "\n".join(warnings) if warnings else ""
    
    def _extract_performance_issues(self, log_excerpt: str) -> str:
        """Extract performance-related patterns from logs."""
        issues = []
        # Slow requests
        slow_pattern = re.compile(
            r'(\d+\.?\d*)\s*(ms|s|seconds?|milliseconds?)\s*(took|elapsed|duration)',
            re.IGNORECASE
        )
        for match in slow_pattern.finditer(log_excerpt):
            duration, unit, _ = match.groups()
            try:
                duration_val = float(duration)
                if 's' in unit.lower() and 'ms' not in unit.lower():
                    duration_ms = duration_val * 1000
                else:
                    duration_ms = duration_val
                if duration_ms > 500:  # Flag anything over 500ms
                    issues.append(f"Slow operation: {duration} {unit}")
            except ValueError:
                pass
        
        # High memory/CPU mentions
        resource_pattern = re.compile(
            r'(high|low|exceeded|limit).*?(memory|cpu|disk|load)',
            re.IGNORECASE
        )
        for match in resource_pattern.finditer(log_excerpt):
            issues.append(f"Resource issue: {match.group(0)}")
        
        return "\n".join(issues) if issues else ""
    
    def _analyze_code_quality(self) -> str:
        """Analyze codebase for quality issues and improvement opportunities."""
        issues = []
        try:
            # Check for common code smells in Python files
            backend_dir = self.repo_root / "backend_api"
            if backend_dir.exists():
                python_files = list(backend_dir.rglob("*.py"))
                # Sample a few files for analysis
                for py_file in python_files[:10]:
                    try:
                        with open(py_file, 'r') as f:
                            content = f.read()
                        
                        # Check for potential issues
                        if content.count('except:') > 0:
                            issues.append(f"{py_file.name}: Bare except clauses found")
                        if len(content.splitlines()) > 1000:
                            issues.append(f"{py_file.name}: Very large file (>1000 lines)")
                        if content.count('TODO') > 0:
                            issues.append(f"{py_file.name}: Contains TODO comments")
                        if content.count('FIXME') > 0:
                            issues.append(f"{py_file.name}: Contains FIXME comments")
                    except Exception:
                        pass
        except Exception as e:
            return f"Error analyzing code quality: {e}"
        
        return "\n".join(issues[:10]) if issues else "No obvious code quality issues detected"
    
    def _analyze_routers(self) -> str:
        """Analyze FastAPI router structure to help AI understand routing."""
        try:
            main_py = self.repo_root / "backend_api" / "main.py"
            if not main_py.exists():
                return ""
            
            with open(main_py, 'r') as f:
                content = f.read()
            
            # Extract router includes
            router_pattern = re.compile(
                r'app\.include_router\((\w+)\.router,\s*prefix=["\']([^"\']+)["\']',
                re.MULTILINE
            )
            routers = []
            for match in router_pattern.finditer(content):
                router_name, prefix = match.groups()
                routers.append(f"{router_name}.router -> prefix: {prefix}")
            
            # Also check for route definitions in router files
            router_files = list((self.repo_root / "backend_api" / "routers").glob("*.py"))
            route_info = []
            for router_file in router_files[:5]:  # Limit to first 5 to avoid too much context
                try:
                    with open(router_file, 'r') as f:
                        router_content = f.read()
                    # Find route decorators
                    route_decorators = re.findall(
                        r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                        router_content
                    )
                    if route_decorators:
                        routes = [f"  {method.upper()} {path}" for method, path in route_decorators[:3]]
                        route_info.append(f"{router_file.name}:\n" + "\n".join(routes))
                except Exception:
                    pass
            
            result = "Registered routers:\n" + "\n".join(routers)
            if route_info:
                result += "\n\nSample route definitions:\n" + "\n".join(route_info)
            
            return result if routers else "No routers found in main.py"
        except Exception as e:
            return f"Error analyzing routers: {e}"


class AutoFixOrchestrator:
    """Coordinate process monitoring and recursive AI fixes."""

    # Comprehensive regex to catch ALL issues: errors, warnings, performance, and opportunities
    ERROR_RE = re.compile(
        r"(error|traceback|exception|unhandled|fatal|404|500|502|503|504|Not Found|Internal Server Error|Bad Request|Method Not Allowed)",
        re.IGNORECASE
    )
    
    # Warning patterns
    WARNING_RE = re.compile(
        r"(warning|warn|deprecated|deprecation|slow|timeout|retry|failed|failure|issue)",
        re.IGNORECASE
    )
    
    # Performance issue patterns
    PERFORMANCE_RE = re.compile(
        r"(\d+\.\d+)\s*(ms|s|seconds?|milliseconds?)\s*(took|elapsed|duration|slow|timeout|lag|delay)",
        re.IGNORECASE
    )
    
    # HTTP status codes (all, not just errors)
    HTTP_STATUS_RE = re.compile(
        r'"(?:GET|POST|PUT|DELETE|PATCH|OPTIONS)\s+([^"]+)\s+HTTP/[^"]+"\s+(\d{3})',
        re.IGNORECASE
    )
    
    # Performance metrics
    PERFORMANCE_METRIC_RE = re.compile(
        r"(cpu|memory|disk|load|latency|throughput|response time|query time|execution time)",
        re.IGNORECASE
    )

    def __init__(
        self,
        specs: List[ProcessSpec],
        fixer: AIFixer,
        *,
        verify_seconds: int = 45,
        buffer_lines: int = 400,
        context_lines: int = 160,
        log_dirs: Optional[List[Path]] = None,
        log_pattern: str = "*.log",
        log_poll_interval: float = 0.5,
        analyze_all_logs: bool = True,
        performance_threshold_ms: float = 1000.0,
        improvement_interval: int = 300,  # Analyze for improvements every 5 minutes
        log_watch_enabled: bool = True,
        auto_binary_monitor: bool = True,
        binary_poll_interval: float = 3.0,
        test_specs: Optional[List[TestSpec]] = None,
        test_interval: int = 0,
        project_root: Path = REPO_ROOT,
    ) -> None:
        self.project_root = project_root
        log_dirs = log_dirs or []
        self.test_specs = list(test_specs or [])
        self.test_interval = max(0, int(test_interval))
        if not specs and not self.test_specs:
            if not log_watch_enabled and not auto_binary_monitor:
                raise ValueError(
                    "At least one process must be specified or enable log watching/binary monitoring via --log-dir/--logs-only."
                )
            if log_watch_enabled and not log_dirs and not auto_binary_monitor:
                raise ValueError(
                    "No processes or log directories to watch. Provide --log-dir entries, --watch commands, or disable --logs-only."
                )
        self.specs = specs
        self.fixer = fixer
        self.verify_seconds = verify_seconds
        self.buffer_lines = buffer_lines
        self.context_lines = context_lines
        self.analyze_all_logs = analyze_all_logs
        self.performance_threshold_ms = performance_threshold_ms
        self.improvement_interval = improvement_interval
        self.buffers: Dict[str, LineBuffer] = {}
        self.processes: Dict[str, ProcessRunner] = {}
        self.events: queue.Queue = queue.Queue()
        self.last_improvement_check: float = 0.0
        self.performance_metrics: Dict[str, List[float]] = {}
        self.http_status_counts: Dict[int, int] = {}
        self._last_stable_announcement: float = 0.0
        self.log_pattern = log_pattern
        self.log_poll_interval = log_poll_interval
        self.log_watch_enabled = log_watch_enabled
        self._log_combined_re = re.compile(
            f"({self.ERROR_RE.pattern}|{self.WARNING_RE.pattern}|{self.PERFORMANCE_RE.pattern})",
            re.IGNORECASE,
        )
        self.log_watchers: Dict[Path, LogDirectoryWatcher] = {}
        self._watcher_lock = threading.Lock()
        self._watchers_active = False
        if self.log_watch_enabled:
            for log_dir in log_dirs:
                self._register_log_dir(log_dir)
        self.auto_binary_monitor = auto_binary_monitor
        self.binary_poll_interval = binary_poll_interval
        self.binary_monitor: Optional[BinaryExecutionMonitor] = None
        self._binary_signatures = self._default_binary_signatures()
        self._test_thread: Optional[threading.Thread] = None
        self._test_stop_event = threading.Event()
        self._test_lock = threading.Lock()

    def _default_binary_signatures(self) -> List[BinarySignature]:
        base_logs = self.project_root / "logs"
        frontend_logs = self.project_root / "frontend" / "logs"
        desktop_logs = self.project_root / "frontend" / "dist-electron" / "logs"
        return [
            BinarySignature("backend-uvicorn", ["uvicorn", "assistant_hub.api.server"], [base_logs]),
            BinarySignature("start-ui", ["start_ui.py"], [base_logs, frontend_logs, desktop_logs]),
            BinarySignature("assistant-hub-gui", ["assistant_hub_gui", "main"], [base_logs, desktop_logs]),
            BinarySignature("frontend-web", ["dev:web"], [frontend_logs, base_logs]),
            BinarySignature("frontend-desktop", ["dev:desktop"], [desktop_logs, base_logs]),
            BinarySignature("electron-shell", ["electron"], [desktop_logs]),
        ]

    def _start_test_thread(self) -> None:
        if not self.test_specs or self.test_interval <= 0:
            return
        self._test_stop_event = threading.Event()
        self._test_thread = threading.Thread(target=self._test_loop, daemon=True)
        self._test_thread.start()

    def _stop_test_thread(self) -> None:
        if not self.test_specs:
            return
        self._test_stop_event.set()
        if self._test_thread and self._test_thread.is_alive():
            self._test_thread.join(timeout=1)
        self._test_thread = None

    def _test_loop(self) -> None:
        while not self._test_stop_event.is_set():
            if self._test_stop_event.wait(self.test_interval):
                break
            self._run_tests(reason="interval")

    def _register_log_dir(self, log_dir: Path | str) -> None:
        if not self.log_watch_enabled:
            return
        path = Path(log_dir)
        if not path.is_absolute():
            path = (self.project_root / path).resolve()
        else:
            path = path.resolve()
        with self._watcher_lock:
            if path in self.log_watchers:
                return
            watcher = LogDirectoryWatcher(
                log_dir=path,
                pattern=self.log_pattern,
                error_re=self._log_combined_re,
                http_re=self.HTTP_STATUS_RE,
                buffer_lines=self.buffer_lines,
                context_lines=self.context_lines,
                poll_interval=self.log_poll_interval,
                event_callback=self._handle_log_event,
            )
            self.log_watchers[path] = watcher
            if self._watchers_active:
                watcher.start()

    def _on_binary_detected(self, signature: BinarySignature, proc_info: Dict[str, Any]) -> None:
        if not self.log_watch_enabled:
            return
        cmdline = " ".join(proc_info.get("cmdline") or [])
        pid = proc_info.get("pid")
        name = proc_info.get("name") or signature.label
        details = cmdline or name
        print(f"🕵️  Detected {signature.label} process (pid={pid}): {details}")
        for log_dir in signature.log_dirs:
            self._register_log_dir(log_dir)

    def _run_tests(self, reason: str = "startup") -> None:
        if not self.test_specs:
            return
        with self._test_lock:
            for spec in self.test_specs:
                try:
                    cmd_display = shlex.join(spec.command)
                except AttributeError:
                    cmd_display = " ".join(spec.command)
                print(f"🧪 Running {spec.name} tests ({reason}): {cmd_display}")
                start = time.perf_counter()
                try:
                    result = subprocess.run(
                        spec.command,
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                    )
                except FileNotFoundError as exc:
                    context = f"Test command '{cmd_display}' failed to launch: {exc}"
                    self.events.put(("test_failure", f"tests:{spec.name}", context))
                    return
                duration_ms = (time.perf_counter() - start) * 1000.0
                if result.returncode != 0:
                    output_chunks: List[str] = []
                    if result.stdout:
                        output_chunks.append("STDOUT:\n" + result.stdout.strip())
                    if result.stderr:
                        output_chunks.append("STDERR:\n" + result.stderr.strip())
                    context = (
                        f"Command: {cmd_display}\nReason: {reason}\nDuration: {duration_ms:.1f} ms\n\n"
                        + ("\n\n".join(chunk for chunk in output_chunks if chunk) or "No output captured.")
                    )
                    self.events.put(("test_failure", f"tests:{spec.name}", context))
                    return
                print(f"✅ {spec.name} passed in {duration_ms/1000.0:.2f}s")

    def run(self, max_attempts: int, *, daemon_mode: bool = False) -> int:
        """Continuously monitor processes, repairing regressions as they surface.

        When ``daemon_mode`` is True the orchestrator never exits on its own; it
        keeps the backend/frontend running and reports health at the configured
        verification interval. Setting ``max_attempts`` to 0 disables the cap on
        recursive fixes.
        """
        attempt = 0
        unlimited = max_attempts <= 0
        self._start_processes()
        try:
            while True:
                event = self._wait_for_event()
                if event is None:
                    message = f"✅ No issues detected for {self.verify_seconds} seconds."
                    if daemon_mode:
                        now = time.time()
                        if now - self._last_stable_announcement >= self.verify_seconds:
                            print(f"{message} Monitoring continues...")
                            self._last_stable_announcement = now
                        continue
                    print(f"{message} Consider things stable.")
                    return 0

                attempt += 1
                label = (
                    f"{attempt}/{max_attempts}"
                    if not unlimited and max_attempts > 0
                    else str(attempt)
                )
                print(f"\n=== Auto-fix attempt {label} ===")

                kind, component, payload = event
                event_emoji = {
                    "error": "❌",
                    "http_404": "🔍",
                    "http_4xx": "⚠️",
                    "http_5xx": "🔥",
                    "warning": "⚠️",
                    "performance": "⏱️",
                    "improvement_opportunity": "💡",
                    "exit": "🛑",
                    "log": "📜",
                    "test_failure": "🧪",
                }.get(kind, "ℹ️")
                print(f"{event_emoji}  Detected {kind} event from {component}. Feeding logs to AI...")

                self._stop_processes()
                if not self.fixer.try_fix(component, payload, attempt, event_type=kind):
                    print("❌ Auto-fix attempt failed. See output above.")
                    return 1

                if not unlimited and attempt >= max_attempts:
                    print("❌ Reached maximum attempts without stabilizing.")
                    return 2

                print("♻️  Restarting monitored processes...")
                self._start_processes()
        finally:
            self._stop_processes()

    def _start_processes(self) -> None:
        self.events = queue.Queue()
        for spec in self.specs:
            self.buffers[spec.name] = LineBuffer(self.buffer_lines)
            try:
                cmd_display = shlex.join(spec.command)
            except AttributeError:
                cmd_display = " ".join(spec.command)
            print(f"🚀 Launching {spec.name}: {cmd_display}")
            runner = ProcessRunner(
                spec,
                line_callback=self._handle_line,
                exit_callback=self._handle_exit,
                cwd=self.project_root,
            )
            try:
                runner.start()
            except FileNotFoundError as exc:
                message = (
                    f"{spec.name} command failed to launch ({exc.strerror or exc}). "
                    "Use --backend none/--frontend none or provide a valid command."
                )
                print(f"⚠️  {message}")
                continue
            except Exception as exc:
                message = f"Failed to start {spec.name}: {exc}"
                print(f"⚠️  {message}")
                continue
            self.processes[spec.name] = runner
        if self.log_watch_enabled:
            self._watchers_active = True
            for watcher in self.log_watchers.values():
                watcher.start()
        if self.auto_binary_monitor:
            if self.binary_monitor is None:
                self.binary_monitor = BinaryExecutionMonitor(
                    signatures=self._binary_signatures,
                    poll_interval=self.binary_poll_interval,
                    on_detect=self._on_binary_detected,
                )
            self.binary_monitor.start()
        if self.test_specs:
            self._run_tests(reason="startup")
            self._start_test_thread()

    def _stop_processes(self) -> None:
        self._stop_test_thread()
        if self.auto_binary_monitor and self.binary_monitor:
            self.binary_monitor.stop()
        if self.log_watch_enabled:
            for watcher in self.log_watchers.values():
                watcher.stop()
            self._watchers_active = False
        for runner in self.processes.values():
            runner.stop()
        self.processes.clear()
        # Drain leftover events triggered while shutting down
        while not self.events.empty():
            try:
                self.events.get_nowait()
            except queue.Empty:
                break

    def _wait_for_event(self) -> Optional[Tuple[str, str, str]]:
        try:
            return self.events.get(timeout=self.verify_seconds)
        except queue.Empty:
            return None

    def _evaluate_text(self, component: str, text: str, snapshot_provider: Callable[[], str]) -> None:
        event_type: Optional[str] = None
        http_match = self.HTTP_STATUS_RE.search(text)
        if http_match:
            _, status_code = http_match.groups()
            try:
                status = int(status_code)
            except ValueError:
                status = 0
            self.http_status_counts[status] = self.http_status_counts.get(status, 0) + 1
            if status >= 400:
                if status == 404:
                    event_type = "http_404"
                elif status >= 500:
                    event_type = "http_5xx"
                else:
                    event_type = "http_4xx"
        if event_type is None and self.ERROR_RE.search(text):
            if re.search(r"\b404\b|\bNot Found\b", text, re.IGNORECASE):
                event_type = "http_404"
            else:
                event_type = "error"
        if event_type is None and self.WARNING_RE.search(text):
            event_type = "warning"
        perf_match = self.PERFORMANCE_RE.search(text)
        if perf_match:
            try:
                duration = float(perf_match.group(1))
                unit = perf_match.group(2).lower()
                duration_ms = duration * 1000 if "s" in unit and "ms" not in unit else duration
                if duration_ms > self.performance_threshold_ms:
                    if component not in self.performance_metrics:
                        self.performance_metrics[component] = []
                    self.performance_metrics[component].append(duration_ms)
                    if event_type is None:
                        event_type = "performance"
            except (ValueError, IndexError):
                pass
        if event_type:
            snapshot = snapshot_provider()
            self.events.put((event_type, component, snapshot))

    def _handle_line(self, component: str, line: str) -> None:
        text = line.rstrip("\n")
        print(f"[{component}] {text}")
        self.buffers[component].push(text)
        snapshot_provider = lambda: self.buffers[component].snapshot(self.context_lines)
        self._evaluate_text(component, text, snapshot_provider)
        
        # Proactive improvement analysis (periodic)
        current_time = time.time()
        if self.analyze_all_logs and (current_time - self.last_improvement_check) > self.improvement_interval:
            snapshot = self.buffers[component].snapshot(self.context_lines)
            self.events.put(("improvement_opportunity", component, snapshot))
            self.last_improvement_check = current_time

    def _handle_exit(self, component: str, code: int) -> None:
        snapshot = self.buffers[component].snapshot(self.context_lines)
        context = f"{component} exited with code {code}\n\n{snapshot}"
        self.events.put(("exit", component, context))

    def _handle_log_event(self, component: str, line: str, snapshot: str) -> None:
        self._evaluate_text(component, line, lambda: snapshot)


@dataclass
class LogFileState:
    path: Path
    handle: object
    buffer: LineBuffer
    position: int = 0


class LogDirectoryWatcher:
    """Poll a log directory and emit events when error patterns appear."""

    def __init__(
        self,
        *,
        log_dir: Path,
        pattern: str,
        error_re: re.Pattern,
        http_re: Optional[re.Pattern],
        buffer_lines: int,
        context_lines: int,
        poll_interval: float,
        event_callback: Callable[[str, str, str], None],
    ) -> None:
        self.log_dir = log_dir
        self.pattern = pattern
        self.error_re = error_re
        self.http_re = http_re
        self.buffer_lines = buffer_lines
        self.context_lines = context_lines
        self.poll_interval = poll_interval
        self.event_callback = event_callback
        self.files: Dict[Path, LogFileState] = {}
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        # Track read offsets so historical logs are processed only once across restarts
        self._offsets: Dict[Path, int] = {}

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        # Always ensure the directory exists so we can start watching immediately.
        # If the directory is created later, the watcher thread keeps polling.
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)
        for state in self.files.values():
            try:
                self._offsets[state.path] = state.position
                state.handle.close()
            except Exception:
                pass
        self.files.clear()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._scan_once()
            except Exception as exc:
                print(f"[log-watcher] warning: {exc}")
            self._stop_event.wait(self.poll_interval)

    def _scan_once(self) -> None:
        if not self.log_dir.exists():
            return
        current_paths = set(self.files.keys())
        discovered_paths = set()
        for path in sorted(self.log_dir.glob(self.pattern)):
            if not path.is_file():
                continue
            discovered_paths.add(path)
            state = self.files.get(path)
            if state is None:
                handle = path.open("r", encoding="utf-8", errors="replace")
                buffer = LineBuffer(self.buffer_lines)
                position = self._offsets.get(path, 0)
                try:
                    size = path.stat().st_size
                except OSError:
                    size = 0
                if position > size:
                    position = 0
                state = LogFileState(path=path, handle=handle, buffer=buffer, position=position)
                self.files[path] = state
            self._consume_file(state)

        stale = current_paths - discovered_paths
        for path in stale:
            state = self.files.pop(path, None)
            if state:
                try:
                    self._offsets.pop(path, None)
                    state.handle.close()
                except Exception:
                    pass

    def _consume_file(self, state: LogFileState) -> None:
        handle = state.handle
        try:
            handle.seek(state.position)
        except Exception:
            handle.close()
            handle = state.path.open("r", encoding="utf-8", errors="replace")
            state.handle = handle
            state.buffer = LineBuffer(self.buffer_lines)
            state.position = 0

        while True:
            line = handle.readline()
            if not line:
                break
            state.position = handle.tell()
            stripped = line.rstrip("\n")
            state.buffer.push(stripped)
            match_error = self.error_re.search(stripped) if self.error_re else False
            match_http = self.http_re.search(stripped) if self.http_re else False
            if match_error or match_http:
                snapshot = state.buffer.snapshot(self.context_lines)
                component = f"log:{state.path.name}"
                self.event_callback(component, stripped, snapshot)
        self._offsets[state.path] = state.position


class BinaryExecutionMonitor:
    """Continuously scan running processes to detect known OS Dashboard binaries."""

    def __init__(
        self,
        *,
        signatures: List[BinarySignature],
        poll_interval: float,
        on_detect: Callable[[BinarySignature, Dict[str, Any]], None],
    ) -> None:
        self.signatures = [sig for sig in signatures if sig.keywords]
        self.poll_interval = max(0.5, poll_interval)
        self.on_detect = on_detect
        self._stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self._seen: Dict[str, set] = {sig.label: set() for sig in self.signatures}

    def start(self) -> None:
        if not self.signatures:
            return
        if self.thread and self.thread.is_alive():
            return
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        if not self.thread:
            return
        self._stop_event.set()
        self.thread.join(timeout=1)
        self.thread = None

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                    info = proc.info
                    pid = info.get("pid")
                    name = (info.get("name") or "").lower()
                    cmdline = " ".join(info.get("cmdline") or []).lower()
                    full_text = f"{name} {cmdline}".strip()
                    for signature in self.signatures:
                        if not all(keyword.lower() in full_text for keyword in signature.keywords):
                            continue
                        seen = self._seen.setdefault(signature.label, set())
                        if pid in seen:
                            continue
                        seen.add(pid)
                        try:
                            self.on_detect(signature, info)
                        except Exception as exc:
                            print(f"[binary-monitor] callback error: {exc}")
                self._stop_event.wait(self.poll_interval)
            except Exception as exc:
                print(f"[binary-monitor] warning: {exc}")
                self._stop_event.wait(self.poll_interval)

def _command_disabled(value: Optional[str]) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    return normalized in {"", "none", "null", "off", "false", "skip", "disabled", "0"}


def _parse_specs(args: argparse.Namespace, project_root: Path = REPO_ROOT) -> List[ProcessSpec]:
    specs: List[ProcessSpec] = []

    if args.backend is not None:
        if not _command_disabled(args.backend):
            specs.append(ProcessSpec("backend", shlex.split(args.backend)))
    elif not args.logs_only:
        specs.append(ProcessSpec("backend", _default_backend_command()))

    if args.frontend is not None:
        if not _command_disabled(args.frontend):
            specs.append(ProcessSpec("frontend", shlex.split(args.frontend)))
    elif not args.logs_only:
        specs.append(ProcessSpec("frontend", _default_frontend_command(project_root)))

    for entry in args.watch or []:
        if "=" not in entry:
            raise ValueError(f"--watch entries must look like label=command (got: {entry})")
        label, raw_cmd = entry.split("=", 1)
        specs.append(ProcessSpec(label.strip(), shlex.split(raw_cmd.strip())))

    return specs


def _parse_test_specs(args: argparse.Namespace) -> List[TestSpec]:
    specs: List[TestSpec] = []
    cli_tests = list(getattr(args, "tests", []) or [])
    for idx, raw in enumerate(cli_tests, start=1):
        label = f"test{idx}"
        command_text = raw
        if "=" in raw:
            possible_label, remaining = raw.split("=", 1)
            if possible_label.strip() and " " not in possible_label.strip():
                label = possible_label.strip()
                command_text = remaining
        command = shlex.split(command_text.strip())
        if not command:
            continue
        specs.append(TestSpec(label, command))
    if os.environ.get("OSDASH_AUTOFIX_DISABLE_DEFAULT_TESTS", "").lower() not in {"1", "true", "yes"}:
        for name, command in DEFAULT_AUTOFIX_TESTS:
            specs.append(TestSpec(name, list(command)))
    return specs


def _default_backend_command() -> List[str]:
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "assistant_hub.api.server:create_app",
        "--factory",
        "--reload",
    ]


def _detect_frontend_script(root: Path = REPO_ROOT) -> str:
    package_json = root / "frontend" / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            scripts = data.get("scripts", {})
            for candidate in ("dev:web", "dev", "start"):
                if candidate in scripts:
                    return candidate
        except Exception:
            pass
    return "dev:web"


def _default_frontend_command(root: Path = REPO_ROOT) -> List[str]:
    npm = shutil.which("npm") or "npm"
    script_name = _detect_frontend_script(root)
    return [npm, "run", script_name]


def _bootstrap_openai_key(manual_key: Optional[str]) -> None:
    """Ensure the OpenAI API key is sourced from env or persisted DB."""
    env_key = manual_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_CHAT_OPENAI_API_KEY")
    stored_key = env_key
    conn = None
    try:
        conn = init_db()
        if env_key:
            save_openai_api_key(conn, env_key)
        else:
            stored = load_openai_api_key(conn)
            if stored:
                stored_key = stored
    except Exception:
        pass
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    if stored_key and not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = stored_key


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Continuously watch dev logs and auto-apply AI patches when errors appear.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/ai_auto_fix.py --backend \"python start_ui.py --mode web\" --frontend \"npm run dev:web\"\n"
            "  python scripts/ai_auto_fix.py --watch celery=\"celery -A tasks worker\" --verify-seconds 90\n"
        ),
    )
    parser.add_argument(
        "--project-root",
        help="Path to the project root directory (defaults to the script's parent repository).",
    )
    parser.add_argument(
        "--backend",
        help="Command to run the backend (defaults to uvicorn). Use 'none' to disable.",
    )
    parser.add_argument(
        "--frontend",
        help="Command to run the frontend (defaults to `npm run dev:web`). Use 'none' to disable.",
    )
    parser.add_argument(
        "--watch",
        action="append",
        metavar="LABEL=CMD",
        help="Additional process to monitor, e.g. --watch worker=\"python worker.py\" (repeatable).",
    )
    parser.add_argument(
        "--test",
        dest="tests",
        action="append",
        metavar="[LABEL=]CMD",
        help="Test command to run after each restart (repeatable). Example: --test \"pytest -q tests/test_office_api.py\".",
    )
    parser.add_argument(
        "--test-interval",
        type=int,
        default=0,
        help="Seconds between background test runs while healthy (0 disables periodic runs).",
    )
    parser.add_argument(
        "--verify-seconds",
        type=int,
        default=45,
        help="Consider the system stable when no errors are detected for this many seconds.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="Maximum recursive fix attempts before giving up (0 = unlimited).",
    )
    parser.add_argument(
        "--persona",
        default="AIC",
        help="Persona to use for the AI request (affects model + tone).",
    )
    parser.add_argument(
        "--diff-limit",
        type=int,
        default=400,
        help="Maximum number of diff lines to send to the AI context window.",
    )
    parser.add_argument(
        "--buffer-lines",
        type=int,
        default=400,
        help="How many log lines to retain per process for debugging context.",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=160,
        help="Maximum number of log lines to send to the AI when an error is detected.",
    )
    parser.add_argument(
        "--log-dir",
        action="append",
        metavar="PATH",
        help="Directory of log files to mirror into the AI context. Pass multiple times to watch web/desktop outputs automatically. Use 'none' to skip defaults.",
    )
    parser.add_argument(
        "--log-pattern",
        default="*.log",
        help="Glob pattern for log files inside --log-dir.",
    )
    parser.add_argument(
        "--log-poll-interval",
        type=float,
        default=0.5,
        help="Seconds between log file scans.",
    )
    parser.add_argument(
        "--disable-log-watch",
        action="store_true",
        help="Disable reading log files entirely (overrides --log-dir).",
    )
    parser.add_argument(
        "--logs-only",
        action="store_true",
        help="Skip launching default backend/frontend processes and rely solely on log files (still honors explicit --watch commands).",
    )
    parser.add_argument(
        "--openai-key",
        help="OpenAI API key to use/store in assistant_hub.db (optional).",
    )
    parser.add_argument(
        "--analyze-all-logs",
        action="store_true",
        default=True,
        help="Analyze all logs for improvement opportunities, not just errors (default: True).",
    )
    parser.add_argument(
        "--no-improvements",
        action="store_true",
        help="Disable proactive improvement analysis.",
    )
    parser.add_argument(
        "--performance-threshold-ms",
        type=float,
        default=1000.0,
        help="Flag performance issues when operations take longer than this (ms, default: 1000).",
    )
    parser.add_argument(
        "--improvement-interval",
        type=int,
        default=300,
        help="Seconds between proactive improvement analysis (default: 300).",
    )
    parser.add_argument(
        "--binary-poll-interval",
        type=float,
        default=3.0,
        help="Seconds between scans for auto-detected backend/frontend binaries.",
    )
    parser.add_argument(
        "--disable-binary-monitor",
        action="store_true",
        help="Disable automatic detection of running OS Dashboard binaries (start_ui.py, npm dev servers, electron).",
    )
    parser.add_argument(
        "--daemon",
        dest="daemon",
        action="store_true",
        help="Keep running indefinitely and auto-monitor backend/frontend activity (default).",
    )
    parser.add_argument(
        "--no-daemon",
        dest="daemon",
        action="store_false",
        help="Exit once the system stays healthy for --verify-seconds (useful for CI).",
    )
    parser.set_defaults(daemon=True)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.logs_only and args.disable_log_watch:
        parser.error("--logs-only requires log watching to remain enabled (remove --disable-log-watch).")

    project_root = Path(args.project_root).resolve() if args.project_root else REPO_ROOT
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        specs = _parse_specs(args, project_root)
    except ValueError as exc:
        parser.error(str(exc))
    test_specs = _parse_test_specs(args)

    _bootstrap_openai_key(args.openai_key)

    fixer = AIFixer(persona=args.persona, diff_limit=args.diff_limit, repo_root=project_root)
    log_dirs: List[Path] = []
    if not args.disable_log_watch:
        raw_dirs: List[Any]
        if args.log_dir:
            raw_dirs = args.log_dir
        else:
            # Re-calculate default log dirs based on project_root
            raw_dirs = [
                project_root / "logs",
                project_root / "frontend" / "logs",
                project_root / "frontend" / "dist-electron" / "logs",
            ]
        for entry in raw_dirs:
            if isinstance(entry, Path):
                path = entry
            else:
                normalized = entry.strip()
                if not normalized or normalized.lower() == "none":
                    continue
                path = Path(normalized)
            if not path.is_absolute():
                path = (project_root / path).resolve()
            else:
                path = path.resolve()
            log_dirs.append(path)
        deduped: List[Path] = []
        seen_paths = set()
        for path in log_dirs:
            if path in seen_paths:
                continue
            seen_paths.add(path)
            deduped.append(path)
        log_dirs = deduped

    if not specs and (args.disable_log_watch or (not log_dirs and args.disable_binary_monitor)):
        parser.error(
            "No processes to run and no log directories to monitor. Provide a backend/frontend/--watch command "
            "or enable log/binary monitoring (remove --disable-log-watch, add --log-dir entries, or keep the binary monitor enabled)."
        )

    orchestrator = AutoFixOrchestrator(
        specs,
        fixer,
        verify_seconds=args.verify_seconds,
        buffer_lines=args.buffer_lines,
        context_lines=args.context_lines,
        log_dirs=log_dirs,
        log_pattern=args.log_pattern,
        log_poll_interval=args.log_poll_interval,
        analyze_all_logs=args.analyze_all_logs and not args.no_improvements,
        performance_threshold_ms=args.performance_threshold_ms,
        improvement_interval=args.improvement_interval,
        log_watch_enabled=not args.disable_log_watch,
        auto_binary_monitor=not args.disable_binary_monitor,
        binary_poll_interval=args.binary_poll_interval,
        test_specs=test_specs,
        test_interval=args.test_interval,
        project_root=project_root,
    )

    try:
        return orchestrator.run(args.max_attempts, daemon_mode=args.daemon)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user, shutting down...")
        orchestrator._stop_processes()
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
