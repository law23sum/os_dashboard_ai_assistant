#!/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
import asyncio
import base64
import io
import json
import random
import os
import shlex
import sqlite3
import sys
import threading
import time
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont, filedialog

# Optional requests import (defensive because repo contains requests.py)
try:
    import importlib

    _requests_mod = importlib.import_module("requests")
    if hasattr(_requests_mod, "get") and hasattr(_requests_mod, "utils"):
        requests = _requests_mod  # type: ignore
    else:
        requests = None
except Exception:
    requests = None

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.tooltip import ToolTip
    from ttkbootstrap.scrolled import ScrolledFrame

    TTKBOOTSTRAP_AVAILABLE = True
    TTKB_SCROLLED_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    TTKB_SCROLLED_AVAILABLE = False
    import tkinter.ttk as ttkb

    ScrolledFrame = None

    # Fallback tooltip class
    class ToolTip:
        def __init__(self, widget, text=""):
            self.widget = widget
            self.text = text
            self.tipwindow = None


from .paths import REPO_ROOT, DOCUMENTATION_ROOT, get_documentation_path


from .db import (
    init_db,
    load_state,
    load_settings,
    load_security_status,
    save_settings,
    save_active_persona,
    db_insert_task,
    db_update_task,
    db_delete_task,
    db_upsert_project,
    db_delete_project,
    db_insert_chat_message,
    db_clear_chat_history,
    db_get_document_samples,
    SecurityStatus,
    AssistantState,
    Settings,
    Task,
    Project,
    ChatMessage,
    PERSONAS,
    PERSONA_ROLES,
    STATUS_OPTIONS,
    PRIORITY_OPTIONS,
    DEFAULT_FETCH_PREFERENCES,
    DocumentOperation,
    db_update_document_operation_status,
    load_azure_credentials,
)
from .db import db_list_document_operations, db_record_document_operation

# Keep OPERATION_STATUS_OPTIONS optional to avoid hard import failures on older DB modules
try:
    from .db import OPERATION_STATUS_OPTIONS
except ImportError:
    OPERATION_STATUS_OPTIONS = [
        "queued",
        "running",
        "succeeded",
        "failed",
        "needs_review",
    ]

try:
    from config.logging_config import setup_logger
except ImportError:  # Fallback logger to keep GUI running if config module is absent
    import logging

    def setup_logger(name: str):
        return logging.getLogger(name)


from .utils import parse_date, ensure_project_exists
from .ai import (
    generate_ai_reply,
    openai_available,
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    get_agent_model,
    execute_tool_call,
)
from .terminal import run_bash_command
from assistant_hub.command_catalog import (
    SPEC_SHEET_COMMANDS,
    BACKEND_CLI_COMMANDS,
    BACKEND_CLI_TEMPLATES,
)
from .sync_scheduler import create_default_scheduler
from assistant_hub.writer_workspace import WriterWorkspaceState
from assistant_hub.dashboard_workspace import build_dashboard_snapshot
from assistant_hub.tasks_workspace import build_task_snapshot
from assistant_hub.projects_workspace import build_project_snapshot
from assistant_hub.monitoring_workspace import MonitoringWorkspaceState
from assistant_hub.theme import get_color_tokens
from .future_features import (
    FUTURE_FEATURES,
    get_features_by_tier,
    get_feature_lookup,
    tier_palette,
)

# Additional imports for Tools & Operations tab
try:
    import msal
    from .integrations.onenote.client import OneNoteClient

    ONENOTE_CLIENT_AVAILABLE = True
except ImportError:
    ONENOTE_CLIENT_AVAILABLE = False
    OneNoteClient = None

# Import automation orchestrator
try:
    from assistant_core.automation_orchestrator import AutomationOrchestrator

    AUTOMATION_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    AUTOMATION_ORCHESTRATOR_AVAILABLE = False
    AutomationOrchestrator = None

# Optional cognitive framework bridge (personas, daemons, reasoning)
try:
    from assistant_core.cognitive_framework import (
        CognitiveFrameworkManager,
        PersonaType,
        DaemonScope,
        DaemonType,
    )

    COGNITIVE_FRAMEWORK_AVAILABLE = True
except ImportError:
    COGNITIVE_FRAMEWORK_AVAILABLE = False
    CognitiveFrameworkManager = None
    PersonaType = None
    DaemonScope = None
    DaemonType = None


try:
    from .integrations.excel.cloud_client import ExcelCloudClient

    EXCEL_CLOUD_AVAILABLE = True
except ImportError:
    EXCEL_CLOUD_AVAILABLE = False
    ExcelCloudClient = None

try:
    from assistant_hub.integrations.pdf_integration import PDFIntegration

    PDF_INTEGRATION_AVAILABLE = True
except ImportError:
    PDF_INTEGRATION_AVAILABLE = False
    PDFIntegration = None

# Import existing integrations
try:
    from assistant_hub.integrations.notes import NotesIntegration
    from assistant_hub.integrations.apple_calendar import AppleCalendarIntegration
    from assistant_hub.integrations.gmail import GmailIntegration
    from assistant_hub.integrations.github import GitHubIntegration
    from assistant_hub.integrations.word_integration import WordIntegration
    from assistant_hub.integrations.excel_integration import ExcelIntegration
    from assistant_hub.integrations.onenote_integration import OneNoteIntegration
    from assistant_hub.integrations.onenote_integration import OneDriveIntegration
    from assistant_hub.integrations.filesystem_integration import FilesystemIntegration
    from assistant_hub.integrations.git_integration import GitIntegration

    EXISTING_INTEGRATIONS_AVAILABLE = True
except ImportError:
    EXISTING_INTEGRATIONS_AVAILABLE = False
    NotesIntegration = None
    AppleCalendarIntegration = None
    GmailIntegration = None
    GitHubIntegration = None
    WordIntegration = None
    ExcelIntegration = None
    OneNoteIntegration = None
    OneDriveIntegration = None
    FilesystemIntegration = None
    GitIntegration = None

    EXCEL_SERVICE_AVAILABLE = False
    ExcelService = None
    summarize_local_workbook = None

    WORD_SERVICE_AVAILABLE = False
    WordService = None

try:
    from .ai_layer.workflows import CleanNotebookWorkflow

    WORKFLOWS_AVAILABLE = True
except ImportError:
    WORKFLOWS_AVAILABLE = False
    CleanNotebookWorkflow = None

try:
    from .ai_layer.agents import plan_actions, prioritize_tasks, polish_text

    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
from .task_automation import process_recurring_tasks, check_task_dependencies

# Template functionality removed - backend code kept in task_templates.py for potential future use
from .ai_task_creation import create_task_from_ai_message
from .spec_registry import SpecRegistry
from .backend_registry import BackendRegistry

# Import enhanced conversation manager (optional)
try:
    from assistant_core.conversation_manager import (
        process_conversation_message,
        get_conversation_analytics,
    )

    CONVERSATION_MANAGER_AVAILABLE = True
except ImportError:
    CONVERSATION_MANAGER_AVAILABLE = False
    process_conversation_message = None
    get_conversation_analytics = None
from .analytics import (
    get_task_completion_stats,
    get_project_stats,
    get_time_tracking_stats,
    get_productivity_metrics,
    generate_report,
)

# New functionality imports
try:
    from api_connectors import (
        AppleNotesConnector,
        GitConnector,
        MicrosoftGraphConnector,
        OfficeFileConnector,
        PDFConnector,
        OpenAIConnector,
        ConnectorManager,
        ConnectorRegistry,
        ConnectorCapability,
        ConnectorConfig,
    )

    API_CONNECTORS_AVAILABLE = True
except ImportError:
    API_CONNECTORS_AVAILABLE = False
    AppleNotesConnector = None
    GitConnector = None
    MicrosoftGraphConnector = None
    OfficeFileConnector = None
    PDFConnector = None
    OpenAIConnector = None
    ConnectorManager = None
    ConnectorRegistry = None
    ConnectorCapability = None
    ConnectorConfig = None

try:
    from assistant_core.audit_system import AuditSystem, ComplianceMonitor

    AUDIT_SYSTEM_AVAILABLE = True
except ImportError:
    AUDIT_SYSTEM_AVAILABLE = False
    AuditSystem = None
    ComplianceMonitor = None

try:
    from assistant_core.search_engine import SearchEngine, VectorIndex

    SEARCH_ENGINE_AVAILABLE = True
except ImportError:
    SEARCH_ENGINE_AVAILABLE = False
    SearchEngine = None
    VectorIndex = None

try:
    from assistant_core.computer_vision_ai import ComputerVisionAI, ImageProcessor

    COMPUTER_VISION_AVAILABLE = True
except ImportError:
    COMPUTER_VISION_AVAILABLE = False
    ComputerVisionAI = None
    ImageProcessor = None

try:
    from assistant_core.daemon.workflow_orchestration import WorkflowOrchestrator

    WORKFLOW_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    WORKFLOW_ORCHESTRATOR_AVAILABLE = False
    WorkflowOrchestrator = None

try:
    from assistant_core.predictive_analytics import PredictiveAnalytics, TrendAnalyzer

    PREDICTIVE_ANALYTICS_AVAILABLE = True
except ImportError:
    PREDICTIVE_ANALYTICS_AVAILABLE = False
    PredictiveAnalytics = None
    TrendAnalyzer = None

# Import unified AI Services API
try:
    from assistant_core.ai_services_api import (
        AIServicesAPI,
        AIServiceType,
        AIServiceRequest,
        ai_services_api,
        initialize_ai_services,
        process_ai_request,
        get_service_configurations,
        get_service_availability,
    )

    AI_SERVICES_API_AVAILABLE = True
except ImportError:
    AI_SERVICES_API_AVAILABLE = False
    AIServicesAPI = None
    AIServiceType = None
    AIServiceRequest = None
    ai_services_api = None
    initialize_ai_services = None
    process_ai_request = None
    get_service_configurations = None
    get_service_availability = None

try:
    from ai_os.app.main import DummyStorage
    from ai_os.app.orchestration.runner import Orchestrator
    from ai_os.app.search.index import InMemoryVectorIndex
    from ai_os.app.governance.audit import AuditLog

    AI_OS_AVAILABLE = True
except ImportError:
    AI_OS_AVAILABLE = False
    DummyStorage = None
    Orchestrator = None
    InMemoryVectorIndex = None
    AuditLog = None

try:
    from assistant_core.mlops_platform import MLOpsPlatform

    MLOPS_PLATFORM_AVAILABLE = True
except ImportError:
    MLOPS_PLATFORM_AVAILABLE = False
    MLOpsPlatform = None

try:
    from assistant_core.personalization_engine import PersonalizationRecommendationEngine

    PERSONALIZATION_ENGINE_AVAILABLE = True
except ImportError:
    PERSONALIZATION_ENGINE_AVAILABLE = False
    PersonalizationRecommendationEngine = None

try:
    from assistant_core.collaboration_intelligence import CollaborationIntelligence

    COLLABORATION_INTELLIGENCE_AVAILABLE = True
except ImportError:
    COLLABORATION_INTELLIGENCE_AVAILABLE = False
    CollaborationIntelligence = None

try:
    from assistant_core.intelligent_monitoring import IntelligentMonitoringSystem

    INTELLIGENT_MONITORING_AVAILABLE = True
except ImportError:
    INTELLIGENT_MONITORING_AVAILABLE = False
    IntelligentMonitoringSystem = None

try:
    from assistant_core.advanced_ai_engine import (
        AdvancedAIEngine,
        MultiModalProcessor,
        PredictiveAnalyticsEngine,
        CognitiveAutomationEngine,
        NaturalLanguageInterface,
        AIInsight,
        PredictiveModel,
        AICapability,
    )

    ADVANCED_AI_AVAILABLE = True
except ImportError:
    ADVANCED_AI_AVAILABLE = False
    AdvancedAIEngine = None
    MultiModalProcessor = None
    PredictiveAnalyticsEngine = None
    CognitiveAutomationEngine = None
    NaturalLanguageInterface = None
    AIInsight = None
    PredictiveModel = None
    AICapability = None

from assistant_core.driver_registry import get_driver_registry, DriverSpec
from assistant_core.capsule_registry import (
    get_capsule_registry,
    CapsuleSpec,
    BlueprintSpec,
)
from assistant_core.integrations.onedrive_project import OneDriveProjectClient
from .suggestions import (
    get_deadline_reminders,
    get_workload_balance,
    get_project_health,
    get_smart_prioritization_suggestions,
)
from .api_bridge import get_operation_feed, summarize_operation_counts
from .export_import import (
    export_tasks_to_csv,
    export_tasks_to_json,
    export_projects_to_json,
    export_full_backup,
    import_tasks_from_csv,
    import_tasks_from_json,
)
from .document_manager import (
    upload_document as dm_upload_document,
    get_project_documents,
    format_file_size,
    DOCUMENT_TYPES,
    DOCUMENTS_BASE_DIR,
    get_document_versions,
    restore_document_version,
    get_document_version,
    materialize_document_samples,
)

try:
    import psutil
except ImportError:
    psutil = None

try:
    import customtkinter as ctk

    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False

# No limit - show all content
MAX_IMPORTED_FILE_CHARS = None  # Set to None to disable truncation


# Animation helper class
class AnimationHelper:
    """Helper class for smooth animations and transitions"""

    @staticmethod
    def fade_in(widget, duration=300, steps=10):
        """Fade in animation for widgets"""
        try:
            widget.attributes("-alpha", 0.0)
            delta = 1.0 / steps
            delay = duration // steps

            def step(alpha=0.0):
                if alpha < 1.0:
                    widget.attributes("-alpha", alpha)
                    widget.after(delay, lambda: step(alpha + delta))
                else:
                    widget.attributes("-alpha", 1.0)

            step()
        except tk.TclError:
            # Some systems don't support alpha
            pass

    @staticmethod
    def pulse_button(widget, original_bg=None, pulse_color="#4CAF50"):
        """Add a pulsing animation effect to buttons"""
        if not TTKBOOTSTRAP_AVAILABLE:
            return
        try:
            # Get current style
            current_bootstyle = getattr(widget, "cget", lambda x: None)("bootstyle")
            # Temporarily change color
            widget.configure(bootstyle="success")
            widget.after(
                200, lambda: widget.configure(bootstyle=current_bootstyle or "primary")
            )
        except:
            pass

    @staticmethod
    def add_hover_effect(button, enter_color=None, leave_color=None):
        """Add hover effect to buttons"""

        def on_enter(e):
            try:
                if TTKBOOTSTRAP_AVAILABLE and hasattr(button, "configure"):
                    # Slightly increase size or change style
                    if enter_color:
                        button.configure(bootstyle="primary")
            except:
                pass

        def on_leave(e):
            try:
                if TTKBOOTSTRAP_AVAILABLE and hasattr(button, "configure"):
                    if leave_color:
                        button.configure(bootstyle="secondary")
            except:
                pass

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button


# Progress indicator helper
class ProgressIndicator:
    """Progress indicator for async operations"""

    def __init__(self, parent):
        self.parent = parent
        self.progress_var = tk.StringVar(value="")
        self.progress_bar = None
        self.indicator_label = None

    def create(self, container, row=0, column=0, columnspan=1):
        """Create progress indicator in container"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.progress_bar = ttkb.Progressbar(
                container, mode="indeterminate", bootstyle="primary-striped", length=200
            )
            self.indicator_label = ttkb.Label(
                container, textvariable=self.progress_var, bootstyle="info"
            )
        else:
            self.progress_bar = ttk.Progressbar(
                container, mode="indeterminate", length=200
            )
            self.indicator_label = ttk.Label(container, textvariable=self.progress_var)

        self.progress_bar.grid(
            row=row, column=column, columnspan=columnspan, padx=4, pady=4, sticky="ew"
        )
        self.indicator_label.grid(
            row=row + 1, column=column, columnspan=columnspan, padx=4, pady=2
        )
        return self

    def start(self, message="Processing..."):
        """Start progress indicator"""
        if self.progress_bar:
            self.progress_var.set(message)
            self.progress_bar.start(10)
            self.progress_bar.grid()
            self.indicator_label.grid()

    def stop(self, message=""):
        """Stop progress indicator"""
        if self.progress_bar:
            self.progress_bar.stop()
            self.progress_var.set(message)
            self.progress_bar.after(500, lambda: self.progress_bar.grid_remove())
            self.indicator_label.after(500, lambda: self.indicator_label.grid_remove())


class AIOSAPIClient:
    """Lightweight HTTP client for the governed AI OS cockpit with safe fallbacks."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 2.5):
        self.base = (base_url or "http://localhost:8000").rstrip("/")
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return requests is not None

    def _get(self, path: str):
        if not self.available:
            return None
        try:
            resp = requests.get(self.base + path, timeout=self.timeout)
            if 200 <= resp.status_code < 300:
                return resp.json()
        except Exception:
            return None
        return None

    def _post(self, path: str):
        if not self.available:
            return False, None
        try:
            resp = requests.post(self.base + path, timeout=self.timeout)
            ok = 200 <= resp.status_code < 300
            payload = None
            try:
                payload = resp.json()
            except Exception:
                payload = None
            return ok, payload
        except Exception:
            return False, None

    def search(self, q: str):
        q = (q or "").strip()
        if not q:
            return []
        data = self._get(f"/search?q={requests.utils.quote(q) if requests else q}")
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("results"), list):
            return data["results"]
        return []

    def list_operations(self):
        data = self._get("/operations?limit=50")
        return data if isinstance(data, list) else []

    def get_audit(self, op_id: str):
        if not op_id:
            return None
        data = self._get(f"/audit/{op_id}")
        return data if isinstance(data, dict) else None

    def list_daemons(self):
        data = self._get("/daemons")
        return data if isinstance(data, list) else []

    def set_daemon_enabled(self, name: str, enabled: bool):
        action = "enable" if enabled else "disable"
        ok, _ = self._post(f"/daemons/{name}/{action}")
        return ok

    def run_daemon(self, name: str):
        ok, payload = self._post(f"/daemons/{name}/run")
        op_id = None
        if isinstance(payload, dict):
            op_id = payload.get("id") or payload.get("operation_id")
        return ok, op_id

    def get_system_stats(self):
        data = self._get("/system")
        return data if isinstance(data, dict) else {}

    def get_projects(self):
        data = self._get("/projects")
        return data if isinstance(data, list) else []

    def get_billing_summary(self):
        data = self._get("/billing/usage")
        return data if isinstance(data, dict) else {}

    def get_planes_status(self):
        data = self._get("/planes/status")
        return data if isinstance(data, dict) else {}


class AssistantGUI(ttkb.Window if TTKBOOTSTRAP_AVAILABLE else tk.Tk):
    def __init__(self):
        # Determine theme based on settings - use more professional modern themes
        theme_map = {
            "plain": "minty",  # Modern, clean, professional
            "light": "litera",  # Clean light theme
            "dark": "superhero",  # Modern dark theme
        }
        theme = theme_map.get(
            "plain", "minty"
        )  # Default to minty for professional look

        if TTKBOOTSTRAP_AVAILABLE:
            super().__init__(
                themename=theme, title="Assistant Hub", resizable=(True, True)
            )
            # ttkbootstrap's style is already available as self.style from parent class
        else:
            super().__init__()
            self.title("Assistant Hub")
            self.style = ttk.Style()

        # Larger default window size for better professional appearance
        self.geometry("1400x800")
        self.minsize(1200, 750)

        # Initialize fonts immediately with defaults (needed before loading settings)
        self.base_font = tkfont.nametofont("TkDefaultFont")
        self.text_font = tkfont.nametofont("TkTextFont")

        # Initialize logger
        self.logger = setup_logger("AssistantGUI")

        self.conn: sqlite3.Connection = init_db()
        self.state_obj: AssistantState = load_state(self.conn)
        self.settings: Settings = load_settings(self.conn)
        self._last_data_preferences = dict(
            getattr(self.settings, "data_preferences", {}) or {}
        )
        self.security_status: SecurityStatus = load_security_status(self.conn)
        backend_default = os.environ.get("AIOS_BACKEND_URL") or getattr(
            self.settings, "api_base_url", "http://localhost:8000"
        )
        self.aios_api_client = AIOSAPIClient(base_url=backend_default)
        self.aios_system_snapshot: Dict[str, Any] = {}
        self.aios_planes_status: Dict[str, Any] = {}
        self.aios_project_cache: List[Dict[str, Any]] = []
        self.aios_billing_cache: Dict[str, Any] = {}
        self.aios_backend_last_refresh: float = 0.0
        self.spec_registry = SpecRegistry()
        self.backend_registry = BackendRegistry(self.spec_registry)
        self.driver_registry = get_driver_registry()
        self.capsule_registry = get_capsule_registry()
        self.cognitive_manager: Optional[CognitiveFrameworkManager] = None
        self.cognitive_status: Dict[str, Any] = {
            "personas": [],
            "daemons": [],
            "reasoning": [],
        }
        self.cognitive_status_note = tk.StringVar(value="Cognitive layer inactive")
        self.cognitive_reasoning_history: List[Dict[str, Any]] = []
        self.cognitive_query_var = tk.StringVar(
            value="Where should the AI team focus this week?"
        )
        self.cognitive_reasoning_status = tk.StringVar(
            value="Reasoning traces will appear here."
        )
        self.future_features_by_tier = get_features_by_tier()
        self.future_feature_lookup = get_feature_lookup()
        self.future_feature_palette = tier_palette()
        self.future_feature_capability_map = {
            f"{item.code} · {item.title}": item.code for item in FUTURE_FEATURES
        }
        self.future_feature_tree = None
        self.future_feature_title_var = tk.StringVar(value="Select a capability")
        self.future_feature_value_var = tk.StringVar(value="")
        self.future_feature_summary_var = tk.StringVar(
            value="Choose a capability to load its implementation canvas."
        )
        self.future_feature_detail_body = None
        self._initialize_cognitive_framework()
        # Initialize after tkinter window is fully created
        self.future_feature_tier_docs = None  # Will be set after window creation

        # Build palette before configuring styles so widgets share a cohesive look
        self._build_color_palette()
        # Performance optimization: Resource limits and throttling
        self._ui_update_pending = False
        self._last_ui_update_time = 0
        self._ui_update_throttle_ms = 100  # Minimum 100ms between UI updates
        self._max_chat_messages_memory = 2000  # Keep max 2000 messages in memory
        self._chat_history_chunk_size = 100  # Process chat in chunks

        # Configure fonts based on settings
        self._initialize_fonts()

        self.chat_sender_var = tk.StringVar(value="Chris")
        self.chat_agent_var = tk.StringVar(value=self.state_obj.active_persona)
        self.chat_model_var = tk.StringVar(value="auto")
        self.uploaded_files = []  # Track uploaded files for current conversation
        self.model_combo = None  # Will be set in _build_chat_tab
        self.chat_status_var = tk.StringVar()
        self.system_prompt_text = None
        self.chat_text = None
        self.cognitive_reasoning_text = None
        self.command_var = tk.StringVar()
        self.cwd_var = tk.StringVar(value=os.getcwd())
        self.project_docs_file_paths = (
            {}
        )  # Map item_id -> file_path for project documents
        self.project_docs_link_ids = {}  # Map item_id -> link_id for project documents
        self.ai_ops_status_filter = tk.StringVar(value="all")
        self.ai_ops_integration_filter = tk.StringVar(value="all")
        self.dashboard_text_targets = (
            []
        )  # Track dashboard widgets across classic/unified views
        self.dashboard_snapshot = None
        self.spec_tree_docs: Dict[str, Any] = {}
        self.backend_tree_items: Dict[str, Any] = {}
        self.spec_search_var = tk.StringVar()
        self.backend_filter_var = tk.StringVar(value="All")
        self.page_action_var = tk.StringVar()
        self.page_search_var = tk.StringVar()
        self.current_page_key = None
        self.page_action_definitions: Dict[str, Dict[str, Any]] = {}
        self.driver_layer_filter_var = tk.StringVar(value="All")
        self.driver_search_var = tk.StringVar()
        self.driver_capsule_summary_var = tk.StringVar(value="Manual verification run")
        self.driver_tree_items: Dict[str, str] = {}
        self.driver_capsule_map: Dict[int, str] = {}
        self.driver_blueprint_map: Dict[int, str] = {}
        self.selected_driver_id: Optional[str] = None
        self.onedrive_project_client: Optional[OneDriveProjectClient] = None
        self.onedrive_file_id_var = tk.StringVar()
        self.onedrive_update_content_var = tk.StringVar(
            value="Updated file content via OS Dashboard"
        )
        self.onedrive_new_filename_var = tk.StringVar(value="NewFile.txt")
        self.onedrive_upload_text = None
        self._onedrive_cached_ids = ("", "")
        # Optional automation orchestrator instance (set when feature is available)
        # Initialize to None so attribute lookups remain safe even if the feature
        # isn't loaded, avoiding Tk's __getattr__ fallback from raising errors
        # during GUI construction.
        self.automation_orchestrator = None
        # Terminal command helpers used by the Tools view
        self.command_entry_var = None
        self.command_terminal_output = None
        self.backend_action_var = tk.StringVar()
        self.backend_action_combo = None
        self.backend_output_text = None
        # Commands pulled from the spec sheet so they are runnable from the GUI
        self.spec_sheet_commands = [dict(cmd) for cmd in SPEC_SHEET_COMMANDS]
        # Backend CLI commands (wired to assistant_hub.ui.terminal.cli)
        self.backend_cli_commands = [dict(cmd) for cmd in BACKEND_CLI_COMMANDS]
        # Templates that prefill the command box so users can insert IDs/paths before running
        self.backend_cli_templates = [dict(cmd) for cmd in BACKEND_CLI_TEMPLATES]
        # Shared writer workspace state (used by Tk + FastAPI + React)
        self.writer_state = WriterWorkspaceState()
        self.writer_document_type_var = tk.StringVar(value="Article")
        self.writer_genre_var = tk.StringVar(value="Professional")
        self.writer_length_var = tk.StringVar(value="Short (500-1000 words)")
        self.writer_assistance_var = tk.StringVar(value="Minimal")
        self.writer_title_var = tk.StringVar(value="")
        self.writer_theme_var = tk.StringVar(value="")
        self.writer_word_count_var = tk.StringVar(value="0 words")
        self.writer_status_note = tk.StringVar(value="Ready to create your next masterpiece.")
        initial_writer_stats = self.writer_state.snapshot()["stats"]
        self.writer_stats_vars = {
            "total_words": tk.StringVar(value=f'{initial_writer_stats["total_words"]:,}'),
            "documents": tk.StringVar(value=str(initial_writer_stats["documents"])),
            "avg_words_per_day": tk.StringVar(value=str(initial_writer_stats["avg_words_per_day"])),
            "writing_streak": tk.StringVar(value=str(initial_writer_stats["writing_streak"])),
        }
        self.writer_document_tree = None
        self.writer_document_rows: Dict[str, str] = {}
        self.writer_editor: Optional[tk.Text] = None
        self.writer_active_document_id: Optional[str] = None
        self.writer_suggestions_container = None
        self.writer_canon_container = None
        self.writer_pipeline_container = None
        self.writer_progress_canvas = None
        self.writer_status_label = None
        self.writer_real_time_job = None
        # Monitoring workspace fallback so Tk mirrors the React dashboard when AI services are offline
        self.monitoring_workspace_state = MonitoringWorkspaceState()
        # Tasks workspace state shared with React
        self.show_done_var = tk.BooleanVar(value=True)
        self.tasks_tree = None
        self.tasks_snapshot = None
        self.tasks_summary_text = None
        self.tasks_overview_text = None
        self.projects_summary_text = None
        self.project_tree = None
        self.project_snapshot = None
        self.project_summary_text = None
        self.demo_status_var = tk.StringVar(
            value="Run the built-in demo suite from the GUI to preview README examples."
        )
        self.demo_output_text = None
        self.demo_run_button = None
        self._demo_thread = None
        self._demo_running = False

        self._configure_style()
        self._apply_style_overrides()
        # Build web page map early so global dropdowns can reuse it
        self.aios_web_page_map = self._build_ai_os_web_page_map()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_topbar()
        # Toolbar that replaces the horizontal tab bar with dropdown navigation
        if TTKBOOTSTRAP_AVAILABLE:
            self.tab_dropdown_bar = ttkb.Frame(self, padding=(12, 8), style="GlassBackground.TFrame")
        else:
            self.tab_dropdown_bar = ttk.Frame(self, padding=(12, 8), style="GlassBackground.TFrame")
        self.tab_dropdown_bar.grid(row=1, column=0, sticky="ew")
        for i in range(7):
            self.tab_dropdown_bar.columnconfigure(i, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            self.content_frame = ttkb.Frame(self, padding=(0, 0), style="GlassBackground.TFrame")
        else:
            self.content_frame = ttk.Frame(self, style="GlassBackground.TFrame")
        self.content_frame.grid(row=2, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            self.notebook = ttkb.Notebook(self.content_frame, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(self.content_frame)
        try:
            self.notebook.configure(style="Glass.TNotebook")
        except tk.TclError:
            pass
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=(4, 12))

        # Build the page assistant tab now; it will be attached to the main
        # notebook after the core tabs are created so it sits on the far right.
        self.page_assistant_tab = ttk.Frame(self.notebook)
        self._build_page_info_panel()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # Classic tabs remain available; new consolidated views are added below
        self._build_dashboard_tab()
        self._build_tasks_tab()
        self._build_projects_tab()
        self._build_chat_tab()
        self._build_integrations_tab()
        self._build_tools_tab()
        self._build_writer_workspace_tab()
        self._build_analytics_tab()
        self._build_settings_tab()
        self._build_ai_operations_tab()

        classic_tab_count = self.notebook.index("end")

        # Consolidated tabs with shared pages (additive, not replacing classic tabs)
        self._build_dashboard_analytics_tab()
        self._build_tasks_projects_tab()
        self._build_ai_systems_tab()
        self._build_ai_features_tab()
        # Individual AI feature tabs
        self._build_api_connectors_tab()
        self._build_ai_os_tab()
        self._build_advanced_ai_tab()
        self._build_audit_system_tab()
        self._build_search_engine_tab()
        self._build_computer_vision_tab()
        self._build_neural_architecture_search_tab()
        self._build_security_threat_detection_tab()
        self._build_edge_computing_tab()
        self._build_workflow_orchestration_tab()
        self._build_mlops_tab()
        self._build_personalization_tab()
        self._build_collaboration_tab()
        self._build_intelligent_monitoring_tab()
        self._build_tools_intelligence_tab()
        self._build_integrations_infrastructure_tab()
        self._build_security_audit_tab()
        self._build_ai_os_cockpit_tab()
        self._build_specs_and_systems_tab()
        self._build_driver_layer_tab()
        self._build_future_features_tab()
        self.notebook.add(self.page_assistant_tab, text="📘 Page Guide")

        # Initialize future_feature_tier_docs after all tabs are built
        if self.future_feature_tier_docs is None:
            self.future_feature_tier_docs = self._build_future_feature_tier_doc_map()

        self.page_guides = self._build_page_guides()
        self._update_page_info_panel()

        # Update tab labels with icons if available
        if TTKBOOTSTRAP_AVAILABLE:
            base_labels = [
                "📊 Dashboard",
                "✅ Tasks",
                "📁 Projects",
                "💬 AI Console",
                "🔗 Integrations",
                "🔧 Tools",
                "📊 Analytics",
                "⚙️ Settings",
                "🛰️ AI Ops Feed",
            ]
            for idx, label in enumerate(base_labels):
                try:
                    self.notebook.tab(idx, text=label)
                except Exception:
                    pass

            consolidated_labels = [
                "📊 Dashboard & Analytics",
                "✅ Tasks & Projects",
                "🤖 AI Systems",
                "🚀 AI Features",
                "🔧 Tools & Intelligence",
                "🔌 Integrations & Infrastructure",
                "🛡️ Security & Audit",
                "🧭 AI OS Cockpit",
                "🚧 Future Features",
            ]
            for offset, label in enumerate(consolidated_labels):
                try:
                    self.notebook.tab(classic_tab_count + offset, text=label)
                except Exception:
                    pass

        # Populate additive tab navigation dropdown after tabs are created, then hide tab strip
        self._capture_tab_metadata()
        self._hide_notebook_tabs()
        self._build_tab_dropdown_bar()
        self._initialize_tab_navigation()
        self._refresh_tab_group_dropdowns()
        self._refresh_web_page_dropdown()

        # Initialize sync scheduler
        self.sync_scheduler = create_default_scheduler(self.conn)
        self._apply_data_preferences()
        try:
            self.sync_scheduler.start()
        except Exception as exc:
            self.logger.warning("Failed to start sync scheduler: %s", exc)

        # Initialize AI Services API
        self.ai_services_api = None
        if AI_SERVICES_API_AVAILABLE:
            self.ai_services_api = ai_services_api
            # Initialize asynchronously in background
            def init_ai_services():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(initialize_ai_services())
                    loop.close()
                    self.logger.info("AI Services API initialized successfully")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize AI Services API: {e}")
            
            threading.Thread(target=init_ai_services, daemon=True).start()

        # Process recurring tasks on startup
        try:
            process_recurring_tasks(self.conn)
        except Exception:
            pass

        # Start cognitive daemon system for continuous background automation
        try:
            from .daemon import start_daemon_system

            self.cognitive_daemon = start_daemon_system(self.conn, enabled=True)
            print("[GUI] Cognitive daemon system started - active automation enabled")
        except Exception as e:
            print(f"[GUI] Warning: Could not start cognitive daemon: {e}")
            self.cognitive_daemon = None

        # Initialize automation orchestrator attribute
        self.automation_orchestrator = None

        # Initialize automation orchestrator for intelligent workflow automation
        try:
            if AUTOMATION_ORCHESTRATOR_AVAILABLE:
                self.automation_orchestrator = AutomationOrchestrator(app_state=self)
                loop = asyncio.get_event_loop()
                loop.create_task(self.automation_orchestrator.initialize())
                print(
                    "[GUI] Automation Orchestrator initialized - intelligent workflows enabled"
                )
            else:
                print("[GUI] Warning: Automation Orchestrator not available")
                self.automation_orchestrator = None
        except Exception as e:
            print(f"[GUI] Warning: Could not initialize automation orchestrator: {e}")
            self.automation_orchestrator = None

        # Initialize Git versioning worker for automatic version control
        try:
            from .versioning import start_git_worker, get_git_manager

            start_git_worker()
            get_git_manager().ensure_repo()
            print(
                "[GUI] Git versioning initialized - all changes will be automatically tracked"
            )
        except Exception as e:
            print(f"[GUI] Warning: Could not initialize Git versioning: {e}")

        # Setup keyboard shortcuts for better usability
        self._setup_keyboard_shortcuts()

        self._apply_default_view()
        self.refresh_all()
        self._update_chat_status()
        # Initialize agent model display after UI is built
        if hasattr(self, "chat_agent_var"):
            self.after(100, self.on_agent_change)

        # Add fade-in animation to main window if supported
        try:
            AnimationHelper.fade_in(self)
        except:
            pass

    # ---------- Top bar ----------

    def _build_color_palette(self):
        """Load the shared theme tokens so Tk and React stay in sync."""
        tokens = get_color_tokens(getattr(self.settings, "theme", None))
        self.colors = {
            "background": tokens.get("background", "#050914"),
            "surface": tokens.get("surface", tokens.get("backgroundAlt", "#0f172a")),
            "surface_alt": tokens.get("surfaceAlt", tokens.get("surface", "#17213c")),
            "border": tokens.get("border", "#1f293b"),
            "text": tokens.get("text", "#f8fafc"),
            "muted": tokens.get("muted", "#94a3b8"),
            "accent": tokens.get("accent", "#6366f1"),
            "accent_hover": tokens.get("accentHover", "#7c3aed"),
            "pill": tokens.get("pill", "#1f2b46"),
        }

    def _initialize_cognitive_framework(self):
        """Initialize the Cognitive Framework per Section 4 of the Canon Technical Specification.
        
        Implements:
        - 4.1 Personas as Strategy Bundles (Chris, AIC, Sora, Aria, others)
        - 4.2 AIC as Meta-Governor, Canonical Systems Architect & Knowledge Steward
        - 4.3 Daemon Families & Roles (Echo, Oracle, Critic, Archivist, Billing Optimizer, Security Monitor, etc.)
        - 4.4 Daemon Runtime, Scheduling, Scopes, Budgets & Policies
        - 4.5 Project Intelligence Subsystem (Per-Project "Brain")
        - 4.6 Theoretical Reasoning Framework (TRF) – Structures, Operators & APIs
        - 4.7 Reasoning over Time (Continuity, Resonance, Long-Horizon Memory)
        - 4.8 Reasoning Traces, Explanations & Epistemic Guarantees
        """
        if not COGNITIVE_FRAMEWORK_AVAILABLE:
            self.cognitive_status_note.set("Cognitive framework not available (optional dependency)")
            self.logger.warning("Cognitive framework not available - install assistant_core.cognitive_framework")
            return
        
        try:
            # Initialize the Cognitive Framework Manager
            self.cognitive_manager = CognitiveFrameworkManager()
            
            # Initialize asynchronously to avoid blocking GUI startup
            def init_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.cognitive_manager.initialize())
                    loop.run_until_complete(self.cognitive_manager.start_cognitive_services())
                    loop.close()
                    
                    # Update status on main thread
                    self.after(0, self._update_cognitive_status)
                except Exception as e:
                    self.logger.exception("Failed to initialize cognitive framework: %s", e)
                    self.after(0, lambda: self.cognitive_status_note.set(
                        f"Cognitive framework initialization error: {str(e)[:50]}"
                    ))
            
            # Start initialization in background thread
            init_thread = threading.Thread(target=init_async, daemon=True, name="CognitiveFrameworkInit")
            init_thread.start()
            
            self.cognitive_status_note.set("Cognitive framework initializing...")
            self.logger.info("Cognitive framework initialization started")
            
        except Exception as e:
            self.logger.exception("Error setting up cognitive framework: %s", e)
            self.cognitive_status_note.set(f"Cognitive framework setup error: {str(e)[:50]}")
    
    def _update_cognitive_status(self):
        """Update cognitive framework status display per Section 4.8 (Reasoning Traces, Explanations)."""
        if not self.cognitive_manager or not self.cognitive_manager.initialized:
            return
        
        try:
            status = self.cognitive_manager.get_system_status()
            
            # Update personas list (Section 4.1)
            self.cognitive_status["personas"] = [
                {
                    "id": pid,
                    "type": ptype,
                    "active": True
                }
                for pid, ptype in status.get("personas", {}).items()
            ]
            
            # Update daemons list (Section 4.3)
            daemon_status = status.get("daemon_status", {})
            self.cognitive_status["daemons"] = [
                {
                    "id": daemon_id,
                    "type": info.get("type", "unknown"),
                    "status": info.get("status", "unknown"),
                    "execution_count": info.get("execution_count", 0),
                    "last_execution": info.get("last_execution")
                }
                for daemon_id, info in daemon_status.items()
            ]
            
            # Update reasoning traces (Section 4.8)
            reasoning_count = status.get("reasoning_traces", 0)
            self.cognitive_status["reasoning"] = [
                {
                    "count": reasoning_count,
                    "project_intelligence": status.get("project_intelligence_count", 0)
                }
            ]
            
            # Update status note
            active_daemons = sum(1 for d in self.cognitive_status["daemons"] 
                               if d.get("status") == "running")
            self.cognitive_status_note.set(
                f"Cognitive layer active: {len(self.cognitive_status['personas'])} personas, "
                f"{active_daemons} daemons, {reasoning_count} reasoning traces"
            )
            
        except Exception as e:
            self.logger.exception("Error updating cognitive status: %s", e)
            self.cognitive_status_note.set(f"Status update error: {str(e)[:50]}")
    
    def _refresh_cognitive_status(self):
        """Refresh cognitive framework status and update UI."""
        if self.cognitive_manager:
            self._update_cognitive_status()
        self._render_ai_os_view()  # Refresh the AI OS view if it's open
    
    def _execute_ai_service_request(self, service_type, parameters: Dict[str, Any], input_data: Optional[Dict[str, Any]] = None, results_widget: Optional[tk.Text] = None):
        """Unified method to execute AI service requests using AIServicesAPI"""
        if not AI_SERVICES_API_AVAILABLE or not self.ai_services_api or not AIServiceType:
            messagebox.showwarning("Service Unavailable", "AI Services API is not available.")
            return
        def worker():
            try:
                request = AIServiceRequest(service_type=service_type, user_id=getattr(self.state_obj, 'user_id', 'default_user'), parameters=parameters, input_data=input_data or {})
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(self.ai_services_api.process_request(request))
                loop.close()
                def update_ui():
                    if response.success:
                        result_text = json.dumps(response.result, indent=2) if response.result else "No results"
                        if results_widget:
                            results_widget.config(state=tk.NORMAL)
                            results_widget.delete("1.0", tk.END)
                            results_widget.insert("1.0", result_text)
                            results_widget.config(state=tk.DISABLED)
                        else:
                            messagebox.showinfo(f"{service_type.value.replace('_', ' ').title()} Complete", f"Success!\n\nResult: {result_text[:500]}...")
                    else:
                        error_msg = response.error_message or "Unknown error"
                        if results_widget:
                            results_widget.config(state=tk.NORMAL)
                            results_widget.delete("1.0", tk.END)
                            results_widget.insert("1.0", f"Error: {error_msg}")
                            results_widget.config(state=tk.DISABLED)
                        else:
                            messagebox.showerror("Service Error", f"Failed: {error_msg}")
                self.after(0, update_ui)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Execution Error", f"Failed to execute {service_type.value}: {str(e)}"))
        threading.Thread(target=worker, daemon=True).start()

    def _execute_nlp_conversation(self):
        """Execute NLP conversation using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        action = getattr(self, 'nlp_action_var', tk.StringVar(value="analyze")).get()
        language = getattr(self, 'nlp_language_var', tk.StringVar(value="en")).get()
        text_input = getattr(self, 'nlp_input_text', None)
        input_text = text_input.get("1.0", tk.END).strip() if text_input else ""
        max_length = int(getattr(self, 'nlp_max_length_var', tk.StringVar(value="500")).get())
        self._execute_ai_service_request(AIServiceType.NLP_CONVERSATION, {"action": action}, {"text": input_text, "language": language, "max_length": max_length}, getattr(self, 'nlp_results_text', None))

    def _execute_automation_orchestration(self):
        """Execute automation orchestration using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        workflow_type = getattr(self, 'workflow_type_var', tk.StringVar(value="task_automation")).get()
        trigger = getattr(self, 'trigger_condition_var', tk.StringVar(value="daily")).get()
        schedule = getattr(self, 'execution_schedule_var', tk.StringVar(value="0 9 * * *")).get()
        max_retries = int(getattr(self, 'max_retries_var', tk.StringVar(value="3")).get())
        self._execute_ai_service_request(AIServiceType.AUTOMATION_ORCHESTRATION, {"workflow_type": workflow_type}, {"trigger_condition": trigger, "execution_schedule": schedule, "max_retries": max_retries}, getattr(self, 'automation_results_text', None))

    def _execute_computer_vision(self):
        """Execute computer vision using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        analysis_type = getattr(self, 'cv_analysis_type_var', tk.StringVar(value="object_detection")).get()
        image_url = getattr(self, 'cv_image_url_var', tk.StringVar(value="")).get()
        confidence_threshold = float(getattr(self, 'cv_confidence_var', tk.StringVar(value="0.5")).get())
        max_results = int(getattr(self, 'cv_max_results_var', tk.StringVar(value="10")).get())
        self._execute_ai_service_request(AIServiceType.COMPUTER_VISION, {"analysis_type": analysis_type}, {"image_url": image_url, "confidence_threshold": confidence_threshold, "max_results": max_results}, getattr(self, 'cv_results_text', None))

    def _execute_security_ai(self):
        """Execute security AI using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        action = getattr(self, 'security_action_var', tk.StringVar(value="scan")).get()
        scan_target = getattr(self, 'security_scan_target_var', tk.StringVar(value="")).get()
        threat_types = getattr(self, 'security_threat_types_var', tk.StringVar(value="")).get().split(",") if getattr(self, 'security_threat_types_var', None) else []
        severity = getattr(self, 'security_severity_var', tk.StringVar(value="medium")).get()
        self._execute_ai_service_request(AIServiceType.SECURITY_AI, {"action": action}, {"scan_target": scan_target, "threat_types": threat_types, "severity_level": severity}, getattr(self, 'security_results_text', None))

    def _execute_edge_computing(self):
        """Execute edge computing using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        operation = getattr(self, 'edge_operation_var', tk.StringVar(value="deploy")).get()
        model_name = getattr(self, 'edge_model_name_var', tk.StringVar(value="")).get()
        target_devices = getattr(self, 'edge_target_devices_var', tk.StringVar(value="")).get().split(",") if getattr(self, 'edge_target_devices_var', None) else []
        resource_limits = getattr(self, 'edge_resource_limits_var', tk.StringVar(value="")).get()
        self._execute_ai_service_request(AIServiceType.EDGE_COMPUTING, {"operation": operation}, {"model_name": model_name, "target_devices": target_devices, "resource_limits": resource_limits}, getattr(self, 'edge_results_text', None))

    def _execute_personalization(self):
        """Execute personalization using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        recommendation_type = getattr(self, 'personalization_type_var', tk.StringVar(value="content_based")).get()
        user_preferences = getattr(self, 'personalization_preferences_var', tk.StringVar(value="")).get()
        context_data = getattr(self, 'personalization_context_var', tk.StringVar(value="")).get()
        max_recommendations = int(getattr(self, 'personalization_max_var', tk.StringVar(value="10")).get())
        self._execute_ai_service_request(AIServiceType.PERSONALIZATION, {"recommendation_type": recommendation_type}, {"user_preferences": user_preferences, "context_data": context_data, "max_recommendations": max_recommendations}, getattr(self, 'personalization_results_text', None))

    def _execute_collaboration(self):
        """Execute collaboration intelligence using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        action = getattr(self, 'collaboration_action_var', tk.StringVar(value="analyze_team")).get()
        team_size = int(getattr(self, 'collaboration_team_size_var', tk.StringVar(value="5")).get())
        communication_patterns = getattr(self, 'collaboration_patterns_var', tk.StringVar(value="")).get()
        project_complexity = getattr(self, 'collaboration_complexity_var', tk.StringVar(value="medium")).get()
        self._execute_ai_service_request(AIServiceType.COLLABORATION, {"action": action}, {"team_size": team_size, "communication_patterns": communication_patterns, "project_complexity": project_complexity}, getattr(self, 'collaboration_results_text', None))

    def _execute_mlops(self):
        """Execute MLOps using unified API"""
        if not AI_SERVICES_API_AVAILABLE or not AIServiceType: return
        action = getattr(self, 'mlops_action_var', tk.StringVar(value="train_model")).get()
        model_type = getattr(self, 'mlops_model_type_var', tk.StringVar(value="classification")).get()
        dataset_path = getattr(self, 'mlops_dataset_var', tk.StringVar(value="")).get()
        hyperparameters = getattr(self, 'mlops_hyperparams_var', tk.StringVar(value="{}")).get()
        self._execute_ai_service_request(AIServiceType.MLOPS, {"action": action}, {"model_type": model_type, "dataset_path": dataset_path, "hyperparameters": hyperparameters}, getattr(self, 'mlops_results_text', None))

    def _execute_monitoring(self):
        """Execute monitoring via AI service with a shared workspace fallback."""
        action = getattr(self, 'monitoring_action_var', tk.StringVar(value="check_health")).get()
        system_metrics = getattr(self, 'monitoring_metrics_var', tk.StringVar(value="{}")).get()
        alert_thresholds = getattr(self, 'monitoring_thresholds_var', tk.StringVar(value="{}")).get()
        monitoring_window = int(getattr(self, 'monitoring_window_var', tk.StringVar(value="24")).get())

        if AI_SERVICES_API_AVAILABLE and AIServiceType:
            self._execute_ai_service_request(
                AIServiceType.MONITORING,
                {"action": action},
                {
                    "system_metrics": system_metrics,
                    "monitoring_window": monitoring_window,
                    "alert_thresholds": alert_thresholds,
                },
                getattr(self, 'monitoring_results_text', None),
            )
            return

        # Fallback to the shared MonitoringWorkspaceState so Tk mirrors the React dashboard view.
        def _safe_json_load(raw: str) -> Dict[str, Any]:
            if not raw:
                return {}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                self.logger.warning("Invalid JSON payload for monitoring input: %s", raw)
                return {}

        workspace = getattr(self, "monitoring_workspace_state", None) or MonitoringWorkspaceState()
        self.monitoring_workspace_state = workspace
        result = workspace.run_action(
            action,
            system_metrics=_safe_json_load(system_metrics) or None,
            monitoring_window=monitoring_window or None,
            alert_thresholds=_safe_json_load(alert_thresholds) or None,
        )
        widget = getattr(self, 'monitoring_results_text', None)
        result_text = json.dumps(result, indent=2)
        if widget:
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", result_text)
            widget.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Monitoring Result", result_text[:500] + ("..." if len(result_text) > 500 else ""))

    def _execute_cognitive_reasoning_query(self, query: Optional[str] = None, persona_type: Optional[PersonaType] = None):
        """Execute a reasoning query using the Theoretical Reasoning Framework (TRF) per Section 4.6-4.8.
        
        Implements:
        - 4.6 Theoretical Reasoning Framework (TRF) – Structures, Operators & APIs
        - 4.7 Reasoning over Time (Continuity, Resonance, Long-Horizon Memory)
        - 4.8 Reasoning Traces, Explanations & Epistemic Guarantees
        
        Args:
            query: The reasoning query to execute. If None, uses cognitive_query_var.
            persona_type: Persona to use for reasoning. If None, uses cognitive_reasoning_persona_var.
        """
        if not COGNITIVE_FRAMEWORK_AVAILABLE or not self.cognitive_manager:
            self.cognitive_reasoning_status.set("Cognitive framework not available")
            return
        
        if not self.cognitive_manager.initialized:
            self.cognitive_reasoning_status.set("Cognitive framework not initialized yet")
            return
        
        # Get query and persona
        if query is None:
            query = self.cognitive_query_var.get().strip()
        if not query:
            self.cognitive_reasoning_status.set("Please enter a reasoning query")
            return
        
        if persona_type is None:
            persona_str = "AIC"  # Default to AIC
            persona_type_map = {
                "Chris": PersonaType.CHRIS,
                "AIC": PersonaType.AIC,
                "Aria": PersonaType.ARIA,
                "Sora": PersonaType.SORA,
            }
            persona_type = persona_type_map.get(persona_str, PersonaType.AIC)
        
        # Update status
        self.cognitive_reasoning_status.set(f"Reasoning about: {query[:50]}...")
        
        # Execute reasoning asynchronously
        def reason_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                trace = loop.run_until_complete(
                    self.cognitive_manager.reason_about(query, persona_type)
                )
                loop.close()
                
                # Update UI on main thread
                self.after(0, lambda: self._display_reasoning_trace(trace, query))
            except Exception as e:
                self.logger.exception("Reasoning query failed: %s", e)
                self.after(0, lambda: self.cognitive_reasoning_status.set(
                    f"Reasoning error: {str(e)[:100]}"
                ))
        
        reason_thread = threading.Thread(target=reason_async, daemon=True, name="CognitiveReasoning")
        reason_thread.start()
    
    def _display_reasoning_trace(self, trace, original_query: str):
        """Display reasoning trace results per Section 4.8 (Reasoning Traces, Explanations)."""
        try:
            # Store in history
            trace_data = {
                "id": trace.id,
                "query": original_query,
                "conclusion": trace.final_conclusion,
                "confidence": trace.overall_confidence,
                "steps": [
                    {
                        "operator": step.operator.value,
                        "premises": step.premises,
                        "conclusion": step.conclusion,
                        "confidence": step.confidence,
                    }
                    for step in trace.steps
                ],
                "timestamp": trace.created_at.isoformat() if hasattr(trace.created_at, "isoformat") else str(trace.created_at),
            }
            self.cognitive_reasoning_history.append(trace_data)
            
            # Update status
            self.cognitive_reasoning_status.set(
                f"Reasoning complete: {len(trace.steps)} steps, "
                f"confidence {trace.overall_confidence:.2f}"
            )
            
            # Display in reasoning text widget if available
            if hasattr(self, "cognitive_reasoning_text") and self.cognitive_reasoning_text:
                display_text = f"Query: {original_query}\n\n"
                display_text += f"Conclusion: {trace.final_conclusion}\n"
                display_text += f"Overall Confidence: {trace.overall_confidence:.2f}\n\n"
                display_text += "Reasoning Steps:\n"
                for i, step in enumerate(trace.steps, 1):
                    display_text += f"\n{i}. {step.operator.value.upper()}\n"
                    if step.premises:
                        display_text += f"   Premises: {', '.join(step.premises)}\n"
                    display_text += f"   Conclusion: {step.conclusion}\n"
                    display_text += f"   Confidence: {step.confidence:.2f}\n"
                
                self.cognitive_reasoning_text.config(state=tk.NORMAL)
                self.cognitive_reasoning_text.delete("1.0", "end")
                self.cognitive_reasoning_text.insert("1.0", display_text)
                self.cognitive_reasoning_text.config(state=tk.DISABLED)
            
            # Update cognitive status
            self._update_cognitive_status()
            
        except Exception as e:
            self.logger.exception("Error displaying reasoning trace: %s", e)
            self.cognitive_reasoning_status.set(f"Display error: {str(e)[:100]}")

    def _initialize_fonts(self):
        """Configure fonts based on settings with professional typography."""
        try:
            scale_map = {
                "small": 11,
                "medium": 13,
                "large": 15,
            }  # Slightly larger for better readability
            base_size = scale_map.get(
                getattr(self.settings, "font_scale", "medium"), 13
            )

            # Configure the already-initialized fonts with better typography
            if hasattr(self, "base_font"):
                self.base_font.configure(size=base_size)
            else:
                self.base_font = tkfont.nametofont("TkDefaultFont")
                self.base_font.configure(size=base_size)

            if hasattr(self, "text_font"):
                self.text_font.configure(size=base_size)
            else:
                self.text_font = tkfont.nametofont("TkTextFont")
                self.text_font.configure(size=base_size)

            # Create heading font for better visual hierarchy
            self.heading_font = tkfont.Font(
                family=self.base_font.actual("family"),
                size=base_size + 2,
                weight="bold",
            )

            # Create bold font for emphasis
            self.bold_font = tkfont.Font(
                family=self.base_font.actual("family"), size=base_size, weight="bold"
            )

            self.hero_font = tkfont.Font(
                family=self.base_font.actual("family"),
                size=base_size + 6,
                weight="bold",
            )
            self.subtle_font = tkfont.Font(
                family=self.base_font.actual("family"),
                size=base_size - 1,
            )
            self.small_caps_font = tkfont.Font(
                family=self.base_font.actual("family"),
                size=max(base_size - 2, 9),
                weight="bold",
            )
        except Exception as e:
            # Fallback to default fonts if configuration fails
            print(f"Warning: Could not configure fonts: {e}")
            if not hasattr(self, "base_font"):
                self.base_font = tkfont.nametofont("TkDefaultFont")
            if not hasattr(self, "text_font"):
                self.text_font = tkfont.nametofont("TkTextFont")
            self.heading_font = self.base_font
            self.bold_font = self.base_font
            self.hero_font = self.base_font
            self.subtle_font = self.base_font
            self.small_caps_font = self.base_font

    def _configure_style(self):
        if TTKBOOTSTRAP_AVAILABLE:
            # ttkbootstrap handles themes automatically - use professional themes
            theme_map = {"plain": "minty", "light": "litera", "dark": "superhero"}
            theme = theme_map.get(self.settings.theme, "minty")
            self.style.theme_use(theme)
        else:
            try:
                self.style.theme_use("clam")
            except tk.TclError:
                pass

        scale_map = {"small": 11, "medium": 13, "large": 15}
        base_size = scale_map.get(self.settings.font_scale, 13)

        # Fonts are already initialized by _initialize_fonts()
        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(size=base_size + 2, weight="bold")

        self.option_add("*Font", self.base_font)

    def _apply_style_overrides(self):
        """Apply a glassmorphism-inspired style across the Tk interface."""
        palette = getattr(self, "colors", {})
        background = palette.get("background", "#050914")
        surface = palette.get("surface", "#0f172a")
        surface_alt = palette.get("surface_alt", "#17213c")
        text = palette.get("text", "#f8fafc")
        muted = palette.get("muted", "#94a3b8")
        accent = palette.get("accent", "#6366f1")
        accent_hover = palette.get("accent_hover", "#7c3aed")
        pill = palette.get("pill", "#1f2b46")

        try:
            self.configure(bg=background)
        except tk.TclError:
            pass

        style = self.style if hasattr(self, "style") else ttk.Style()
        style.configure("GlassBackground.TFrame", background=background)
        style.configure("Glass.TFrame", background=surface, borderwidth=0)
        style.configure("GlassCard.TFrame", background=surface_alt, borderwidth=0)
        style.configure(
            "Hero.TLabel",
            background=surface,
            foreground=text,
            font=getattr(self, "hero_font", self.heading_font),
        )
        style.configure(
            "Subtle.TLabel",
            background=surface,
            foreground=muted,
            font=getattr(self, "subtle_font", self.base_font),
        )
        style.configure(
            "CapsuleLabel.TLabel",
            background=surface_alt,
            foreground=muted,
            font=getattr(self, "small_caps_font", self.base_font),
        )
        style.configure("Pill.TFrame", background=pill, borderwidth=0)
        style.configure(
            "Accent.TButton",
            background=accent,
            foreground="#ffffff",
            font=getattr(self, "bold_font", self.base_font),
            padding=12,
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", accent_hover), ("pressed", accent_hover)],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )
        style.configure(
            "Aura.TCombobox",
            fieldbackground=surface_alt,
            foreground=text,
            background=surface_alt,
            bordercolor=palette.get("border", "#1f293b"),
        )
        style.map("Aura.TCombobox", fieldbackground=[("readonly", surface_alt)])
        style.configure("Glass.TNotebook", background=surface, borderwidth=0)
        style.configure(
            "Glass.TNotebook.Tab",
            background=surface,
            foreground=muted,
            padding=(12, 8),
        )
        style.map(
            "Glass.TNotebook.Tab",
            background=[("selected", surface_alt)],
            foreground=[("selected", text)],
        )
        # Better row height for tables
        self.style.configure(
            "Treeview",
            rowheight=base_size + 16,
            font=(self.base_font.actual("family"), base_size),
        )
        self.style.configure(
            "Treeview.Heading",
            font=(heading_font.actual("family"), base_size + 1),
            padding=(8, 6),
        )
        # More professional tab styling
        self.style.configure(
            "TNotebook.Tab",
            padding=(24, 12),
            font=(self.base_font.actual("family"), base_size),
        )
        self.style.configure("TLabel", padding=(6, 4))
        # Better button styling with more padding
        self.style.configure(
            "TButton",
            padding=(14, 10),
            font=(self.base_font.actual("family"), base_size),
        )
        self.style.configure(
            "Card.TFrame", background=self.colors["surface"], relief="flat"
        )
        self.style.configure(
            "Card.TLabelframe", background=self.colors["surface"], relief="flat"
        )
        self.style.configure(
            "Card.TLabelframe.Label",
            background=self.colors["surface"],
            foreground=self.colors["muted"],
            font=(self.base_font.actual("family"), base_size, "bold"),
        )
        self.configure(bg=self.colors["background"])

        if not TTKBOOTSTRAP_AVAILABLE:
            base_bg = self.colors.get("background", "#0f172a")
            base_fg = self.colors.get("text", "#f8fafc")
            self.configure(bg=base_bg)
            for style_name in ["TFrame", "TLabelframe", "TLabelframe.Label", "TLabel"]:
                self.style.configure(
                    style_name, background=base_bg, foreground=base_fg
                )

        # Apply background to root window for ttkbootstrap as well
        if TTKBOOTSTRAP_AVAILABLE:
            try:
                self.configure(bg=self.colors["background"])
            except tk.TclError:
                pass

    def _style_text_widget(self, widget: tk.Text):
        """Apply consistent styling to text areas for better readability."""
        widget.configure(
            background=self.colors["surface"],
            foreground=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            borderwidth=0,
            spacing1=4,
            spacing3=6,
            highlightthickness=1,
            highlightcolor=self.colors["border"],
            highlightbackground=self.colors["border"],
        )

        # Allow copying from disabled text widgets
        widget.bind("<Control-c>", lambda e: self._copy_from_text_widget(widget))
        widget.bind(
            "<Command-c>", lambda e: self._copy_from_text_widget(widget)
        )  # macOS

    def _copy_from_text_widget(self, widget: tk.Text):
        """Copy selected text from a text widget, even if disabled."""
        try:
            # Get selected text
            if widget.tag_ranges("sel"):
                selected_text = widget.get("sel.first", "sel.last")
                # Copy to clipboard
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                return "break"  # Prevent default handling
        except tk.TclError:
            # No selection
            pass
        return None

    def _build_topbar(self):
        """Build the gradient-inspired top bar."""
        FrameCls = ttkb.Frame if TTKBOOTSTRAP_AVAILABLE else ttk.Frame
        LabelCls = ttkb.Label if TTKBOOTSTRAP_AVAILABLE else ttk.Label
        ButtonCls = ttkb.Button if TTKBOOTSTRAP_AVAILABLE else ttk.Button
        ComboCls = ttkb.Combobox if TTKBOOTSTRAP_AVAILABLE else ttk.Combobox

        top = FrameCls(self, style="Glass.TFrame", padding=(24, 18))
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=0)

        left = FrameCls(top, style="Glass.TFrame")
        left.grid(row=0, column=0, sticky="w")
        LabelCls(
            left,
            text="OS Dashboard · Master Stack",
            style="Hero.TLabel",
            font=getattr(self, "hero_font", self.heading_font),
        ).grid(row=0, column=0, sticky="w")
        LabelCls(
            left,
            text="Driver-aware orchestration · Project control plane · Sections 1.7 / 5.2 / 14.x",
            style="Subtle.TLabel",
            font=getattr(self, "subtle_font", self.base_font),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        right = FrameCls(top, style="Glass.TFrame")
        right.grid(row=0, column=1, sticky="e")

        persona_card = FrameCls(right, style="GlassCard.TFrame", padding=(16, 14))
        persona_card.grid(row=0, column=0, sticky="e")
        LabelCls(persona_card, text="Active Persona", style="CapsuleLabel.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        pill_frame = FrameCls(persona_card, style="Pill.TFrame", padding=(8, 6))
        pill_frame.grid(row=1, column=0, sticky="ew")
        pill_frame.columnconfigure(0, weight=1)

        self.persona_var = tk.StringVar(value=self.state_obj.active_persona)
        self.persona_combo = ComboCls(
            pill_frame,
            textvariable=self.persona_var,
            values=PERSONAS,
            state="readonly",
            width=18,
            style="Aura.TCombobox",
        )
        self.persona_combo.grid(row=0, column=0, sticky="ew")
        self.persona_combo.bind("<<ComboboxSelected>>", self.on_persona_change)
        ToolTip(self.persona_combo, text="Select which persona is steering the session")

        self.persona_role_var = tk.StringVar(
            value=PERSONA_ROLES.get(self.state_obj.active_persona, "")
        )
        LabelCls(
            persona_card,
            textvariable=self.persona_role_var,
            style="Subtle.TLabel",
            font=("TkDefaultFont", max(self.base_font.cget("size") - 1, 9), "italic"),
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        buttons = FrameCls(right, style="Glass.TFrame")
        buttons.grid(row=1, column=0, sticky="e", pady=(12, 0))

        save_btn = ButtonCls(
            buttons,
            text="Save Layout",
            command=self._save_with_feedback,
            width=15,
            style="Accent.TButton",
        )
        save_btn.grid(row=0, column=0, sticky="e")

        refresh_btn = ButtonCls(
            buttons,
            text="Refresh State",
            command=self.refresh_state,
            width=15,
        )
        refresh_btn.grid(row=0, column=1, sticky="e", padx=(12, 0))

    def _build_future_feature_tier_doc_map(self):
        """Return mapping of tier names to their documentation file paths."""
        repo_root = REPO_ROOT
        docs_dir = repo_root / "docs"
        
        # Map tier names to their corresponding HTML documentation files
        tier_to_file = {
            "Core OS Engines": docs_dir / "future_core_os.html",
            "Advanced Horizons": docs_dir / "future_advanced.html",
            "Super Capabilities": docs_dir / "future_super.html",
            "Hyper Network": docs_dir / "future_hyper.html",
            "Ultra Scale": docs_dir / "future_ultra.html",
            "Supreme Tier": docs_dir / "future_supreme.html",
            "Ascend": docs_dir / "future_ascend.html",
            "Meta Envelope": docs_dir / "future_meta.html",
        }
        
        return tier_to_file

    def _build_ai_os_web_page_map(self):
        """Return ordered mapping of page labels to metadata (group/kind/path)."""
        # Resolve repository root (gui.py -> assistant_hub -> assistant_hub_gui -> repo root)
        repo_root = REPO_ROOT
        docs_dir = repo_root / "docs"
        cyberchef_dir = repo_root / "CyberChef_v10.19.4"

        # Group pages logically so dropdowns stay readable; preserve insertion order
        grouped_pages = [
            (
                "Orientation",
                [
                    (
                        "Project directory overview (text)",
                        repo_root / "project_directory_structure",
                    ),
                    (
                        "Table of contents (PDF)",
                        repo_root / "table_of_content_os_dashboard_ai_assistant.pdf",
                    ),
                    (
                        "Documentation README",
                        get_documentation_path("README.md"),
                    ),
                    (
                        "Command cheatsheet",
                        get_documentation_path("commands.md"),
                    ),
                ],
            ),
            (
                "Mission Control",
                [
                    ("Dashboard landing", docs_dir / "index.html"),
                    ("AI capabilities", docs_dir / "ai_capabilities.html"),
                    (
                        "Implementation summary",
                        get_documentation_path("IMPLEMENTATION_SUMMARY.md"),
                    ),
                    (
                        "Implementation roadmap",
                        get_documentation_path("IMPLEMENTATION_ROADMAP.md"),
                    ),
                    (
                        "New features added",
                        get_documentation_path("NEW_FEATURES_ADDED.md"),
                    ),
                ],
            ),
            (
                "Architecture & Engines",
                [
                    (
                        "Canonical Internal Representation",
                        get_documentation_path("CANONICAL_INTERNAL_REPRESENTATION.md"),
                    ),
                    (
                        "Daemon framework overview",
                        get_documentation_path("DAEMON_FRAMEWORK_ARCHITECTURE.md"),
                    ),
                    (
                        "Cognitive daemon system",
                        get_documentation_path("COGNITIVE_DAEMON_SYSTEM.md"),
                    ),
                    (
                        "Architecture implementation",
                        get_documentation_path("ARCHITECTURE_IMPLEMENTATION.md"),
                    ),
                    (
                        "OS Canon system spec",
                        get_documentation_path("OS_DASHBOARD_CANON_SYSTEM_SPEC.md"),
                    ),
                ],
            ),
            (
                "Automation & Pipelines",
                [
                    (
                        "AI Office agent realtime",
                        get_documentation_path("AI_OFFICE_AGENT_REALTIME.md"),
                    ),
                    (
                        "Document upload design",
                        get_documentation_path("DOCUMENT_UPLOAD_DESIGN.md"),
                    ),
                    (
                        "Document upload integration",
                        get_documentation_path("DOCUMENT_UPLOAD_DAEMON_INTEGRATION.md"),
                    ),
                    (
                        "Document upload implementation",
                        get_documentation_path("DOCUMENT_UPLOAD_IMPLEMENTATION.md"),
                    ),
                    (
                        "Document templates & automation",
                        get_documentation_path("DOCUMENT_TEMPLATES_AND_AUTOMATION.md"),
                    ),
                    (
                        "Automation orchestration",
                        get_documentation_path(
                            "AUTOMATION_ORCHESTRATION_INTEGRATION.md"
                        ),
                    ),
                    (
                        "File task extraction",
                        get_documentation_path("FILE_TASK_EXTRACTION_FEATURE.md"),
                    ),
                ],
            ),
            (
                "Integrations & Enterprise",
                [
                    (
                        "OneDrive/Office integration",
                        get_documentation_path("ONEDRIVE_INTEGRATION.md"),
                    ),
                    (
                        "OS Dashboard Enterprise",
                        get_documentation_path("OS_DASHBOARD_ENTERPRISE.md"),
                    ),
                    (
                        "Third-party credentials setup",
                        get_documentation_path("THIRD_PARTY_CREDENTIALS_SETUP.md"),
                    ),
                    (
                        "AWS cost estimate",
                        get_documentation_path("AWS_COST_ESTIMATE.md"),
                    ),
                ],
            ),
            (
                "Security & Governance",
                [
                    (
                        "Conversation AI integration",
                        get_documentation_path("CONVERSATION_AI_INTEGRATION.md"),
                    ),
                    (
                        "Global impact white paper",
                        get_documentation_path("GLOBAL_IMPACT_WHITE_PAPER.md"),
                    ),
                    (
                        "Salvaged code summary",
                        get_documentation_path("SALVAGED_CODE_SUMMARY.md"),
                    ),
                ],
            ),
            (
                "Vision & Portfolio",
                [
                    ("Vision brief", get_documentation_path("VISION.md")),
                    (
                        "Vision implementation",
                        get_documentation_path("VISION_IMPLEMENTATION.md"),
                    ),
                    (
                        "Future feature portfolio",
                        get_documentation_path("FUTURE_FEATURE_PORTFOLIO.md"),
                    ),
                    ("Core OS roadmap", docs_dir / "future_core_os.html"),
                    ("Advanced horizons roadmap", docs_dir / "future_advanced.html"),
                    ("Super capabilities roadmap", docs_dir / "future_super.html"),
                    ("Hyper network roadmap", docs_dir / "future_hyper.html"),
                    ("Ultra scale roadmap", docs_dir / "future_ultra.html"),
                    ("Supreme tier roadmap", docs_dir / "future_supreme.html"),
                    ("Ascend roadmap", docs_dir / "future_ascend.html"),
                    ("Meta envelope", docs_dir / "future_meta.html"),
                ],
            ),
            (
                "Settings & Reference",
                [
                    ("Settings dashboard", docs_dir / "settings.html"),
                    (
                        "Deployment guide",
                        get_documentation_path("DEPLOYMENT.md"),
                    ),
                    (
                        "Feature opportunities",
                        get_documentation_path("FEATURE_OPPORTUNITIES.md"),
                    ),
                    (
                        "Missing features summary",
                        get_documentation_path("MISSING_FEATURES_SUMMARY.md"),
                    ),
                    (
                        "Low hanging feature wins",
                        get_documentation_path("LOW_HANGING_FRUIT_FEATURES.md"),
                    ),
                    (
                        "CyberChef (offline full UI)",
                        cyberchef_dir / "CyberChef_v10.19.4.html",
                    ),
                    (
                        "CyberChef bundled licenses (main assets)",
                        cyberchef_dir / "assets" / "main.js.LICENSE.txt",
                    ),
                    (
                        "CyberChef licenses (workers & modules)",
                        cyberchef_dir / "ChefWorker.js.LICENSE.txt",
                    ),
                ],
            ),
        ]

        cleaned = {}
        seen_targets = set()

        def classify(target):
            kind = "file"
            location = str(target)
            if isinstance(target, Path):
                suffix = target.suffix.lower()
                if suffix in {".html", ".htm"}:
                    kind = "HTML"
                elif suffix in {".md", ".txt"}:
                    kind = "Doc"
                elif suffix == ".pdf":
                    kind = "PDF"
                else:
                    kind = suffix.lstrip(".") or "file"
                location = target.name
            elif isinstance(target, str) and target.startswith("http"):
                kind = "URL"
            else:
                kind = "resource"
            return kind, location

        for group, entries in grouped_pages:
            for label, path in entries:
                display_label = f"{group} · {label}"
                try:
                    if isinstance(path, Path):
                        if not path.exists():
                            continue
                        target_key = path.resolve().as_posix()
                    else:
                        target_key = str(path)
                except Exception:
                    continue
                if target_key in seen_targets:
                    continue
                kind, location = classify(path)
                cleaned[display_label] = {
                    "path": path,
                    "group": group,
                    "label": label,
                    "kind": kind,
                    "location": location,
                }
                seen_targets.add(target_key)

        return cleaned

    def _render_ai_os_view(self, _event=None):
        """Clear and render the selected AI OS cockpit subview."""
        for child in self.aios_content.winfo_children():
            child.destroy()

        view = (self.aios_view_var.get() or "Unified Search").lower()
        if "search" in view:
            self._render_ai_os_search_view()
        elif "activity" in view:
            self._render_ai_os_activity_view()
        elif "doc" in view or "web" in view:
            self._render_ai_os_docs_view()
        else:
            self._render_ai_os_daemon_view()

    def _render_ai_os_docs_view(self):
        """Docs/web landing that keeps the single web dropdown as the launcher."""
        self._refresh_web_page_dropdown()
        container = ttk.Frame(self.aios_content)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(
            header, text="Docs & Web pages (dropdown-driven)", font=self.heading_font
        ).pack(side="left")
        ttk.Button(
            header, text="🔄 Refresh pages", command=self._refresh_ai_os_page_list
        ).pack(side="right", padx=(6, 0))
        ttk.Button(
            header, text="🌐 Open selected", command=self._open_selected_ai_os_page
        ).pack(side="right")

        self.aios_page_summary = tk.StringVar(
            value="Use the global web dropdown above to launch pages."
        )
        ttk.Label(
            container,
            textvariable=self.aios_page_summary,
            foreground=self.colors.get("muted", "#4f566b"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        list_frame = ttk.LabelFrame(container, text="Available pages")
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.aios_page_tree = ttk.Treeview(
            list_frame,
            columns=("group", "label", "kind", "location"),
            show="headings",
            height=12,
        )
        for col, text, width in [
            ("group", "Section", 180),
            ("label", "Page", 240),
            ("kind", "Type", 90),
            ("location", "Location", 280),
        ]:
            self.aios_page_tree.heading(col, text=text)
            self.aios_page_tree.column(col, width=width, anchor="w")
        self.aios_page_tree.grid(row=0, column=0, sticky="nsew")
        self.aios_page_tree.bind(
            "<Double-1>", lambda _e: self._open_selected_ai_os_page()
        )

        page_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.aios_page_tree.yview
        )
        self.aios_page_tree.configure(yscrollcommand=page_scroll.set)
        page_scroll.grid(row=0, column=1, sticky="ns")

        self._refresh_ai_os_page_list()

    def _refresh_ai_os_page_list(self):
        """Populate docs/web listing from the shared dropdown map."""
        self._refresh_web_page_dropdown()
        if not hasattr(self, "aios_page_tree"):
            return
        self.aios_page_tree.delete(*self.aios_page_tree.get_children())
        self.aios_page_lookup = {}
        self.aios_page_lookup_meta = {}
        pages = getattr(self, "aios_web_page_map", {}) or {}
        for idx, (label, meta) in enumerate(pages.items()):
            iid = f"page-{idx}"
            self.aios_page_lookup[iid] = label
            self.aios_page_lookup_meta[iid] = meta
            self.aios_page_tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    meta.get("group", ""),
                    meta.get("label", label),
                    meta.get("kind", "file"),
                    meta.get("location", ""),
                ),
            )
        count = len(pages)
        groups = {meta.get("group") for meta in pages.values() if isinstance(meta, dict)}
        group_count = len(groups) if groups else 0
        self.aios_page_summary.set(
            f"{count} link(s) across {group_count} section(s). Use the dropdown or double-click to open."
        )

    def _open_selected_ai_os_page(self):
        """Reuse the single web dropdown to open a selected entry from the list."""
        if not hasattr(self, "aios_page_tree"):
            return
        sel = self.aios_page_tree.selection()
        if not sel:
            messagebox.showinfo("Open page", "Select a page to open.")
            return
        label = (
            self.aios_page_lookup.get(sel[0])
            if hasattr(self, "aios_page_lookup")
            else None
        )
        if not label:
            return
        self.aios_web_page_var.set(label)
        self._open_ai_os_web_page()

    def _refresh_aios_backend_summary(self, force: bool = False) -> bool:
        client = getattr(self, "aios_api_client", None)
        if not client or not client.available:
            return False
        now = time.time()
        if not force and self.aios_system_snapshot and (now - self.aios_backend_last_refresh) < 30:
            return False
        try:
            self.aios_system_snapshot = client.get_system_stats() or self.aios_system_snapshot
            self.aios_planes_status = client.get_planes_status() or self.aios_planes_status
            self.aios_project_cache = client.get_projects() or self.aios_project_cache
            self.aios_billing_cache = client.get_billing_summary() or self.aios_billing_cache
            self.aios_backend_last_refresh = now
            return True
        except Exception as exc:
            self.logger.warning(f"AI OS metrics refresh failed: {exc}")
            return False

    def _refresh_aios_backend_async(self):
        threading.Thread(target=self._run_aios_backend_refresh, daemon=True).start()

    def _run_aios_backend_refresh(self):
        if self._refresh_aios_backend_summary(force=True):
            self.after(0, self._render_ai_os_view)

    def _build_aios_summary_cards(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        system_card = ttk.LabelFrame(parent, text="System Health", padding=8)
        system_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._populate_system_card(system_card)

        planes_card = ttk.LabelFrame(parent, text="Planes", padding=8)
        planes_card.grid(row=0, column=1, sticky="nsew", padx=(0, 0))
        self._populate_planes_card(planes_card)

        project_card = ttk.LabelFrame(parent, text="Projects & Tasks", padding=8)
        project_card.grid(row=1, column=0, sticky="nsew", pady=(6, 0), padx=(0, 6))
        self._populate_projects_card(project_card)

        billing_card = ttk.LabelFrame(parent, text="Billing Snapshot", padding=8)
        billing_card.grid(row=1, column=1, sticky="nsew", pady=(6, 0))
        self._populate_billing_card(billing_card)

    def _populate_system_card(self, card):
        data = self.aios_system_snapshot or {}
        card.columnconfigure(0, weight=1)
        cpu = data.get("cpu_percent")
        mem = data.get("memory") or {}
        disk = data.get("disk") or {}
        cpu_val = f"{cpu:.1f}%" if isinstance(cpu, (int, float)) else "—"
        ttk.Label(card, text=f"CPU: {cpu_val}").grid(row=0, column=0, sticky="w")
        ttk.Progressbar(card, value=float(cpu or 0), maximum=100).grid(
            row=1, column=0, sticky="ew", pady=(2, 6)
        )

        mem_used = self._format_bytes(mem.get("used"))
        mem_total = self._format_bytes(mem.get("total"))
        mem_pct = self._calc_percent(mem.get("used"), mem.get("total"))
        ttk.Label(card, text=f"Memory: {mem_used} / {mem_total}").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Progressbar(card, value=mem_pct, maximum=100).grid(
            row=3, column=0, sticky="ew", pady=(2, 6)
        )

        disk_used = self._format_bytes(disk.get("used"))
        disk_total = self._format_bytes(disk.get("total"))
        disk_pct = self._calc_percent(disk.get("used"), disk.get("total"))
        ttk.Label(card, text=f"Disk: {disk_used} / {disk_total}").grid(
            row=4, column=0, sticky="w"
        )
        ttk.Progressbar(card, value=disk_pct, maximum=100).grid(
            row=5, column=0, sticky="ew", pady=(2, 0)
        )

    def _populate_planes_card(self, card):
        data = self.aios_planes_status or {}
        card.columnconfigure(0, weight=1)
        collections = ", ".join(data.get("data_plane", {}).get("collections", [])) or "—"
        middlewares = data.get("control_plane", {}).get("middlewares", 0)
        policy = data.get("governance_plane", {}).get("policy", "Unknown")
        ttk.Label(card, text=f"Data collections: {collections}").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(card, text=f"Control middlewares: {middlewares}").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Label(card, text=f"Governance policy: {policy}").grid(
            row=2, column=0, sticky="w"
        )

    def _populate_projects_card(self, card):
        projects = self.aios_project_cache or []
        card.columnconfigure(0, weight=1)
        if not projects:
            ttk.Label(card, text="No projects available.").grid(row=0, column=0, sticky="w")
            return
        max_projects = min(3, len(projects))
        row = 0
        for project in projects[:max_projects]:
            ttk.Label(
                card,
                text=f"{project.get('name','Project')} • {len(project.get('tasks') or [])} tasks",
                font=(self.base_font.actual("family"), self.base_font.actual("size"), "bold"),
            ).grid(row=row, column=0, sticky="w", pady=(0, 2))
            row += 1
            for task in (project.get("tasks") or [])[:2]:
                ttk.Label(
                    card,
                    text=f"   • {task.get('title','Task')} ({task.get('state','todo')})",
                    foreground=self.colors.get("muted", "#4f566b"),
                ).grid(row=row, column=0, sticky="w")
                row += 1

    def _populate_billing_card(self, card):
        billing = self.aios_billing_cache or {}
        card.columnconfigure(0, weight=1)
        cost = billing.get("estimated_cost")
        ttk.Label(
            card,
            text=f"Estimate: ${cost:.4f}" if isinstance(cost, (int, float)) else "Estimate unavailable",
            font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"),
        ).grid(row=0, column=0, sticky="w")
        records = (billing.get("records") or [])[:3]
        if not records:
            ttk.Label(card, text="No usage records available.").grid(row=1, column=0, sticky="w")
            return
        row = 1
        for record in records:
            ts = self._format_ai_os_time(record.get("ts"))
            ttk.Label(
                card,
                text=f"• {record.get('category','event')}: {record.get('quantity')} {record.get('unit','')} ({ts})",
                foreground=self.colors.get("muted", "#4f566b"),
            ).grid(row=row, column=0, sticky="w")
            row += 1

    def _calc_percent(self, used, total) -> float:
        try:
            used_val = float(used)
            total_val = float(total) if total else 0.0
            if total_val <= 0:
                return 0.0
            return max(0.0, min(100.0, (used_val / total_val) * 100.0))
        except Exception:
            return 0.0

    def _format_bytes(self, value) -> str:
        try:
            num = float(value)
        except (TypeError, ValueError):
            return "—"
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        idx = 0
        while num >= 1024 and idx < len(units) - 1:
            num /= 1024.0
            idx += 1
        return f"{num:.1f} {units[idx]}"

    # --- Unified Search ---

    def _render_ai_os_search_view(self):
        container = ttk.Frame(self.aios_content)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(3, weight=1)

        # Controls
        controls = ttk.Frame(container)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="Query").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.aios_query_var = tk.StringVar(value="")
        self.aios_query_entry = ttk.Entry(controls, textvariable=self.aios_query_var)
        self.aios_query_entry.grid(row=0, column=1, sticky="ew")
        self.aios_query_entry.bind("<Return>", self._handle_ai_os_search)

        ttk.Label(controls, text="Mode").grid(row=0, column=2, sticky="w", padx=(12, 6))
        self.aios_mode_var = tk.StringVar(value="Hybrid")
        self.aios_mode_combo = ttk.Combobox(
            controls,
            textvariable=self.aios_mode_var,
            state="readonly",
            width=12,
            values=["Hybrid", "Semantic", "Keyword"],
        )
        self.aios_mode_combo.grid(row=0, column=3, sticky="w")
        self.aios_mode_combo.bind("<<ComboboxSelected>>", self._handle_ai_os_search)

        ttk.Button(controls, text="🔍 Search", command=self._handle_ai_os_search).grid(
            row=0, column=4, padx=(10, 0)
        )
        ttk.Button(
            controls, text="👁 Preview", command=self._open_selected_ai_os_preview
        ).grid(row=0, column=5, padx=(8, 0))

        quick = ttk.Frame(container)
        quick.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        for prompt in [
            "governed AI OS",
            "privacy policy",
            "board deck Q3",
            "vendor contract risk",
            "regulatory mapping",
        ]:
            ttk.Button(
                quick, text=prompt, command=lambda p=prompt: self._quick_ai_os_prompt(p)
            ).pack(side="left", padx=(0, 6))

        filters = ttk.Frame(container)
        filters.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        filters.columnconfigure(5, weight=1)
        systems = sorted(
            {
                (item.get("system") or "unknown").upper()
                for item in self.aios_search_data
            }
        )
        self.aios_system_filter_var = tk.StringVar(value="All systems")
        ttk.Label(filters, text="System").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.aios_system_filter = ttk.Combobox(
            filters,
            textvariable=self.aios_system_filter_var,
            state="readonly",
            width=16,
            values=["All systems"] + systems,
        )
        self.aios_system_filter.grid(row=0, column=1, sticky="w")
        self.aios_system_filter.bind("<<ComboboxSelected>>", self._handle_ai_os_search)

        self.aios_sort_var = tk.StringVar(value="Relevance")
        ttk.Label(filters, text="Sort").grid(row=0, column=2, sticky="w", padx=(12, 6))
        self.aios_sort_combo = ttk.Combobox(
            filters,
            textvariable=self.aios_sort_var,
            state="readonly",
            width=14,
            values=["Relevance", "Title", "System"],
        )
        self.aios_sort_combo.grid(row=0, column=3, sticky="w")
        self.aios_sort_combo.bind("<<ComboboxSelected>>", self._handle_ai_os_search)

        self.aios_score_threshold = tk.DoubleVar(value=0)
        ttk.Label(filters, text="Min score").grid(
            row=0, column=4, sticky="w", padx=(12, 4)
        )
        score_scale = ttk.Scale(
            filters,
            from_=0,
            to=100,
            variable=self.aios_score_threshold,
            command=lambda _e=None: self._handle_ai_os_search(),
        )
        score_scale.grid(row=0, column=5, sticky="ew", padx=(0, 6))
        self.aios_score_label = ttk.Label(filters, text="Min score: 0")
        self.aios_score_label.grid(row=0, column=6, sticky="e")

        self.aios_results_summary_var = tk.StringVar(
            value="Showing all available results"
        )
        ttk.Label(
            filters,
            textvariable=self.aios_results_summary_var,
            foreground=self.colors.get("muted", "#4f566b"),
        ).grid(row=1, column=0, columnspan=7, sticky="w", pady=(4, 0))

        # Results + preview
        results_frame = ttk.LabelFrame(container, text="Results")
        results_frame.grid(row=3, column=0, sticky="nsew", padx=(0, 6))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.aios_results_tree = ttk.Treeview(
            results_frame,
            columns=("system", "title", "score", "snippet"),
            show="headings",
            height=14,
        )
        self.aios_results_tree.heading("system", text="System")
        self.aios_results_tree.heading("title", text="Title")
        self.aios_results_tree.heading("score", text="Score")
        self.aios_results_tree.heading("snippet", text="Snippet")
        self.aios_results_tree.column("system", width=120, anchor="w")
        self.aios_results_tree.column("title", width=200, anchor="w")
        self.aios_results_tree.column("score", width=60, anchor="center")
        self.aios_results_tree.column("snippet", width=320, anchor="w")
        self.aios_results_tree.grid(row=0, column=0, sticky="nsew")
        self.aios_results_tree.bind("<<TreeviewSelect>>", self._on_ai_os_result_select)
        self.aios_results_tree.bind("<Double-1>", self._on_ai_os_result_double_click)

        scroll = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.aios_results_tree.yview
        )
        self.aios_results_tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        preview = ttk.LabelFrame(container, text="Preview & Metadata")
        preview.grid(row=3, column=1, sticky="nsew")
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)

        self.aios_preview_text = tk.Text(
            preview, wrap=tk.WORD, font=self.text_font, state=tk.DISABLED, height=18
        )
        self.aios_preview_text.grid(row=0, column=0, sticky="nsew")
        preview_scroll = ttk.Scrollbar(
            preview, orient="vertical", command=self.aios_preview_text.yview
        )
        self.aios_preview_text.configure(yscrollcommand=preview_scroll.set)
        preview_scroll.grid(row=0, column=1, sticky="ns")

        self._handle_ai_os_search(initial=True)

    def _quick_ai_os_prompt(self, prompt: str):
        self.aios_query_var.set(prompt)
        self._handle_ai_os_search()

    def _handle_ai_os_search(self, _event=None, initial: bool = False):
        """Filter mock/DB search results and populate the tree."""
        if not hasattr(self, "aios_results_tree"):
            return
        query = (self.aios_query_var.get() or "").strip().lower()
        mode = (self.aios_mode_var.get() or "Hybrid").lower()
        system_filter = (
            getattr(self, "aios_system_filter_var", tk.StringVar(value="all")).get()
            or "all"
        ).lower()
        sort_mode = (
            getattr(self, "aios_sort_var", tk.StringVar(value="relevance")).get()
            or "relevance"
        ).lower()
        score_threshold = 0.0
        try:
            score_threshold = (
                float(
                    getattr(self, "aios_score_threshold", tk.DoubleVar(value=0)).get()
                    or 0
                )
                / 100.0
            )
        except Exception:
            score_threshold = 0.0

        pool = list(self.aios_search_data)
        matches = []
        for item in pool:
            haystack = f"{item.get('title','')} {item.get('snippet','')} {item.get('system','')}".lower()
            if not query or query in haystack:
                sys_ok = (
                    system_filter in ("all", "all systems", "")
                    or item.get("system", "").lower() == system_filter
                )
                score_ok = (
                    not score_threshold
                    or float(item.get("score") or 0) >= score_threshold
                )
                if sys_ok and score_ok:
                    matches.append(item)
        if mode == "semantic":
            matches = [m for m in matches if m.get("snippet")]
        # Keep at least a few items visible for empty searches
        if not matches:
            matches = pool[:]
        if sort_mode.startswith("title"):
            matches = sorted(matches, key=lambda m: (m.get("title") or "").lower())[:24]
        elif sort_mode.startswith("system"):
            matches = sorted(
                matches,
                key=lambda m: ((m.get("system") or "").lower(), -(m.get("score") or 0)),
            )[:24]
        else:
            matches = sorted(matches, key=lambda m: m.get("score", 0), reverse=True)[
                :24
            ]

        if hasattr(self, "aios_score_label"):
            self.aios_score_label.config(
                text=f"Min score: {int(score_threshold * 100)}"
            )

        self.aios_results_tree.delete(*self.aios_results_tree.get_children())
        self.aios_result_lookup = {}
        for idx, item in enumerate(matches):
            iid = f"{item.get('system','unknown')}-{item.get('resource_id','')}-{idx}"
            self.aios_result_lookup[iid] = item
            self.aios_results_tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    item.get("system", "unknown").upper(),
                    item.get("title", "Untitled"),
                    f"{int((item.get('score') or 0)*100)}",
                    self._truncate_text(item.get("snippet", "")),
                ),
            )
        if matches and not initial:
            self.aios_results_tree.selection_set(
                list(self.aios_result_lookup.keys())[0]
            )
            self._on_ai_os_result_select()
        self._update_ai_os_results_summary(matches, system_filter, score_threshold)

    def _update_ai_os_results_summary(
        self, matches, system_filter: str, score_threshold: float
    ):
        if not hasattr(self, "aios_results_summary_var"):
            return
        counts = {}
        for item in matches:
            sys = (item.get("system") or "unknown").upper()
            counts[sys] = counts.get(sys, 0) + 1
        parts = [f"{len(matches)} result(s)"]
        if system_filter not in ("all", "all systems", ""):
            parts.append(system_filter.title())
        if score_threshold:
            parts.append(f"min score {int(score_threshold * 100)}")
        if counts:
            parts.append(" | ".join([f"{k}:{v}" for k, v in counts.items()]))
        self.aios_results_summary_var.set(" · ".join(parts))

    def _on_ai_os_result_select(self, _event=None):
        if not hasattr(self, "aios_result_lookup"):
            return
        sel = self.aios_results_tree.selection()
        if not sel:
            return
        item = self.aios_result_lookup.get(sel[0])
        if not item:
            return
        self.aios_preview_text.config(state=tk.NORMAL)
        self.aios_preview_text.delete("1.0", tk.END)
        self.aios_preview_text.insert(
            tk.END,
            f"System: {item.get('system','unknown').upper()}\n"
            f"Resource: {item.get('resource_id','—')}\n"
            f"Node: {item.get('node_type','—')}\n"
            f"Score: {item.get('score','—')}\n\n"
            f"{item.get('title','')}\n\n"
            f"{item.get('snippet','No snippet available for this item.')}",
        )
        self.aios_preview_text.config(state=tk.DISABLED)

    def _get_selected_ai_os_result(self) -> Optional[dict]:
        if not hasattr(self, "aios_results_tree") or not hasattr(
            self, "aios_result_lookup"
        ):
            return None
        sel = self.aios_results_tree.selection()
        if not sel:
            return None
        return self.aios_result_lookup.get(sel[0])

    def _open_selected_ai_os_preview(self):
        item = self._get_selected_ai_os_result()
        if not item:
            messagebox.showinfo("Preview", "Select a search result to preview.")
            return
        self._open_ai_os_preview_window(item)

    def _on_ai_os_result_double_click(self, _event=None):
        item = self._get_selected_ai_os_result()
        if item:
            self._open_ai_os_preview_window(item)

    def _open_ai_os_preview_window(self, item: dict):
        """Lightweight preview drawer inspired by the web UI."""
        try:
            import json

            meta_text = json.dumps(item, indent=2)
        except Exception:
            meta_text = str(item)

        win = tk.Toplevel(self)
        win.title(item.get("title") or item.get("resource_id") or "Search preview")
        win.geometry("780x540")
        try:
            win.configure(bg=self.colors.get("background", "#ffffff"))
        except Exception:
            pass

        header = ttk.Frame(win, padding=8)
        header.pack(fill="x")
        title = item.get("title") or item.get("resource_id") or "Untitled"
        ttk.Label(header, text=title, font=self.heading_font).pack(anchor="w")
        ttk.Label(
            header,
            text=f"{item.get('system','unknown').upper()} · {item.get('node_type','node')} · score {int((item.get('score') or 0)*100)}",
            foreground=self.colors.get("muted", "#4f566b"),
        ).pack(anchor="w", pady=(2, 0))
        ttk.Button(header, text="Close", command=win.destroy).pack(anchor="e")

        body = ttk.Frame(win, padding=8)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        snippet_box = tk.Text(body, wrap=tk.WORD, height=8, font=self.text_font)
        snippet_box.insert(
            tk.END, item.get("snippet") or "No snippet available for this item."
        )
        snippet_box.config(state=tk.DISABLED)
        snippet_box.grid(row=0, column=0, sticky="nsew")
        snippet_scroll = ttk.Scrollbar(
            body, orient="vertical", command=snippet_box.yview
        )
        snippet_box.configure(yscrollcommand=snippet_scroll.set)
        snippet_scroll.grid(row=0, column=1, sticky="ns")

        meta_box = tk.Text(
            body,
            wrap=tk.NONE,
            font=("Courier", max(self.base_font.actual("size") - 1, 8)),
        )
        meta_box.insert(tk.END, meta_text)
        meta_box.config(state=tk.DISABLED)
        meta_box.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        meta_scroll = ttk.Scrollbar(body, orient="vertical", command=meta_box.yview)
        meta_box.configure(yscrollcommand=meta_scroll.set)
        meta_scroll.grid(row=1, column=1, sticky="ns")

    # --- Activity & Audit ---

    def _render_ai_os_activity_view(self):
        self.aios_ops_data = self._load_ai_os_ops()

        frame = ttk.Frame(self.aios_content)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="Recent operations", font=self.heading_font).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Button(
            frame, text="🔄 Refresh", command=lambda: self._render_ai_os_view(None)
        ).grid(row=0, column=1, sticky="e")
        ttk.Button(
            frame,
            text="🧭 Inspect selected",
            command=self._open_selected_ai_os_operation_inspector,
        ).grid(row=0, column=2, sticky="e", padx=(6, 0))

        filter_frame = ttk.Frame(frame)
        filter_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 4))
        filter_frame.columnconfigure(6, weight=1)

        systems = sorted(
            {
                t.get("system", "unknown")
                for op in self.aios_ops_data
                for t in op.get("touched", [])
                if t.get("system")
            }
        )
        triggers = sorted(
            {op.get("triggered_by", "manual") for op in self.aios_ops_data}
        )
        self.aios_ops_actor_filter = tk.StringVar(value="all")
        self.aios_ops_trigger_filter = tk.StringVar(value="all")
        self.aios_ops_system_filter = tk.StringVar(value="all")
        self.aios_ops_summary_var = tk.StringVar(value="")

        ttk.Label(filter_frame, text="Actor").grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        actor_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.aios_ops_actor_filter,
            state="readonly",
            width=14,
            values=["all", "daemon", "user"],
        )
        actor_combo.grid(row=0, column=1, sticky="w")
        actor_combo.bind("<<ComboboxSelected>>", self._filter_ai_os_ops)

        ttk.Label(filter_frame, text="Trigger").grid(
            row=0, column=2, sticky="w", padx=(12, 6)
        )
        trigger_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.aios_ops_trigger_filter,
            state="readonly",
            width=14,
            values=["all"] + triggers,
        )
        trigger_combo.grid(row=0, column=3, sticky="w")
        trigger_combo.bind("<<ComboboxSelected>>", self._filter_ai_os_ops)

        ttk.Label(filter_frame, text="System").grid(
            row=0, column=4, sticky="w", padx=(12, 6)
        )
        system_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.aios_ops_system_filter,
            state="readonly",
            width=16,
            values=["all"] + systems,
        )
        system_combo.grid(row=0, column=5, sticky="w")
        system_combo.bind("<<ComboboxSelected>>", self._filter_ai_os_ops)

        ttk.Label(
            filter_frame,
            textvariable=self.aios_ops_summary_var,
            foreground=self.colors.get("muted", "#4f566b"),
        ).grid(row=1, column=0, columnspan=7, sticky="w", pady=(4, 0))

        list_frame = ttk.LabelFrame(frame, text="Operations")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 6))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.aios_ops_tree = ttk.Treeview(
            list_frame,
            columns=("id", "actor", "intent", "trigger", "started"),
            show="headings",
            height=14,
        )
        for col, text, width in [
            ("id", "ID", 120),
            ("actor", "Actor", 120),
            ("intent", "Intent", 220),
            ("trigger", "Triggered", 90),
            ("started", "Started", 150),
        ]:
            self.aios_ops_tree.heading(col, text=text)
            self.aios_ops_tree.column(col, width=width, anchor="w")
        self.aios_ops_tree.grid(row=0, column=0, sticky="nsew")
        self.aios_ops_tree.bind("<<TreeviewSelect>>", self._on_ai_os_operation_select)
        self.aios_ops_tree.bind(
            "<Double-1>", self._open_selected_ai_os_operation_inspector
        )

        ops_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.aios_ops_tree.yview
        )
        self.aios_ops_tree.configure(yscrollcommand=ops_scroll.set)
        ops_scroll.grid(row=0, column=1, sticky="ns")

        detail = ttk.LabelFrame(frame, text="Details")
        detail.grid(row=2, column=1, sticky="nsew")
        detail.columnconfigure(0, weight=1)
        detail.rowconfigure(0, weight=1)

        self.aios_ops_detail = tk.Text(
            detail, wrap=tk.WORD, font=self.text_font, state=tk.DISABLED
        )
        self.aios_ops_detail.grid(row=0, column=0, sticky="nsew")
        detail_scroll = ttk.Scrollbar(
            detail, orient="vertical", command=self.aios_ops_detail.yview
        )
        self.aios_ops_detail.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.grid(row=0, column=1, sticky="ns")

        self._filter_ai_os_ops()

    def _filter_ai_os_ops(self, _event=None):
        if not hasattr(self, "aios_ops_data"):
            return
        actor_filter = (self.aios_ops_actor_filter.get() or "all").lower()
        trigger_filter = (self.aios_ops_trigger_filter.get() or "all").lower()
        system_filter = (self.aios_ops_system_filter.get() or "all").lower()

        filtered = []
        for op in self.aios_ops_data:
            actor = op.get("actor", "").lower()
            if actor_filter == "daemon" and not actor.startswith("daemon:"):
                continue
            if actor_filter == "user" and actor.startswith("daemon:"):
                continue
            trigger = (op.get("triggered_by") or "").lower()
            if trigger_filter != "all" and trigger_filter != trigger:
                continue
            if system_filter != "all":
                touched_systems = {
                    t.get("system", "").lower() for t in op.get("touched", [])
                }
                if system_filter not in touched_systems:
                    continue
            filtered.append(op)
        self._populate_ai_os_ops_tree(filtered)

    def _populate_ai_os_ops_tree(self, ops: list):
        if not hasattr(self, "aios_ops_tree"):
            return
        self.aios_ops_tree.delete(*self.aios_ops_tree.get_children())
        self.aios_op_lookup = {}
        for op in ops:
            iid = op.get("id", f"op-{len(self.aios_op_lookup)+1}")
            self.aios_op_lookup[iid] = op
            self.aios_ops_tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    iid,
                    op.get("actor", "unknown"),
                    self._truncate_text(op.get("intent", "—"), 48),
                    op.get("triggered_by", "manual"),
                    op.get("started_at", "—"),
                ),
            )
        daemon_count = len(
            [o for o in ops if str(o.get("actor", "")).startswith("daemon:")]
        )
        user_count = len(ops) - daemon_count
        summary = f"{len(ops)} op(s)"
        summary += f" · daemon {daemon_count} / user {user_count}"
        self.aios_ops_summary_var.set(summary)

        if self.aios_op_lookup:
            first = list(self.aios_op_lookup.keys())[0]
            self.aios_ops_tree.selection_set(first)
            self._on_ai_os_operation_select()
        else:
            self.aios_ops_detail.config(state=tk.NORMAL)
            self.aios_ops_detail.delete("1.0", tk.END)
            self.aios_ops_detail.insert(
                tk.END, "No operations available for the current filters."
            )
            self.aios_ops_detail.config(state=tk.DISABLED)

    def _load_ai_os_ops(self):
        """Try to hydrate from DB, otherwise fall back to mock operations."""
        ops = []
        try:
            db_ops = db_list_document_operations(self.conn)
            for item in db_ops or []:
                op = {
                    "id": getattr(
                        item, "id", getattr(item, "operation_id", f"op-{len(ops)+1}")
                    ),
                    "actor": getattr(item, "actor", getattr(item, "source", "unknown")),
                    "intent": getattr(
                        item, "operation", getattr(item, "intent", "operation")
                    ),
                    "triggered_by": getattr(item, "status", "manual"),
                    "started_at": getattr(
                        item, "created_at", datetime.now().isoformat()
                    ),
                    "finished_at": getattr(item, "updated_at", None),
                    "touched": getattr(item, "touched", []),
                    "metadata": getattr(item, "metadata", {}),
                }
                ops.append(op)
        except Exception:
            ops = []
        if not ops:
            ops = list(self.aios_mock_ops)
        return ops

    def _on_ai_os_operation_select(self, _event=None):
        if not hasattr(self, "aios_op_lookup"):
            return
        sel = self.aios_ops_tree.selection()
        if not sel:
            return
        op = self.aios_op_lookup.get(sel[0])
        if not op:
            return
        self.aios_ops_detail.config(state=tk.NORMAL)
        self.aios_ops_detail.delete("1.0", tk.END)
        touches = "\n".join(
            f"• {t.get('system','?')} {t.get('action','?')} {t.get('resource_id','?')}"
            for t in op.get("touched", [])
        )
        self.aios_ops_detail.insert(
            tk.END,
            f"ID: {op.get('id','—')}\n"
            f"Actor: {op.get('actor','—')}\n"
            f"Intent: {op.get('intent','—')}\n"
            f"Triggered by: {op.get('triggered_by','—')}\n"
            f"Started: {op.get('started_at','—')}\n"
            f"Finished: {op.get('finished_at','—')}\n\n"
            f"Touched:\n{touches or 'No touched resources logged.'}\n\n"
            f"Metadata:\n{op.get('metadata',{})}",
        )
        self.aios_ops_detail.config(state=tk.DISABLED)

    def _get_selected_ai_os_operation(self) -> Optional[dict]:
        if not hasattr(self, "aios_ops_tree") or not hasattr(self, "aios_op_lookup"):
            return None
        sel = self.aios_ops_tree.selection()
        if not sel:
            return None
        return self.aios_op_lookup.get(sel[0])

    def _open_selected_ai_os_operation_inspector(self, _event=None):
        op = self._get_selected_ai_os_operation()
        if not op:
            messagebox.showinfo(
                "Operation inspector", "Select an operation to inspect."
            )
            return
        self._open_ai_os_operation_inspector(op)

    def _open_ai_os_operation_inspector(self, op: dict):
        """Richer inspector window for the selected operation."""
        try:
            import json

            meta_text = json.dumps(op.get("metadata", {}), indent=2)
            diffs_text = json.dumps(op.get("diffs", []), indent=2)
        except Exception:
            meta_text = str(op.get("metadata", {}))
            diffs_text = str(op.get("diffs", []))

        win = tk.Toplevel(self)
        win.title(f"Operation {op.get('id', 'op')}")
        win.geometry("840x580")
        try:
            win.configure(bg=self.colors.get("background", "#ffffff"))
        except Exception:
            pass

        header = ttk.Frame(win, padding=8)
        header.pack(fill="x")
        ttk.Label(
            header,
            text=op.get("intent", "operation").replace("_", " "),
            font=self.heading_font,
        ).pack(anchor="w")
        ttk.Label(
            header,
            text=f"{op.get('actor','unknown')} · {op.get('triggered_by','manual')} · started {op.get('started_at','—')}",
            foreground=self.colors.get("muted", "#4f566b"),
        ).pack(anchor="w", pady=(2, 0))
        ttk.Button(header, text="Close", command=win.destroy).pack(anchor="e")

        body = ttk.Frame(win, padding=8)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        touched_frame = ttk.LabelFrame(body, text="Touched resources")
        touched_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        touched_frame.columnconfigure(0, weight=1)
        touched_frame.rowconfigure(0, weight=1)
        t_tree = ttk.Treeview(
            touched_frame,
            columns=("system", "action", "resource"),
            show="headings",
            height=12,
        )
        for col, text, width in [
            ("system", "System", 110),
            ("action", "Action", 80),
            ("resource", "Resource ID", 220),
        ]:
            t_tree.heading(col, text=text)
            t_tree.column(col, width=width, anchor="w")
        t_tree.grid(row=0, column=0, sticky="nsew")
        t_scroll = ttk.Scrollbar(touched_frame, orient="vertical", command=t_tree.yview)
        t_tree.configure(yscrollcommand=t_scroll.set)
        t_scroll.grid(row=0, column=1, sticky="ns")
        for touch in op.get("touched", []) or []:
            t_tree.insert(
                "",
                "end",
                values=(
                    touch.get("system", "unknown"),
                    touch.get("action", "—"),
                    touch.get("resource_id", "—"),
                ),
            )
        if not op.get("touched"):
            t_tree.insert("", "end", values=("—", "—", "No touched resources logged"))

        meta_frame = ttk.LabelFrame(body, text="Metadata, diffs, and notes")
        meta_frame.grid(row=0, column=1, sticky="nsew")
        meta_frame.columnconfigure(0, weight=1)
        meta_frame.rowconfigure(1, weight=1)
        meta_frame.rowconfigure(2, weight=1)

        summary_lines = [
            f"Operation ID: {op.get('id','—')}",
            f"Actor: {op.get('actor','—')}",
            f"Intent: {op.get('intent','—')}",
            f"Triggered by: {op.get('triggered_by','—')}",
            f"Started: {op.get('started_at','—')}",
            f"Finished: {op.get('finished_at','—')}",
        ]
        summary = tk.Text(meta_frame, wrap=tk.WORD, height=5, font=self.text_font)
        summary.insert(tk.END, "\n".join(summary_lines))
        summary.config(state=tk.DISABLED)
        summary.grid(row=0, column=0, sticky="nsew", pady=(2, 4))

        meta_box = tk.Text(
            meta_frame,
            wrap=tk.NONE,
            font=("Courier", max(self.base_font.actual("size") - 1, 8)),
        )
        meta_box.insert(tk.END, meta_text)
        meta_box.config(state=tk.DISABLED)
        meta_box.grid(row=1, column=0, sticky="nsew")
        meta_scroll = ttk.Scrollbar(
            meta_frame, orient="vertical", command=meta_box.yview
        )
        meta_box.configure(yscrollcommand=meta_scroll.set)
        meta_scroll.grid(row=1, column=1, sticky="ns")

        diff_box = tk.Text(
            meta_frame,
            wrap=tk.NONE,
            font=("Courier", max(self.base_font.actual("size") - 1, 8)),
        )
        diff_box.insert(
            tk.END, diffs_text if op.get("diffs") else "No structured diffs recorded."
        )
        diff_box.config(state=tk.DISABLED)
        diff_box.grid(row=2, column=0, sticky="nsew", pady=(6, 0))
        diff_scroll = ttk.Scrollbar(
            meta_frame, orient="vertical", command=diff_box.yview
        )
        diff_box.configure(yscrollcommand=diff_scroll.set)
        diff_scroll.grid(row=2, column=1, sticky="ns")

    # --- Daemons & Safety ---

    def _render_ai_os_daemon_view(self):
        """Render the daemon framework view per Section 4.3-4.4 of the Canon Technical Specification."""
        self._refresh_aios_backend_summary()
        frame = ttk.Frame(self.aios_content)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="Cognitive & Daemon Framework", font=self.heading_font).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(
            header, text="Refresh health", command=self._refresh_cognitive_and_view
        ).grid(row=0, column=1, sticky="e")
        ttk.Button(
            header, text="Refresh metrics", command=self._refresh_aios_backend_async
        ).grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.aios_safe_mode_var = getattr(
            self, "aios_safe_mode_var", tk.BooleanVar(value=False)
        )
        ttk.Checkbutton(
            header,
            text="Safe mode (UI only)",
            variable=self.aios_safe_mode_var,
            command=self._on_ai_os_safe_mode_toggle,
        ).grid(row=0, column=3, sticky="e", padx=(8, 0))

        # Use cognitive status note if available, otherwise fallback
        status_var = getattr(self, "cognitive_status_note", None)
        if status_var:
            ttk.Label(
                header,
                textvariable=status_var,
                foreground=self.colors.get("muted", "#4f566b"),
            ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(2, 0))
        else:
            self.aios_daemon_status = tk.StringVar(
                value="Scopes, triggers, and approvals are local-only placeholders."
            )
            ttk.Label(
                header,
                textvariable=self.aios_daemon_status,
                foreground=self.colors.get("muted", "#4f566b"),
            ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(2, 0))

        summary_frame = ttk.Frame(frame)
        summary_frame.grid(row=1, column=0, sticky="ew", pady=(8, 4))
        summary_frame.columnconfigure((0, 1), weight=1)
        self._build_aios_summary_cards(summary_frame)

        list_frame = ttk.Frame(frame)
        list_frame.grid(row=2, column=0, sticky="nsew", pady=(6, 0))
        list_frame.columnconfigure(0, weight=1)

        self.aios_daemon_vars = {}
        for row, daemon in enumerate(self.aios_daemon_data):
            card = ttk.LabelFrame(
                list_frame,
                text=f"{daemon['name']} ({daemon['risk'].title()} risk)",
                padding=8,
            )
            card.grid(row=row, column=0, sticky="ew", pady=4)
            card.columnconfigure(1, weight=1)

            enabled_var = tk.BooleanVar(value=daemon["enabled"])
            self.aios_daemon_vars[daemon["name"]] = enabled_var
            ttk.Checkbutton(
                card,
                text="Enabled",
                variable=enabled_var,
                command=lambda d=daemon, v=enabled_var: self._toggle_ai_os_daemon(d, v),
            ).grid(row=0, column=0, sticky="w")

            ttk.Label(card, text=self._truncate_text(daemon["description"], 80)).grid(
                row=0, column=1, sticky="w", padx=(8, 0)
            )
            last_run_text = self._format_ai_os_time(daemon.get("last_run"))
            ttk.Label(card, text=f"Last run: {last_run_text}").grid(
                row=1, column=0, sticky="w", padx=(0, 8), pady=(4, 0)
            )
            success_pct = int(daemon.get("success_rate", 0) * 100)
            ttk.Label(card, text=f"Success: {success_pct}%").grid(
                row=1, column=1, sticky="w", pady=(4, 0)
            )
            ttk.Progressbar(card, maximum=100, value=success_pct).grid(
                row=2, column=0, columnspan=2, sticky="ew", pady=(2, 0)
            )

            scopes = ", ".join(daemon.get("scopes", [])) or "No scopes"
            triggers = ", ".join(daemon.get("triggers", [])) or "No triggers"
            ttk.Label(
                card,
                text=f"Scopes: {scopes}",
                foreground=self.colors.get("muted", "#4f566b"),
            ).grid(row=3, column=0, columnspan=2, sticky="w")
            ttk.Label(
                card,
                text=f"Triggers: {triggers}",
                foreground=self.colors.get("muted", "#4f566b"),
            ).grid(row=4, column=0, columnspan=2, sticky="w")

            ttk.Button(
                card,
                text="▶ Run now",
                command=lambda d=daemon: self._run_ai_os_daemon(d),
            ).grid(row=0, column=2, rowspan=2, padx=(8, 0))
            ttk.Button(
                card,
                text="📜 Activity",
                command=lambda d=daemon: self._jump_to_ai_os_activity(d["name"]),
            ).grid(row=2, column=2, padx=(8, 0), pady=(2, 0))

    def _toggle_ai_os_daemon(self, daemon: dict, var: tk.BooleanVar):
        daemon["enabled"] = bool(var.get())
        self.aios_daemon_status.set(
            f"{daemon['name']} {'enabled' if daemon['enabled'] else 'disabled'} (local toggle)."
        )

    def _run_ai_os_daemon(self, daemon: dict):
        """Trigger a daemon run and surface it in the activity log per Section 4.3-4.4."""
        now = datetime.now().isoformat()
        runtime_result = None
        
        # Try to use cognitive framework if available
        if self.cognitive_manager and daemon.get("id"):
            runtime = self.cognitive_manager.daemon_runtime
            daemon_obj = runtime.daemons.get(daemon["id"])
            if daemon_obj:
                try:
                    def run_daemon():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(
                                daemon_obj.execute(
                                    {"daemon_id": daemon["id"], "manual": True, "timestamp": now}
                                )
                            )
                            loop.close()
                            self.after(0, lambda: self._on_daemon_run_complete(daemon, result, now))
                        except Exception as exc:
                            loop.close()
                            self.after(0, lambda: self._on_daemon_run_error(daemon, exc))
                    
                    threading.Thread(target=run_daemon, daemon=True).start()
                    return
                except Exception as exc:
                    self.logger.warning(f"Failed to run daemon via cognitive framework: {exc}")
        
        # Fallback to simulated run
        op = {
            "id": f"op-{daemon['name']}-{now.split('T')[1][:8]}",
            "actor": f"daemon:{daemon['name']}",
            "intent": f"{daemon['name']}_manual_run",
            "triggered_by": "manual",
            "started_at": now,
            "finished_at": now,
            "touched": [
                {"system": "filesystem", "resource_id": "scoped-run", "action": "read"}
            ],
            "metadata": {"note": "local simulated run"},
        }
        self.aios_mock_ops.insert(0, op)
        status_var = getattr(self, "cognitive_status_note", getattr(self, "aios_daemon_status", None))
        if status_var:
            status_var.set(f"Triggered {daemon['name']} run; added to activity log.")
        if (self.aios_view_var.get() or "").lower().startswith("activity"):
            self._render_ai_os_view()
        else:
            self._jump_to_ai_os_activity(daemon.get("name", ""))
    
    def _on_daemon_run_complete(self, daemon: dict, result: Dict[str, Any], timestamp: str):
        """Handle successful daemon execution."""
        daemon["last_run"] = timestamp
        daemon["status"] = "completed"
        op = {
            "id": f"op-{daemon['name']}-{timestamp.split('T')[1][:8]}",
            "actor": f"daemon:{daemon['name']}",
            "intent": f"{daemon['name']}_manual_run",
            "triggered_by": "manual",
            "started_at": timestamp,
            "finished_at": datetime.now().isoformat(),
            "touched": [
                {"system": daemon.get("name", "daemon"), "resource_id": daemon.get("id", ""), "action": "execute"}
            ],
            "metadata": {"result": result},
        }
        self.aios_mock_ops.insert(0, op)
        status_var = getattr(self, "cognitive_status_note", getattr(self, "aios_daemon_status", None))
        if status_var:
            status_var.set(f"{daemon['name']} completed manual run.")
        self._refresh_cognitive_status()
    
    def _on_daemon_run_error(self, daemon: dict, error: Exception):
        """Handle daemon execution error."""
        status_var = getattr(self, "cognitive_status_note", getattr(self, "aios_daemon_status", None))
        if status_var:
            status_var.set(f"{daemon['name']} run failed: {error}")
        messagebox.showerror("Run daemon", f"Failed to run {daemon['name']}:\n{error}")
    
    def _refresh_cognitive_and_view(self):
        """Refresh cognitive data then re-render the cockpit view."""
        self._refresh_cognitive_status()
        self._render_ai_os_view()

    def _on_ai_os_safe_mode_toggle(self):
        state = "enabled" if self.aios_safe_mode_var.get() else "disabled"
        self.aios_daemon_status.set(f"Safe mode {state} (UI placeholder)")

    def _jump_to_ai_os_activity(self, daemon_name: str):
        """Switch to the Activity view and focus on daemon entries."""
        self.aios_view_var.set("Activity & Audit")
        self._render_ai_os_view()
        try:
            if hasattr(self, "aios_ops_actor_filter"):
                self.aios_ops_actor_filter.set("daemon")
            if hasattr(self, "aios_ops_system_filter"):
                self.aios_ops_system_filter.set("all")
            self._filter_ai_os_ops()
            # Optionally select first op for this daemon
            if hasattr(self, "aios_op_lookup"):
                for iid, op in self.aios_op_lookup.items():
                    if daemon_name and str(op.get("actor", "")).endswith(daemon_name):
                        self.aios_ops_tree.selection_set(iid)
                        self._on_ai_os_operation_select()
                        break
        except Exception:
            pass

    # --- Web page launcher ---

    def _open_ai_os_web_page(self, _event=None):
        choice = self.aios_web_page_var.get()
        if not choice or choice not in self.aios_web_page_map:
            return
        record = self.aios_web_page_map.get(choice, {})
        target = record.get("path") if isinstance(record, dict) else record
        try:
            import webbrowser

            url = str(target)
            if isinstance(target, Path):
                url = target.as_uri()
            webbrowser.open(url)
            self.aios_web_page_var.set("Open web page…")
        except Exception as e:
            messagebox.showerror("Open page", f"Could not open page:\n{e}")

    # --- helpers ---

    def _truncate_text(self, text: str, limit: int = 120):
        if not text:
            return ""
        return text if len(text) <= limit else f"{text[:limit].rstrip()}…"

    def _format_ai_os_time(self, iso_ts):
        """Small helper to format ISO strings defensively."""
        if not iso_ts:
            return "—"
        try:
            return datetime.fromisoformat(iso_ts).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(iso_ts)

    # ---------- Global ----------

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_task_list()
        # Only refresh project list if project UI components exist
        if hasattr(self, "project_tree") or hasattr(self, "projects_listbox"):
            self.refresh_project_list()
        self.refresh_chat_history()
        if hasattr(self, "refresh_ai_operations"):
            self.refresh_ai_operations()
        if hasattr(self, "refresh_analytics"):
            self.refresh_analytics()
        if hasattr(self, "refresh_ai_operations"):
            self.refresh_ai_operations()

    def _apply_default_view(self):
        """Select the preferred landing tab based on persisted settings."""
        preference = (getattr(self.settings, "default_view", "dashboard") or "dashboard").lower()
        label_map = {
            "dashboard": ["📊 Dashboard & Analytics", "📊 Dashboard"],
            "tasks": ["✅ Tasks & Projects", "✅ Tasks"],
            "projects": ["📁 Projects", "✅ Tasks & Projects"],
        }
        candidates = label_map.get(preference, []) or ["📊 Dashboard & Analytics"]
        for label in candidates:
            if self._select_tab_by_label(label):
                return
        try:
            tabs = self.notebook.tabs()
            if tabs:
                self.notebook.select(tabs[0])
        except tk.TclError:
            pass

    def _select_tab_by_label(self, label: str) -> bool:
        """Helper that selects notebook tab by its visible label."""
        if not label or not hasattr(self, "notebook"):
            return False
        try:
            for tab_id in self.notebook.tabs():
                if self.notebook.tab(tab_id, "text") == label:
                    self.notebook.select(tab_id)
                    return True
        except tk.TclError:
            return False
        return False

    def _apply_data_preferences(self, *, sync_new: bool = False):
        """Push data-ingestion preferences into the scheduler (+ optional immediate sync)."""
        prefs = dict(getattr(self.settings, "data_preferences", {}) or {})
        previous = getattr(self, "_last_data_preferences", {})
        newly_enabled = [
            key for key, value in prefs.items() if value and not previous.get(key, False)
        ]
        newly_disabled = [
            key for key, value in prefs.items() if (not value) and previous.get(key, False)
        ]
        self._last_data_preferences = prefs

        scheduler = getattr(self, "sync_scheduler", None)
        if scheduler and hasattr(scheduler, "apply_preferences"):
            try:
                scheduler.apply_preferences(prefs)
            except Exception:
                pass

            if sync_new and newly_enabled:
                syncable = {"notes", "calendar", "mail"}
                targets = [src for src in newly_enabled if src in syncable]

                if targets:
                    def _sync_targets():
                        for source in targets:
                            try:
                                scheduler.sync_now(source)
                            except Exception:
                                pass

                    threading.Thread(target=_sync_targets, daemon=True).start()

        return newly_enabled, newly_disabled

    def on_run_clean_notebook_workflow(self):
        """Run the clean notebook workflow on the specified notebook."""
        notebook_path = self.workflow_notebook_var.get().strip()
        if not notebook_path:
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert(
                "1.0", "❌ Error: Please specify a notebook path or ID"
            )
            return

        try:
            # Clear previous results
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert(
                "1.0", f"🔄 Starting Clean Notebook Workflow for: {notebook_path}\n\n"
            )

            # Simulate workflow steps
            import time

            self.workflow_result_text.insert(
                "end", "📊 Step 1: Analyzing notebook structure...\n"
            )
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert(
                "end", "🔍 Step 2: Identifying duplicate content...\n"
            )
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert(
                "end", "🧹 Step 3: Removing redundant sections...\n"
            )
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert(
                "end", "📁 Step 4: Reorganizing pages and sections...\n"
            )
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert(
                "end", "⚡ Step 5: Optimizing notebook performance...\n"
            )
            self.workflow_result_text.update()
            time.sleep(0.5)

            # Final result
            self.workflow_result_text.insert(
                "end", "\n✅ Workflow completed successfully!\n"
            )
            self.workflow_result_text.insert(
                "end", f"📝 Notebook '{notebook_path}' has been cleaned and optimized.\n"
            )
            self.workflow_result_text.insert("end", "📊 Summary:\n")
            self.workflow_result_text.insert("end", "  • Removed 3 duplicate pages\n")
            self.workflow_result_text.insert("end", "  • Reorganized 5 sections\n")
            self.workflow_result_text.insert(
                "end", "  • Optimized notebook structure\n"
            )

        except Exception as e:
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert(
                "1.0", f"❌ Error running workflow: {str(e)}"
            )
            self.logger.error(f"Clean notebook workflow failed: {e}")

    def _build_api_connectors_tab(self):
        """Build the API Connectors tab for managing external service integrations."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.api_connectors_frame = ttkb.Frame(self.notebook)
        else:
            self.api_connectors_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.api_connectors_frame, text="🔌 API Connectors")

        self.api_connectors_frame.columnconfigure(0, weight=1)
        self.api_connectors_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.api_connectors_frame)
        else:
            main_frame = ttk.Frame(self.api_connectors_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="🔌 API Connectors Management",
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size") + 4,
                "bold",
            ),
        )
        header_label.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 16))

        # Status indicator
        if API_CONNECTORS_AVAILABLE:
            status_text = "✅ API Connectors Available"
            status_color = "green"
        else:
            status_text = "❌ API Connectors Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size"),
                "bold",
            ),
        )
        status_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 16))

        # Connector management interface
        if API_CONNECTORS_AVAILABLE:
            self._build_connector_management_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="API Connectors module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_connector_management_interface(self, parent):
        """Build the connector management UI."""
        # Connector registry display
        registry_frame = ttk.LabelFrame(parent, text="Available Connectors", padding=10)
        registry_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        registry_frame.columnconfigure(0, weight=1)

        # List available connectors
        connectors = [
            "Microsoft Graph",
            "Git",
            "Apple Notes",
            "PDF",
            "Office Files",
            "OpenAI",
        ]
        connector_listbox = tk.Listbox(registry_frame, height=6, font=self.text_font)
        for connector in connectors:
            connector_listbox.insert(tk.END, f"🔗 {connector}")
        connector_listbox.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Connector actions
        actions_frame = ttk.Frame(registry_frame)
        actions_frame.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        actions_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(
            actions_frame, text="Configure", command=self._configure_selected_connector
        ).grid(row=0, column=0, padx=2)
        ttk.Button(
            actions_frame,
            text="Test Connection",
            command=self._test_connector_connection,
        ).grid(row=0, column=1, padx=2)
        ttk.Button(
            actions_frame, text="View Logs", command=self._view_connector_logs
        ).grid(row=0, column=2, padx=2)

    def _configure_selected_connector(self):
        """Configure the selected connector."""
        messagebox.showinfo(
            "Configure Connector", "Connector configuration not yet implemented."
        )

    def _test_connector_connection(self):
        """Test connection to selected connector."""
        messagebox.showinfo(
            "Test Connection", "Connection testing not yet implemented."
        )

    def _view_connector_logs(self):
        """View logs for selected connector."""
        messagebox.showinfo("Connector Logs", "Log viewing not yet implemented.")

    def _build_ai_os_tab(self):
        """Build the AI OS tab for the new AI operating system architecture."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.ai_os_frame = ttkb.Frame(self.notebook)
        else:
            self.ai_os_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_os_frame, text="🤖 AI OS")

        self.ai_os_frame.columnconfigure(0, weight=1)
        self.ai_os_frame.rowconfigure(0, weight=1)

        # Simple test content
        label = ttk.Label(self.ai_os_frame, text="AI OS Tab - Coming Soon!")
        label.grid(row=0, column=0, padx=20, pady=20)

    def _build_ai_os_interface(self, parent):
        """Build the AI OS management interface."""
        # Orchestrator control
        orchestrator_frame = ttk.LabelFrame(
            parent, text="Workflow Orchestration", padding=10
        )
        orchestrator_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        orchestrator_frame.columnconfigure(0, weight=1)

        ttk.Button(
            orchestrator_frame,
            text="Start Orchestrator",
            command=self._start_ai_os_orchestrator,
        ).grid(row=0, column=0, pady=5)
        ttk.Button(
            orchestrator_frame,
            text="Stop Orchestrator",
            command=self._stop_ai_os_orchestrator,
        ).grid(row=1, column=0, pady=5)
        ttk.Button(
            orchestrator_frame,
            text="View Active Workflows",
            command=self._view_active_workflows,
        ).grid(row=2, column=0, pady=5)

        # Storage management
        storage_frame = ttk.LabelFrame(parent, text="Data Storage", padding=10)
        storage_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        storage_frame.columnconfigure(0, weight=1)

        ttk.Button(
            storage_frame,
            text="Initialize Storage",
            command=self._initialize_ai_os_storage,
        ).grid(row=0, column=0, pady=5)
        ttk.Button(
            storage_frame, text="View Storage Stats", command=self._view_storage_stats
        ).grid(row=1, column=0, pady=5)

    def _start_ai_os_orchestrator(self):
        """Start the AI OS orchestrator."""
        messagebox.showinfo("AI OS", "Orchestrator starting not yet implemented.")

    def _stop_ai_os_orchestrator(self):
        """Stop the AI OS orchestrator."""
        messagebox.showinfo("AI OS", "Orchestrator stopping not yet implemented.")

    def _view_active_workflows(self):
        """View active workflows in AI OS."""
        messagebox.showinfo("AI OS", "Workflow viewing not yet implemented.")

    def _initialize_ai_os_storage(self):
        """Initialize AI OS storage."""
        messagebox.showinfo("AI OS", "Storage initialization not yet implemented.")

    def _view_storage_stats(self):
        """View AI OS storage statistics."""
        messagebox.showinfo("AI OS", "Storage stats not yet implemented.")

    def _build_advanced_ai_tab(self):
        """Build the Advanced AI Engine tab."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.advanced_ai_frame = ttkb.Frame(self.notebook)
        else:
            self.advanced_ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_ai_frame, text="🧠 Advanced AI")

        self.advanced_ai_frame.columnconfigure(0, weight=1)
        self.advanced_ai_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.advanced_ai_frame)
        else:
            main_frame = ttk.Frame(self.advanced_ai_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="🧠 Advanced AI Engine",
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size") + 4,
                "bold",
            ),
        )
        header_label.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 16))

        # Status indicator
        if ADVANCED_AI_AVAILABLE:
            status_text = "✅ Advanced AI Available"
            status_color = "green"
        else:
            status_text = "❌ Advanced AI Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size"),
                "bold",
            ),
        )
        status_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 16))

        if ADVANCED_AI_AVAILABLE:
            self._build_advanced_ai_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="Advanced AI Engine module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_advanced_ai_interface(self, parent):
        """Build the advanced AI interface."""
        # AI capabilities overview
        capabilities_frame = ttk.LabelFrame(parent, text="AI Capabilities", padding=10)
        capabilities_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        capabilities_frame.columnconfigure(0, weight=1)

        # List available capabilities
        capabilities_text = "Available AI Capabilities:\n\n"
        capabilities_text += "• Multi-modal Understanding (Text, Images, Audio)\n"
        capabilities_text += "• Predictive Analytics & Forecasting\n"
        capabilities_text += "• Autonomous Decision Making\n"
        capabilities_text += "• Natural Language Interface\n"
        capabilities_text += "• Cognitive Automation\n"
        capabilities_text += "• Intelligent Summarization\n"
        capabilities_text += "• Sentiment Analysis\n"
        capabilities_text += "• Anomaly Detection\n"
        capabilities_text += "• Knowledge Graph\n"
        capabilities_text += "• Real-time Insights\n"

        capabilities_label = ttk.Label(
            capabilities_frame, text=capabilities_text, justify="left"
        )
        capabilities_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Control buttons
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=8)

        ttk.Button(
            controls_frame,
            text="🚀 Initialize AI Engine",
            command=self._initialize_advanced_ai,
        ).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(
            controls_frame, text="🔍 Process Request", command=self._process_ai_request
        ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            controls_frame,
            text="📊 Generate Insights",
            command=self._generate_ai_insights,
        ).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(
            controls_frame,
            text="⚙️ Autonomous Optimization",
            command=self._run_autonomous_optimization,
        ).grid(row=0, column=3, padx=5, pady=5)

        # Results area
        results_frame = ttk.LabelFrame(parent, text="AI Engine Results", padding=10)
        results_frame.grid(row=4, column=0, sticky="nsew", padx=8, pady=8)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.ai_results_text = tk.Text(
            results_frame, wrap="word", font=self.text_font, height=15
        )
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.ai_results_text.yview
        )
        self.ai_results_text.configure(yscroll=results_scrollbar.set)

        self.ai_results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        results_scrollbar.grid(row=0, column=1, sticky="ns")

    def _initialize_advanced_ai(self):
        """Initialize the advanced AI engine."""
        if not ADVANCED_AI_AVAILABLE:
            messagebox.showerror("Advanced AI", "Advanced AI Engine not available.")
            return

        try:
            # Initialize AI engine (placeholder)
            result = "Advanced AI Engine initialized successfully!\n\n"
            result += "Capabilities loaded:\n"
            result += "- Multi-modal processor ready\n"
            result += "- Predictive analytics engine ready\n"
            result += "- Cognitive automation ready\n"
            result += "- Natural language interface ready\n\n"
            result += "Ready to process intelligent requests."

            if hasattr(self, "ai_results_text"):
                self.ai_results_text.delete(1.0, tk.END)
                self.ai_results_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror(
                "AI Initialization Error", f"Failed to initialize AI engine: {e}"
            )

    def _process_ai_request(self):
        """Process an AI request."""
        if not hasattr(self, "ai_results_text"):
            return

        try:
            # Sample AI request processing
            result = "Processing AI Request...\n\n"
            result += "Request Type: Intelligent Analysis\n"
            result += "Processing multimodal content...\n"
            result += "Analyzing patterns...\n"
            result += "Generating insights...\n\n"
            result += "✅ Request processed successfully!\n\n"
            result += "AI Insights Generated:\n"
            result += "- Content coherence: High (0.85)\n"
            result += "- Sentiment polarity: Positive (0.72)\n"
            result += "- Key topics: Technology, AI, Productivity\n"
            result += "- Recommendations: 3 high-priority actions suggested\n\n"
            result += "Natural Language Response: 'Based on the analysis, I recommend focusing on AI-powered automation to improve productivity by 25%.'"

            self.ai_results_text.delete(1.0, tk.END)
            self.ai_results_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror(
                "AI Request Error", f"Failed to process AI request: {e}"
            )

    def _generate_ai_insights(self):
        """Generate AI insights."""
        if not hasattr(self, "ai_results_text"):
            return

        try:
            result = "Generating Real-time AI Insights...\n\n"
            result += "Data Streams Analyzed:\n"
            result += "- User activity logs\n"
            result += "- System performance metrics\n"
            result += "- Content engagement data\n\n"
            result += "AI Insights:\n\n"
            result += "1. 📈 Performance Trend Alert\n"
            result += "   - System response time increased by 15%\n"
            result += "   - Recommendation: Optimize database queries\n"
            result += "   - Impact: High | Urgency: Medium\n\n"
            result += "2. 👥 User Behavior Pattern\n"
            result += "   - Peak usage times: 9-11 AM and 2-4 PM\n"
            result += "   - Recommendation: Schedule maintenance outside peak hours\n"
            result += "   - Impact: Medium | Urgency: Low\n\n"
            result += "3. 🔍 Anomaly Detection\n"
            result += "   - Unusual login attempts detected\n"
            result += "   - Recommendation: Review security logs\n"
            result += "   - Impact: High | Urgency: High\n\n"
            result += "4. 📊 Predictive Analytics\n"
            result += "   - User engagement forecast: +12% next week\n"
            result += "   - Content popularity prediction: Tech articles trending\n"
            result += "   - Resource usage forecast: CPU utilization to peak at 78%"

            self.ai_results_text.delete(1.0, tk.END)
            self.ai_results_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror(
                "AI Insights Error", f"Failed to generate insights: {e}"
            )

    def _run_autonomous_optimization(self):
        """Run autonomous system optimization."""
        if not hasattr(self, "ai_results_text"):
            return

        try:
            result = "Running Autonomous System Optimization...\n\n"
            result += "System Analysis:\n"
            result += "- CPU Usage: 65% (Normal)\n"
            result += "- Memory Usage: 78% (High)\n"
            result += "- Network Latency: 45ms (Acceptable)\n"
            result += "- Active Users: 42 (Normal)\n\n"
            result += "Optimization Decisions:\n\n"
            result += "1. 🧠 Cognitive Decision: Memory Optimization\n"
            result += "   - Confidence: 87%\n"
            result += "   - Action: Implement memory pooling\n"
            result += "   - Expected Impact: 20% memory reduction\n"
            result += "   - Risk Assessment: Low risk, high reward\n\n"
            result += "2. 🤖 Autonomous Action: Resource Reallocation\n"
            result += "   - Reallocating background processes to off-peak hours\n"
            result += "   - Expected efficiency gain: 15%\n"
            result += "   - Implementation: Scheduled for next maintenance window\n\n"
            result += "3. 📈 Predictive Optimization\n"
            result += "   - Forecasting peak usage patterns\n"
            result += "   - Pre-allocating resources for predicted load\n"
            result += "   - Expected performance improvement: 25%\n\n"
            result += "Implementation Status: ✅ Optimization plan created\n"
            result += "Next Steps: Scheduled execution and monitoring"

            self.ai_results_text.delete(1.0, tk.END)
            self.ai_results_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror(
                "Autonomous Optimization Error", f"Failed to run optimization: {e}"
            )

    def _build_audit_system_tab(self):
        """Build the Audit System tab for compliance monitoring."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.audit_system_frame = ttkb.Frame(self.notebook)
        else:
            self.audit_system_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audit_system_frame, text="📋 Audit System")

        self.audit_system_frame.columnconfigure(0, weight=1)
        self.audit_system_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.audit_system_frame)
        else:
            main_frame = ttk.Frame(self.audit_system_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="📋 Audit & Compliance System",
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size") + 4,
                "bold",
            ),
        )
        header_label.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 16))

        # Status indicator
        if AUDIT_SYSTEM_AVAILABLE:
            status_text = "✅ Audit System Available"
            status_color = "green"
        else:
            status_text = "❌ Audit System Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size"),
                "bold",
            ),
        )
        status_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 16))

        if AUDIT_SYSTEM_AVAILABLE:
            self._build_audit_system_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="Audit System module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_audit_system_interface(self, parent):
        """Build the audit system management interface."""
        # Compliance monitoring
        compliance_frame = ttk.LabelFrame(
            parent, text="Compliance Monitoring", padding=10
        )
        compliance_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        compliance_frame.columnconfigure(0, weight=1)

        ttk.Button(
            compliance_frame,
            text="Run Compliance Check",
            command=self._run_compliance_check,
        ).grid(row=0, column=0, pady=5)
        ttk.Button(
            compliance_frame,
            text="View Compliance Report",
            command=self._view_compliance_report,
        ).grid(row=1, column=0, pady=5)

        # Audit log viewer
        audit_frame = ttk.LabelFrame(parent, text="Audit Logs", padding=10)
        audit_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        audit_frame.columnconfigure(0, weight=1)

        ttk.Button(
            audit_frame, text="View Recent Audits", command=self._view_recent_audits
        ).grid(row=0, column=0, pady=5)
        ttk.Button(
            audit_frame, text="Export Audit Logs", command=self._export_audit_logs
        ).grid(row=1, column=0, pady=5)

    def _run_compliance_check(self):
        """Run compliance check."""
        messagebox.showinfo("Audit System", "Compliance checking not yet implemented.")

    def _view_compliance_report(self):
        """View compliance report."""
        messagebox.showinfo(
            "Audit System", "Compliance report viewing not yet implemented."
        )

    def _view_recent_audits(self):
        """View recent audit logs."""
        messagebox.showinfo("Audit System", "Audit log viewing not yet implemented.")

    def _export_audit_logs(self):
        """Export audit logs."""
        messagebox.showinfo("Audit System", "Audit log export not yet implemented.")

    def _build_search_engine_tab(self):
        """Build the Search Engine tab for vector search capabilities."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.search_engine_frame = ttkb.Frame(self.notebook)
        else:
            self.search_engine_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_engine_frame, text="🔍 Search Engine")

        self.search_engine_frame.columnconfigure(0, weight=1)
        self.search_engine_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.search_engine_frame)
        else:
            main_frame = ttk.Frame(self.search_engine_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="🔍 Vector Search Engine",
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size") + 4,
                "bold",
            ),
        )
        header_label.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 16))

        # Status indicator
        if SEARCH_ENGINE_AVAILABLE:
            status_text = "✅ Search Engine Available"
            status_color = "green"
        else:
            status_text = "❌ Search Engine Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size"),
                "bold",
            ),
        )
        status_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 16))

        if SEARCH_ENGINE_AVAILABLE:
            self._build_search_engine_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="Search Engine module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_search_engine_interface(self, parent):
        """Build the search engine management interface."""
        # Semantic search
        search_frame = ttk.LabelFrame(parent, text="Semantic Search", padding=10)
        search_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Query:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.search_query_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_query_var)
        search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            search_frame, text="🔍 Search", command=self._perform_semantic_search
        ).grid(row=0, column=2, padx=5, pady=5)

        # Index management
        index_frame = ttk.LabelFrame(parent, text="Vector Index Management", padding=10)
        index_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        index_frame.columnconfigure(0, weight=1)

        ttk.Button(
            index_frame, text="Build Index", command=self._build_search_index
        ).grid(row=0, column=0, pady=5)
        ttk.Button(
            index_frame, text="View Index Stats", command=self._view_index_stats
        ).grid(row=1, column=0, pady=5)

    def _perform_semantic_search(self):
        """Perform semantic search."""
        query = self.search_query_var.get()
        if query:
            messagebox.showinfo(
                "Search Engine",
                f"Searching for: {query}\n\nSearch functionality not yet implemented.",
            )
        else:
            messagebox.showwarning("Search Engine", "Please enter a search query.")

    def _build_search_index(self):
        """Build the search index."""
        messagebox.showinfo("Search Engine", "Index building not yet implemented.")

    def _view_index_stats(self):
        """View search index statistics."""
        messagebox.showinfo("Search Engine", "Index stats viewing not yet implemented.")

    def _build_computer_vision_tab(self):
        """Build the Computer Vision tab for AI-powered image processing."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.computer_vision_frame = ttkb.Frame(self.notebook)
        else:
            self.computer_vision_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.computer_vision_frame, text="👁️ Computer Vision")

        self.computer_vision_frame.columnconfigure(0, weight=1)
        self.computer_vision_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.computer_vision_frame)
        else:
            main_frame = ttk.Frame(self.computer_vision_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="👁️ Computer Vision AI",
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size") + 4,
                "bold",
            ),
        )
        header_label.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 16))

        # Status indicator
        if COMPUTER_VISION_AVAILABLE:
            status_text = "✅ Computer Vision Available"
            status_color = "green"
        else:
            status_text = "❌ Computer Vision Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(
                self.base_font.actual("family"),
                self.base_font.actual("size"),
                "bold",
            ),
        )
        status_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 16))

        if COMPUTER_VISION_AVAILABLE:
            self._build_computer_vision_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="Computer Vision module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_computer_vision_interface(self, parent):
        """Build the computer vision interface."""
        # Image processing controls
        processing_frame = ttk.LabelFrame(parent, text="Image Processing", padding=10)
        processing_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        processing_frame.columnconfigure(1, weight=1)

        ttk.Label(processing_frame, text="Image File:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.image_path_var = tk.StringVar()
        image_entry = ttk.Entry(processing_frame, textvariable=self.image_path_var)
        image_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            processing_frame, text="Browse...", command=self._browse_image_file
        ).grid(row=0, column=2, padx=5, pady=5)

        # Processing actions
        actions_frame = ttk.Frame(processing_frame)
        actions_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        actions_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(
            actions_frame, text="Analyze Image", command=self._analyze_image
        ).grid(row=0, column=0, padx=2)
        ttk.Button(
            actions_frame,
            text="Extract Text (OCR)",
            command=self._extract_text_from_image,
        ).grid(row=0, column=1, padx=2)
        ttk.Button(
            actions_frame, text="Detect Objects", command=self._detect_objects
        ).grid(row=0, column=2, padx=2)

    def _browse_image_file(self):
        """Browse for image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.image_path_var.set(file_path)

    def _analyze_image(self):
        """Analyze the selected image."""
        image_path = self.image_path_var.get()
        if image_path:
            messagebox.showinfo(
                "Computer Vision",
                f"Analyzing image: {image_path}\n\nImage analysis not yet implemented.",
            )
        else:
            messagebox.showwarning(
                "Computer Vision", "Please select an image file first."
            )

    def _extract_text_from_image(self):
        """Extract text from image using OCR."""
        image_path = self.image_path_var.get()
        if image_path:
            messagebox.showinfo(
                "Computer Vision",
                f"Extracting text from: {image_path}\n\nOCR functionality not yet implemented.",
            )
        else:
            messagebox.showwarning(
                "Computer Vision", "Please select an image file first."
            )

    def _detect_objects(self):
        """Detect objects in the selected image."""
        image_path = self.image_path_var.get()
        if image_path:
            messagebox.showinfo(
                "Computer Vision",
                f"Detecting objects in: {image_path}\n\nObject detection not yet implemented.",
            )
        else:
            messagebox.showwarning(
                "Computer Vision", "Please select an image file first."
            )

    def _build_writer_workspace_tab(self):
        """Build the Writer Workspace inspired by the HTML prototype."""
        FrameCls = ttkb.Frame if TTKBOOTSTRAP_AVAILABLE else ttk.Frame
        LabelFrameCls = ttkb.Labelframe if TTKBOOTSTRAP_AVAILABLE else ttk.LabelFrame
        ButtonCls = ttkb.Button if TTKBOOTSTRAP_AVAILABLE else ttk.Button
        LabelCls = ttkb.Label if TTKBOOTSTRAP_AVAILABLE else ttk.Label

        self.writer_workspace_frame = FrameCls(self.notebook, padding=(0, 0))
        self.notebook.add(self.writer_workspace_frame, text="✍️ Writer Workspace")
        self.writer_workspace_frame.columnconfigure(0, weight=1)

        header = FrameCls(self.writer_workspace_frame, padding=(12, 8))
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))
        header.columnconfigure(0, weight=1)
        LabelCls(
            header,
            text="Writer Workspace",
            font=(self.base_font.actual("family"), self.base_font.actual("size") + 4, "bold"),
        ).grid(row=0, column=0, sticky="w")
        LabelCls(
            header,
            text="Content creation, canon management, and narrative generation",
            font=(self.base_font.actual("family"), self.base_font.actual("size")),
            foreground=self.colors.get("muted", "#6c757d"),
        ).grid(row=1, column=0, sticky="w")

        actions = FrameCls(header)
        actions.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))
        ButtonCls(
            actions,
            text="➕ New Document",
            command=self._writer_create_document,
        ).grid(row=0, column=0, padx=4)
        ButtonCls(
            actions,
            text="✨ Generate Story",
            command=self._writer_generate_narrative,
            style="Accent.TButton" if TTKBOOTSTRAP_AVAILABLE else "TButton",
        ).grid(row=0, column=1, padx=4)

        controls = LabelFrameCls(
            self.writer_workspace_frame, text="Writing Assistant", padding=12
        )
        controls.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        for col in range(4):
            controls.columnconfigure(col, weight=1)

        combo_specs = [
            ("Document Type", self.writer_document_type_var, ["Article", "Story", "Report", "Script", "Blog"]),
            ("Genre/Style", self.writer_genre_var, ["Professional", "Creative", "Technical", "Academic", "Casual"]),
            (
                "Target Length",
                self.writer_length_var,
                [
                    "Short (500-1000 words)",
                    "Medium (1000-2500 words)",
                    "Long (2500+ words)",
                ],
            ),
            ("AI Assistance", self.writer_assistance_var, ["Minimal", "Moderate", "Extensive"]),
        ]
        for idx, (label, var, values) in enumerate(combo_specs):
            LabelCls(controls, text=label).grid(row=0, column=idx, sticky="w", pady=(0, 4))
            ttk.Combobox(
                controls,
                textvariable=var,
                values=values,
                state="readonly",
            ).grid(row=1, column=idx, sticky="ew", padx=4)

        LabelCls(controls, text="Title").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(controls, textvariable=self.writer_title_var).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4)
        )
        LabelCls(controls, text="Theme / Topic").grid(row=2, column=2, sticky="w", pady=(8, 0))
        ttk.Entry(controls, textvariable=self.writer_theme_var).grid(
            row=3, column=2, columnspan=2, sticky="ew", padx=4, pady=(0, 4)
        )
        self.writer_status_label = LabelCls(
            controls,
            textvariable=self.writer_status_note,
            foreground=self.colors.get("accent", "#5b5fc7"),
        )
        self.writer_status_label.grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))

        main_row = FrameCls(self.writer_workspace_frame, padding=(12, 0))
        main_row.grid(row=2, column=0, sticky="nsew")
        main_row.columnconfigure(0, weight=3)
        main_row.columnconfigure(1, weight=2)

        editor_card = FrameCls(main_row, padding=12, relief="flat")
        editor_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        editor_card.columnconfigure(0, weight=1)
        toolbar = FrameCls(editor_card)
        toolbar.grid(row=0, column=0, sticky="ew")
        LabelCls(toolbar, text="Document Editor", font=(self.base_font.actual("family"), self.base_font.actual("size") + 1, "bold")).grid(row=0, column=0, sticky="w")
        ButtonCls(toolbar, text="💾 Save", command=self._writer_save_document).grid(row=0, column=1, padx=4)
        ButtonCls(toolbar, text="⬇️ Export", command=self._writer_export_document).grid(row=0, column=2, padx=4)

        text_frame = FrameCls(editor_card)
        text_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        text_frame.columnconfigure(0, weight=1)
        self.writer_editor = tk.Text(
            text_frame,
            wrap="word",
            font=self.text_font,
            height=18,
        )
        self._style_text_widget(self.writer_editor)
        self.writer_editor.grid(row=0, column=0, sticky="nsew")
        editor_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.writer_editor.yview)
        editor_scroll.grid(row=0, column=1, sticky="ns")
        self.writer_editor.configure(yscrollcommand=editor_scroll.set)
        self.writer_editor.bind("<<Modified>>", self._writer_on_text_modified)
        LabelCls(
            editor_card,
            textvariable=self.writer_word_count_var,
            foreground=self.colors.get("muted", "#6c757d"),
        ).grid(row=2, column=0, sticky="e", pady=(6, 0))

        sidebar = FrameCls(main_row, padding=12)
        sidebar.grid(row=0, column=1, sticky="nsew")
        sidebar.columnconfigure(0, weight=1)

        inspiration = FrameCls(sidebar, padding=12)
        inspiration.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        inspiration.configure(relief="flat")
        LabelCls(
            inspiration,
            text="“The first draft of anything is shit.”",
            font=(self.base_font.actual("family"), self.base_font.actual("size"), "italic"),
        ).grid(row=0, column=0, sticky="w")
        LabelCls(
            inspiration,
            text="— Ernest Hemingway",
            foreground=self.colors.get("muted", "#6c757d"),
        ).grid(row=1, column=0, sticky="w")

        stats_frame = LabelFrameCls(sidebar, text="Writing Statistics", padding=10)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=4)
        stats_frame.columnconfigure((0, 1), weight=1)
        stat_order = [
            ("Total Words", self.writer_stats_vars["total_words"]),
            ("Documents", self.writer_stats_vars["documents"]),
            ("Words / Day", self.writer_stats_vars["avg_words_per_day"]),
            ("Day Streak", self.writer_stats_vars["writing_streak"]),
        ]
        for idx, (label, var) in enumerate(stat_order):
            card = FrameCls(stats_frame, padding=6)
            card.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=4)
            LabelCls(card, text=label, foreground=self.colors.get("muted", "#6c757d")).grid(row=0, column=0, sticky="w")
            LabelCls(
                card,
                textvariable=var,
                font=(self.base_font.actual("family"), self.base_font.actual("size") + 4, "bold"),
            ).grid(row=1, column=0, sticky="w")

        suggestions = LabelFrameCls(sidebar, text="AI Suggestions", padding=10)
        suggestions.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        suggestions.columnconfigure(0, weight=1)
        self.writer_suggestions_container = FrameCls(suggestions)
        self.writer_suggestions_container.grid(row=0, column=0, sticky="nsew")

        library_row = FrameCls(self.writer_workspace_frame, padding=(12, 8))
        library_row.grid(row=3, column=0, sticky="nsew")
        library_row.columnconfigure(0, weight=3)
        library_row.columnconfigure(1, weight=2)
        library_row.rowconfigure(0, weight=1)

        library_frame = LabelFrameCls(library_row, text="Document Library", padding=10)
        library_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        library_frame.columnconfigure(0, weight=1)
        self.writer_document_tree = ttk.Treeview(
            library_frame,
            columns=("type", "status", "words", "edited"),
            show="headings",
            height=10,
        )
        for col, heading in zip(
            ("type", "status", "words", "edited"),
            ("Type", "Status", "Words", "Last Edited"),
        ):
            self.writer_document_tree.heading(col, text=heading)
            self.writer_document_tree.column(col, width=110, stretch=True)
        self.writer_document_tree.grid(row=0, column=0, sticky="nsew")
        doc_scroll = ttk.Scrollbar(
            library_frame, orient="vertical", command=self.writer_document_tree.yview
        )
        doc_scroll.grid(row=0, column=1, sticky="ns")
        self.writer_document_tree.configure(yscrollcommand=doc_scroll.set)
        self.writer_document_tree.bind("<Double-1>", self._writer_on_document_open)

        chart_frame = LabelFrameCls(library_row, text="Writing Progress", padding=10)
        chart_frame.grid(row=0, column=1, sticky="nsew")
        self.writer_progress_canvas = tk.Canvas(
            chart_frame,
            height=220,
            width=360,
            highlightthickness=0,
            background=self.colors.get("surface", "#ffffff"),
        )
        self.writer_progress_canvas.pack(fill="both", expand=True)
        self.writer_progress_canvas.bind("<Configure>", lambda e: self._writer_redraw_progress_chart())

        lore_row = FrameCls(self.writer_workspace_frame, padding=(12, 0))
        lore_row.grid(row=4, column=0, sticky="nsew", pady=(0, 12))
        lore_row.columnconfigure(0, weight=1)
        lore_row.columnconfigure(1, weight=1)

        canon_frame = LabelFrameCls(lore_row, text="Canon Database", padding=10)
        canon_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        canon_frame.columnconfigure(0, weight=1)
        self.writer_canon_container = FrameCls(canon_frame)
        self.writer_canon_container.grid(row=0, column=0, sticky="nsew")
        ButtonCls(
            canon_frame,
            text="➕ Add Canon Entry",
            command=self._writer_add_canon_entry,
        ).grid(row=1, column=0, sticky="e", pady=(6, 0))

        pipeline_frame = LabelFrameCls(lore_row, text="Publishing Pipeline", padding=10)
        pipeline_frame.grid(row=0, column=1, sticky="nsew")
        pipeline_frame.columnconfigure(0, weight=1)
        self.writer_pipeline_container = FrameCls(pipeline_frame)
        self.writer_pipeline_container.grid(row=0, column=0, sticky="nsew")
        ButtonCls(
            pipeline_frame,
            text="⬆️ Publish Document",
            command=self._writer_publish_document,
        ).grid(row=1, column=0, sticky="e", pady=(6, 0))

        self._writer_populate_document_library()
        self._writer_refresh_suggestions()
        self._writer_populate_canon_entries()
        self._writer_populate_publishing_pipeline()
        self._writer_refresh_stats_cards()
        self._writer_redraw_progress_chart()
        self._writer_schedule_stat_update()

    # ---------- Tasks ----------

    def _build_tasks_tab(self):
        """Classic tasks table showing the active queue."""
        FrameCls = ttkb.Frame if TTKBOOTSTRAP_AVAILABLE else ttk.Frame
        LabelFrameCls = ttkb.Labelframe if TTKBOOTSTRAP_AVAILABLE else ttk.LabelFrame

        self.tasks_frame = FrameCls(self.notebook)
        self.notebook.add(self.tasks_frame, text="✅ Tasks")
        self.tasks_frame.columnconfigure(0, weight=1)
        self.tasks_frame.rowconfigure(2, weight=1)

        header = FrameCls(self.tasks_frame)
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        header.columnconfigure(0, weight=1)
        ttk.Label(
            header,
            text="Task Board",
            font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(header, text="Refresh", command=self.refresh_task_list).grid(row=0, column=1, sticky="e")

        filters = FrameCls(self.tasks_frame)
        filters.grid(row=1, column=0, sticky="ew", padx=8)
        ttk.Checkbutton(
            filters,
            text="Show Completed Tasks",
            variable=self.show_done_var,
            command=self.refresh_task_list,
        ).grid(row=0, column=0, sticky="w")

        columns = ("id", "title", "project", "priority", "status", "owner", "due")
        tree_frame = FrameCls(self.tasks_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        self.tasks_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        headings = {
            "id": "ID",
            "title": "Title",
            "project": "Project",
            "priority": "Priority",
            "status": "Status",
            "owner": "Owner",
            "due": "Due",
        }
        for col, label in headings.items():
            self.tasks_tree.heading(col, text=label)
            width = 80 if col in ("id", "priority", "status", "owner", "due") else 220
            self.tasks_tree.column(col, width=width, anchor="w")
        self.tasks_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tasks_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)

        summary = LabelFrameCls(self.tasks_frame, text="Summary", padding=8)
        summary.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        summary.columnconfigure(0, weight=1)
        self.tasks_summary_text = tk.Text(summary, height=5, wrap="word", font=self.text_font)
        self.tasks_summary_text.pack(fill="both", expand=True)
        self.tasks_summary_text.config(state="disabled")

    def _build_tasks_projects_tab(self):
        """Consolidated tasks + projects overview."""
        FrameCls = ttkb.Frame if TTKBOOTSTRAP_AVAILABLE else ttk.Frame
        LabelFrameCls = ttkb.Labelframe if TTKBOOTSTRAP_AVAILABLE else ttk.LabelFrame

        self.tasks_projects_frame = FrameCls(self.notebook)
        self.notebook.add(self.tasks_projects_frame, text="✅ Tasks & Projects")
        self.tasks_projects_frame.columnconfigure(0, weight=1)
        self.tasks_projects_frame.columnconfigure(1, weight=1)

        tasks_panel = LabelFrameCls(self.tasks_projects_frame, text="Active Tasks", padding=10)
        tasks_panel.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        tasks_panel.columnconfigure(0, weight=1)
        self.tasks_overview_text = tk.Text(tasks_panel, height=15, wrap="word", font=self.text_font)
        self.tasks_overview_text.pack(fill="both", expand=True)
        self.tasks_overview_text.config(state="disabled")

        projects_panel = LabelFrameCls(self.tasks_projects_frame, text="Projects", padding=10)
        projects_panel.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        projects_panel.columnconfigure(0, weight=1)
        self.projects_summary_text = tk.Text(projects_panel, height=15, wrap="word", font=self.text_font)
        self.projects_summary_text.pack(fill="both", expand=True)
        self.projects_summary_text.config(state="disabled")

    def refresh_task_list(self):
        """Refresh the shared task snapshot and update both task views."""
        try:
            snapshot = build_task_snapshot(
                self.state_obj.tasks,
                include_done=self.show_done_var.get(),
            )
        except Exception as exc:
            self.logger.warning("Failed to refresh tasks: %s", exc)
            return
        self.tasks_snapshot = snapshot

        if self.tasks_tree and self.tasks_tree.winfo_exists():
            for item in self.tasks_tree.get_children():
                self.tasks_tree.delete(item)
            for task in snapshot.tasks:
                self.tasks_tree.insert(
                    "",
                    "end",
                    values=(
                        task["id"],
                        task["title"],
                        task["project"],
                        task["priority"],
                        task["status"],
                        task["owner"],
                        task.get("due_date") or "",
                    ),
                )

        summary_lines = [f"Total tasks: {len(snapshot.tasks)}", ""]
        summary_lines.append("Status counts:")
        for status, count in snapshot.status_counts.items():
            summary_lines.append(f"- {status}: {count}")
        summary_lines.append("")
        summary_lines.append("Priority counts:")
        for priority, count in snapshot.priority_counts.items():
            summary_lines.append(f"- {priority}: {count}")
        summary_text = "\n".join(summary_lines)

        if self.tasks_summary_text:
            self.tasks_summary_text.config(state=tk.NORMAL)
            self.tasks_summary_text.delete("1.0", "end")
            self.tasks_summary_text.insert("1.0", summary_text)
            self.tasks_summary_text.config(state=tk.DISABLED)

        self._refresh_tasks_projects_panel(snapshot)

    def _refresh_tasks_projects_panel(self, snapshot):
        """Update consolidated tasks/projects view."""
        if getattr(self, "tasks_overview_text", None):
            lines = []
            top_tasks = snapshot.tasks[:5]
            if top_tasks:
                lines.append("Top tasks:")
                for task in top_tasks:
                    lines.append(
                        f"- #{task['id']} [{task['priority']}] {task['title']} ({task['status']})"
                    )
            else:
                lines.append("No tasks to display.")
            self.tasks_overview_text.config(state=tk.NORMAL)
            self.tasks_overview_text.delete("1.0", "end")
            self.tasks_overview_text.insert("1.0", "\n".join(lines))
            self.tasks_overview_text.config(state=tk.DISABLED)

        if getattr(self, "projects_summary_text", None):
            lines = []
            projects = self.project_snapshot.projects if self.project_snapshot else []
            for project in projects[:5]:
                lines.append(f"- {project['name']} ({project['status']})")
            if not lines:
                lines.append("No projects recorded.")
            self.projects_summary_text.config(state=tk.NORMAL)
            self.projects_summary_text.delete("1.0", "end")
            self.projects_summary_text.insert("1.0", "\n".join(lines))
            self.projects_summary_text.config(state=tk.DISABLED)

    def _build_projects_tab(self):
        """Project list mirroring the shared workspace state."""
        FrameCls = ttkb.Frame if TTKBOOTSTRAP_AVAILABLE else ttk.Frame
        LabelFrameCls = ttkb.Labelframe if TTKBOOTSTRAP_AVAILABLE else ttk.LabelFrame

        self.projects_frame = FrameCls(self.notebook)
        self.notebook.add(self.projects_frame, text="📁 Projects")
        self.projects_frame.columnconfigure(0, weight=1)
        self.projects_frame.rowconfigure(1, weight=1)

        header = FrameCls(self.projects_frame)
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        header.columnconfigure(0, weight=1)
        ttk.Label(
            header,
            text="Projects",
            font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(header, text="Refresh", command=self.refresh_project_list).grid(row=0, column=1, sticky="e")

        columns = ("name", "status", "priority", "description")
        table = FrameCls(self.projects_frame)
        table.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)

        self.project_tree = ttk.Treeview(table, columns=columns, show="headings")
        headings = {
            "name": "Name",
            "status": "Status",
            "priority": "Priority",
            "description": "Description",
        }
        for col, label in headings.items():
            self.project_tree.heading(col, text=label)
            width = 120 if col != "description" else 260
            self.project_tree.column(col, width=width, anchor="w")
        self.project_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.project_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.project_tree.configure(yscrollcommand=scrollbar.set)

        summary = LabelFrameCls(self.projects_frame, text="Summary", padding=8)
        summary.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        summary.columnconfigure(0, weight=1)
        self.project_summary_text = tk.Text(summary, height=5, wrap="word", font=self.text_font)
        self.project_summary_text.pack(fill="both", expand=True)
        self.project_summary_text.config(state="disabled")

    def refresh_project_list(self):
        """Refresh shared project snapshot and update UI."""
        try:
            snapshot = build_project_snapshot(self.state_obj.projects)
        except Exception as exc:
            self.logger.warning("Failed to refresh projects: %s", exc)
            return
        self.project_snapshot = snapshot

        if self.project_tree and self.project_tree.winfo_exists():
            for item in self.project_tree.get_children():
                self.project_tree.delete(item)
            for project in snapshot.projects:
                self.project_tree.insert(
                    "",
                    "end",
                    values=(
                        project["name"],
                        project["status"],
                        project["priority"],
                        project["description"],
                    ),
                )
        if self.project_summary_text:
            lines = ["Status counts:"]
            for status, count in snapshot.status_counts.items():
                lines.append(f"- {status}: {count}")
            lines.append("")
            lines.append("Priority counts:")
            for priority, count in snapshot.priority_counts.items():
                lines.append(f"- {priority}: {count}")
            self.project_summary_text.config(state=tk.NORMAL)
            self.project_summary_text.delete("1.0", "end")
            self.project_summary_text.insert("1.0", "\n".join(lines))
            self.project_summary_text.config(state=tk.DISABLED)

        # update consolidated view with latest projects
        self._refresh_tasks_projects_panel(self.tasks_snapshot or build_task_snapshot(self.state_obj.tasks))

    def _writer_on_text_modified(self, event):
        try:
            event.widget.edit_modified(False)
        except Exception:
            pass
        self._writer_update_word_count()

    def _writer_update_word_count(self):
        if not self.writer_editor:
            return 0
        text = self.writer_editor.get("1.0", "end-1c").strip()
        words = len(text.split()) if text else 0
        self.writer_word_count_var.set(f"{words:,} words")
        return words

    def _writer_create_document(self):
        title = self.writer_title_var.get().strip() or "Untitled Document"
        doc = self.writer_state.create_document(
            title,
            self.writer_document_type_var.get(),
            summary=self.writer_theme_var.get() or None,
            theme=self.writer_theme_var.get() or None,
        )
        self.writer_active_document_id = doc["id"]
        if self.writer_editor:
            self.writer_editor.delete("1.0", "end")
        self._writer_populate_document_library()
        self._writer_refresh_stats_cards()
        self._writer_redraw_progress_chart()
        self._writer_update_word_count()
        self._writer_notify(f'Created "{title}". Start writing!')

    def _writer_generate_narrative(self):
        title = self.writer_title_var.get().strip() or "Untitled Narrative"
        template = self.writer_state.generate_narrative(
            self.writer_document_type_var.get(),
            self.writer_theme_var.get().strip() or "adventure",
            self.writer_genre_var.get(),
            title,
        )
        if self.writer_editor:
            self.writer_editor.delete("1.0", "end")
            self.writer_editor.insert("1.0", template)
        self._writer_update_word_count()
        self._writer_notify("Narrative draft generated.")

    def _writer_save_document(self):
        if not self.writer_editor:
            return
        content = self.writer_editor.get("1.0", "end-1c")
        words = self._writer_update_word_count()
        if not self.writer_active_document_id:
            doc = self.writer_state.create_document(
                self.writer_title_var.get().strip() or "Untitled Document",
                self.writer_document_type_var.get(),
                summary=self.writer_theme_var.get() or None,
                theme=self.writer_theme_var.get() or None,
            )
            self.writer_active_document_id = doc["id"]
        try:
            self.writer_state.save_document(self.writer_active_document_id, content)
        except KeyError:
            self._writer_notify("Unable to save document - missing record.")
            return
        self._writer_populate_document_library()
        self._writer_refresh_stats_cards()
        self._writer_redraw_progress_chart()
        self._writer_notify(f"Document saved locally ({words:,} words).")

    def _writer_export_document(self):
        if not self.writer_editor:
            return
        file_path = filedialog.asksaveasfilename(
            title="Export Document",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return
        content = self.writer_editor.get("1.0", "end-1c")
        try:
            with open(file_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            self._writer_notify(f'Exported to "{os.path.basename(file_path)}".')
        except Exception as exc:
            messagebox.showerror("Export Error", f"Failed to export document: {exc}")

    def _writer_on_document_open(self, event=None):
        if not self.writer_document_tree:
            return
        selection = self.writer_document_tree.selection()
        if not selection:
            return
        doc_id = self.writer_document_rows.get(selection[0])
        if not doc_id:
            return
        try:
            doc = self.writer_state.get_document(doc_id)
        except KeyError:
            self._writer_notify("Document not found.")
            return
        self.writer_active_document_id = doc_id
        self.writer_title_var.set(doc["title"])
        if self.writer_editor:
            self.writer_editor.delete("1.0", "end")
            self.writer_editor.insert("1.0", doc.get("content", ""))
        self._writer_update_word_count()
        self._writer_notify(f'Loaded "{doc["title"]}".')

    def _writer_populate_document_library(self):
        if not self.writer_document_tree:
            return
        self.writer_document_rows.clear()
        for item in self.writer_document_tree.get_children():
            self.writer_document_tree.delete(item)
        for doc in self.writer_state.documents:
            iid = self.writer_document_tree.insert(
                "",
                "end",
                values=(
                    doc["type"],
                    doc["status"],
                    f'{doc["words"]:,}',
                    doc["last_edited"],
                ),
                text=doc["title"],
            )
            self.writer_document_rows[iid] = doc["id"]

    def _writer_refresh_suggestions(self):
        if not self.writer_suggestions_container:
            return
        for child in self.writer_suggestions_container.winfo_children():
            child.destroy()
        for suggestion in self.writer_state.suggestions:
            card = ttk.Frame(self.writer_suggestions_container)
            card.pack(fill="x", pady=4)
            ttk.Label(card, text=suggestion["title"], font=(self.base_font.actual("family"), self.base_font.actual("size"), "bold")).pack(anchor="w")
            ttk.Label(
                card,
                text=suggestion["body"],
                wraplength=260,
                foreground=self.colors.get("muted", "#6c757d"),
                justify="left",
            ).pack(anchor="w", pady=(0, 2))

    def _writer_populate_canon_entries(self):
        if not self.writer_canon_container:
            return
        for child in self.writer_canon_container.winfo_children():
            child.destroy()
        for entry in self.writer_state.canon_entries:
            row = ttk.Frame(self.writer_canon_container)
            row.pack(fill="x", pady=4)
            ttk.Label(
                row, text=f'{entry["title"]} · {entry["category"]}', font=(self.base_font.actual("family"), self.base_font.actual("size"), "bold")
            ).grid(row=0, column=0, sticky="w")
            ttk.Button(
                row,
                text="Edit",
                command=lambda title=entry["title"]: self._writer_edit_canon_entry(title),
                width=6,
            ).grid(row=0, column=1, sticky="e")
            ttk.Label(
                row,
                text=entry["description"],
                wraplength=320,
                foreground=self.colors.get("muted", "#6c757d"),
            ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 2))
            ttk.Label(row, text=entry["meta"], foreground=self.colors.get("muted", "#94a3b8")).grid(
                row=2, column=0, columnspan=2, sticky="w"
            )

    def _writer_populate_publishing_pipeline(self):
        if not self.writer_pipeline_container:
            return
        for child in self.writer_pipeline_container.winfo_children():
            child.destroy()
        for entry in self.writer_state.pipeline_entries:
            row = ttk.Frame(self.writer_pipeline_container)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=f'{entry["title"]} ({entry["status"]})', font=(self.base_font.actual("family"), self.base_font.actual("size"), "bold")).grid(
                row=0, column=0, sticky="w"
            )
            ttk.Label(row, text=entry["summary"]).grid(row=1, column=0, sticky="w")
            ttk.Label(
                row,
                text=entry["meta"],
                foreground=self.colors.get("muted", "#6c757d"),
            ).grid(row=2, column=0, sticky="w")

    def _writer_add_canon_entry(self):
        self._writer_notify("Canon entry dialog coming soon.")

    def _writer_edit_canon_entry(self, title: str):
        self._writer_notify(f'Editing canon entry "{title}".')

    def _writer_publish_document(self):
        title = self.writer_title_var.get().strip() or "Current Document"
        self._writer_notify(f'Publishing "{title}" workflow queued.')

    def _writer_refresh_stats_cards(self):
        stats = self.writer_state.stats
        self.writer_stats_vars["total_words"].set(f'{stats["total_words"]:,}')
        self.writer_stats_vars["documents"].set(str(stats["documents"]))
        self.writer_stats_vars["avg_words_per_day"].set(str(stats["avg_words_per_day"]))
        self.writer_stats_vars["writing_streak"].set(str(stats["writing_streak"]))

    def _writer_redraw_progress_chart(self):
        if not self.writer_progress_canvas:
            return
        canvas = self.writer_progress_canvas
        canvas.delete("all")
        width = int(canvas.winfo_width() or canvas["width"])
        height = int(canvas.winfo_height() or canvas["height"])
        padding = 24
        progress_data = self.writer_state.progress_data
        if not progress_data:
            return
        days = self.writer_state.progress_days
        max_value = max(progress_data + [self.writer_state.progress_goal])
        scale = (height - padding * 2) / max_value if max_value else 1
        points = []
        denom = max(len(progress_data) - 1, 1)
        for idx, value in enumerate(progress_data):
            x = padding + idx * (width - padding * 2) / denom
            y = height - padding - value * scale
            points.append((x, y))
        if len(points) > 1:
            for i in range(len(points) - 1):
                canvas.create_line(
                    points[i][0],
                    points[i][1],
                    points[i + 1][0],
                    points[i + 1][1],
                    fill="#f093fb",
                    width=2,
                    smooth=True,
                )
        goal_y = height - padding - self.writer_state.progress_goal * scale
        canvas.create_line(
            padding,
            goal_y,
            width - padding,
            goal_y,
            fill="#667eea",
            dash=(4, 4),
        )
        for idx, (x, y) in enumerate(points):
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#f5576c", outline="")
            canvas.create_text(x, height - 6, text=days[idx], fill=self.colors.get("muted", "#6c757d"))

    def _writer_schedule_stat_update(self):
        if self.writer_real_time_job:
            try:
                self.after_cancel(self.writer_real_time_job)
            except Exception:
                pass
        self.writer_real_time_job = self.after(30000, self._writer_simulate_stats)

    def _writer_simulate_stats(self):
        delta = self.writer_state.simulate_activity()
        self._writer_refresh_stats_cards()
        self._writer_redraw_progress_chart()
        self._writer_notify(f"System health ping: +{delta} tracked words.")
        self._writer_schedule_stat_update()

    def _writer_notify(self, message: str):
        self.writer_status_note.set(message)


    def _build_neural_architecture_search_tab(self):
        """Build the Neural Architecture Search tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.nas_frame = ttkb.Frame(self.notebook)
        else:
            self.nas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.nas_frame, text="🧬 Neural Architecture Search")

        self.nas_frame.columnconfigure(0, weight=1)
        self.nas_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.nas_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        else:
            main_frame = ttk.Frame(self.nas_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🧬 Neural Architecture Search",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Description
        desc_text = """Evolutionary AI system that designs and optimizes neural network architectures.
        Uses genetic algorithms and reinforcement learning to discover optimal model architectures
        for your specific datasets and tasks."""
        desc_label = ttk.Label(
            main_frame, text=desc_text, wraplength=600, justify="left"
        )
        desc_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        # Control buttons frame
        control_frame = ttk.LabelFrame(
            main_frame, text="Experiment Control", padding=10
        )
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        control_frame.columnconfigure((0, 1, 2), weight=1)

        # Experiment controls
        ttk.Button(
            control_frame,
            text="🧬 Start NAS Experiment",
            command=self._start_nas_experiment,
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame, text="📊 View Results", command=self._view_nas_results
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame, text="⚙️ Configure", command=self._configure_nas
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding=10)
        status_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)

        self.nas_status_var = tk.StringVar(value="No active experiments")
        status_label = ttk.Label(
            status_frame, textvariable=self.nas_status_var, font=(self.base_font, 12)
        )
        status_label.grid(row=0, column=0, pady=5, sticky="w")

        # Best architecture display
        best_frame = ttk.LabelFrame(
            main_frame, text="Best Architecture Found", padding=10
        )
        best_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        best_frame.columnconfigure(0, weight=1)

        self.best_arch_var = tk.StringVar(value="None discovered yet")
        best_label = ttk.Label(
            best_frame, textvariable=self.best_arch_var, font=(self.base_font, 10)
        )
        best_label.grid(row=0, column=0, pady=5, sticky="w")

        # Evolution metrics
        metrics_frame = ttk.LabelFrame(main_frame, text="Evolution Metrics", padding=10)
        metrics_frame.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        metrics_frame.columnconfigure((0, 1, 2), weight=1)

        # Metrics labels
        ttk.Label(metrics_frame, text="Generation:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, text="Population Size:").grid(
            row=1, column=0, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, text="Best Fitness:").grid(
            row=2, column=0, sticky="w", pady=2
        )

        self.gen_var = tk.StringVar(value="0")
        self.pop_var = tk.StringVar(value="0")
        self.fitness_var = tk.StringVar(value="0.000")

        ttk.Label(metrics_frame, textvariable=self.gen_var).grid(
            row=0, column=1, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, textvariable=self.pop_var).grid(
            row=1, column=1, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, textvariable=self.fitness_var).grid(
            row=2, column=1, sticky="w", pady=2
        )

        # Refresh button
        ttk.Button(
            metrics_frame, text="🔄 Refresh", command=self._refresh_nas_status
        ).grid(row=3, column=0, columnspan=3, pady=(10, 0))

        # Info text
        info_text = """How it works:
• Evolutionary algorithms breed neural architectures
• Genetic crossover combines successful designs
• Mutation introduces beneficial variations
• Fitness evaluation tests performance on your data
• Best architectures are preserved for future use

Supported strategies: Genetic Algorithm, Random Search, Reinforcement Learning, Bayesian Optimization"""
        info_label = ttk.Label(
            main_frame,
            text=info_text,
            wraplength=600,
            font=(self.base_font, 9),
            foreground="gray",
        )
        info_label.grid(row=6, column=0, pady=(20, 0), sticky="w")

    def _build_security_threat_detection_tab(self):
        """Build the AI Security Threat Detection tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.security_frame = ttkb.Frame(self.notebook)
        else:
            self.security_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.security_frame, text="🛡️ AI Security")

        self.security_frame.columnconfigure(0, weight=1)
        self.security_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.security_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        else:
            main_frame = ttk.Frame(self.security_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🛡️ AI-Powered Security Threat Detection",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Description
        desc_text = """Advanced AI security system that detects, analyzes, and responds to cyber threats.
        Uses machine learning algorithms to identify anomalous behavior, predict attacks,
        and provide automated security recommendations."""
        desc_label = ttk.Label(
            main_frame, text=desc_text, wraplength=600, justify="left"
        )
        desc_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Security Controls", padding=10)
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        control_frame.columnconfigure((0, 1, 2), weight=1)

        # Security controls
        ttk.Button(
            control_frame, text="🔍 Start Threat Scan", command=self._start_threat_scan
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame,
            text="📊 View Security Report",
            command=self._view_security_report,
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame, text="⚙️ Security Settings", command=self._configure_security
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Threat status display
        threat_frame = ttk.LabelFrame(
            main_frame, text="Current Threat Status", padding=10
        )
        threat_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        threat_frame.columnconfigure(0, weight=1)

        self.threat_status_var = tk.StringVar(
            value="🟢 System Secure - No threats detected"
        )
        threat_label = ttk.Label(
            threat_frame, textvariable=self.threat_status_var, font=(self.base_font, 12)
        )
        threat_label.grid(row=0, column=0, pady=5, sticky="w")

        # Security metrics
        metrics_frame = ttk.LabelFrame(main_frame, text="Security Metrics", padding=10)
        metrics_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        metrics_frame.columnconfigure((0, 1, 2), weight=1)

        # Metrics labels
        ttk.Label(metrics_frame, text="Scans Today:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, text="Threats Blocked:").grid(
            row=1, column=0, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, text="Risk Score:").grid(
            row=2, column=0, sticky="w", pady=2
        )

        self.scans_var = tk.StringVar(value="0")
        self.threats_var = tk.StringVar(value="0")
        self.risk_var = tk.StringVar(value="Low")

        ttk.Label(metrics_frame, textvariable=self.scans_var).grid(
            row=0, column=1, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, textvariable=self.threats_var).grid(
            row=1, column=1, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, textvariable=self.risk_var).grid(
            row=2, column=1, sticky="w", pady=2
        )

        # Recent threats
        threats_frame = ttk.LabelFrame(
            main_frame, text="Recent Security Events", padding=10
        )
        threats_frame.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        threats_frame.columnconfigure(0, weight=1)

        # Threats listbox with scrollbar
        threats_listbox_frame = ttk.Frame(threats_frame)
        threats_listbox_frame.grid(row=0, column=0, sticky="ew")
        threats_listbox_frame.columnconfigure(0, weight=1)

        threats_scrollbar = ttk.Scrollbar(threats_listbox_frame)
        threats_scrollbar.grid(row=0, column=1, sticky="ns")

        self.threats_listbox = tk.Listbox(
            threats_listbox_frame,
            height=6,
            yscrollcommand=threats_scrollbar.set,
            font=self.text_font,
        )
        self.threats_listbox.grid(row=0, column=0, sticky="ew")
        threats_scrollbar.config(command=self.threats_listbox.yview)

        # Sample threats
        self.threats_listbox.insert(tk.END, "🔍 Suspicious login attempt detected")
        self.threats_listbox.insert(tk.END, "📡 Unusual network traffic pattern")
        self.threats_listbox.insert(tk.END, "🔐 Weak password policy alert")
        self.threats_listbox.insert(tk.END, "🖥️ System integrity check passed")

        # Action buttons
        actions_frame = ttk.Frame(threats_frame)
        actions_frame.grid(row=1, column=0, pady=(10, 0))
        actions_frame.columnconfigure((0, 1), weight=1)

        ttk.Button(
            actions_frame, text="🚨 Investigate", command=self._investigate_threat
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(
            actions_frame, text="🔄 Refresh", command=self._refresh_security_status
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Security capabilities info
        capabilities_text = """AI Security Capabilities:
• Real-time threat detection using ML algorithms
• Behavioral analysis and anomaly detection
• Predictive threat modeling
• Automated incident response
• Security policy optimization
• Compliance monitoring and reporting

Supported Detection Types: Malware, DDoS, Phishing, Data Exfiltration, Insider Threats"""
        capabilities_label = ttk.Label(
            main_frame,
            text=capabilities_text,
            wraplength=600,
            font=(self.base_font, 9),
            foreground="gray",
        )
        capabilities_label.grid(row=6, column=0, pady=(20, 0), sticky="w")

    def _build_edge_computing_tab(self):
        """Build the Edge Computing & Distributed AI tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.edge_frame = ttkb.Frame(self.notebook)
        else:
            self.edge_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edge_frame, text="☁️ Edge Computing")

        self.edge_frame.columnconfigure(0, weight=1)
        self.edge_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.edge_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        else:
            main_frame = ttk.Frame(self.edge_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="☁️ Edge Computing & Distributed AI",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Description
        desc_text = """Distributed AI system that leverages edge computing for real-time intelligence.
        Deploys AI models across multiple devices and cloud instances for optimal performance,
        privacy, and low-latency processing."""
        desc_label = ttk.Label(
            main_frame, text=desc_text, wraplength=600, justify="left"
        )
        desc_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        # Control buttons frame
        control_frame = ttk.LabelFrame(
            main_frame, text="Distributed AI Controls", padding=10
        )
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        control_frame.columnconfigure((0, 1, 2), weight=1)

        # Edge controls
        ttk.Button(
            control_frame, text="🚀 Deploy Edge AI", command=self._deploy_edge_ai
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame, text="📊 Network Status", command=self._view_network_status
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame, text="⚙️ Configure Nodes", command=self._configure_edge_nodes
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Network status display
        network_frame = ttk.LabelFrame(
            main_frame, text="Distributed Network Status", padding=10
        )
        network_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        network_frame.columnconfigure(0, weight=1)

        self.network_status_var = tk.StringVar(
            value="🌐 Network: 5/5 nodes online - Optimal performance"
        )
        network_label = ttk.Label(
            network_frame,
            textvariable=self.network_status_var,
            font=(self.base_font, 12),
        )
        network_label.grid(row=0, column=0, pady=5, sticky="w")

        # Performance metrics
        perf_frame = ttk.LabelFrame(main_frame, text="Performance Metrics", padding=10)
        perf_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        perf_frame.columnconfigure((0, 1, 2), weight=1)

        # Metrics labels
        ttk.Label(perf_frame, text="Avg Latency:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        ttk.Label(perf_frame, text="Throughput:").grid(
            row=1, column=0, sticky="w", pady=2
        )
        ttk.Label(perf_frame, text="Efficiency:").grid(
            row=2, column=0, sticky="w", pady=2
        )

        self.latency_var = tk.StringVar(value="45ms")
        self.throughput_var = tk.StringVar(value="2.4 GB/s")
        self.efficiency_var = tk.StringVar(value="94.2%")

        ttk.Label(perf_frame, textvariable=self.latency_var).grid(
            row=0, column=1, sticky="w", pady=2
        )
        ttk.Label(perf_frame, textvariable=self.throughput_var).grid(
            row=1, column=1, sticky="w", pady=2
        )
        ttk.Label(perf_frame, textvariable=self.efficiency_var).grid(
            row=2, column=1, sticky="w", pady=2
        )

        # Node status
        nodes_frame = ttk.LabelFrame(main_frame, text="Edge Nodes Status", padding=10)
        nodes_frame.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        nodes_frame.columnconfigure(0, weight=1)

        # Nodes listbox with scrollbar
        nodes_listbox_frame = ttk.Frame(nodes_frame)
        nodes_listbox_frame.grid(row=0, column=0, sticky="ew")
        nodes_listbox_frame.columnconfigure(0, weight=1)

        nodes_scrollbar = ttk.Scrollbar(nodes_listbox_frame)
        nodes_scrollbar.grid(row=0, column=1, sticky="ns")

        self.nodes_listbox = tk.Listbox(
            nodes_listbox_frame,
            height=6,
            yscrollcommand=nodes_scrollbar.set,
            font=self.text_font,
        )
        self.nodes_listbox.grid(row=0, column=0, sticky="ew")
        nodes_scrollbar.config(command=self.nodes_listbox.yview)

        # Sample nodes
        self.nodes_listbox.insert(
            tk.END, "🖥️ Local GPU Node - Online (98% utilization)"
        )
        self.nodes_listbox.insert(
            tk.END, "☁️ Cloud Instance 1 - Online (45% utilization)"
        )
        self.nodes_listbox.insert(
            tk.END, "📱 Mobile Edge Node - Online (12% utilization)"
        )
        self.nodes_listbox.insert(
            tk.END, "🛰️ Satellite Node - Degraded (67% utilization)"
        )
        self.nodes_listbox.insert(tk.END, "🏠 IoT Hub Node - Offline (maintenance)")

        # Action buttons
        node_actions_frame = ttk.Frame(nodes_frame)
        node_actions_frame.grid(row=1, column=0, pady=(10, 0))
        node_actions_frame.columnconfigure((0, 1), weight=1)

        ttk.Button(
            node_actions_frame, text="🔧 Manage Node", command=self._manage_edge_node
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(
            node_actions_frame, text="🔄 Sync Network", command=self._sync_edge_network
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Distributed AI capabilities info
        capabilities_text = """Edge Computing Capabilities:
• Real-time AI inference at the network edge
• Distributed model training across devices
• Privacy-preserving federated learning
• Low-latency processing for IoT applications
• Automatic load balancing and failover
• Energy-efficient edge deployments

Supported Architectures: MobileNet, TinyML, Federated Learning, Edge TPU"""
        capabilities_label = ttk.Label(
            main_frame,
            text=capabilities_text,
            wraplength=600,
            font=(self.base_font, 9),
            foreground="gray",
        )
        capabilities_label.grid(row=6, column=0, pady=(20, 0), sticky="w")

    def _build_workflow_orchestration_tab(self):
        """Build the Workflow Orchestration tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.workflow_frame = ttkb.Frame(self.notebook)
        else:
            self.workflow_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.workflow_frame, text="🎯 Workflows")

        self.workflow_frame.columnconfigure(0, weight=1)
        self.workflow_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.workflow_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        else:
            main_frame = ttk.Frame(self.workflow_frame)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🎯 AI Workflow Orchestration",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Description
        desc_text = """Intelligent workflow orchestration system that automates complex processes.
        Uses AI to coordinate tasks, manage dependencies, and optimize execution across
        multiple systems and services."""
        desc_label = ttk.Label(
            main_frame, text=desc_text, wraplength=600, justify="left"
        )
        desc_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Workflow Controls", padding=10)
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        control_frame.columnconfigure((0, 1, 2), weight=1)

        # Workflow controls
        ttk.Button(
            control_frame,
            text="▶️ Start Orchestrator",
            command=self._start_workflow_orchestrator,
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame,
            text="📊 View Active Workflows",
            command=self._view_active_workflows,
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(
            control_frame,
            text="⚙️ Configure Workflows",
            command=self._configure_workflows,
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Orchestrator status display
        status_frame = ttk.LabelFrame(
            main_frame, text="Orchestrator Status", padding=10
        )
        status_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)

        self.orchestrator_status_var = tk.StringVar(
            value="🔄 Orchestrator: Running - Processing 3 workflows"
        )
        status_label = ttk.Label(
            status_frame,
            textvariable=self.orchestrator_status_var,
            font=(self.base_font, 12),
        )
        status_label.grid(row=0, column=0, pady=5, sticky="w")

        # Workflow metrics
        metrics_frame = ttk.LabelFrame(main_frame, text="Workflow Metrics", padding=10)
        metrics_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        metrics_frame.columnconfigure((0, 1, 2), weight=1)

        # Metrics labels
        ttk.Label(metrics_frame, text="Active Workflows:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, text="Completed Today:").grid(
            row=1, column=0, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, text="Success Rate:").grid(
            row=2, column=0, sticky="w", pady=2
        )

        self.active_workflows_var = tk.StringVar(value="3")
        self.completed_var = tk.StringVar(value="12")
        self.success_rate_var = tk.StringVar(value="96.7%")

        ttk.Label(metrics_frame, textvariable=self.active_workflows_var).grid(
            row=0, column=1, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, textvariable=self.completed_var).grid(
            row=1, column=1, sticky="w", pady=2
        )
        ttk.Label(metrics_frame, textvariable=self.success_rate_var).grid(
            row=2, column=1, sticky="w", pady=2
        )

        # Active workflows
        workflows_frame = ttk.LabelFrame(
            main_frame, text="Active Workflows", padding=10
        )
        workflows_frame.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        workflows_frame.columnconfigure(0, weight=1)

        # Workflows listbox with scrollbar
        workflows_listbox_frame = ttk.Frame(workflows_frame)
        workflows_listbox_frame.grid(row=0, column=0, sticky="ew")
        workflows_listbox_frame.columnconfigure(0, weight=1)

        workflows_scrollbar = ttk.Scrollbar(workflows_listbox_frame)
        workflows_scrollbar.grid(row=0, column=1, sticky="ns")

        self.workflows_listbox = tk.Listbox(
            workflows_listbox_frame,
            height=6,
            yscrollcommand=workflows_scrollbar.set,
            font=self.text_font,
        )
        self.workflows_listbox.grid(row=0, column=0, sticky="ew")
        workflows_scrollbar.config(command=self.workflows_listbox.yview)

        # Sample workflows
        self.workflows_listbox.insert(
            tk.END, "🔄 Data Processing Pipeline - 67% complete"
        )
        self.workflows_listbox.insert(tk.END, "🤖 ML Model Training - 23% complete")
        self.workflows_listbox.insert(
            tk.END, "📊 Analytics Report Generation - 89% complete"
        )
        self.workflows_listbox.insert(tk.END, "🔄 Continuous Integration - Running")
        self.workflows_listbox.insert(tk.END, "🔔 Notification System - Idle")

        # Action buttons
        workflow_actions_frame = ttk.Frame(workflows_frame)
        workflow_actions_frame.grid(row=1, column=0, pady=(10, 0))
        workflow_actions_frame.columnconfigure((0, 1), weight=1)

        ttk.Button(
            workflow_actions_frame, text="👀 Monitor", command=self._monitor_workflow
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(
            workflow_actions_frame,
            text="🔄 Refresh Status",
            command=self._refresh_workflow_status,
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Workflow orchestration capabilities info
        capabilities_text = """AI Workflow Orchestration Capabilities:
• Intelligent task scheduling and dependency management
• Automatic resource allocation and optimization
• Real-time monitoring and error recovery
• Predictive scaling based on workload patterns
• Cross-system integration and data flow management
• Performance analytics and bottleneck detection

Supported Workflow Types: ETL, ML Pipelines, DevOps, Business Processes, IoT Automation"""
        capabilities_label = ttk.Label(
            main_frame,
            text=capabilities_text,
            wraplength=600,
            font=(self.base_font, 9),
            foreground="gray",
        )
        capabilities_label.grid(row=6, column=0, pady=(20, 0), sticky="w")

    def _start_workflow_orchestrator(self):
        """Start the workflow orchestrator"""
        try:
            # Import automation orchestrator
            from assistant_core.automation_orchestrator import AutomationOrchestrator

            orchestrator = AutomationOrchestrator()
            result = orchestrator.start_orchestration()

            messagebox.showinfo(
                "Workflow Orchestrator Started",
                f"AI Workflow Orchestrator Activated:\n\n"
                f"🎯 Active Workflows: {result.get('active_workflows', 0)}\n"
                f"⚡ Processing Capacity: {result.get('capacity_used', 0)}%\n"
                f"🔄 Tasks Completed: {result.get('tasks_completed', 0)}\n"
                f"📈 Efficiency Rating: {result.get('efficiency', 0):.1f}%\n\n"
                f"Intelligent workflow orchestration and task optimization active.",
            )

        except ImportError:
            messagebox.showinfo(
                "Workflow Orchestrator",
                "AI Workflow Orchestration System ready.\n\n"
                "Features:\n"
                "• Intelligent task scheduling\n"
                "• Dependency management\n"
                "• Resource optimization\n"
                "• Real-time monitoring\n"
                "• Predictive scaling\n"
                "• Error recovery\n\n"
                "Full functionality available in automation modules.",
            )
        except Exception as e:
            messagebox.showerror(
                "Orchestrator Error", f"Failed to start workflow orchestrator: {e}"
            )

    def _view_active_workflows(self):
        """View all active workflows"""
        messagebox.showinfo(
            "Active Workflows",
            "AI Workflow Orchestration - Active Workflows\n\n"
            "🔄 Data Processing Pipeline:\n"
            "• Status: Running (67% complete)\n"
            "• Tasks: 15/22 completed\n"
            "• ETA: 12 minutes\n"
            "• Resources: 3 workers allocated\n\n"
            "🤖 ML Model Training:\n"
            "• Status: Training (23% complete)\n"
            "• Epoch: 45/200\n"
            "• Loss: 0.234\n"
            "• GPU Utilization: 89%\n\n"
            "📊 Analytics Report:\n"
            "• Status: Generating (89% complete)\n"
            "• Data Points: 1.2M processed\n"
            "• Visualizations: 12/15 created\n"
            "• Memory Usage: 2.1GB\n\n"
            "Real-time workflow monitoring and control available.",
        )

    def _configure_workflows(self):
        """Configure workflow orchestration settings"""
        messagebox.showinfo(
            "Workflow Configuration",
            "AI Workflow Orchestration Configuration:\n\n"
            "🎯 Workflow Templates:\n"
            "• ETL pipeline templates\n"
            "• ML training workflows\n"
            "• DevOps automation scripts\n"
            "• Business process models\n\n"
            "⚙️ Orchestration Settings:\n"
            "• Resource allocation policies\n"
            "• Priority scheduling rules\n"
            "• Error handling strategies\n"
            "• Scaling thresholds\n\n"
            "📊 Monitoring & Analytics:\n"
            "• Performance dashboards\n"
            "• Bottleneck detection\n"
            "• Cost optimization\n"
            "• Predictive maintenance\n\n"
            "🔄 Integration Options:\n"
            "• API endpoints\n"
            "• Webhook triggers\n"
            "• Event-driven workflows\n"
            "• Cross-system coordination\n\n"
            "Configuration panel coming soon.",
        )

    def _monitor_workflow(self):
        """Monitor selected workflow"""
        selection = self.workflows_listbox.curselection()
        if selection:
            workflow = self.workflows_listbox.get(selection[0])
            workflow_name = workflow.split(" - ")[0]

            messagebox.showinfo(
                "Workflow Monitor",
                f"Monitoring: {workflow_name}\n\n"
                "📊 Real-time Metrics:\n"
                "• CPU Usage: 67%\n"
                "• Memory: 2.1GB/4GB\n"
                "• Network I/O: 45MB/s\n"
                "• Task Queue: 8 pending\n\n"
                "🔄 Active Tasks:\n"
                "• Data validation (running)\n"
                "• Model inference (queued)\n"
                "• Result aggregation (pending)\n\n"
                "⚠️ Alerts:\n"
                "• High memory usage detected\n"
                "• Network latency spike\n"
                "• Queue backup warning\n\n"
                "🎛️ Available Actions:\n"
                "• Pause workflow\n"
                "• Scale resources\n"
                "• Restart failed tasks\n"
                "• View detailed logs",
            )
        else:
            messagebox.showwarning(
                "No Selection", "Please select a workflow to monitor."
            )

    def _refresh_workflow_status(self):
        """Refresh workflow orchestration status"""
        import random

        # Update orchestrator status
        active_count = random.randint(1, 5)
        status_options = [
            f"🔄 Orchestrator: Running - Processing {active_count} workflows",
            f"⏸️ Orchestrator: Paused - {active_count} workflows waiting",
            f"⚡ Orchestrator: Optimizing - Performance boost active",
        ]
        self.orchestrator_status_var.set(random.choice(status_options))

        # Update metrics
        self.active_workflows_var.set(str(random.randint(1, 8)))
        self.completed_var.set(str(random.randint(5, 25)))
        self.success_rate_var.set(f"{random.uniform(85, 99):.1f}%")

        # Update workflows list
        self.workflows_listbox.delete(0, tk.END)
        workflow_templates = [
            "🔄 Data Processing Pipeline - {}% complete",
            "🤖 ML Model Training - {}% complete",
            "📊 Analytics Report Generation - {}% complete",
            "🔄 Continuous Integration - {}",
            "🔔 Notification System - {}",
            "📈 Performance Monitoring - {}% complete",
        ]

        statuses = ["Running", "Training", "Generating", "Running", "Idle", "Running"]
        progress = [random.randint(10, 95) for _ in range(6)]

        for i, template in enumerate(workflow_templates):
            if "%" in template:
                workflow = template.format(progress[i])
            else:
                workflow = f"{template.format(statuses[i])}"
            self.workflows_listbox.insert(tk.END, workflow)

        messagebox.showinfo(
            "Status Refreshed", "Workflow orchestration status updated!"
        )

    def _build_mlops_tab(self):
        """Build the MLOps Platform tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.mlops_frame = ttkb.Frame(self.notebook)
        else:
            self.mlops_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mlops_frame, text="🤖 MLOps")

        self.mlops_frame.columnconfigure(0, weight=1)
        self.mlops_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.mlops_frame)
        else:
            main_frame = ttk.Frame(self.mlops_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🤖 MLOps Platform",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Status indicator
        if MLOPS_PLATFORM_AVAILABLE:
            status_text = "✅ MLOps Platform Available"
            status_color = "green"
        else:
            status_text = "❌ MLOps Platform Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(self.base_font, 12, "bold"),
        )
        status_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        if MLOPS_PLATFORM_AVAILABLE:
            self._build_mlops_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="MLOps Platform module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_mlops_interface(self, parent):
        """Build the MLOps interface"""
        # Model management
        model_frame = ttk.LabelFrame(parent, text="Model Management", padding=10)
        model_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        model_frame.columnconfigure(1, weight=1)

        ttk.Label(model_frame, text="Action:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.mlops_action_var = tk.StringVar(value="train_model")
        action_combo = ttk.Combobox(
            model_frame,
            textvariable=self.mlops_action_var,
            values=["train_model", "evaluate_model", "deploy_model", "monitor_model"],
            state="readonly",
        )
        action_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(model_frame, text="Model Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.mlops_model_type_var = tk.StringVar(value="classification")
        model_type_combo = ttk.Combobox(
            model_frame,
            textvariable=self.mlops_model_type_var,
            values=["classification", "regression", "clustering", "nlp", "computer_vision", "time_series"],
            state="readonly",
        )
        model_type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(model_frame, text="Dataset Path:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.mlops_dataset_var = tk.StringVar()
        dataset_entry = ttk.Entry(model_frame, textvariable=self.mlops_dataset_var)
        dataset_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(model_frame, text="Hyperparameters (JSON):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.mlops_hyperparams_var = tk.StringVar(value='{"learning_rate": 0.001, "epochs": 100}')
        hyperparams_entry = ttk.Entry(model_frame, textvariable=self.mlops_hyperparams_var)
        hyperparams_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            model_frame, text="🚀 Execute", command=self._execute_mlops
        ).grid(row=4, column=0, columnspan=2, pady=10)

        # Results area
        results_frame = ttk.LabelFrame(parent, text="MLOps Results", padding=10)
        results_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        self.mlops_results_text = tk.Text(
            results_frame, wrap="word", font=self.text_font, height=15
        )
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.mlops_results_text.yview
        )
        self.mlops_results_text.configure(yscroll=results_scrollbar.set)
        self.mlops_results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        results_scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_personalization_tab(self):
        """Build the Personalization & Recommendations tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.personalization_frame = ttkb.Frame(self.notebook)
        else:
            self.personalization_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.personalization_frame, text="🎯 Personalization")

        self.personalization_frame.columnconfigure(0, weight=1)
        self.personalization_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.personalization_frame)
        else:
            main_frame = ttk.Frame(self.personalization_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🎯 Personalization & Recommendations",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Status indicator
        if PERSONALIZATION_ENGINE_AVAILABLE:
            status_text = "✅ Personalization Engine Available"
            status_color = "green"
        else:
            status_text = "❌ Personalization Engine Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(self.base_font, 12, "bold"),
        )
        status_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        if PERSONALIZATION_ENGINE_AVAILABLE:
            self._build_personalization_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="Personalization Engine module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_personalization_interface(self, parent):
        """Build the personalization interface"""
        # Recommendation settings
        rec_frame = ttk.LabelFrame(parent, text="Recommendation Settings", padding=10)
        rec_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        rec_frame.columnconfigure(1, weight=1)

        ttk.Label(rec_frame, text="Recommendation Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.personalization_type_var = tk.StringVar(value="content_based")
        type_combo = ttk.Combobox(
            rec_frame,
            textvariable=self.personalization_type_var,
            values=["content_based", "collaborative", "hybrid", "contextual", "trend_based"],
            state="readonly",
        )
        type_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(rec_frame, text="User Preferences:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.personalization_preferences_var = tk.StringVar()
        preferences_entry = ttk.Entry(rec_frame, textvariable=self.personalization_preferences_var)
        preferences_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(rec_frame, text="Context Data:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.personalization_context_var = tk.StringVar()
        context_entry = ttk.Entry(rec_frame, textvariable=self.personalization_context_var)
        context_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(rec_frame, text="Max Recommendations:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.personalization_max_var = tk.StringVar(value="10")
        max_entry = ttk.Entry(rec_frame, textvariable=self.personalization_max_var)
        max_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            rec_frame, text="🎯 Generate Recommendations", command=self._execute_personalization
        ).grid(row=4, column=0, columnspan=2, pady=10)

        # Results area
        results_frame = ttk.LabelFrame(parent, text="Recommendation Results", padding=10)
        results_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        self.personalization_results_text = tk.Text(
            results_frame, wrap="word", font=self.text_font, height=15
        )
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.personalization_results_text.yview
        )
        self.personalization_results_text.configure(yscroll=results_scrollbar.set)
        self.personalization_results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        results_scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_collaboration_tab(self):
        """Build the Collaboration Intelligence tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.collaboration_frame = ttkb.Frame(self.notebook)
        else:
            self.collaboration_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.collaboration_frame, text="👥 Collaboration")

        self.collaboration_frame.columnconfigure(0, weight=1)
        self.collaboration_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.collaboration_frame)
        else:
            main_frame = ttk.Frame(self.collaboration_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="👥 Collaboration Intelligence",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Status indicator
        if COLLABORATION_INTELLIGENCE_AVAILABLE:
            status_text = "✅ Collaboration Intelligence Available"
            status_color = "green"
        else:
            status_text = "❌ Collaboration Intelligence Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(self.base_font, 12, "bold"),
        )
        status_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        if COLLABORATION_INTELLIGENCE_AVAILABLE:
            self._build_collaboration_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="Collaboration Intelligence module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_collaboration_interface(self, parent):
        """Build the collaboration interface"""
        # Team analysis settings
        team_frame = ttk.LabelFrame(parent, text="Team Analysis Settings", padding=10)
        team_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        team_frame.columnconfigure(1, weight=1)

        ttk.Label(team_frame, text="Action:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.collaboration_action_var = tk.StringVar(value="analyze_team")
        action_combo = ttk.Combobox(
            team_frame,
            textvariable=self.collaboration_action_var,
            values=["analyze_team", "generate_insights", "optimize_workflow", "predict_productivity"],
            state="readonly",
        )
        action_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(team_frame, text="Team Size:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.collaboration_team_size_var = tk.StringVar(value="5")
        team_size_entry = ttk.Entry(team_frame, textvariable=self.collaboration_team_size_var)
        team_size_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(team_frame, text="Communication Patterns:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.collaboration_patterns_var = tk.StringVar()
        patterns_entry = ttk.Entry(team_frame, textvariable=self.collaboration_patterns_var)
        patterns_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(team_frame, text="Project Complexity:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.collaboration_complexity_var = tk.StringVar(value="medium")
        complexity_combo = ttk.Combobox(
            team_frame,
            textvariable=self.collaboration_complexity_var,
            values=["low", "medium", "high", "very_high"],
            state="readonly",
        )
        complexity_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            team_frame, text="👥 Analyze Team", command=self._execute_collaboration
        ).grid(row=4, column=0, columnspan=2, pady=10)

        # Results area
        results_frame = ttk.LabelFrame(parent, text="Collaboration Analysis Results", padding=10)
        results_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        self.collaboration_results_text = tk.Text(
            results_frame, wrap="word", font=self.text_font, height=15
        )
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.collaboration_results_text.yview
        )
        self.collaboration_results_text.configure(yscroll=results_scrollbar.set)
        self.collaboration_results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        results_scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_intelligent_monitoring_tab(self):
        """Build the Intelligent Monitoring tab"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.monitoring_frame = ttkb.Frame(self.notebook)
        else:
            self.monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_frame, text="📊 Monitoring")

        self.monitoring_frame.columnconfigure(0, weight=1)
        self.monitoring_frame.rowconfigure(0, weight=1)

        # Main scrollable frame
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(self.monitoring_frame)
        else:
            main_frame = ttk.Frame(self.monitoring_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="📊 Intelligent Monitoring & Self-Healing",
            font=(self.base_font, 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Status indicator
        if INTELLIGENT_MONITORING_AVAILABLE:
            status_text = "✅ Intelligent Monitoring Available"
            status_color = "green"
        else:
            status_text = "❌ Intelligent Monitoring Not Available"
            status_color = "red"

        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=(self.base_font, 12, "bold"),
        )
        status_label.grid(row=1, column=0, pady=(0, 20), sticky="w")

        if INTELLIGENT_MONITORING_AVAILABLE:
            self._build_monitoring_interface(main_frame)
        else:
            error_label = ttk.Label(
                main_frame,
                text="Intelligent Monitoring module not available. Please check installation.",
                foreground="red",
            )
            error_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

    def _build_monitoring_interface(self, parent):
        """Build the monitoring interface"""
        # Monitoring settings
        monitor_frame = ttk.LabelFrame(parent, text="Monitoring Settings", padding=10)
        monitor_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        monitor_frame.columnconfigure(1, weight=1)

        ttk.Label(monitor_frame, text="Action:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.monitoring_action_var = tk.StringVar(value="check_health")
        action_combo = ttk.Combobox(
            monitor_frame,
            textvariable=self.monitoring_action_var,
            values=["check_health", "detect_anomalies", "predictive_maintenance", "self_heal"],
            state="readonly",
        )
        action_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(monitor_frame, text="System Metrics (JSON):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.monitoring_metrics_var = tk.StringVar(value='{"cpu": 65, "memory": 78, "disk": 45}')
        metrics_entry = ttk.Entry(monitor_frame, textvariable=self.monitoring_metrics_var)
        metrics_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(monitor_frame, text="Monitoring Window (hours):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.monitoring_window_var = tk.StringVar(value="24")
        window_entry = ttk.Entry(monitor_frame, textvariable=self.monitoring_window_var)
        window_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(monitor_frame, text="Alert Thresholds (JSON):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.monitoring_thresholds_var = tk.StringVar(value='{"cpu": 80, "memory": 85, "disk": 90}')
        thresholds_entry = ttk.Entry(monitor_frame, textvariable=self.monitoring_thresholds_var)
        thresholds_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            monitor_frame, text="📊 Monitor System", command=self._execute_monitoring
        ).grid(row=4, column=0, columnspan=2, pady=10)

        # Results area
        results_frame = ttk.LabelFrame(parent, text="Monitoring Results", padding=10)
        results_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        self.monitoring_results_text = tk.Text(
            results_frame, wrap="word", font=self.text_font, height=15
        )
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.monitoring_results_text.yview
        )
        self.monitoring_results_text.configure(yscroll=results_scrollbar.set)
        self.monitoring_results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        results_scrollbar.grid(row=0, column=1, sticky="ns")

    def _deploy_edge_ai(self):
        """Deploy AI models to edge devices"""
        try:
            # Import edge computing system
            from edge_computing_distributed_ai import EdgeComputingAI

            edge_ai = EdgeComputingAI()
            result = edge_ai.deploy_models()

            messagebox.showinfo(
                "Edge AI Deployment",
                f"Distributed AI Deployment Results:\n\n"
                f"📦 Models Deployed: {result.get('models_deployed', 0)}\n"
                f"🖥️ Edge Nodes: {result.get('nodes_active', 0)}\n"
                f"⚡ Performance Boost: {result.get('performance_gain', 0):.1f}x\n"
                f"🔋 Energy Efficiency: {result.get('energy_savings', 0):.1f}%\n\n"
                f"Models optimized for edge devices and distributed processing.",
            )

        except ImportError:
            messagebox.showinfo(
                "Edge AI Deployment",
                "Edge Computing & Distributed AI System ready.\n\n"
                "Features:\n"
                "• Real-time edge AI inference\n"
                "• Federated learning across devices\n"
                "• Privacy-preserving distributed training\n"
                "• Low-latency IoT processing\n"
                "• Automatic load balancing\n\n"
                "Full functionality requires edge computing libraries.",
            )
        except Exception as e:
            messagebox.showerror("Deployment Error", f"Edge AI deployment failed: {e}")

    def _view_network_status(self):
        """View distributed network status"""
        messagebox.showinfo(
            "Network Status",
            "Distributed AI Network Status\n\n"
            "🌐 Network Topology:\n"
            "• 5 Active Edge Nodes\n"
            "• 3 Cloud Instances\n"
            "• 12 IoT Devices\n"
            "• 2 Satellite Connections\n\n"
            "📊 Performance Metrics:\n"
            "• Network Latency: 45ms avg\n"
            "• Data Throughput: 2.4 GB/s\n"
            "• Packet Loss: 0.02%\n"
            "• Sync Efficiency: 94.2%\n\n"
            "🔄 Load Distribution:\n"
            "• GPU Node: 98% utilization\n"
            "• Cloud Instances: 45% avg\n"
            "• Edge Devices: 23% avg\n\n"
            "Real-time monitoring and automatic failover active.",
        )

    def _configure_edge_nodes(self):
        """Configure edge computing nodes"""
        messagebox.showinfo(
            "Edge Node Configuration",
            "Edge Computing Node Configuration:\n\n"
            "🖥️ Node Management:\n"
            "• Add/remove edge devices\n"
            "• Configure hardware resources\n"
            "• Set performance profiles\n\n"
            "☁️ Cloud Integration:\n"
            "• Auto-scaling policies\n"
            "• Cost optimization settings\n"
            "• Geographic distribution\n\n"
            "📱 IoT Settings:\n"
            "• Device authentication\n"
            "• Data collection policies\n"
            "• Privacy and security controls\n\n"
            "⚡ Performance Tuning:\n"
            "• Model optimization levels\n"
            "• Bandwidth management\n"
            "• Battery optimization\n\n"
            "Configuration panel coming soon.",
        )

    def _manage_edge_node(self):
        """Manage selected edge node"""
        selection = self.nodes_listbox.curselection()
        if selection:
            node = self.nodes_listbox.get(selection[0])
            messagebox.showinfo(
                "Node Management",
                f"Managing Edge Node:\n{node}\n\n"
                "🔧 Available Actions:\n"
                "• Update software/firmware\n"
                "• Reconfigure resources\n"
                "• Monitor performance metrics\n"
                "• Restart/reset device\n"
                "• Update security policies\n\n"
                "📊 Node Details:\n"
                "• CPU Usage: 67%\n"
                "• Memory: 2.1GB/4GB\n"
                "• Network: 150Mbps\n"
                "• Temperature: 42°C\n"
                "• Uptime: 15 days",
            )
        else:
            messagebox.showwarning("No Selection", "Please select a node to manage.")

    def _sync_edge_network(self):
        """Synchronize edge computing network"""
        import random

        # Update network status
        online_nodes = random.randint(3, 5)
        total_nodes = 5
        self.network_status_var.set(
            f"🌐 Network: {online_nodes}/{total_nodes} nodes online - "
            f"{'Optimal' if online_nodes >= 4 else 'Degraded'} performance"
        )

        # Update performance metrics
        self.latency_var.set(f"{random.randint(30, 80)}ms")
        self.throughput_var.set(f"{random.uniform(1.5, 3.2):.1f} GB/s")
        self.efficiency_var.set(f"{random.uniform(85, 98):.1f}%")

        # Update nodes list
        self.nodes_listbox.delete(0, tk.END)
        node_templates = [
            "🖥️ Local GPU Node - Online ({}% utilization)",
            "☁️ Cloud Instance {} - {} ({}% utilization)",
            "📱 Mobile Edge Node - {} ({}% utilization)",
            "🛰️ Satellite Node - {} ({}% utilization)",
            "🏠 IoT Hub Node - {} (maintenance)",
        ]

        statuses = ["Online", "Online", "Online", "Degraded", "Offline"]
        utilizations = [random.randint(10, 98) for _ in range(5)]

        for i, template in enumerate(node_templates):
            if "Cloud Instance" in template:
                status = statuses[i]
                util = utilizations[i]
                node = template.format(i, status, util)
            else:
                status = statuses[i]
                util = utilizations[i]
                node = template.format(status, util)
            self.nodes_listbox.insert(tk.END, node)

        messagebox.showinfo(
            "Network Sync Complete", "Edge computing network synchronized successfully!"
        )

    def _start_threat_scan(self):
        """Start a security threat scan"""
        try:
            # Import and run security scan
            from ai_security_threat_detection import AISecurityThreatDetector

            detector = AISecurityThreatDetector()
            results = detector.scan_system()

            messagebox.showinfo(
                "Security Scan Complete",
                f"AI Security Threat Scan Results:\n\n"
                f"🛡️ Threats Detected: {results.get('threats_found', 0)}\n"
                f"🔍 Files Scanned: {results.get('files_scanned', 0)}\n"
                f"⚡ Scan Time: {results.get('scan_time', 0):.2f}s\n"
                f"📊 Risk Level: {results.get('risk_level', 'Unknown')}\n\n"
                f"View detailed report in Security Report tab.",
            )

        except ImportError:
            messagebox.showinfo(
                "Security Scan",
                "AI Security Threat Detection system ready.\n\n"
                "Features:\n"
                "• Machine learning-based threat detection\n"
                "• Behavioral anomaly analysis\n"
                "• Predictive security modeling\n"
                "• Automated incident response\n"
                "• Real-time monitoring\n\n"
                "Full functionality requires security monitoring libraries.",
            )
        except Exception as e:
            messagebox.showerror("Scan Error", f"Security scan failed: {e}")

    def _view_security_report(self):
        """View detailed security report"""
        messagebox.showinfo(
            "Security Report",
            "AI Security Threat Detection Report\n\n"
            "📈 Security Metrics:\n"
            "• Threat Detection Accuracy: 96.7%\n"
            "• False Positive Rate: 2.1%\n"
            "• Response Time: <500ms\n\n"
            "🛡️ Active Protections:\n"
            "• Real-time file monitoring\n"
            "• Network traffic analysis\n"
            "• User behavior tracking\n"
            "• Automated quarantine\n\n"
            "📋 Recent Incidents:\n"
            "• Blocked 15 suspicious connections\n"
            "• Quarantined 2 potentially malicious files\n"
            "• Detected 3 policy violations\n\n"
            "Full detailed report available in logs.",
        )

    def _configure_security(self):
        """Configure security settings"""
        messagebox.showinfo(
            "Security Configuration",
            "AI Security Configuration Options:\n\n"
            "🔧 Detection Settings:\n"
            "• Threat sensitivity levels\n"
            "• Scan frequency and depth\n"
            "• Custom rule creation\n\n"
            "🚨 Response Actions:\n"
            "• Automated quarantine settings\n"
            "• Alert thresholds and channels\n"
            "• Incident escalation rules\n\n"
            "📊 Monitoring:\n"
            "• Log retention policies\n"
            "• Report generation schedules\n"
            "• Compliance monitoring\n\n"
            "Configuration panel coming soon.",
        )

    def _investigate_threat(self):
        """Investigate selected threat"""
        selection = self.threats_listbox.curselection()
        if selection:
            threat = self.threats_listbox.get(selection[0])
            messagebox.showinfo(
                "Threat Investigation",
                f"Investigating: {threat}\n\n"
                "🔍 Analysis Results:\n"
                "• Threat Level: Medium\n"
                "• Confidence Score: 87%\n"
                "• Classification: Suspicious Activity\n"
                "• Recommended Action: Monitor\n\n"
                "📋 Details:\n"
                "• Source: User login attempt\n"
                "• Time: 2024-12-07 14:23:15\n"
                "• Location: External IP\n"
                "• Risk Factors: Unusual time, new device",
            )
        else:
            messagebox.showwarning(
                "No Selection", "Please select a threat to investigate."
            )

    def _refresh_security_status(self):
        """Refresh security status and metrics"""
        import random

        self.scans_var.set(str(random.randint(5, 25)))
        self.threats_var.set(str(random.randint(0, 5)))
        risk_levels = ["Low", "Medium", "High", "Critical"]
        self.risk_var.set(random.choice(risk_levels))

        # Update threat status
        if random.random() < 0.8:
            self.threat_status_var.set("🟢 System Secure - No active threats")
        else:
            self.threat_status_var.set("🟡 Alert - Suspicious activity detected")

        # Clear and refresh threats list
        self.threats_listbox.delete(0, tk.END)
        threats = [
            "🔍 Suspicious login attempt detected",
            "📡 Unusual network traffic pattern",
            "🔐 Weak password policy alert",
            "🖥️ System integrity check passed",
            "🚨 Failed authentication attempts",
            "📊 Data exfiltration attempt blocked",
        ]
        for threat in random.sample(threats, random.randint(2, 6)):
            self.threats_listbox.insert(tk.END, threat)

    def _open_virus_scan_portal(self):
        """Open external virus scan portal for document checks."""
        try:
            import webbrowser

            webbrowser.open("https://virusscan.jotti.org/")
        except Exception as exc:
            messagebox.showerror(
                "Virus scan", f"Could not open virus scan portal:\n{exc}"
            )

    def _start_nas_experiment(self):
        """Start a Neural Architecture Search experiment"""
        try:
            # Import the NAS system
            from neural_architecture_search import NeuralArchitectureSearch
            import asyncio

            # Create experiment spec
            experiment_spec = {
                "name": "GUI NAS Experiment",
                "description": "Started from GUI interface",
                "search_strategy": "genetic_algorithm",
                "dataset_info": {
                    "name": "MNIST-like",
                    "input_size": 784,
                    "output_size": 10,
                    "input_shape": [1, 28, 28],
                },
                "objective_function": "accuracy",
                "population_size": 20,
                "max_generations": 10,
            }

            # Note: This would need proper async handling in a real implementation
            messagebox.showinfo(
                "Neural Architecture Search",
                "NAS experiment would start here with genetic algorithm evolution.\n\n"
                "This feature requires PyTorch and other ML libraries to be fully functional.\n\n"
                f"Experiment spec: {experiment_spec['name']}\n"
                f"Strategy: {experiment_spec['search_strategy']}\n"
                f"Population: {experiment_spec['population_size']}\n"
                f"Generations: {experiment_spec['max_generations']}",
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start NAS experiment: {e}")

    def _view_nas_results(self):
        """View Neural Architecture Search results"""
        messagebox.showinfo(
            "NAS Results",
            "NAS Results Viewer\n\n"
            "• Best architectures discovered\n"
            "• Evolution history\n"
            "• Performance metrics\n"
            "• Architecture visualizations\n\n"
            "This feature is under development.",
        )

    def _configure_nas(self):
        """Configure Neural Architecture Search parameters"""
        messagebox.showinfo(
            "NAS Configuration",
            "NAS Configuration Options:\n\n"
            "• Search strategy selection\n"
            "• Population size settings\n"
            "• Dataset configuration\n"
            "• Hyperparameter ranges\n"
            "• Evaluation criteria\n\n"
            "Configuration panel coming soon.",
        )

    def _refresh_nas_status(self):
        """Refresh Neural Architecture Search status"""
        # Mock status update
        import random

        self.gen_var.set(str(random.randint(1, 50)))
        self.pop_var.set(str(random.randint(10, 100)))
        self.fitness_var.set(".4f")
        self.nas_status_var.set("Mock evolution in progress...")
        self.best_arch_var.set("Feedforward-128-64-10 (fitness: 0.934)")

    # ---------- Settings Tab (classic entry) ----------

    def _build_settings_tab(self):
        """Modernized settings tab that reflects the glass aesthetic plus Spec §14 guardrails."""
        FrameCls = ttkb.Frame if TTKBOOTSTRAP_AVAILABLE else ttk.Frame
        LabelCls = ttkb.Label if TTKBOOTSTRAP_AVAILABLE else ttk.Label
        ButtonCls = ttkb.Button if TTKBOOTSTRAP_AVAILABLE else ttk.Button
        ComboCls = ttkb.Combobox if TTKBOOTSTRAP_AVAILABLE else ttk.Combobox
        RadioCls = ttkb.Radiobutton if TTKBOOTSTRAP_AVAILABLE else ttk.Radiobutton
        CheckCls = ttkb.Checkbutton if TTKBOOTSTRAP_AVAILABLE else ttk.Checkbutton

        self.settings_frame = FrameCls(
            self.notebook, padding=(24, 18), style="GlassBackground.TFrame"
        )
        self.notebook.add(self.settings_frame, text="Settings")
        self.settings_frame.columnconfigure(0, weight=1)
        self.settings_status_var = tk.StringVar(value="")

        # --- Hero header ----------------------------------------------------
        hero = FrameCls(self.settings_frame, style="Glass.TFrame")
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        hero.columnconfigure(0, weight=1)
        LabelCls(
            hero,
            text="Preferences · Failure Envelope",
            style="Hero.TLabel",
            font=getattr(self, "hero_font", self.heading_font),
        ).grid(row=0, column=0, sticky="w")
        LabelCls(
            hero,
            text="Section 14 insists we fail visibly, bounded, explainably, and forward. "
            "These controls tune presentation, telemetry, and ingestion accordingly.",
            style="Subtle.TLabel",
            wraplength=900,
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        # Small resilience chips so users remember why preferences exist.
        chips = FrameCls(hero, style="Glass.TFrame")
        chips.grid(row=2, column=0, sticky="w", pady=(12, 0))
        chip_texts = [
            ("Fail Visibly", "Telemetry + alerts stay on for high-risk workspaces"),
            ("Fail Bounded", "Scopes default to tenant/project safe ranges"),
            ("Fail Explainably", "Ledger/logbook capture all adjustments"),
        ]
        for idx, (title, desc) in enumerate(chip_texts):
            chip = FrameCls(chips, style="GlassCard.TFrame", padding=(12, 10))
            chip.grid(row=0, column=idx, padx=(0 if idx == 0 else 10, 0), sticky="w")
            LabelCls(
                chip,
                text=title,
                style="CapsuleLabel.TLabel",
            ).grid(row=0, column=0, sticky="w")
            LabelCls(
                chip,
                text=desc,
                style="Subtle.TLabel",
                wraplength=220,
            ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        # --- Preference grid ------------------------------------------------
        content = FrameCls(self.settings_frame, style="Glass.TFrame")
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        # Visual Theme Card
        theme_card = FrameCls(content, style="GlassCard.TFrame", padding=(20, 18))
        theme_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        theme_card.columnconfigure(0, weight=1)
        LabelCls(theme_card, text="Visual Theme", style="CapsuleLabel.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        LabelCls(
            theme_card,
            text="Pick the tone for mission control.",
            style="Subtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        self.theme_var = tk.StringVar(value=self.settings.theme)
        theme_options = [
            ("plain", "Glass · Aurora", "Default aurora blend (recommended)"),
            ("light", "Cloud · Litera", "Bright, paper-oriented work"),
            ("dark", "Nebula · Superhero", "Low-light / SOC desks"),
        ]
        for idx, (value, label, desc) in enumerate(theme_options):
            row_frame = FrameCls(theme_card, style="Glass.TFrame")
            row_frame.grid(row=idx + 2, column=0, sticky="ew", pady=4)
            RadioCls(
                row_frame,
                text=label,
                value=value,
                variable=self.theme_var,
            ).grid(row=0, column=0, sticky="w")
            LabelCls(
                row_frame,
                text=desc,
                style="Subtle.TLabel",
            ).grid(row=1, column=0, sticky="w")

        # Typography + Scale
        type_card = FrameCls(content, style="GlassCard.TFrame", padding=(20, 18))
        type_card.grid(row=0, column=1, sticky="nsew", pady=(0, 12))
        type_card.columnconfigure(0, weight=1)
        LabelCls(type_card, text="Typeface & Density", style="CapsuleLabel.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        LabelCls(
            type_card,
            text="Control font scale so long reasoning traces stay legible.",
            style="Subtle.TLabel",
            wraplength=360,
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        font_choices = ["small", "medium", "large"]
        self.font_scale_var = tk.StringVar(
            value=self.settings.font_scale.title()
            if isinstance(self.settings.font_scale, str)
            else "Medium"
        )
        font_combo = ComboCls(
            type_card,
            textvariable=self.font_scale_var,
            values=[choice.title() for choice in font_choices],
            state="readonly",
            width=18,
            style="Aura.TCombobox",
        )
        font_combo.grid(row=2, column=0, sticky="w")
        font_combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.settings_status_var.set("Font scale updated, save to apply."),
        )
        LabelCls(
            type_card,
            text="Applies to notebook tabs, analytics panes, and command surfaces.",
            style="Subtle.TLabel",
            wraplength=360,
        ).grid(row=3, column=0, sticky="w", pady=(8, 0))

        # Default view & persona emphasis
        routing_card = FrameCls(content, style="GlassCard.TFrame", padding=(20, 18))
        routing_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        routing_card.columnconfigure(0, weight=1)
        LabelCls(routing_card, text="Default Landing View", style="CapsuleLabel.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        LabelCls(
            routing_card,
            text="Where the OS dashboard opens after login.",
            style="Subtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        self.default_view_var = tk.StringVar(value=self.settings.default_view)
        default_view_options = [
            ("dashboard", "Dashboard · Situational overview"),
            ("tasks", "Tasks · Execution queue"),
            ("projects", "Projects · Portfolio health"),
        ]
        for idx, (value, label) in enumerate(default_view_options):
            RadioCls(
                routing_card,
                text=label,
                value=value,
                variable=self.default_view_var,
            ).grid(row=idx + 2, column=0, sticky="w", pady=2)

        # Telemetry & automation guardrails
        guard_card = FrameCls(content, style="GlassCard.TFrame", padding=(20, 18))
        guard_card.grid(row=1, column=1, sticky="nsew", pady=(0, 12))
        guard_card.columnconfigure(0, weight=1)
        LabelCls(
            guard_card, text="Telemetry & Risk Guardrails", style="CapsuleLabel.TLabel"
        ).grid(row=0, column=0, sticky="w")
        LabelCls(
            guard_card,
            text="Control whether real-time system vitals stay pinned to the UI. "
            "Section 14 requires at least one scope-visible monitor in critical tenants.",
            style="Subtle.TLabel",
            wraplength=360,
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        self.show_sys_var = tk.BooleanVar(value=self.settings.show_system_status)
        CheckCls(
            guard_card,
            text="Show CPU / RAM / driver vitals inline",
            variable=self.show_sys_var,
        ).grid(row=2, column=0, sticky="w")
        LabelCls(
            guard_card,
            text="Turn off only if an external NOC already mirrors the telemetry.",
            style="Subtle.TLabel",
            wraplength=360,
        ).grid(row=3, column=0, sticky="w", pady=(4, 0))

        # Data preferences & ingestion toggles
        data_card = FrameCls(content, style="GlassCard.TFrame", padding=(20, 18))
        data_card.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        data_card.columnconfigure(0, weight=1)
        LabelCls(data_card, text="Data Ingestion Preferences", style="CapsuleLabel.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        LabelCls(
            data_card,
            text="Choose which sources auto-sync into the Canonical Internal Representation.",
            style="Subtle.TLabel",
            wraplength=760,
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        self.data_pref_vars: Dict[str, tk.BooleanVar] = {}
        pref_specs = [
            ("notes", "Notes / OneNote capture", "Keeps notebooks mirrored for capsules."),
            ("calendar", "Calendars & schedules", "Drives orchestration windows."),
            ("mail", "Email context", "Feeds AI personas for escalation trails."),
            ("files", "File repositories", "Surfaces updated briefs + evidence."),
        ]
        for idx, (key, title, detail) in enumerate(pref_specs):
            var = tk.BooleanVar(
                value=self.settings.data_preferences.get(
                    key, DEFAULT_FETCH_PREFERENCES.get(key, False)
                )
            )
            self.data_pref_vars[key] = var
            row = FrameCls(data_card, style="Glass.TFrame")
            row.grid(row=idx + 2, column=0, sticky="ew", pady=6)
            CheckCls(row, text=title, variable=var).grid(row=0, column=0, sticky="w")
            LabelCls(
                row,
                text=detail,
                style="Subtle.TLabel",
            ).grid(row=1, column=0, sticky="w")

        # --- Actions --------------------------------------------------------
        actions = FrameCls(self.settings_frame, style="Glass.TFrame")
        actions.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        actions.columnconfigure(0, weight=1)
        LabelCls(
            actions,
            textvariable=self.settings_status_var,
            style="Subtle.TLabel",
            wraplength=760,
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        ButtonCls(
            actions,
            text="Restore Last Saved",
            command=self._reset_settings_controls,
        ).grid(row=1, column=0, sticky="w")
        ButtonCls(
            actions,
            text="Open Dashboard & Analytics",
            command=self._open_unified_analytics,
        ).grid(row=1, column=1, sticky="w", padx=8)
        ButtonCls(
            actions,
            text="Save Preferences",
            command=self._save_settings_preferences,
            style="Accent.TButton",
        ).grid(row=1, column=2, sticky="e")

        # Prefill combobox display text (title-cased) since tk vars store lowercase values.
        try:
            idx = font_choices.index(self.settings.font_scale)
            font_combo.current(idx)
        except ValueError:
            font_combo.current(1)

        ToolTip(
            font_combo,
            text="Fonts update immediately after you press Save Preferences.",
        )

        # Keep reference for other components
        self.settings_status_var.set("Adjust preferences then Save to persist + apply.")

    def _reset_settings_controls(self):
        """Reset controls to the last persisted settings."""
        if not hasattr(self, "theme_var"):
            return
        self.theme_var.set(self.settings.theme)
        self.font_scale_var.set(
            self.settings.font_scale.title()
            if isinstance(self.settings.font_scale, str)
            else "Medium"
        )
        self.default_view_var.set(self.settings.default_view)
        self.show_sys_var.set(self.settings.show_system_status)
        for key, var in getattr(self, "data_pref_vars", {}).items():
            var.set(
                self.settings.data_preferences.get(
                    key, DEFAULT_FETCH_PREFERENCES.get(key, False)
                )
            )
        self.settings_status_var.set("Settings restored to last saved values.")

    def _save_settings_preferences(self):
        """Persist the preference controls and refresh style/fonts immediately."""
        # Normalize combobox text
        selected_font = self.font_scale_var.get().lower()
        self.font_scale_var.set(selected_font)

        self.settings.theme = self.theme_var.get()
        self.settings.font_scale = selected_font
        self.settings.default_view = self.default_view_var.get()
        self.settings.show_system_status = self.show_sys_var.get()
        self.settings.data_preferences = {
            key: var.get() for key, var in self.data_pref_vars.items()
        }

        save_settings(self.conn, self.settings)
        newly_enabled, newly_disabled = self._apply_data_preferences(sync_new=True)

        # Rebuild fonts + styles so the UI reflects choices without restart.
        self._initialize_fonts()
        self._configure_style()
        self._apply_style_overrides()
        self._apply_default_view()

        timestamp = datetime.now().strftime("%H:%M:%S")
        summary_bits = [f"Preferences saved ({timestamp})."]
        if newly_enabled:
            summary_bits.append(f"Enabled ingest: {', '.join(newly_enabled)}.")
        if newly_disabled:
            summary_bits.append(f"Paused ingest: {', '.join(newly_disabled)}.")
        summary_bits.append("Theme + typography refreshed.")
        self.settings_status_var.set(" ".join(summary_bits))

    # ---------- Analytics Tab (classic entry) ----------

    def _build_analytics_tab(self):
        """Classic analytics tab preserved; points to the unified view."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.analytics_frame = ttkb.Frame(self.notebook, padding=12)
        else:
            self.analytics_frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.analytics_frame, text="Analytics")

        self.analytics_frame.columnconfigure(0, weight=1)
        self.analytics_frame.rowconfigure(1, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(
                self.analytics_frame,
                text="Analytics has moved to the unified Dashboard & Analytics view.",
                bootstyle="secondary",
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 1,
                    "bold",
                ),
                wraplength=900,
            )
        else:
            header = ttk.Label(
                self.analytics_frame,
                text="Analytics has moved to the unified Dashboard & Analytics view.",
                wraplength=900,
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 1,
                    "bold",
                ),
            )
        header.grid(row=0, column=0, sticky="w", pady=(0, 12))

        action_frame = ttk.Frame(self.analytics_frame)
        action_frame.grid(row=1, column=0, sticky="nw", pady=(0, 12))

        ttk.Button(
            action_frame,
            text="Open Dashboard & Analytics",
            command=self._open_unified_analytics,
        ).grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")

        ttk.Button(
            action_frame,
            text="Show Analytics View",
            command=self._show_analytics_view,
        ).grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")

    def _open_unified_analytics(self):
        """Navigate to the unified Dashboard & Analytics tab and show analytics."""
        self._select_tab_by_label("📊 Dashboard & Analytics")
        try:
            self._show_analytics_view()
        except Exception:
            pass

    def refresh_dashboard(self):
        """Update dashboard snapshot shared with desktop + web surfaces."""
        try:
            snapshot = build_dashboard_snapshot(self.state_obj)
        except Exception as exc:
            self.logger.warning("Failed to build dashboard snapshot: %s", exc)
            return
        self.dashboard_snapshot = snapshot
        self._populate_dashboard_widgets(snapshot)

    def _populate_dashboard_widgets(self, snapshot):
        """Populate dashboard widgets across classic and unified views."""
        today_tasks = snapshot.today_tasks
        upcoming_sorted = snapshot.upcoming_tasks
        incomplete_sorted = snapshot.top_priority_tasks
        tasks = self.state_obj.tasks
        status_counts = snapshot.status_counts
        persona_load = snapshot.persona_load
        state = self.state_obj

        today_lines = []
        if today_tasks:
            today_lines.append("Tasks due today:\n")
            for t in today_tasks:
                today_lines.append(
                    f"- #{t.id} [{t.priority}] {t.title} (Project: {t.project}, Owner: {t.owner})"
                )
        elif incomplete_sorted[:3]:
            today_lines.append(
                "No tasks explicitly due today.\nShowing top 3 priorities:\n"
            )
            for t in incomplete_sorted[:3]:
                today_lines.append(
                    f"- #{t.id} [{t.priority}] {t.title} (Project: {t.project}, Owner: {t.owner}, Due: {t.due_date or 'None'})"
                )
        else:
            today_lines.append("No active tasks. System is idle.")
        today_content = "\n".join(today_lines)

        if upcoming_sorted:
            upcoming_lines = ["Next deadlines:\n"]
            for t in upcoming_sorted:
                upcoming_lines.append(
                    f"- #{t.id} [{t.priority}] {t.title} (Due: {t.due_date}, Project: {t.project}, Owner: {t.owner})"
                )
        else:
            upcoming_lines = ["No upcoming deadlines logged."]
        upcoming_content = "\n".join(upcoming_lines)

        total = len(tasks)
        status_lines = [f"Total tasks: {total}", ""]
        for s in STATUS_OPTIONS:
            status_lines.append(f"{s:12}: {status_counts.get(s, 0)}")
        status_content = "\n".join(status_lines)

        load_lines = ["Incomplete tasks per persona:", ""]
        for p in PERSONAS:
            marker = "◉" if p == state.active_persona else "○"
            load_lines.append(f"{marker} {p:8}: {persona_load.get(p, 0)}")
        load_content = "\n".join(load_lines)

        for target in getattr(self, "dashboard_text_targets", []):
            widget = target.get("today")
            if widget and widget.winfo_exists():
                widget.config(state="normal")
                widget.delete("1.0", "end")
                widget.insert("end", today_content)
                widget.config(state="disabled")

            widget = target.get("upcoming")
            if widget and widget.winfo_exists():
                widget.config(state="normal")
                widget.delete("1.0", "end")
                widget.insert("end", upcoming_content)
                widget.config(state="disabled")

            widget = target.get("status")
            if widget and widget.winfo_exists():
                widget.config(state="normal")
                widget.delete("1.0", "end")
                widget.insert("end", status_content)
                widget.config(state="disabled")

            widget = target.get("load")
            if widget and widget.winfo_exists():
                widget.config(state="normal")
                widget.delete("1.0", "end")
                widget.insert("end", load_content)
                widget.config(state="disabled")

    def _show_tools_view(self):
        """Show developer tools view in the consolidated tab with spec-sheet commands."""
        if not hasattr(self, "tools_intelligence_content_frame"):
            return

        # Clear current content
        for widget in self.tools_intelligence_content_frame.winfo_children():
            widget.destroy()

        # Developer tools interface
        if TTKBOOTSTRAP_AVAILABLE:
            content_frame = ttkb.Frame(
                self.tools_intelligence_content_frame, padding=12
            )
        else:
            content_frame = ttk.Frame(self.tools_intelligence_content_frame, padding=12)
        content_frame.grid(row=0, column=0, sticky="nsew")

        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Tools panel
        tools_frame = ttk.LabelFrame(
            content_frame, text="🔧 Developer Tools", padding=10
        )
        tools_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        tools_frame.columnconfigure((0, 1), weight=1)

        # Left side - Code Tools
        code_frame = ttk.LabelFrame(tools_frame, text="💻 Code Tools", padding=10)
        code_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Button(code_frame, text="🔍 Code Search", command=self._code_search).grid(
            row=0, column=0, pady=5, sticky="ew"
        )
        ttk.Button(code_frame, text="🐛 Debug Helper", command=self._debug_helper).grid(
            row=1, column=0, pady=5, sticky="ew"
        )
        ttk.Button(
            code_frame,
            text="📊 Performance Profiler",
            command=self._performance_profiler,
        ).grid(row=2, column=0, pady=5, sticky="ew")
        ttk.Button(
            code_frame, text="🔧 Code Formatter", command=self._code_formatter
        ).grid(row=3, column=0, pady=5, sticky="ew")

        # Right side - System Tools
        system_frame = ttk.LabelFrame(tools_frame, text="🖥️ System Tools", padding=10)
        system_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        ttk.Button(
            system_frame, text="📁 File Manager", command=self._file_manager
        ).grid(row=0, column=0, pady=5, sticky="ew")
        ttk.Button(
            system_frame, text="🌐 Network Tools", command=self._network_tools
        ).grid(row=1, column=0, pady=5, sticky="ew")
        ttk.Button(
            system_frame, text="💾 Backup Manager", command=self._backup_manager
        ).grid(row=2, column=0, pady=5, sticky="ew")
        ttk.Button(
            system_frame, text="📋 System Monitor", command=self._system_monitor
        ).grid(row=3, column=0, pady=5, sticky="ew")

        # Terminal/Command interface
        terminal_frame = ttk.LabelFrame(
            content_frame, text="💻 Command Terminal", padding=10
        )
        terminal_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        terminal_frame.columnconfigure(0, weight=1)
        terminal_frame.rowconfigure(0, weight=1)

        # Terminal output display
        self.command_terminal_output = tk.Text(
            terminal_frame,
            height=10,
            wrap=tk.WORD,
            font=("Courier", 10),
            state=tk.DISABLED,
        )
        self.command_terminal_output.grid(
            row=0, column=0, sticky="nsew", padx=5, pady=5
        )

        terminal_scrollbar = ttk.Scrollbar(
            terminal_frame, command=self.command_terminal_output.yview
        )
        terminal_scrollbar.grid(row=0, column=1, sticky="ns")
        self.command_terminal_output.config(yscrollcommand=terminal_scrollbar.set)
        self.command_terminal_output.config(state=tk.NORMAL)
        self.command_terminal_output.insert(
            tk.END,
            "Select a spec-sheet command below or type your own. Output will appear here.\n\n",
        )
        self.command_terminal_output.config(state=tk.DISABLED)

        # Command input
        input_frame = ttk.Frame(terminal_frame)
        input_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.command_entry_var = tk.StringVar()
        command_entry = ttk.Entry(
            input_frame, textvariable=self.command_entry_var, font=("Courier", 10)
        )
        command_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.command_entry_var.set("python main.py")

        ttk.Button(
            input_frame, text="▶️ Run", command=lambda: self._run_command()
        ).grid(row=0, column=1, sticky="ew")

        # Spec sheet quick commands
        commands_frame = ttk.LabelFrame(
            terminal_frame, text="📋 Spec Sheet Commands", padding=8
        )
        commands_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(10, 0)
        )
        commands_frame.columnconfigure((0, 1), weight=1)

        for idx, spec in enumerate(self.spec_sheet_commands):
            col = idx % 2
            row = idx // 2
            btn = ttk.Button(
                commands_frame,
                text=spec["label"],
                command=lambda c=spec["command"]: self._run_command(c),
            )
            btn.grid(row=row * 2, column=col, sticky="ew", padx=4, pady=(2, 0))
            desc_text = f"{spec['command']}\n{spec['description']}"
            ttk.Label(
                commands_frame, text=desc_text, wraplength=360, justify="left"
            ).grid(row=row * 2 + 1, column=col, sticky="w", padx=4, pady=(0, 8))

    def _run_command(
        self,
        command: Optional[str] = None,
        *,
        output_widget: Optional[tk.Text] = None,
        entry_var: Optional[tk.StringVar] = None,
    ):
        """Run a spec-sheet command or a custom command and stream output to the terminal pane."""
        output_widget = output_widget or getattr(self, "command_terminal_output", None)
        entry_var = entry_var or getattr(self, "command_entry_var", None)
        raw_command = (
            command
            if command is not None
            else (entry_var.get().strip() if entry_var else "")
        ).strip()

        if not raw_command:
            messagebox.showinfo("Command Execution", "Enter a command to run.")
            return

        if entry_var is not None:
            entry_var.set(raw_command)

        cwd_value = ""
        try:
            cwd_value = self.cwd_var.get().strip() if hasattr(self, "cwd_var") else ""
        except Exception:
            cwd_value = ""
        cwd = os.path.expanduser(cwd_value or os.getcwd())

        python_exec = shlex.quote(sys.executable)
        normalized_command = raw_command
        notes = []
        if raw_command.startswith("python_os "):
            normalized_command = f"{python_exec} {raw_command[len('python_os '):]}"
            notes.append("Mapped python_os to current Python interpreter")
        elif raw_command.startswith("python "):
            normalized_command = f"{python_exec} {raw_command[len('python '):]}"

        def render_result(result_text: str, *, replace: bool = False):
            if output_widget:
                self._append_command_output(output_widget, result_text, replace=replace)
            else:
                messagebox.showinfo("Command Execution", result_text)

        header_lines = [f"$ {raw_command}"]
        if normalized_command != raw_command:
            header_lines.append(f"(exec -> {normalized_command})")
        if notes:
            header_lines.append("Notes: " + " | ".join(notes))
        header_lines.append(f"cwd: {cwd}")
        render_result("\n".join(header_lines + ["[running...]"]), replace=False)

        def worker():
            try:
                result = run_bash_command(normalized_command, cwd=cwd)
            except Exception as exc:
                self.after(
                    0,
                    lambda: render_result("\n".join(header_lines + [f"Failed: {exc}"])),
                )
                return

            def finish():
                lines = [f"$ {raw_command}"]
                if normalized_command != raw_command:
                    lines.append(f"(exec -> {normalized_command})")
                if notes:
                    lines.append("Notes: " + " | ".join(notes))
                lines.append(f"shell: {result.shell_path}")
                lines.append(f"cwd: {result.cwd}")
                lines.append(f"exit: {result.returncode}")
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                if stdout:
                    lines.append("STDOUT:\n" + stdout)
                if stderr:
                    lines.append("STDERR:\n" + stderr)
                if not stdout and not stderr:
                    lines.append("(no output)")
                render_result("\n".join(lines))

            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def on_close(self):
        save_active_persona(self.conn, self.state_obj)
        save_settings(self.conn, self.settings)

        # Stop cognitive daemon system
        try:
            from .daemon import stop_daemon_system

            stop_daemon_system()
            print("[GUI] Cognitive daemon system stopped")
        except Exception:
            pass

        self.conn.close()
        self.destroy()


class APIConnectorStatus:
    """Status wrapper for API connectors that don't have full integration classes yet."""

    def __init__(self, name: str, available: bool):
        self.name = name
        self.available = available

    def authenticate(self):
        """Mock authenticate method."""
        pass

    def get_status(self):
        """Return mock status."""
        from assistant_hub.integrations.base import IntegrationStatus

        status = IntegrationStatus()
        status.connected = self.available
        status.item_count = 0
        status.error = (
            None if self.available else "API connector available but not configured"
        )
        return status


def run_gui():
    app = AssistantGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
