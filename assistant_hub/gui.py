#!/usr/bin/env python3
import base64
import json
import os
import sqlite3
import subprocess
import threading
import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from queue import Queue

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont, filedialog

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.tooltip import ToolTip

    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    import tkinter.ttk as ttkb

    # Fallback tooltip class
    class ToolTip:
        def __init__(self, widget, text=""):
            self.widget = widget
            self.text = text
            self.tipwindow = None


from .config import DB_PATH
from .core.api_server import start_api_server
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
)
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
from .sync_scheduler import create_default_scheduler
from .integrations import (
    GoogleCalendarIntegration,
    GmailIntegration,
    GitHubIntegration,
    NotesIntegration,
    WordIntegration,
    ExcelIntegration,
    OneNoteIntegration,
    FilesystemIntegration,
    GitIntegration,
    PDFIntegration,
    IntegrationAPIGateway,
    IntegrationPreviewError,
    preview_for_integration,
)
from .task_automation import process_recurring_tasks, check_task_dependencies
from .task_templates import (
    load_templates,
    save_template,
    delete_template,
    create_task_from_template,
    TaskTemplate,
)
from .ai_task_creation import create_task_from_ai_message
from .analytics import (
    get_task_completion_stats,
    get_project_stats,
    get_time_tracking_stats,
    get_productivity_metrics,
    generate_report,
)
from .suggestions import (
    get_deadline_reminders,
    get_workload_balance,
    get_project_health,
    get_smart_prioritization_suggestions,
)
from .export_import import (
    export_tasks_to_csv,
    export_tasks_to_json,
    export_projects_to_json,
    export_full_backup,
    import_tasks_from_csv,
    import_tasks_from_json,
)
from .daemon import start_daemon_system

try:
    import psutil
except ImportError:
    psutil = None

try:
    import customtkinter as ctk

    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False

MAX_IMPORTED_FILE_CHARS = int(os.getenv("ASSISTANT_HUB_FILE_CHAR_LIMIT", "60000"))


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


class AssistantGUI(ttkb.Window if TTKBOOTSTRAP_AVAILABLE else tk.Tk):
    def __init__(self):
        # Determine theme based on settings
        theme_map = {"plain": "cosmo", "light": "litera", "dark": "darkly"}
        theme = theme_map.get("plain", "cosmo")  # Default to cosmo

        if TTKBOOTSTRAP_AVAILABLE:
            super().__init__(
                themename=theme, title="Assistant Hub (GUI)", resizable=(True, True)
            )
            # ttkbootstrap's style is already available as self.style (read-only property)
        else:
            super().__init__()
            self.title("Assistant Hub (GUI)")
            self.style = ttk.Style()

        self.geometry("1200x700")
        self.minsize(1150, 720)

        self.conn: sqlite3.Connection = init_db()
        self.state_obj: AssistantState = load_state(self.conn)
        self.settings: Settings = load_settings(self.conn)
        self.security_status: SecurityStatus = load_security_status(self.conn)

        self.chat_sender_var = tk.StringVar(value="Chris")
        self.chat_agent_var = tk.StringVar(value=self.state_obj.active_persona)
        self.chat_model_var = tk.StringVar(value="auto")
        self.uploaded_files = []  # Track uploaded files for current conversation
        self.active_file_path: Optional[str] = None
        self.active_file_mtime: Optional[float] = None
        self.active_file_content: str = ""
        self.active_file_watch_job: Optional[str] = None
        self.active_file_status = tk.StringVar(value="No active file selected")
        self.model_combo = None  # Will be set in _build_chat_tab
        self.chat_status_var = tk.StringVar()
        self.system_prompt_text = None
        self.chat_text = None
        self.change_log_text = None
        self.file_preview_text = None
        self.command_var = tk.StringVar()
        self.cwd_var = tk.StringVar(value=os.getcwd())

        # Initialize fonts before building tabs (needed by all tabs)
        scale_map = {"small": 10, "medium": 12, "large": 14}
        base_size = scale_map.get(self.settings.font_scale, 12)

        self.base_font = tkfont.nametofont("TkDefaultFont")
        self.base_font.configure(size=base_size)

        self.text_font = tkfont.nametofont("TkTextFont")
        self.text_font.configure(size=base_size)

        if not TTKBOOTSTRAP_AVAILABLE:
            self._configure_style()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_topbar()

        if TTKBOOTSTRAP_AVAILABLE:
            self.notebook = ttkb.Notebook(self, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        self._build_dashboard_tab()
        self._build_tasks_tab()
        self._build_projects_tab()
        self._build_chat_tab()
        self._build_integrations_tab()
        self._build_analytics_tab()
        self._build_templates_tab()
        self._build_settings_tab()

        # Update tab labels with icons if available
        if TTKBOOTSTRAP_AVAILABLE:
            self.notebook.tab(0, text="📊 Dashboard")
            self.notebook.tab(1, text="✅ Tasks")
            self.notebook.tab(2, text="📁 Projects")
            self.notebook.tab(3, text="💬 AI Console")

        # Initialize sync scheduler
        self.sync_scheduler = create_default_scheduler(self.conn)
        self.integration_api = IntegrationAPIGateway(
            self.conn, scheduler=self.sync_scheduler
        )
        # Start scheduler in background (optional - can be started manually)
        # self.sync_scheduler.start()

        # Process recurring tasks on startup
        try:
            process_recurring_tasks(self.conn)
        except Exception:
            pass

        # Start cognitive daemon system for continuous background automation
        try:
            self.cognitive_daemon = start_daemon_system(self.conn, enabled=True)
            print("[GUI] Cognitive daemon system started - active automation enabled")
        except Exception as e:
            print(f"[GUI] Warning: Could not start cognitive daemon: {e}")
            self.cognitive_daemon = None

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

        self.api_server = None
        api_enabled = os.getenv("ASSISTANT_HUB_API_ENABLED", "1").lower() not in (
            "0",
            "false",
            "off",
        )
        if api_enabled:
            try:
                api_host = os.getenv("ASSISTANT_HUB_API_HOST", "127.0.0.1")
                api_port = int(os.getenv("ASSISTANT_HUB_API_PORT", "8070"))
                self.api_server = start_api_server(
                    DB_PATH, host=api_host, port=api_port
                )
                print(
                    f"[GUI] Dashboard API server available at http://{api_host}:{self.api_server.server_address[1]}"
                )
            except Exception as e:
                print(f"[GUI] Warning: Could not start dashboard API server: {e}")

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

    def _configure_style(self):
        if TTKBOOTSTRAP_AVAILABLE:
            # ttkbootstrap handles themes automatically
            theme_map = {"plain": "cosmo", "light": "litera", "dark": "darkly"}
            theme = theme_map.get(self.settings.theme, "cosmo")
            self.style.theme_use(theme)
        else:
            try:
                self.style.theme_use("clam")
            except tk.TclError:
                pass

        # Fonts are already initialized in __init__, just configure style-specific settings
        base_size = self.base_font.actual("size")
        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(size=base_size + 1, weight="bold")

        self.option_add("*Font", self.base_font)
        self.style.configure(
            "Treeview",
            rowheight=base_size + 12,
            font=(self.base_font.actual("family"), base_size),
        )
        self.style.configure(
            "Treeview.Heading", font=(heading_font.actual("family"), base_size)
        )
        self.style.configure("TNotebook.Tab", padding=(18, 8))
        self.style.configure("TLabel", padding=(4, 2))
        self.style.configure("TButton", padding=(8, 6))

        if not TTKBOOTSTRAP_AVAILABLE:
            palette = {
                "plain": {"bg": "#f4f4f4", "fg": "#202020"},
                "light": {"bg": "#ffffff", "fg": "#202020"},
                "dark": {"bg": "#1b1b1f", "fg": "#f2f2f2"},
            }
            colors = palette.get(self.settings.theme, palette["plain"])
            self.configure(bg=colors["bg"])
            for style_name in ["TFrame", "TLabelframe", "TLabelframe.Label", "TLabel"]:
                self.style.configure(
                    style_name, background=colors["bg"], foreground=colors["fg"]
                )

    def _build_topbar(self):
        if TTKBOOTSTRAP_AVAILABLE:
            top = ttkb.Frame(self)
        else:
            top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        top.columnconfigure(1, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            persona_label = ttkb.Label(top, text="Active Persona:", bootstyle="primary")
        else:
            persona_label = ttk.Label(top, text="Active Persona:")
        persona_label.grid(row=0, column=0, sticky="w", padx=(0, 4))

        self.persona_var = tk.StringVar(value=self.state_obj.active_persona)
        if TTKBOOTSTRAP_AVAILABLE:
            self.persona_combo = ttkb.Combobox(
                top,
                textvariable=self.persona_var,
                values=PERSONAS,
                state="readonly",
                width=12,
                bootstyle="primary",
            )
        else:
            self.persona_combo = ttk.Combobox(
                top,
                textvariable=self.persona_var,
                values=PERSONAS,
                state="readonly",
                width=12,
            )
        self.persona_combo.grid(row=0, column=1, sticky="w", padx=4)
        self.persona_combo.bind("<<ComboboxSelected>>", self.on_persona_change)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(self.persona_combo, text="Select the active assistant persona")

        if TTKBOOTSTRAP_AVAILABLE:
            role_label = ttkb.Label(top, text="Role:", bootstyle="secondary")
        else:
            role_label = ttk.Label(top, text="Role:")
        role_label.grid(row=0, column=2, sticky="e", padx=(10, 4))
        self.persona_role_var = tk.StringVar(
            value=PERSONA_ROLES.get(self.state_obj.active_persona, "")
        )
        if TTKBOOTSTRAP_AVAILABLE:
            self.persona_role_display = ttkb.Label(
                top, textvariable=self.persona_role_var, bootstyle="info"
            )
        else:
            self.persona_role_display = ttk.Label(
                top, textvariable=self.persona_role_var
            )
        self.persona_role_display.grid(row=0, column=3, sticky="w", padx=4)

        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(
                top,
                text="💾 Save",
                command=self._save_with_feedback,
                bootstyle="success",
            )
            refresh_btn = ttkb.Button(
                top,
                text="🔄 Refresh",
                command=self._refresh_with_feedback,
                bootstyle="info",
            )
        else:
            save_btn = ttk.Button(top, text="Save", command=self._save_with_feedback)
            refresh_btn = ttk.Button(
                top, text="Refresh", command=self._refresh_with_feedback
            )
        save_btn.grid(row=0, column=4, sticky="e", padx=(10, 5))
        refresh_btn.grid(row=0, column=5, sticky="e", padx=(5, 0))

        # Add hover effects
        AnimationHelper.add_hover_effect(save_btn)
        AnimationHelper.add_hover_effect(refresh_btn)

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(save_btn, text="Save current state and settings")
            ToolTip(refresh_btn, text="Refresh all views with latest data")

    def on_persona_change(self, event=None):
        val = self.persona_var.get()
        if val in PERSONAS:
            self.state_obj.active_persona = val
            save_active_persona(self.conn, self.state_obj)
            self.persona_role_var.set(PERSONA_ROLES.get(val, ""))
            if hasattr(self, "chat_agent_var"):
                self.chat_agent_var.set(val)
                self.on_agent_change()
            self.refresh_dashboard()
            self.refresh_task_list()

    def on_agent_change(self, event=None):
        """Update model when agent changes."""
        agent = self.chat_agent_var.get()
        if agent and self.chat_model_var.get() == "auto":
            model = get_agent_model(agent)
            self._update_chat_status(f"Agent: {agent} | Model: {model} (auto)")

    def _save_with_feedback(self):
        """Save with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_save_btn_ref", None))
        self.on_save()

    def on_save(self):
        save_active_persona(self.conn, self.state_obj)
        save_settings(self.conn, self.settings)
        messagebox.showinfo("Saved", "Assistant state & settings saved.")

    def _refresh_with_feedback(self):
        """Refresh with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_refresh_btn_ref", None))
        self.refresh_all()

    # ---------- Dashboard Tab ----------

    def _build_dashboard_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.dashboard_frame = ttkb.Frame(self.notebook)
        else:
            self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")

        self.dashboard_frame.columnconfigure(0, weight=1)
        self.dashboard_frame.columnconfigure(1, weight=1)
        self.dashboard_frame.rowconfigure(0, weight=1)
        self.dashboard_frame.rowconfigure(1, weight=1)
        self.dashboard_frame.rowconfigure(2, weight=0)
        self.dashboard_frame.rowconfigure(3, weight=0)

        if TTKBOOTSTRAP_AVAILABLE:
            self.today_box = ttkb.Labelframe(
                self.dashboard_frame, text="📋 Today's Focus", bootstyle="primary"
            )
            self.upcoming_box = ttkb.Labelframe(
                self.dashboard_frame, text="📅 Upcoming Deadlines", bootstyle="info"
            )
            self.status_box = ttkb.Labelframe(
                self.dashboard_frame, text="📊 Status Overview", bootstyle="success"
            )
            self.load_box = ttkb.Labelframe(
                self.dashboard_frame, text="👥 Load by Persona", bootstyle="secondary"
            )
            self.cyber_box = ttkb.Labelframe(
                self.dashboard_frame,
                text="🛡️ Cyber Defense Status",
                bootstyle="warning",
            )
        else:
            self.today_box = ttk.LabelFrame(self.dashboard_frame, text="Today's Focus")
            self.upcoming_box = ttk.LabelFrame(
                self.dashboard_frame, text="Upcoming Deadlines"
            )
            self.status_box = ttk.LabelFrame(
                self.dashboard_frame, text="Status Overview"
            )
            self.load_box = ttk.LabelFrame(self.dashboard_frame, text="Load by Persona")
            self.cyber_box = ttk.LabelFrame(
                self.dashboard_frame, text="Cyber Defense Status"
            )
        self.today_box.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.today_text = tk.Text(
            self.today_box, height=10, wrap="word", font=self.text_font
        )
        self.today_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.upcoming_box.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.upcoming_text = tk.Text(
            self.upcoming_box, height=10, wrap="word", font=self.text_font
        )
        self.upcoming_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.status_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.status_text = tk.Text(
            self.status_box, height=8, wrap="word", font=self.text_font
        )
        self.status_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.load_box.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self.load_text = tk.Text(
            self.load_box, height=8, wrap="word", font=self.text_font
        )
        self.load_text.pack(fill="both", expand=True, padx=4, pady=4)
        self.cyber_box.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8)
        )
        self.cyber_box.columnconfigure(0, weight=1)

        self.cyber_status_var = tk.StringVar(value="Status: offline")
        if TTKBOOTSTRAP_AVAILABLE:
            self.cyber_status_label = ttkb.Label(
                self.cyber_box,
                textvariable=self.cyber_status_var,
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 1,
                    "bold",
                ),
                bootstyle="info",
            )
        else:
            self.cyber_status_label = ttk.Label(
                self.cyber_box,
                textvariable=self.cyber_status_var,
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 1,
                    "bold",
                ),
            )
        self.cyber_status_label.grid(row=0, column=0, sticky="w", padx=6, pady=(4, 2))

        self.cyber_message_var = tk.StringVar(value="Telemetry not available.")
        if TTKBOOTSTRAP_AVAILABLE:
            self.cyber_message_label = ttkb.Label(
                self.cyber_box,
                textvariable=self.cyber_message_var,
                wraplength=800,
                justify="left",
                bootstyle="secondary",
            )
        else:
            self.cyber_message_label = ttk.Label(
                self.cyber_box,
                textvariable=self.cyber_message_var,
                wraplength=800,
                justify="left",
            )
        self.cyber_message_label.grid(row=1, column=0, sticky="w", padx=6, pady=2)

        self.cyber_updated_var = tk.StringVar(value="Updated: n/a")
        if TTKBOOTSTRAP_AVAILABLE:
            self.cyber_updated_label = ttkb.Label(
                self.cyber_box,
                textvariable=self.cyber_updated_var,
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") - 1,
                ),
                bootstyle="secondary",
            )
        else:
            self.cyber_updated_label = ttk.Label(
                self.cyber_box,
                textvariable=self.cyber_updated_var,
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") - 1,
                ),
            )
        self.cyber_updated_label.grid(row=2, column=0, sticky="w", padx=6, pady=(0, 4))

        if TTKBOOTSTRAP_AVAILABLE:
            self.sys_box = ttkb.Labelframe(
                self.dashboard_frame,
                text="💻 System Status (Optional)",
                bootstyle="secondary",
            )
        else:
            self.sys_box = ttk.LabelFrame(
                self.dashboard_frame, text="System Status (Optional)"
            )
        self.sys_box.grid(
            row=3, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8)
        )
        self.sys_text = tk.Text(
            self.sys_box, height=4, wrap="word", font=self.text_font
        )
        self.sys_text.pack(fill="both", expand=True, padx=4, pady=4)

    def refresh_dashboard(self):
        state = self.state_obj
        tasks = state.tasks
        today_str = datetime.now().strftime("%Y-%m-%d")

        today_tasks = [
            t for t in tasks if t.due_date == today_str and t.status != "DONE"
        ]
        priority_weight = {
            p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)
        }
        incomplete = [t for t in tasks if t.status != "DONE"]
        incomplete_sorted = sorted(
            incomplete,
            key=lambda t: (
                priority_weight.get(t.priority, 1),
                t.due_date or "9999-99-99",
                t.id,
            ),
            reverse=True,
        )

        upcoming = [
            t
            for t in tasks
            if t.due_date and t.due_date > today_str and t.status != "DONE"
        ]
        upcoming_sorted = sorted(upcoming, key=lambda t: t.due_date)[:5]

        status_counts: Dict[str, int] = {s: 0 for s in STATUS_OPTIONS}
        for t in tasks:
            status_counts[t.status] = status_counts.get(t.status, 0) + 1

        persona_load: Dict[str, int] = {p: 0 for p in PERSONAS}
        for t in incomplete:
            persona_load[t.owner] = persona_load.get(t.owner, 0) + 1

        self.today_text.config(state="normal")
        self.today_text.delete("1.0", "end")
        if today_tasks:
            self.today_text.insert("end", "Tasks due today:\n\n")
            for t in today_tasks:
                self.today_text.insert(
                    "end",
                    f"- #{t.id} [{t.priority}] {t.title} (Project: {t.project}, Owner: {t.owner})\n",
                )
        elif incomplete_sorted[:3]:
            self.today_text.insert(
                "end", "No tasks explicitly due today.\nShowing top 3 priorities:\n\n"
            )
            for t in incomplete_sorted[:3]:
                self.today_text.insert(
                    "end",
                    f"- #{t.id} [{t.priority}] {t.title} (Project: {t.project}, Owner: {t.owner}, Due: {t.due_date or 'None'})\n",
                )
        else:
            self.today_text.insert("end", "No active tasks. System is idle.")
        self.today_text.config(state="disabled")

        self.upcoming_text.config(state="normal")
        self.upcoming_text.delete("1.0", "end")
        if upcoming_sorted:
            self.upcoming_text.insert("end", "Next deadlines:\n\n")
            for t in upcoming_sorted:
                self.upcoming_text.insert(
                    "end",
                    f"- #{t.id} [{t.priority}] {t.title} (Due: {t.due_date}, Project: {t.project}, Owner: {t.owner})\n",
                )
        else:
            self.upcoming_text.insert("end", "No upcoming deadlines logged.")
        self.upcoming_text.config(state="disabled")

        self.status_text.config(state="normal")
        self.status_text.delete("1.0", "end")
        total = len(tasks)
        self.status_text.insert("end", f"Total tasks: {total}\n\n")
        for s in STATUS_OPTIONS:
            self.status_text.insert("end", f"{s:12}: {status_counts.get(s, 0)}\n")
        self.status_text.config(state="disabled")

        self.load_text.config(state="normal")
        self.load_text.delete("1.0", "end")
        self.load_text.insert("end", "Incomplete tasks per persona:\n\n")
        for p in PERSONAS:
            marker = "◉" if p == state.active_persona else "○"
            self.load_text.insert("end", f"{marker} {p:8}: {persona_load.get(p, 0)}\n")
        self.load_text.config(state="disabled")

        # Show external data items if preferences enabled
        if (
            self.settings.data_preferences.get("calendar", False)
            or self.settings.data_preferences.get("mail", False)
            or self.settings.data_preferences.get("notes", False)
        ):
            try:
                from .db import get_meta
                import json

                # Get recent external items
                c = self.conn.cursor()
                c.execute(
                    """
                    SELECT ei.title, ei.kind, es.name, ei.last_seen_at
                    FROM external_items ei
                    JOIN external_sources es ON ei.source_id = es.id
                    ORDER BY ei.last_seen_at DESC
                    LIMIT 5
                """
                )
                items = c.fetchall()
                if items:
                    self.load_text.config(state="normal")
                    self.load_text.insert("end", "\n--- Recent External Items ---\n")
                    for item in items:
                        self.load_text.insert("end", f"• {item[0][:40]} ({item[2]})\n")
                    self.load_text.config(state="disabled")
            except Exception:
                pass

        self.sys_text.config(state="normal")
        self.sys_text.delete("1.0", "end")
        if self.settings.show_system_status and psutil is not None:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            self.sys_text.insert(
                "end",
                f"CPU: {cpu:.1f}%   RAM: {mem.percent:.1f}% "
                f"({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)\n",
            )
            self.sys_text.insert("end", "(Toggle in Settings if you want this hidden.)")
        else:
            self.sys_text.insert("end", "System status disabled. Enable from Settings.")
        self.sys_text.config(state="disabled")

        # Cyber defense status tile
        self.security_status = load_security_status(self.conn)
        status_text = self.security_status.status.upper()
        status_emoji = {
            "secure": "✅",
            "vulnerable": "⚠️",
            "exploited": "🔴",
            "offline": "⚫",
        }
        emoji = status_emoji.get(self.security_status.status, "⚫")
        self.cyber_status_var.set(f"{emoji} Status: {status_text}")

        if TTKBOOTSTRAP_AVAILABLE:
            bootstyle_map = {
                "secure": "success",
                "vulnerable": "warning",
                "exploited": "danger",
                "offline": "secondary",
            }
            bootstyle = bootstyle_map.get(self.security_status.status, "secondary")
            self.cyber_status_label.configure(bootstyle=bootstyle)
        else:
            color_map = {
                "secure": "#2e7d32",
                "vulnerable": "#ef6c00",
                "exploited": "#b71c1c",
                "offline": "#616161",
            }
            self.cyber_status_label.configure(
                foreground=color_map.get(self.security_status.status, "#202020")
            )

        message = self.security_status.message.strip() or "Telemetry not available."
        self.cyber_message_var.set(message)
        if self.security_status.updated_at:
            human_ts = self.security_status.updated_at.replace("T", " ")
        else:
            human_ts = "n/a"
        source = self.security_status.source or "mac_guard"
        self.cyber_updated_var.set(f"Updated: {human_ts} via {source}")

    # ---------- Tasks Tab ----------

    def _build_tasks_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.tasks_frame = ttkb.Frame(self.notebook)
        else:
            self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text="Tasks")

        self.tasks_frame.columnconfigure(0, weight=3)
        self.tasks_frame.columnconfigure(1, weight=2)
        self.tasks_frame.rowconfigure(1, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            filters = ttkb.Frame(self.tasks_frame)
        else:
            filters = ttk.Frame(self.tasks_frame)
        filters.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))
        filters.columnconfigure(3, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            ttkb.Label(filters, text="Project:", bootstyle="secondary").grid(
                row=0, column=0, padx=(0, 4)
            )
            self.filter_project_var = tk.StringVar()
            self.filter_project_combo = ttkb.Combobox(
                filters,
                textvariable=self.filter_project_var,
                state="readonly",
                bootstyle="secondary",
            )
            self.filter_project_combo.grid(row=0, column=1, padx=(0, 10))

            ttkb.Label(filters, text="Owner:", bootstyle="secondary").grid(
                row=0, column=2, padx=(0, 4)
            )
            self.filter_owner_var = tk.StringVar()
            self.filter_owner_combo = ttkb.Combobox(
                filters,
                textvariable=self.filter_owner_var,
                state="readonly",
                bootstyle="secondary",
            )
            self.filter_owner_combo.grid(row=0, column=3, sticky="w", padx=(0, 10))

            self.show_done_var = tk.BooleanVar(value=True)
            show_done_check = ttkb.Checkbutton(
                filters,
                text="Show Done",
                variable=self.show_done_var,
                command=self.refresh_task_list,
                bootstyle="primary-round-toggle",
            )
        else:
            ttk.Label(filters, text="Project:").grid(row=0, column=0, padx=(0, 4))
            self.filter_project_var = tk.StringVar()
            self.filter_project_combo = ttk.Combobox(
                filters, textvariable=self.filter_project_var, state="readonly"
            )
            self.filter_project_combo.grid(row=0, column=1, padx=(0, 10))

            ttk.Label(filters, text="Owner:").grid(row=0, column=2, padx=(0, 4))
            self.filter_owner_var = tk.StringVar()
            self.filter_owner_combo = ttk.Combobox(
                filters, textvariable=self.filter_owner_var, state="readonly"
            )
            self.filter_owner_combo.grid(row=0, column=3, sticky="w", padx=(0, 10))

            self.show_done_var = tk.BooleanVar(value=True)
            show_done_check = ttk.Checkbutton(
                filters,
                text="Show Done",
                variable=self.show_done_var,
                command=self.refresh_task_list,
            )
        show_done_check.grid(row=0, column=4, padx=(0, 10))

        if TTKBOOTSTRAP_AVAILABLE:
            refresh_btn = ttkb.Button(
                filters,
                text="🔍 Apply Filters",
                command=self.refresh_task_list,
                bootstyle="info-outline",
            )
        else:
            refresh_btn = ttk.Button(
                filters, text="Apply Filters", command=self.refresh_task_list
            )
        refresh_btn.grid(row=0, column=5, padx=(4, 0))
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(refresh_btn, text="Apply filters and refresh the task list")

        if TTKBOOTSTRAP_AVAILABLE:
            list_frame = ttkb.Frame(self.tasks_frame)
        else:
            list_frame = ttk.Frame(self.tasks_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("id", "title", "project", "owner", "status", "priority", "due")
        self.task_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        for col in columns:
            self.task_tree.heading(col, text=col.upper())
        self.task_tree.column("id", width=40, anchor="center")
        self.task_tree.column("title", width=260)
        self.task_tree.column("project", width=140)
        self.task_tree.column("owner", width=80, anchor="center")
        self.task_tree.column("status", width=90, anchor="center")
        self.task_tree.column("priority", width=90, anchor="center")
        self.task_tree.column("due", width=90, anchor="center")

        self.task_tree.grid(row=0, column=0, sticky="nsew")
        if TTKBOOTSTRAP_AVAILABLE:
            scrollbar = ttkb.Scrollbar(
                list_frame,
                orient="vertical",
                command=self.task_tree.yview,
                bootstyle="primary-round",
            )
        else:
            scrollbar = ttk.Scrollbar(
                list_frame, orient="vertical", command=self.task_tree.yview
            )
        self.task_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        # Add double-click to edit
        self.task_tree.bind(
            "<Double-1>",
            lambda e: self.on_save_task_changes()
            if self.task_tree.selection()
            else None,
        )
        # Add keyboard shortcuts
        self.task_tree.bind(
            "<Return>",
            lambda e: self.on_save_task_changes()
            if self.task_tree.selection()
            else None,
        )
        self.task_tree.bind(
            "<Delete>",
            lambda e: self.on_delete_task() if self.task_tree.selection() else None,
        )

        if TTKBOOTSTRAP_AVAILABLE:
            detail = ttkb.Labelframe(
                self.tasks_frame, text="📝 Task Details", bootstyle="primary"
            )
        else:
            detail = ttk.LabelFrame(self.tasks_frame, text="Task Details")
        detail.grid(row=1, column=1, sticky="nsew", padx=8, pady=4)
        for i in range(2):
            detail.columnconfigure(i, weight=1)

        row = 0
        ttk.Label(detail, text="ID:").grid(
            row=row, column=0, sticky="e", padx=4, pady=2
        )
        self.task_id_var = tk.StringVar()
        ttk.Label(detail, textvariable=self.task_id_var).grid(
            row=row, column=1, sticky="w", padx=4, pady=2
        )

        row += 1
        ttk.Label(detail, text="Title:").grid(
            row=row, column=0, sticky="e", padx=4, pady=2
        )
        self.title_entry = ttk.Entry(detail)
        self.title_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Project:").grid(
            row=row, column=0, sticky="e", padx=4, pady=2
        )
        self.project_entry = ttk.Entry(detail)
        self.project_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Owner:").grid(
            row=row, column=0, sticky="e", padx=4, pady=2
        )
        self.owner_combo = ttk.Combobox(detail, values=PERSONAS, state="readonly")
        self.owner_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Status:").grid(
            row=row, column=0, sticky="e", padx=4, pady=2
        )
        self.status_combo = ttk.Combobox(
            detail, values=STATUS_OPTIONS, state="readonly"
        )
        self.status_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Priority:").grid(
            row=row, column=0, sticky="e", padx=4, pady=2
        )
        self.priority_combo = ttk.Combobox(
            detail, values=PRIORITY_OPTIONS, state="readonly"
        )
        self.priority_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Due (YYYY-MM-DD):").grid(
            row=row, column=0, sticky="e", padx=4, pady=2
        )
        self.due_entry = ttk.Entry(detail)
        self.due_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Notes:").grid(
            row=row, column=0, sticky="ne", padx=4, pady=2
        )
        self.notes_text = tk.Text(detail, height=5, wrap="word", font=self.text_font)
        self.notes_text.grid(row=row, column=1, sticky="nsew", padx=4, pady=2)
        detail.rowconfigure(row, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            btns = ttkb.Frame(detail)
        else:
            btns = ttk.Frame(detail)
        btns.grid(row=row + 1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        btns.columnconfigure(2, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            add_btn = ttkb.Button(
                btns,
                text="➕ New Task",
                command=self.on_new_task,
                bootstyle="primary-outline",
            )
            save_btn = ttkb.Button(
                btns,
                text="💾 Save Changes",
                command=self._save_task_with_feedback,
                bootstyle="success",
            )
            delete_btn = ttkb.Button(
                btns,
                text="🗑️ Delete Task",
                command=self._delete_task_with_feedback,
                bootstyle="danger-outline",
            )
        else:
            add_btn = ttk.Button(btns, text="New Task", command=self.on_new_task)
            save_btn = ttk.Button(
                btns, text="Save Changes", command=self._save_task_with_feedback
            )
            delete_btn = ttk.Button(
                btns, text="Delete Task", command=self._delete_task_with_feedback
            )
        add_btn.grid(row=0, column=0, padx=4, sticky="ew")
        save_btn.grid(row=0, column=1, padx=4, sticky="ew")
        delete_btn.grid(row=0, column=2, padx=4, sticky="ew")

        # Add hover effects and store references
        AnimationHelper.add_hover_effect(add_btn)
        AnimationHelper.add_hover_effect(save_btn)
        AnimationHelper.add_hover_effect(delete_btn)
        self._task_add_btn = add_btn
        self._task_save_btn = save_btn
        self._task_delete_btn = delete_btn

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(add_btn, text="Create a new task")
            ToolTip(save_btn, text="Save changes to the current task")
            ToolTip(delete_btn, text="Delete the selected task (irreversible)")

    def refresh_task_filters(self):
        projects = sorted(set(t.project for t in self.state_obj.tasks)) or ["(All)"]
        projects = ["(All)"] + projects
        self.filter_project_combo["values"] = projects
        if not self.filter_project_var.get():
            self.filter_project_var.set("(All)")

        owners = ["(All)"] + PERSONAS
        self.filter_owner_combo["values"] = owners
        if not self.filter_owner_var.get():
            self.filter_owner_var.set("(All)")

    def refresh_task_list(self):
        self.refresh_task_filters()
        for row in self.task_tree.get_children():
            self.task_tree.delete(row)

        proj_filter = self.filter_project_var.get()
        if proj_filter == "(All)" or not proj_filter:
            proj_filter = None
        owner_filter = self.filter_owner_var.get()
        if owner_filter == "(All)" or not owner_filter:
            owner_filter = None
        show_done = self.show_done_var.get()

        tasks = self.state_obj.tasks
        if proj_filter:
            tasks = [t for t in tasks if t.project == proj_filter]
        if owner_filter:
            tasks = [t for t in tasks if t.owner == owner_filter]
        if not show_done:
            tasks = [t for t in tasks if t.status != "DONE"]

        priority_weight = {
            p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)
        }
        tasks_sorted = sorted(
            tasks,
            key=lambda t: (
                priority_weight.get(t.priority, 1),
                t.due_date or "9999-99-99",
                t.id,
            ),
            reverse=True,
        )

        for t in tasks_sorted:
            self.task_tree.insert(
                "",
                "end",
                iid=str(t.id),
                values=(
                    t.id,
                    t.title,
                    t.project,
                    t.owner,
                    t.status,
                    t.priority,
                    t.due_date or "",
                ),
            )

    def on_task_select(self, event=None):
        sel = self.task_tree.selection()
        if not sel:
            return
        task_id = int(sel[0])
        task = next((t for t in self.state_obj.tasks if t.id == task_id), None)
        if not task:
            return

        self.task_id_var.set(str(task.id))
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, task.title)

        self.project_entry.delete(0, "end")
        self.project_entry.insert(0, task.project)

        self.owner_combo.set(task.owner)
        self.status_combo.set(task.status)
        self.priority_combo.set(task.priority)

        self.due_entry.delete(0, "end")
        self.due_entry.insert(0, task.due_date or "")

        self.notes_text.delete("1.0", "end")
        if task.notes:
            self.notes_text.insert("1.0", task.notes)

    def on_new_task(self):
        self.task_id_var.set("NEW")
        self.title_entry.delete(0, "end")
        self.project_entry.delete(0, "end")
        self.owner_combo.set(self.state_obj.active_persona)
        self.status_combo.set("TODO")
        self.priority_combo.set("MEDIUM")
        self.due_entry.delete(0, "end")
        if hasattr(self, "time_estimated_entry"):
            self.time_estimated_entry.delete(0, "end")
        if hasattr(self, "time_logged_entry"):
            self.time_logged_entry.delete(0, "end")
        if hasattr(self, "depends_on_entry"):
            self.depends_on_entry.delete(0, "end")
        if hasattr(self, "recurrence_pattern_var"):
            self.recurrence_pattern_var.set("")
        if hasattr(self, "recurrence_end_entry"):
            self.recurrence_end_entry.delete(0, "end")
        self.notes_text.delete("1.0", "end")

    def _save_task_with_feedback(self):
        """Save task with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_task_save_btn", None))
        self.on_save_task_changes()

    def _delete_task_with_feedback(self):
        """Delete task with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_task_delete_btn", None))
        self.on_delete_task()

    def on_save_task_changes(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Task title is required.")
            return

        proj_name = self.project_entry.get().strip() or "General"
        owner = self.owner_combo.get().strip() or self.state_obj.active_persona
        if owner not in PERSONAS:
            owner = self.state_obj.active_persona

        status = self.status_combo.get().strip().upper()
        if status not in STATUS_OPTIONS:
            status = "TODO"

        priority = self.priority_combo.get().strip().upper()
        if priority not in PRIORITY_OPTIONS:
            priority = "MEDIUM"

        due = self.due_entry.get().strip()
        if due and not parse_date(due):
            messagebox.showwarning(
                "Invalid Date", "Due date must be YYYY-MM-DD or blank."
            )
            return

        # Get time tracking values
        time_estimated = None
        if hasattr(self, "time_estimated_entry"):
            time_est_str = self.time_estimated_entry.get().strip()
            if time_est_str:
                try:
                    time_estimated = int(time_est_str)
                except ValueError:
                    pass

        time_logged = None
        if hasattr(self, "time_logged_entry"):
            time_log_str = self.time_logged_entry.get().strip()
            if time_log_str:
                try:
                    time_logged = int(time_log_str)
                except ValueError:
                    pass

        # Get dependency
        depends_on = None
        if hasattr(self, "depends_on_entry"):
            dep_str = self.depends_on_entry.get().strip()
            if dep_str:
                try:
                    depends_on = int(dep_str)
                except ValueError:
                    pass

        # Get recurrence
        recurrence_pattern = None
        if hasattr(self, "recurrence_pattern_var"):
            rec_pattern = self.recurrence_pattern_var.get().strip()
            if rec_pattern:
                recurrence_pattern = rec_pattern

        recurrence_end = None
        if hasattr(self, "recurrence_end_entry"):
            rec_end = self.recurrence_end_entry.get().strip()
            if rec_end:
                if parse_date(rec_end):
                    recurrence_end = rec_end

        notes = self.notes_text.get("1.0", "end").strip()

        ensure_project_exists(self.conn, self.state_obj, proj_name)

        id_str = self.task_id_var.get()
        if id_str == "NEW" or not id_str:
            new_task = Task(
                id=0,
                title=title,
                project=proj_name,
                status=status,
                priority=priority,
                due_date=due,
                notes=notes,
                owner=owner,
                created_at=datetime.now().isoformat(timespec="seconds"),
                depends_on=depends_on,
                recurrence_pattern=recurrence_pattern,
                recurrence_end=recurrence_end,
                time_estimated=time_estimated,
                time_logged=time_logged,
                template_id=None,
            )
            new_id = db_insert_task(self.conn, new_task)
            new_task.id = new_id
            self.state_obj.tasks.append(new_task)
            self.task_id_var.set(str(new_task.id))
        else:
            try:
                tid = int(id_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid task ID.")
                return
            task = next((t for t in self.state_obj.tasks if t.id == tid), None)
            if not task:
                messagebox.showerror("Error", "Task not found.")
                return
            task.title = title
            task.project = proj_name
            task.owner = owner
            task.status = status
            task.priority = priority
            task.due_date = due
            task.notes = notes
            task.depends_on = depends_on
            task.recurrence_pattern = recurrence_pattern
            task.recurrence_end = recurrence_end
            task.time_estimated = time_estimated
            task.time_logged = time_logged
            db_update_task(self.conn, task)

        self.refresh_all()

    def on_delete_task(self):
        id_str = self.task_id_var.get()
        if not id_str or id_str == "NEW":
            messagebox.showinfo("No Task", "Select a task to delete.")
            return
        try:
            tid = int(id_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid task ID.")
            return

        if not messagebox.askyesno("Confirm Delete", f"Delete task #{tid}?"):
            return

        db_delete_task(self.conn, tid)
        self.state_obj.tasks = [t for t in self.state_obj.tasks if t.id != tid]
        self.task_id_var.set("")
        self.title_entry.delete(0, "end")
        self.project_entry.delete(0, "end")
        self.owner_combo.set("")
        self.status_combo.set("")
        self.priority_combo.set("")
        self.due_entry.delete(0, "end")
        if hasattr(self, "time_estimated_entry"):
            self.time_estimated_entry.delete(0, "end")
        if hasattr(self, "time_logged_entry"):
            self.time_logged_entry.delete(0, "end")
        if hasattr(self, "depends_on_entry"):
            self.depends_on_entry.delete(0, "end")
        if hasattr(self, "recurrence_pattern_var"):
            self.recurrence_pattern_var.set("")
        if hasattr(self, "recurrence_end_entry"):
            self.recurrence_end_entry.delete(0, "end")
        self.notes_text.delete("1.0", "end")
        self.refresh_all()

    def on_start_timer(self):
        """Start a timer for the current task."""
        id_str = self.task_id_var.get()
        if not id_str or id_str == "NEW":
            messagebox.showinfo("No Task", "Select a task to start timer.")
            return

        try:
            tid = int(id_str)
        except ValueError:
            return

        task = next((t for t in self.state_obj.tasks if t.id == tid), None)
        if not task:
            return

        # Store start time
        if not hasattr(self, "_timer_start_time"):
            self._timer_start_time = {}
        self._timer_start_time[tid] = datetime.now()

        messagebox.showinfo(
            "Timer Started",
            f"Timer started for task #{tid}. Click 'Stop Timer' when done.",
        )

        # Update button
        if hasattr(self, "_timer_button"):
            if TTKBOOTSTRAP_AVAILABLE:
                self._timer_button.config(
                    text="⏹️ Stop Timer",
                    command=self.on_stop_timer,
                    bootstyle="danger-outline",
                )
            else:
                self._timer_button.config(text="Stop Timer", command=self.on_stop_timer)

    def on_stop_timer(self):
        """Stop the timer and add time to the task."""
        id_str = self.task_id_var.get()
        if not id_str or id_str == "NEW":
            return

        try:
            tid = int(id_str)
        except ValueError:
            return

        if not hasattr(self, "_timer_start_time") or tid not in self._timer_start_time:
            return

        start_time = self._timer_start_time[tid]
        elapsed = (datetime.now() - start_time).total_seconds() / 60  # minutes
        elapsed_minutes = int(elapsed)

        task = next((t for t in self.state_obj.tasks if t.id == tid), None)
        if task:
            current_logged = task.time_logged or 0
            task.time_logged = current_logged + elapsed_minutes
            db_update_task(self.conn, task)

            # Update UI
            if hasattr(self, "time_logged_entry"):
                self.time_logged_entry.delete(0, "end")
                self.time_logged_entry.insert(0, str(task.time_logged))

            messagebox.showinfo(
                "Timer Stopped", f"Added {elapsed_minutes} minutes to task #{tid}."
            )

        # Remove from timer dict
        del self._timer_start_time[tid]

        # Update button
        if hasattr(self, "_timer_button"):
            if TTKBOOTSTRAP_AVAILABLE:
                self._timer_button.config(
                    text="⏱️ Start Timer",
                    command=self.on_start_timer,
                    bootstyle="info-outline",
                )
            else:
                self._timer_button.config(
                    text="Start Timer", command=self.on_start_timer
                )

        self.refresh_all()

    # ---------- Projects Tab ----------

    def _build_projects_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.projects_frame = ttkb.Frame(self.notebook)
        else:
            self.projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_frame, text="Projects")

        self.projects_frame.columnconfigure(1, weight=1)
        self.projects_frame.rowconfigure(0, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            list_frame = ttkb.Frame(self.projects_frame)
        else:
            list_frame = ttk.Frame(self.projects_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("name", "priority", "status", "tasks")
        self.project_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.project_tree.heading("name", text="NAME")
        self.project_tree.heading("priority", text="PRIORITY")
        self.project_tree.heading("status", text="STATUS")
        self.project_tree.heading("tasks", text="#TASKS")

        self.project_tree.column("name", width=220)
        self.project_tree.column("priority", width=90, anchor="center")
        self.project_tree.column("status", width=100, anchor="center")
        self.project_tree.column("tasks", width=70, anchor="center")

        self.project_tree.grid(row=0, column=0, sticky="nsew")
        if TTKBOOTSTRAP_AVAILABLE:
            scrollbar = ttkb.Scrollbar(
                list_frame,
                orient="vertical",
                command=self.project_tree.yview,
                bootstyle="primary-round",
            )
        else:
            scrollbar = ttk.Scrollbar(
                list_frame, orient="vertical", command=self.project_tree.yview
            )
        self.project_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.project_tree.bind("<<TreeviewSelect>>", self.on_project_select)
        # Add double-click to edit
        self.project_tree.bind(
            "<Double-1>",
            lambda e: self.on_save_project() if self.project_tree.selection() else None,
        )
        # Add keyboard shortcuts
        self.project_tree.bind(
            "<Return>",
            lambda e: self.on_save_project() if self.project_tree.selection() else None,
        )
        self.project_tree.bind(
            "<Delete>",
            lambda e: self.on_delete_project()
            if self.project_tree.selection()
            else None,
        )

        if TTKBOOTSTRAP_AVAILABLE:
            detail = ttkb.Labelframe(
                self.projects_frame, text="📁 Project Details", bootstyle="primary"
            )
        else:
            detail = ttk.LabelFrame(self.projects_frame, text="Project Details")
        detail.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        for i in range(2):
            detail.columnconfigure(i, weight=1)

        row = 0
        ttk.Label(detail, text="Name:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.proj_name_entry = ttk.Entry(detail)
        self.proj_name_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(detail, text="Priority:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.proj_priority_combo = ttk.Combobox(
            detail, values=PRIORITY_OPTIONS, state="readonly"
        )
        self.proj_priority_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(detail, text="Status:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.proj_status_combo = ttk.Combobox(
            detail, values=["active", "paused", "archived"], state="readonly"
        )
        self.proj_status_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(detail, text="Description:").grid(
            row=row, column=0, sticky="ne", padx=4, pady=4
        )
        self.proj_desc_text = tk.Text(
            detail, height=6, wrap="word", font=self.text_font
        )
        self.proj_desc_text.grid(row=row, column=1, sticky="nsew", padx=4, pady=4)
        detail.rowconfigure(row, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            btns = ttkb.Frame(detail)
        else:
            btns = ttk.Frame(detail)
        btns.grid(row=row + 1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        btns.columnconfigure(2, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            new_btn = ttkb.Button(
                btns,
                text="➕ New Project",
                command=self.on_new_project,
                bootstyle="primary-outline",
            )
            save_btn = ttkb.Button(
                btns,
                text="💾 Save Project",
                command=self._save_project_with_feedback,
                bootstyle="success",
            )
            delete_btn = ttkb.Button(
                btns,
                text="🗑️ Delete Project",
                command=self._delete_project_with_feedback,
                bootstyle="danger-outline",
            )
        else:
            new_btn = ttk.Button(btns, text="New Project", command=self.on_new_project)
            save_btn = ttk.Button(
                btns, text="Save Project", command=self._save_project_with_feedback
            )
            delete_btn = ttk.Button(
                btns, text="Delete Project", command=self._delete_project_with_feedback
            )
        new_btn.grid(row=0, column=0, padx=4, sticky="ew")
        save_btn.grid(row=0, column=1, padx=4, sticky="ew")
        delete_btn.grid(row=0, column=2, padx=4, sticky="ew")

        # Add hover effects
        AnimationHelper.add_hover_effect(new_btn)
        AnimationHelper.add_hover_effect(save_btn)
        AnimationHelper.add_hover_effect(delete_btn)
        self._project_save_btn = save_btn
        self._project_delete_btn = delete_btn

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(new_btn, text="Create a new project")
            ToolTip(save_btn, text="Save changes to the current project")
            ToolTip(delete_btn, text="Delete the selected project")

    def refresh_project_list(self):
        for row in self.project_tree.get_children():
            self.project_tree.delete(row)

        counts: Dict[str, int] = {}
        for t in self.state_obj.tasks:
            counts[t.project] = counts.get(t.project, 0) + 1

        priority_weight = {
            p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)
        }
        projects_sorted = sorted(
            self.state_obj.projects,
            key=lambda p: (priority_weight.get(p.priority, 1), p.name),
            reverse=True,
        )

        for p in projects_sorted:
            self.project_tree.insert(
                "",
                "end",
                iid=p.name,
                values=(p.name, p.priority, p.status, counts.get(p.name, 0)),
            )

    def on_project_select(self, event=None):
        sel = self.project_tree.selection()
        if not sel:
            return
        name = sel[0]
        proj = next((p for p in self.state_obj.projects if p.name == name), None)
        if not proj:
            return

        self.proj_name_entry.delete(0, "end")
        self.proj_name_entry.insert(0, proj.name)

        self.proj_priority_combo.set(proj.priority)
        self.proj_status_combo.set(proj.status)
        self.proj_desc_text.delete("1.0", "end")
        if proj.description:
            self.proj_desc_text.insert("1.0", proj.description)

    def on_new_project(self):
        self.project_tree.selection_remove(*self.project_tree.selection())
        self.proj_name_entry.delete(0, "end")
        self.proj_priority_combo.set("MEDIUM")
        self.proj_status_combo.set("active")
        self.proj_desc_text.delete("1.0", "end")

    def _save_project_with_feedback(self):
        """Save project with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_project_save_btn", None))
        self.on_save_project()

    def _delete_project_with_feedback(self):
        """Delete project with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_project_delete_btn", None))
        self.on_delete_project()

    def on_save_project(self):
        name = self.proj_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Project name is required.")
            return
        priority = self.proj_priority_combo.get().strip().upper() or "MEDIUM"
        if priority not in PRIORITY_OPTIONS:
            priority = "MEDIUM"
        status = self.proj_status_combo.get().strip() or "active"
        if status not in ("active", "paused", "archived"):
            status = "active"
        desc = self.proj_desc_text.get("1.0", "end").strip()

        existing = next((p for p in self.state_obj.projects if p.name == name), None)
        if existing:
            existing.priority = priority
            existing.status = status
            existing.description = desc
        else:
            new_proj = Project(
                name=name, description=desc, status=status, priority=priority
            )
            self.state_obj.projects.append(new_proj)

        db_upsert_project(
            self.conn, next(p for p in self.state_obj.projects if p.name == name)
        )
        self.refresh_project_list()

    def on_delete_project(self):
        sel = self.project_tree.selection()
        if not sel:
            messagebox.showinfo("No Project", "Select a project to delete.")
            return
        name = sel[0]
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete project '{name}'? (Tasks will keep their project name.)",
        ):
            return

        db_delete_project(self.conn, name)
        self.state_obj.projects = [p for p in self.state_obj.projects if p.name != name]
        self.refresh_project_list()
        self.on_new_project()

    # ---------- AI Chat + Terminal Tab ----------

    def _build_chat_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.chat_frame = ttkb.Frame(self.notebook)
        else:
            self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="AI Console")

        self.chat_frame.columnconfigure(0, weight=1)
        self.chat_frame.rowconfigure(0, weight=1)

        # Two-column layout: documents on the left, conversation on the right
        chat_container = (
            ttkb.Frame(self.chat_frame)
            if TTKBOOTSTRAP_AVAILABLE
            else ttk.Frame(self.chat_frame)
        )
        chat_container.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        chat_container.columnconfigure(0, weight=1)
        chat_container.columnconfigure(1, weight=2)
        chat_container.columnconfigure(2, weight=2)
        chat_container.rowconfigure(0, weight=3)
        chat_container.rowconfigure(1, weight=1)

        self._build_document_panel(chat_container)
        self._build_conversation_panel(chat_container)
        self._build_file_preview_panel(chat_container)
        self._build_change_monitor(chat_container)

    def _build_document_panel(self, parent):
        if TTKBOOTSTRAP_AVAILABLE:
            doc_frame = ttkb.Labelframe(
                parent, text="📁 Document Intake", bootstyle="info"
            )
        else:
            doc_frame = ttk.LabelFrame(parent, text="Document Intake")
        doc_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)
        doc_frame.columnconfigure(0, weight=1)

        help_text = "Import snippets directly into the prompt or upload reference files for agents."
        ttk.Label(doc_frame, text=help_text, wraplength=280, justify="left").grid(
            row=0, column=0, sticky="w", padx=6, pady=4
        )

        btns = ttkb.Frame(doc_frame) if TTKBOOTSTRAP_AVAILABLE else ttk.Frame(doc_frame)
        btns.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        btns.columnconfigure((0, 1), weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            import_btn = ttkb.Button(
                btns,
                text="📥 Import to Prompt",
                command=self.on_import_chat_file,
                bootstyle="secondary-outline",
            )
            upload_btn = ttkb.Button(
                btns,
                text="☁️ Upload to Agents",
                command=self._upload_file_with_feedback,
                bootstyle="primary",
            )
        else:
            import_btn = ttk.Button(
                btns, text="Import to Prompt", command=self.on_import_chat_file
            )
            upload_btn = ttk.Button(
                btns, text="Upload to Agents", command=self._upload_file_with_feedback
            )
        import_btn.grid(row=0, column=0, padx=4, pady=2, sticky="ew")
        upload_btn.grid(row=0, column=1, padx=4, pady=2, sticky="ew")

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(
                import_btn, text="Load a file's content directly into the chat input"
            )
            ToolTip(upload_btn, text="Send a file to AI agents for reference")

        # Uploaded file list
        if TTKBOOTSTRAP_AVAILABLE:
            list_label = ttkb.Label(
                doc_frame, text="Uploaded Files", bootstyle="secondary"
            )
        else:
            list_label = ttk.Label(doc_frame, text="Uploaded Files")
        list_label.grid(row=2, column=0, sticky="w", padx=6, pady=(6, 2))

        self.upload_list = tk.Listbox(doc_frame, height=8)
        self.upload_list.grid(row=3, column=0, sticky="nsew", padx=6, pady=(0, 6))
        doc_frame.rowconfigure(3, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            preview_btn = ttkb.Button(
                doc_frame,
                text="👁️ Preview Selected",
                command=self.on_preview_selected_upload,
                bootstyle="secondary-outline",
            )
            clear_btn = ttkb.Button(
                doc_frame,
                text="🗑️ Clear List",
                command=self._clear_uploaded_files,
                bootstyle="danger-outline",
            )
        else:
            preview_btn = ttk.Button(
                doc_frame,
                text="Preview Selected",
                command=self.on_preview_selected_upload,
            )
            clear_btn = ttk.Button(
                doc_frame, text="Clear List", command=self._clear_uploaded_files
            )
        preview_btn.grid(row=4, column=0, sticky="ew", padx=6, pady=(2, 2))
        clear_btn.grid(row=5, column=0, sticky="ew", padx=6, pady=(0, 4))

        self._refresh_upload_list()

    def _build_conversation_panel(self, parent):
        if TTKBOOTSTRAP_AVAILABLE:
            convo_frame = ttkb.Labelframe(
                parent, text="💬 Chat & Terminal", bootstyle="primary"
            )
            compose = ttkb.Labelframe(
                parent, text="✍️ Compose Message & Terminal", bootstyle="info"
            )
        else:
            convo_frame = ttk.LabelFrame(parent, text="Chat & Terminal")
            compose = ttk.LabelFrame(parent, text="Compose Message & Terminal")
        convo_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=4)
        convo_frame.columnconfigure(0, weight=1)
        convo_frame.rowconfigure(0, weight=1)
        self.chat_text = tk.Text(
            convo_frame, wrap="word", state="disabled", font=self.text_font
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        if TTKBOOTSTRAP_AVAILABLE:
            chat_scroll = ttkb.Scrollbar(
                convo_frame,
                orient="vertical",
                command=self.chat_text.yview,
                bootstyle="primary-round",
            )
        else:
            chat_scroll = ttk.Scrollbar(
                convo_frame, orient="vertical", command=self.chat_text.yview
            )
        self.chat_text.configure(yscrollcommand=chat_scroll.set)
        chat_scroll.grid(row=0, column=1, sticky="ns")
        compose.grid(row=1, column=1, sticky="nsew", padx=(0, 0), pady=(4, 4))
        compose.columnconfigure(1, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            ttkb.Label(compose, text="From:", bootstyle="secondary").grid(
                row=0, column=0, sticky="e", padx=4, pady=2
            )
            sender_combo = ttkb.Combobox(
                compose,
                textvariable=self.chat_sender_var,
                values=PERSONAS,
                state="readonly",
                width=12,
                bootstyle="primary",
            )
            ttkb.Label(compose, text="AI Persona:", bootstyle="secondary").grid(
                row=0, column=2, sticky="e", padx=4, pady=2
            )
            agent_label = ttkb.Label(
                compose, textvariable=self.chat_agent_var, bootstyle="info"
            )
            ttkb.Label(compose, text="Model:", bootstyle="secondary").grid(
                row=0, column=4, sticky="e", padx=4, pady=2
            )
            self.model_combo = ttkb.Combobox(
                compose,
                textvariable=self.chat_model_var,
                values=["auto", "gpt-4o", "gpt-4o-mini", "o1-preview", "gpt-4-turbo"],
                state="readonly",
                width=16,
                bootstyle="success",
            )
            ttkb.Label(compose, text="System Prompt:", bootstyle="secondary").grid(
                row=1, column=0, sticky="ne", padx=4, pady=2
            )
            ttkb.Label(compose, text="Message:", bootstyle="secondary").grid(
                row=2, column=0, sticky="ne", padx=4, pady=(4, 2)
            )
        else:
            ttk.Label(compose, text="From:").grid(
                row=0, column=0, sticky="e", padx=4, pady=2
            )
            sender_combo = ttk.Combobox(
                compose,
                textvariable=self.chat_sender_var,
                values=PERSONAS,
                state="readonly",
                width=12,
            )
            ttk.Label(compose, text="AI Persona:").grid(
                row=0, column=2, sticky="e", padx=4, pady=2
            )
            agent_label = ttk.Label(compose, textvariable=self.chat_agent_var)
            ttk.Label(compose, text="Model:").grid(
                row=0, column=4, sticky="e", padx=4, pady=2
            )
            self.model_combo = ttk.Combobox(
                compose,
                textvariable=self.chat_model_var,
                values=["auto", "gpt-4o", "gpt-4o-mini", "o1-preview", "gpt-4-turbo"],
                state="readonly",
                width=16,
            )
            ttk.Label(compose, text="System Prompt:").grid(
                row=1, column=0, sticky="ne", padx=4, pady=2
            )
            ttk.Label(compose, text="Input:").grid(
                row=2, column=0, sticky="ne", padx=4, pady=(4, 2)
            )
        sender_combo.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=2)
        agent_label.grid(row=0, column=3, sticky="w", padx=(0, 4), pady=2)
        self.model_combo.grid(row=0, column=5, sticky="w", padx=(0, 4), pady=2)
        self.model_combo.set("auto")
        self.model_combo.bind("<<ComboboxSelected>>", self.on_agent_change)

        self.system_prompt_text = tk.Text(
            compose, height=3, wrap="word", font=self.text_font
        )
        self.system_prompt_text.grid(
            row=1, column=1, columnspan=5, sticky="nsew", padx=4, pady=2
        )
        self.system_prompt_text.insert("1.0", DEFAULT_SYSTEM_PROMPT)

        # Combined input section - CWD selector and unified input field
        if TTKBOOTSTRAP_AVAILABLE:
            input_meta_frame = ttkb.Frame(compose)
        else:
            input_meta_frame = ttk.Frame(compose)
        input_meta_frame.grid(
            row=2, column=1, columnspan=5, sticky="ew", padx=4, pady=(4, 2)
        )
        input_meta_frame.columnconfigure(1, weight=1)

        # CWD selector (compact, on same row as input hint)
        if TTKBOOTSTRAP_AVAILABLE:
            cwd_label = ttkb.Label(input_meta_frame, text="CWD:", bootstyle="secondary")
            self.cwd_entry = ttkb.Entry(
                input_meta_frame,
                textvariable=self.cwd_var,
                bootstyle="primary",
                width=20,
            )
            browse_btn = ttkb.Button(
                input_meta_frame,
                text="📂",
                command=self.on_browse_cwd,
                bootstyle="secondary-outline",
                width=3,
            )
        else:
            cwd_label = ttk.Label(input_meta_frame, text="CWD:")
            self.cwd_entry = ttk.Entry(
                input_meta_frame, textvariable=self.cwd_var, width=20
            )
            browse_btn = ttk.Button(
                input_meta_frame, text="📂", command=self.on_browse_cwd, width=3
            )
        cwd_label.grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.cwd_entry.grid(row=0, column=1, sticky="w", padx=(0, 4))
        browse_btn.grid(row=0, column=2, sticky="w", padx=(0, 0))
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(browse_btn, text="Browse for working directory")

        # Combined input field (replaces both chat_input and command_entry)
        # Use Text widget for multi-line support (both messages and commands)
        self.chat_input = tk.Text(compose, height=4, wrap="word", font=self.text_font)
        self.chat_input.grid(
            row=3, column=1, columnspan=5, sticky="nsew", padx=4, pady=(4, 2)
        )
        # Ctrl+Enter sends as chat message, Enter alone checks if it's a command
        self.chat_input.bind(
            "<Control-Return>",
            lambda e: (self.on_handle_combined_input(chat_mode=True), "break"),
        )
        self.chat_input.bind(
            "<Return>", lambda e: self.on_handle_combined_input_enter(e)
        )

        # Placeholder hint
        placeholder_text = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        self.chat_input.insert("1.0", placeholder_text)
        self.chat_input.config(foreground="gray")
        self.chat_input.bind("<FocusIn>", self.on_input_focus_in)
        self.chat_input.bind("<FocusOut>", self.on_input_focus_out)

        # Keep command_var for backward compatibility but use chat_input
        self.command_var = tk.StringVar()

        # Buttons row - consolidated and no duplicates
        if TTKBOOTSTRAP_AVAILABLE:
            btns = ttkb.Frame(compose)
        else:
            btns = ttk.Frame(compose)
        btns.grid(row=4, column=0, columnspan=6, sticky="ew", pady=(4, 0))

        # Configure columns for buttons
        for idx in range(3):
            btns.columnconfigure(idx, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            import_btn = ttkb.Button(
                btns,
                text="📁 Import",
                command=self.on_import_chat_file,
                bootstyle="info-outline",
            )
            send_btn = ttkb.Button(
                btns,
                text="🚀 Send",
                command=lambda: self.on_handle_combined_input(chat_mode=True),
                bootstyle="primary",
            )
            clear_btn = ttkb.Button(
                btns,
                text="🗑️ Clear",
                command=self.on_clear_chat_history,
                bootstyle="danger-outline",
            )
        else:
            import_btn = ttk.Button(
                btns, text="Import", command=self.on_import_chat_file
            )
            send_btn = ttk.Button(
                btns,
                text="Send",
                command=lambda: self.on_handle_combined_input(chat_mode=True),
            )
            clear_btn = ttk.Button(
                btns, text="Clear", command=self.on_clear_chat_history
            )
        import_btn.grid(row=0, column=0, padx=4, sticky="ew")
        send_btn.grid(row=0, column=1, padx=4, sticky="ew")
        clear_btn.grid(row=0, column=2, padx=4, sticky="ew")

        # Add hover effects to chat buttons
        AnimationHelper.add_hover_effect(import_btn)
        AnimationHelper.add_hover_effect(send_btn)
        AnimationHelper.add_hover_effect(clear_btn)
        self._chat_send_btn = send_btn

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(import_btn, text="Import file content into input")
            ToolTip(
                send_btn,
                text="Send message (Ctrl+Enter) or run command (Enter for single-line, prefix with $)",
            )
            ToolTip(clear_btn, text="Clear all chat history")

        if TTKBOOTSTRAP_AVAILABLE:
            self.chat_status_label = ttkb.Label(
                compose, textvariable=self.chat_status_var, bootstyle="info"
            )
        else:
            self.chat_status_label = ttk.Label(
                compose, textvariable=self.chat_status_var
            )
        self.chat_status_label.grid(
            row=5, column=0, columnspan=6, sticky="w", padx=4, pady=(2, 0)
        )

        # Add progress indicator for AI responses
        progress_container = (
            ttkb.Frame(compose) if TTKBOOTSTRAP_AVAILABLE else ttk.Frame(compose)
        )
        progress_container.grid(
            row=6, column=0, columnspan=6, sticky="ew", padx=4, pady=(2, 0)
        )
        progress_container.columnconfigure(0, weight=1)
        self.chat_progress = ProgressIndicator(self).create(
            progress_container, row=0, column=0, columnspan=1
        )
        self.chat_progress.progress_bar.grid_remove()
        self.chat_progress.indicator_label.grid_remove()

    def _build_file_preview_panel(self, parent):
        if TTKBOOTSTRAP_AVAILABLE:
            preview_frame = ttkb.Labelframe(
                parent, text="📄 Active File", bootstyle="secondary"
            )
        else:
            preview_frame = ttk.LabelFrame(parent, text="Active File")
        preview_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=4)
        preview_frame.columnconfigure(0, weight=1)

        status_row = (
            ttkb.Frame(preview_frame)
            if TTKBOOTSTRAP_AVAILABLE
            else ttk.Frame(preview_frame)
        )
        status_row.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 0))
        status_row.columnconfigure(0, weight=1)

        status_label = (
            ttkb.Label(
                status_row, textvariable=self.active_file_status, bootstyle="info"
            )
            if TTKBOOTSTRAP_AVAILABLE
            else ttk.Label(status_row, textvariable=self.active_file_status)
        )
        status_label.grid(row=0, column=0, sticky="w")

        btn_row = (
            ttkb.Frame(preview_frame)
            if TTKBOOTSTRAP_AVAILABLE
            else ttk.Frame(preview_frame)
        )
        btn_row.grid(row=1, column=0, sticky="ew", padx=4, pady=2)
        btn_row.columnconfigure((0, 1), weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            choose_btn = ttkb.Button(
                btn_row,
                text="🔍 Choose File",
                command=self.on_choose_active_file,
                bootstyle="info-outline",
            )
            refresh_btn = ttkb.Button(
                btn_row,
                text="🔄 Refresh",
                command=self._render_active_file_content,
                bootstyle="secondary-outline",
            )
        else:
            choose_btn = ttk.Button(
                btn_row, text="Choose File", command=self.on_choose_active_file
            )
            refresh_btn = ttk.Button(
                btn_row, text="Refresh", command=self._render_active_file_content
            )
        choose_btn.grid(row=0, column=0, padx=2, sticky="ew")
        refresh_btn.grid(row=0, column=1, padx=2, sticky="ew")

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(choose_btn, text="Pick a file to watch and share with the AI")
            ToolTip(refresh_btn, text="Manually refresh the live preview")

        self.file_preview_text = tk.Text(
            preview_frame, height=18, wrap="word", state="disabled", font=self.text_font
        )
        self.file_preview_text.grid(row=2, column=0, sticky="nsew", padx=4, pady=(4, 6))
        preview_frame.rowconfigure(2, weight=1)

        scroll = ttk.Scrollbar(
            preview_frame, orient="vertical", command=self.file_preview_text.yview
        )
        self.file_preview_text.configure(yscrollcommand=scroll.set)
        scroll.grid(row=2, column=1, sticky="ns")

    def _build_change_monitor(self, parent):
        if TTKBOOTSTRAP_AVAILABLE:
            change_frame = ttkb.Labelframe(
                parent, text="🛠️ Live Change Log", bootstyle="secondary"
            )
        else:
            change_frame = ttk.LabelFrame(parent, text="Live Change Log")
        change_frame.grid(
            row=1, column=0, columnspan=3, sticky="nsew", padx=2, pady=(0, 4)
        )
        change_frame.columnconfigure(0, weight=1)
        change_frame.rowconfigure(0, weight=1)

        self.change_log_text = tk.Text(
            change_frame, height=8, wrap="word", state="disabled", font=self.text_font
        )
        self.change_log_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        scrollbar = ttk.Scrollbar(
            change_frame, orient="vertical", command=self.change_log_text.yview
        )
        self.change_log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        refresh_btn = (
            ttkb.Button(
                change_frame,
                text="🔄 Refresh",
                command=self.refresh_change_log,
                bootstyle="secondary-outline",
            )
            if TTKBOOTSTRAP_AVAILABLE
            else ttk.Button(
                change_frame, text="Refresh", command=self.refresh_change_log
            )
        )
        refresh_btn.grid(row=1, column=0, columnspan=2, sticky="e", padx=4, pady=(0, 4))
        self.after(50, self.refresh_change_log)

    def _get_git_output(self, args):
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                return None
            return completed.stdout.strip()
        except Exception:
            return None

    def _summarize_agent_activity(self) -> str:
        recent_actions = [
            msg
            for msg in self.state_obj.chat_messages
            if msg.kind in ("terminal", "terminal_result")
        ][-10:]
        if not recent_actions:
            return "No recent agent commands yet."
        lines = []
        for msg in recent_actions:
            lines.append(
                f"[{msg.created_at}] {msg.persona}: {msg.content.splitlines()[0]}"
            )
        return "\n".join(lines)

    def refresh_change_log(self):
        if not self.change_log_text:
            return
        status_output = self._get_git_output(["status", "--short"])
        log_output = self._get_git_output(["log", "-5", "--oneline"])

        sections = []
        if status_output:
            sections.append("📂 Working Tree\n" + status_output)
        else:
            sections.append("📂 Working Tree\n(clean or unavailable)")

        if log_output:
            sections.append("📜 Recent Commits\n" + log_output)
        else:
            sections.append("📜 Recent Commits\n(unavailable)")

        sections.append("🤖 Agent Activity\n" + self._summarize_agent_activity())

        self.change_log_text.config(state="normal")
        self.change_log_text.delete("1.0", "end")
        self.change_log_text.insert("1.0", "\n\n".join(sections))
        self.change_log_text.config(state="disabled")

    def _update_chat_status(self, message: Optional[str] = None):
        if not hasattr(self, "chat_status_var"):
            return
        if message:
            self.chat_status_var.set(message)
        elif openai_available():
            agent = (
                self.chat_agent_var.get() if hasattr(self, "chat_agent_var") else None
            )
            if agent:
                model = (
                    get_agent_model(agent)
                    if self.chat_model_var.get() == "auto"
                    else self.chat_model_var.get()
                )
                self.chat_status_var.set(
                    f"ChatGPT ready. Agent: {agent} | Model: {model}"
                )
            else:
                self.chat_status_var.set("ChatGPT ready.")
        else:
            self.chat_status_var.set("OpenAI key missing – offline fallback only.")

    def refresh_chat_history(self):
        if not self.chat_text:
            return
        self.chat_text.config(state="normal")
        self.chat_text.delete("1.0", "end")
        for msg in self.state_obj.chat_messages[-400:]:
            timestamp = msg.created_at.replace("T", " ")
            if msg.kind == "terminal":
                kind_label = " [TERMINAL COMMAND]"
            elif msg.kind == "terminal_result":
                kind_label = " [TERMINAL OUTPUT]"
            elif msg.kind == "file":
                kind_label = " [FILE]"
            else:
                kind_label = ""
            self.chat_text.insert(
                "end", f"[{timestamp}] {msg.persona}{kind_label}\n{msg.content}\n\n"
            )
        self.chat_text.config(state="disabled")

    def on_import_chat_file(self):
        """Import file content into chat input."""
        initial_dir = self.cwd_var.get().strip() if hasattr(self, "cwd_var") else ""
        path = filedialog.askopenfilename(initialdir=initial_dir or os.getcwd())
        if not path:
            self._update_chat_status("File import cancelled.")
            return
        try:
            content, descriptor = self._read_file_for_chat(path)
        except OSError as exc:
            messagebox.showerror("Import File", f"Unable to read file:\n{exc}")
            self._update_chat_status("Import failed.")
            return

        truncated = False
        raw_len = len(content)
        if raw_len > MAX_IMPORTED_FILE_CHARS:
            content = content[:MAX_IMPORTED_FILE_CHARS] + "\n... [truncated for length]"
            truncated = True

        label = os.path.basename(path)
        block = f"\n[Imported file: {label}{descriptor}]\n{content}\n"

        # Clear placeholder if present
        current = self.chat_input.get("1.0", "end").strip()
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        if current == placeholder:
            self.chat_input.delete("1.0", "end")
            self.chat_input.config(foreground="black")

        self.chat_input.insert("end", block)
        if truncated:
            self.chat_input.insert("end", "\n[Note: content truncated to fit limit]\n")
        self._set_active_file(path, reason="Imported to prompt")
        self._update_chat_status(
            f"Imported '{label}' ({'truncated' if truncated else 'full'})."
        )

    def on_upload_file(self):
        """Upload file to OpenAI and attach to conversation."""
        initial_dir = self.cwd_var.get().strip() if hasattr(self, "cwd_var") else ""
        path = filedialog.askopenfilename(initialdir=initial_dir or os.getcwd())
        if not path:
            self._update_chat_status("File upload cancelled.")
            return

        try:
            from .ai import get_openai_client

            client = get_openai_client()

            # Upload file to OpenAI
            with open(path, "rb") as f:
                file_obj = client.files.create(file=f, purpose="assistants")

            label = os.path.basename(path)
            self.uploaded_files.append({"name": label, "id": file_obj.id, "path": path})
            self._refresh_upload_list()

            # Add file reference to chat input
            self.chat_input.insert(
                "end", f"\n[Uploaded file: {label} (ID: {file_obj.id})]\n"
            )
            self._update_chat_status(
                f"Uploaded '{label}' to OpenAI (ID: {file_obj.id})"
            )
            self._set_active_file(path, reason="Uploaded to agents")

            # Store file info in chat
            self._store_chat_message(
                "System",
                "system",
                f"File uploaded: {label} (OpenAI ID: {file_obj.id})",
                kind="file",
            )
            self.refresh_chat_history()

        except Exception as exc:
            messagebox.showerror("Upload File", f"Failed to upload file:\n{exc}")
            self._update_chat_status("File upload failed.")

    def _read_file_for_chat(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = fh.read()
            return data, ""
        except UnicodeDecodeError:
            with open(path, "rb") as fh:
                binary = fh.read()
        encoded = base64.b64encode(binary).decode("ascii")
        notice = " (base64 encoded)"
        return f"(base64)\n{encoded}", notice

    def _store_chat_message(
        self, persona: str, role: str, content: str, kind: str = "chat"
    ) -> ChatMessage:
        role = (role or "user").lower()
        now = datetime.now().isoformat(timespec="seconds")
        msg = ChatMessage(
            id=0, persona=persona, role=role, kind=kind, content=content, created_at=now
        )
        msg.id = db_insert_chat_message(self.conn, msg)
        self.state_obj.chat_messages.append(msg)
        return msg

    def _send_chat_with_feedback(self, invoke_ai: bool = True):
        """Send chat message with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_chat_send_btn", None))
        self.on_send_chat_message(invoke_ai)

    def _upload_file_with_feedback(self):
        """Upload file with visual feedback"""
        self.on_upload_file()

    def _run_terminal_with_feedback(self, event=None):
        """Run terminal command with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, "_terminal_run_btn", None))
        self.on_run_terminal_command(event)

    def _is_command_low_risk(self, command: str) -> bool:
        """Heuristic to decide if a command is safe enough to auto-approve."""
        safe_prefixes = (
            "ls",
            "pwd",
            "cat ",
            "echo ",
            "stat ",
            "head ",
            "tail ",
            "git status",
            "sed -n",
        )
        stripped = command.strip().lower()
        return any(stripped.startswith(prefix) for prefix in safe_prefixes)

    def _request_overwrite_permission(self, command: str, cwd: str) -> bool:
        mode = getattr(self.settings, "change_permission_mode", "ask_when_unsure")
        command_text = command or ""
        if mode == "auto":
            return True
        if mode == "ask_when_unsure" and self._is_command_low_risk(command_text):
            return True

        q: Queue = Queue()

        def ask():
            allowed = messagebox.askyesno(
                "Allow AI change?",
                f"The AI wants to run:\n{command_text or '[no command provided]'}\n\nWorking directory: {cwd}\nProceed?",
            )
            q.put(allowed)

        self.after(0, ask)
        return q.get()

    def _refresh_upload_list(self):
        if not hasattr(self, "upload_list"):
            return
        self.upload_list.delete(0, tk.END)
        for item in self.uploaded_files:
            name = item.get("name", "(file)") if isinstance(item, dict) else str(item)
            file_id = item.get("id") if isinstance(item, dict) else None
            path = item.get("path") if isinstance(item, dict) else None
            display = name if not file_id else f"{name} — {file_id}"
            if path:
                display += f" ({os.path.basename(path)})"
            self.upload_list.insert(tk.END, display)

    def _clear_uploaded_files(self):
        self.uploaded_files = []
        self._refresh_upload_list()
        self._update_chat_status("Cleared uploaded file list.")

    def on_preview_selected_upload(self):
        selection = self.upload_list.curselection()
        if not selection:
            messagebox.showinfo(
                "Preview", "Select an uploaded file with a known path to preview."
            )
            return
        idx = selection[0]
        if idx >= len(self.uploaded_files):
            return
        entry = self.uploaded_files[idx]
        path = entry.get("path") if isinstance(entry, dict) else None
        if not path:
            messagebox.showwarning(
                "Preview", "This upload does not have a local path to watch."
            )
            return
        if not os.path.exists(path):
            messagebox.showerror("Preview", f"File not found: {path}")
            return
        self._set_active_file(path, reason="Preview from uploads")

    def on_choose_active_file(self):
        """Let the user pick a file to preview and feed into AI context."""
        initial_dir = (
            self.cwd_var.get().strip() if hasattr(self, "cwd_var") else os.getcwd()
        )
        path = filedialog.askopenfilename(initialdir=initial_dir or os.getcwd())
        if not path:
            self.active_file_status.set("Active file selection cancelled")
            return
        self._set_active_file(path, reason="Manual selection")

    def _set_active_file(self, path: str, reason: str = ""):
        normalized = os.path.abspath(path)
        self.active_file_path = normalized
        try:
            self.active_file_mtime = os.path.getmtime(normalized)
        except OSError:
            self.active_file_mtime = None
        suffix = f" ({reason})" if reason else ""
        self.active_file_status.set(f"Watching: {os.path.basename(normalized)}{suffix}")
        self._load_active_file_content()
        self._schedule_active_file_watch()
        self._update_chat_status(f"Active file set: {os.path.basename(normalized)}")

    def _load_active_file_content(self):
        if not self.active_file_path:
            self.active_file_content = ""
            self._render_active_file_content()
            return
        try:
            with open(self.active_file_path, "r", encoding="utf-8") as fh:
                data = fh.read()
        except UnicodeDecodeError:
            with open(self.active_file_path, "rb") as fh:
                data = fh.read().decode("utf-8", errors="replace")
        except OSError as exc:
            self.active_file_content = f"[Unable to read file: {exc}]"
            self._render_active_file_content()
            return

        self.active_file_content = data
        self._render_active_file_content()

    def _render_active_file_content(self):
        if not self.file_preview_text:
            return
        status_parts = []
        if self.active_file_path:
            status_parts.append(f"Watching {self.active_file_path}")
            if self.active_file_mtime:
                status_parts.append(
                    f"updated {datetime.fromtimestamp(self.active_file_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
                )
        else:
            status_parts.append("No active file selected")
        self.active_file_status.set(" — ".join(status_parts))

        self.file_preview_text.config(state="normal")
        self.file_preview_text.delete("1.0", "end")
        if self.active_file_content:
            self.file_preview_text.insert("1.0", self.active_file_content)
        else:
            self.file_preview_text.insert("1.0", "(empty file)")
        self.file_preview_text.config(state="disabled")

    def _schedule_active_file_watch(self):
        if self.active_file_watch_job:
            try:
                self.after_cancel(self.active_file_watch_job)
            except Exception:
                pass
        if self.active_file_path:
            self.active_file_watch_job = self.after(1500, self._poll_active_file)
        else:
            self.active_file_watch_job = None

    def _poll_active_file(self):
        self.active_file_watch_job = None
        if not self.active_file_path:
            return
        try:
            current_mtime = os.path.getmtime(self.active_file_path)
        except OSError as exc:
            self.active_file_status.set(f"File unavailable: {exc}")
            return

        if self.active_file_mtime is None or current_mtime != self.active_file_mtime:
            self.active_file_mtime = current_mtime
            self._load_active_file_content()
            self.after(0, self.refresh_chat_history)
            self._update_chat_status(
                f"Active file changed: {os.path.basename(self.active_file_path)}"
            )
        self._schedule_active_file_watch()

    def _append_active_file_context(self, messages):
        """Inject active file context so the AI knows what the user is viewing."""
        if not self.active_file_path:
            return messages
        preview_len = 2000
        snippet = self.active_file_content[:preview_len]
        updated = (
            datetime.fromtimestamp(self.active_file_mtime).strftime("%Y-%m-%d %H:%M:%S")
            if self.active_file_mtime
            else "unknown"
        )
        context = ChatMessage(
            id=0,
            persona="System",
            role="system",
            kind="file",
            content=(
                f"Active file in UI: {self.active_file_path}\n"
                f"Last updated: {updated}\n"
                f"Preview (first {preview_len} chars):\n{snippet}"
            ),
        )
        return messages + [context]

    def on_send_chat_message(self, invoke_ai: bool = True):
        if not hasattr(self, "chat_input"):
            return
        text = self.chat_input.get("1.0", "end").strip()

        # Ignore placeholder text
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        if not text or text == placeholder:
            messagebox.showinfo("Chat", "Type a message first.")
            return
        sender = self.chat_sender_var.get().strip() or "Chris"
        if sender not in PERSONAS:
            sender = "Chris"
        user_msg = self._store_chat_message(sender, "user", text)

        # Try to extract and create tasks from the message
        try:
            created_tasks = create_task_from_ai_message(
                self.conn, text, default_project="General", default_owner=sender
            )
            if created_tasks:
                self._update_chat_status(
                    f"Created {len(created_tasks)} task(s) from message."
                )
                self.refresh_task_list()
                self.refresh_dashboard()
        except Exception:
            pass

        self.chat_input.delete("1.0", "end")
        self.on_input_focus_out()  # Restore placeholder if empty
        self.refresh_chat_history()
        if not invoke_ai:
            self._update_chat_status("Message logged without contacting ChatGPT.")
            return

        responder = self.chat_agent_var.get().strip() or self.state_obj.active_persona
        instruction = None
        if responder and responder != sender:
            instruction = f"Please respond as {responder}."

        system_prompt = self.system_prompt_text.get("1.0", "end").strip()
        model_input = self.chat_model_var.get().strip()
        if model_input == "auto" or not model_input:
            model = get_agent_model(responder)
        else:
            model = model_input

        cwd = os.path.expanduser(self.cwd_var.get().strip() or os.getcwd())
        self._start_ai_response(
            user_msg=user_msg,
            system_prompt=system_prompt,
            model=model,
            responder=responder,
            instruction=instruction,
            fallback_prompt=text,
            cwd=cwd,
        )

    def _start_ai_response(
        self,
        user_msg: ChatMessage,
        system_prompt: str,
        model: str,
        responder: str,
        instruction: Optional[str],
        fallback_prompt: str,
        cwd: str,
    ):
        self._update_chat_status(f"Contacting ChatGPT ({model})...")
        # Start progress indicator
        if hasattr(self, "chat_progress"):
            self.chat_progress.start(f"Generating response with {model}...")

        def worker():
            # Interactive loop: handle tool calls
            max_iterations = 10  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                # Refresh messages from state for each iteration and inject live context
                current_messages = self._append_active_file_context(
                    self.state_obj.chat_messages.copy()
                )

                reply, error, tool_calls = generate_ai_reply(
                    current_messages,
                    persona=user_msg.persona,
                    prompt=instruction if iteration == 0 else None,
                    append_prompt=bool(instruction) and iteration == 0,
                    fallback_prompt=fallback_prompt,
                    system_prompt=system_prompt,
                    model=model,
                    cwd=cwd,
                    enable_shell=True,
                )

                if error:
                    self.after(
                        0,
                        lambda r=reply, e=error: self._handle_ai_reply(r, e, responder),
                    )
                    return

                # If there are tool calls, execute them
                if tool_calls:
                    tool_results = []
                    for tool_call in tool_calls:
                        command_preview = None
                        if tool_call.function.name == "execute_command":
                            try:
                                args = json.loads(tool_call.function.arguments)
                                command_preview = args.get("command", "")
                            except Exception:
                                command_preview = None

                            if (
                                command_preview
                                and not self._request_overwrite_permission(
                                    command_preview, cwd
                                )
                            ):
                                self._store_chat_message(
                                    responder,
                                    "assistant",
                                    f"Skipped command: {command_preview}",
                                    kind="terminal_result",
                                )
                                continue

                        result = execute_tool_call(tool_call, cwd=cwd)
                        tool_results.append(result)

                        # Store terminal command and result in chat immediately
                        if tool_call.function.name == "execute_command":
                            try:
                                args = json.loads(tool_call.function.arguments)
                                cmd = args.get("command", "")
                                if cmd:
                                    header = f"$ {cmd}\n(cwd: {cwd})"
                                    self._store_chat_message(
                                        responder, "user", header, kind="terminal"
                                    )
                                    self._store_chat_message(
                                        responder,
                                        "assistant",
                                        result["content"],
                                        kind="terminal_result",
                                    )
                                    self.after(0, self.refresh_chat_history)
                                    self.after(0, self.refresh_change_log)
                            except Exception:
                                pass

                    # Store tool results in chat for next iteration
                    for result in tool_results:
                        self._store_chat_message(
                            responder, "tool", result["content"], kind="tool_result"
                        )

                    self.after(0, self.refresh_chat_history)
                    iteration += 1
                    import time

                    time.sleep(0.5)  # Brief pause to allow UI update
                    continue
                else:
                    # No more tool calls, return the final reply
                    self.after(
                        0,
                        lambda r=reply, e=error: self._handle_ai_reply(r, e, responder),
                    )
                    return

            # Max iterations reached
            final_reply = (
                reply
                if "reply" in locals() and reply
                else "Maximum interaction iterations reached."
            )
            self.after(
                0, lambda r=final_reply: self._handle_ai_reply(r, None, responder)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _handle_ai_reply(self, reply_text: str, error: Optional[str], responder: str):
        # Stop progress indicator
        if hasattr(self, "chat_progress"):
            if error:
                self.chat_progress.stop("Error occurred")
            else:
                self.chat_progress.stop("Response received")

        persona = responder or self.chat_agent_var.get().strip() or "AI Team"
        text = reply_text.strip() if reply_text else "(no response)"
        self._store_chat_message(persona, "assistant", text)
        self.refresh_chat_history()
        if error:
            self._update_chat_status(f"ChatGPT error (fallback used): {error}")
        else:
            self._update_chat_status("ChatGPT response ready.")

    def on_clear_chat_history(self):
        if not messagebox.askyesno(
            "Clear Chat", "Delete the entire chat + terminal log?"
        ):
            return
        db_clear_chat_history(self.conn)
        self.state_obj.chat_messages.clear()
        self.refresh_chat_history()

    def on_run_terminal_command(self, event=None):
        command = self.command_var.get().strip()
        if not command:
            messagebox.showinfo("Terminal", "Enter a command to run.")
            return
        cwd = os.path.expanduser(self.cwd_var.get().strip() or os.getcwd())
        if not os.path.isdir(cwd):
            messagebox.showerror("Terminal", f"Working directory not found: {cwd}")
            return
        try:
            result = run_bash_command(command, cwd=cwd)
        except Exception as exc:
            messagebox.showerror("Terminal", f"Failed to execute command: {exc}")
            return

        header = f"$ {command}\n(cwd: {result.cwd})"
        self._store_chat_message("Terminal", "user", header, kind="terminal")

        parts = [f"shell: {result.shell_path}", f"exit: {result.returncode}"]
        output = result.stdout.strip()
        err = result.stderr.strip()
        body = " | ".join(parts)
        if output:
            body += f"\n{output}"
        if err:
            body += f"\n[stderr]\n{err}"
        self._store_chat_message(
            "Terminal", "assistant", body or "(no output)", kind="terminal_result"
        )

        self.command_var.set("")
        self.refresh_chat_history()
        self.refresh_change_log()

    def on_browse_cwd(self):
        initial = self.cwd_var.get().strip() or os.getcwd()
        path = filedialog.askdirectory(initialdir=initial)
        if path:
            self.cwd_var.set(path)

    def on_input_focus_in(self, event=None):
        """Clear placeholder text when input gains focus."""
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        current_text = self.chat_input.get("1.0", "end").strip()
        if current_text == placeholder:
            self.chat_input.delete("1.0", "end")
            self.chat_input.config(foreground="black")

    def on_input_focus_out(self, event=None):
        """Restore placeholder text if input is empty."""
        current_text = self.chat_input.get("1.0", "end").strip()
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        if not current_text:
            self.chat_input.insert("1.0", placeholder)
            self.chat_input.config(foreground="gray")

    def on_handle_combined_input(self, chat_mode=False):
        """Handle combined input field - can be either chat message or terminal command."""
        if not hasattr(self, "chat_input"):
            return

        text = self.chat_input.get("1.0", "end").strip()
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."

        # Ignore placeholder text
        if not text or text == placeholder:
            return

        # Check if it's a command (starts with $ or chat_mode is False and it's a single line)
        is_command = text.startswith("$") or (not chat_mode and "\n" not in text)

        if is_command:
            # Remove $ prefix if present
            command = text.lstrip("$").strip()
            if command:
                # Update command_var for backward compatibility
                self.command_var.set(command)
                # Run the terminal command
                self._run_terminal_with_feedback()
        else:
            # Send as chat message
            self.on_send_chat_message(invoke_ai=True)

        # Clear input and restore placeholder
        self.chat_input.delete("1.0", "end")
        self.on_input_focus_out()

    def on_handle_combined_input_enter(self, event):
        """Handle Enter key in combined input - check if it's a command or newline."""
        if not hasattr(self, "chat_input"):
            return None

        text = self.chat_input.get("1.0", "end").strip()
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."

        # Ignore placeholder text
        if not text or text == placeholder:
            return "break"  # Prevent default Enter behavior

        # If Ctrl is pressed, always allow newline (user wants multi-line)
        if event.state & 0x4:  # Ctrl pressed
            return None  # Allow default Enter behavior (newline)

        # Check if it's a single-line command
        # If it starts with $, it's definitely a command
        # If it's a single line (no newlines), treat as command
        has_newlines = "\n" in text
        starts_with_dollar = text.startswith("$")

        if starts_with_dollar or (not has_newlines and len(text) > 0):
            # Treat as command - execute it
            self.on_handle_combined_input(chat_mode=False)
            return "break"  # Prevent default Enter behavior

        # Otherwise, allow Enter to create a newline (default behavior for multi-line messages)
        return None

    # ---------- Integrations Tab ----------

    def _build_integrations_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.integrations_frame = ttkb.Frame(self.notebook)
        else:
            self.integrations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.integrations_frame, text="🔌 Integrations")

        self.integrations_frame.columnconfigure(0, weight=1)
        self.integrations_frame.rowconfigure(0, weight=1)

        # Use existing scheduler from __init__
        if not hasattr(self, "sync_scheduler"):
            self.sync_scheduler = create_default_scheduler(self.conn)

        # Main container
        if TTKBOOTSTRAP_AVAILABLE:
            main_container = ttkb.Frame(self.integrations_frame)
        else:
            main_container = ttk.Frame(self.integrations_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Header
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(
                main_container,
                text="External Data Integrations",
                bootstyle="primary",
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 2,
                    "bold",
                ),
            )
        else:
            header = ttk.Label(
                main_container,
                text="External Data Integrations",
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 2,
                    "bold",
                ),
            )
        header.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Integrations list
        list_frame = ttk.Frame(main_container)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("service", "status", "last_sync", "items")
        self.integrations_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.integrations_tree.heading("service", text="SERVICE")
        self.integrations_tree.heading("status", text="STATUS")
        self.integrations_tree.heading("last_sync", text="LAST SYNC")
        self.integrations_tree.heading("items", text="ITEMS")

        self.integrations_tree.column("service", width=200)
        self.integrations_tree.column("status", width=120)
        self.integrations_tree.column("last_sync", width=150)
        self.integrations_tree.column("items", width=80)

        self.integrations_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.integrations_tree.yview
        )
        self.integrations_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Buttons
        if TTKBOOTSTRAP_AVAILABLE:
            btn_frame = ttkb.Frame(main_container)
        else:
            btn_frame = ttk.Frame(main_container)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        if TTKBOOTSTRAP_AVAILABLE:
            sync_btn = ttkb.Button(
                btn_frame,
                text="🔄 Sync All",
                command=self.on_sync_all_integrations,
                bootstyle="primary",
            )
            sync_selected_btn = ttkb.Button(
                btn_frame,
                text="🔄 Sync Selected",
                command=self.on_sync_selected_integration,
                bootstyle="info-outline",
            )
            refresh_btn = ttkb.Button(
                btn_frame,
                text="🔄 Refresh",
                command=self.refresh_integrations_list,
                bootstyle="secondary-outline",
            )
            preview_btn = ttkb.Button(
                btn_frame,
                text="👁️ Preview Data",
                command=self.on_preview_integration_data,
                bootstyle="warning-outline",
            )
        else:
            sync_btn = ttk.Button(
                btn_frame, text="Sync All", command=self.on_sync_all_integrations
            )
            sync_selected_btn = ttk.Button(
                btn_frame,
                text="Sync Selected",
                command=self.on_sync_selected_integration,
            )
            refresh_btn = ttk.Button(
                btn_frame, text="Refresh", command=self.refresh_integrations_list
            )
            preview_btn = ttk.Button(
                btn_frame, text="Preview Data", command=self.on_preview_integration_data
            )

        sync_btn.grid(row=0, column=0, padx=4)
        sync_selected_btn.grid(row=0, column=1, padx=4)
        refresh_btn.grid(row=0, column=2, padx=4)
        preview_btn.grid(row=0, column=3, padx=4)

        # API console to trigger integration actions programmatically
        if TTKBOOTSTRAP_AVAILABLE:
            api_box = ttkb.Labelframe(
                main_container, text="🛰️ Integration API", bootstyle="secondary"
            )
        else:
            api_box = ttk.LabelFrame(main_container, text="Integration API")
        api_box.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        api_box.columnconfigure(1, weight=1)

        self.integration_actions_metadata = self.integration_api.list_actions()
        targets = ["all", *sorted(self.integration_api.available_integrations().keys())]
        self.integration_api_target_var = tk.StringVar(value=targets[0])
        self.integration_api_action_var = tk.StringVar(value="status")
        self.integration_api_options_var = tk.StringVar(value="")

        ttk.Label(api_box, text="Target:").grid(
            row=0, column=0, sticky="e", padx=4, pady=4
        )
        target_combo = ttk.Combobox(
            api_box,
            textvariable=self.integration_api_target_var,
            values=targets,
            state="readonly",
        )
        target_combo.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(api_box, text="Action:").grid(
            row=1, column=0, sticky="e", padx=4, pady=4
        )
        self.integration_api_action_combo = ttk.Combobox(
            api_box,
            textvariable=self.integration_api_action_var,
            values=self._get_integration_actions_for_target(targets[0]),
            state="readonly",
        )
        self.integration_api_action_combo.grid(
            row=1, column=1, sticky="w", padx=4, pady=4
        )
        actions = self.integration_api.integration_actions().get(
            self.integration_api_target_var.get(), []
        )
        action_values = [action.get("name") for action in actions] or ["status", "sync"]
        self.integration_api_action_combo = ttk.Combobox(
            api_box,
            textvariable=self.integration_api_action_var,
            values=action_values,
            state="readonly",
        )
        self.integration_api_action_combo.grid(
            row=1, column=1, sticky="w", padx=4, pady=4
        )

        ttk.Label(api_box, text="Options (JSON):").grid(
            row=2, column=0, sticky="e", padx=4, pady=4
        )
        options_entry = ttk.Entry(
            api_box,
            textvariable=self.integration_api_options_var,
            width=50,
        )
        options_entry.grid(row=2, column=1, sticky="we", padx=4, pady=4)

        call_btn = (
            ttkb.Button(
                api_box,
                text="Invoke",
                command=self.on_call_integration_api,
                bootstyle="success",
            )
            if TTKBOOTSTRAP_AVAILABLE
            else ttk.Button(
                api_box, text="Invoke", command=self.on_call_integration_api
            )
        )
        call_btn.grid(row=0, column=2, rowspan=3, padx=4, pady=4, sticky="ns")

        self.integration_action_fields_frame = ttk.Frame(api_box)
        self.integration_action_fields_frame.grid(
            row=2, column=0, columnspan=3, sticky="ew", padx=4, pady=(4, 0)
        )
        self.integration_action_field_vars: Dict[str, tk.StringVar] = {}
        self._render_integration_action_fields(
            targets[0], self.integration_api_action_var.get()
        )

        self.integration_api_output = tk.Text(
            api_box, height=4, wrap="word", state="disabled"
        )
        self.integration_api_output.grid(
            row=3, column=0, columnspan=3, sticky="ew", padx=4, pady=(4, 6)
        )

        target_combo.bind("<<ComboboxSelected>>", self._on_integration_target_change)
        self.integration_api_action_combo.bind(
            "<<ComboboxSelected>>", self._on_integration_action_change
        )

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(sync_btn, text="Sync all enabled integrations")
            ToolTip(sync_selected_btn, text="Sync the selected integration")
            ToolTip(refresh_btn, text="Refresh the integrations list")
            ToolTip(preview_btn, text="Preview new data from the selected integration")

        target_combo.bind("<<ComboboxSelected>>", self.on_integration_target_change)

    def _write_integration_output(self, text: str):
        """Populate the integration API output box with new content."""
        if not hasattr(self, "integration_api_output"):
            return
        self.integration_api_output.config(state="normal")
        self.integration_api_output.delete("1.0", "end")
        self.integration_api_output.insert("1.0", text)
        self.integration_api_output.config(state="disabled")

    def _resolve_integration_slug(self, display_name: str) -> str:
        """Map a human-friendly integration name to its slug."""
        name_map = {
            "Local Notes": "notes",
            "Google Calendar": "calendar",
            "Gmail": "mail",
            "GitHub": "github",
            "Word": "word",
            "Excel": "excel",
            "OneNote": "onenote",
            "Local Files": "filesystem",
            "Git": "git",
            "PDF": "pdf",
        }
        return name_map.get(display_name, display_name.lower().replace(" ", "_"))

    def refresh_integrations_list(self):
        """Refresh the integrations list display."""
        for row in self.integrations_tree.get_children():
            self.integrations_tree.delete(row)

        # Get integration statuses via the API gateway
        if not hasattr(self, "integration_api"):
            self.integration_api = IntegrationAPIGateway(
                self.conn, scheduler=self.sync_scheduler
            )
        self.integration_actions_metadata = self.integration_api.list_actions()

        display_map = {
            "notes": "Local Notes",
            "calendar": "Google Calendar",
            "mail": "Gmail",
            "github": "GitHub",
            "word": "Word",
            "excel": "Excel",
            "onenote": "OneNote",
            "filesystem": "Local Files",
            "git": "Git",
            "pdf": "PDF",
        }

        statuses = self.integration_api.list_statuses()
        for slug, display in display_map.items():
            status_data = statuses.get(slug)
            if not status_data:
                continue
            status_text = (
                "✅ Connected" if status_data.get("connected") else "❌ Disconnected"
            )
            if status_data.get("error"):
                status_text += f" ({str(status_data.get('error'))[:30]})"

            last_sync = status_data.get("last_sync") or "Never"
            if last_sync != "Never" and "T" in last_sync:
                last_sync = last_sync.replace("T", " ")[:16]

            self.integrations_tree.insert(
                "",
                "end",
                iid=display,
                values=(
                    display,
                    status_text,
                    last_sync,
                    status_data.get("item_count", 0),
                ),
            )

    def on_sync_all_integrations(self):
        """Sync all enabled integrations."""
        results = (
            self.integration_api.call_action("all", action="sync")
            if hasattr(self, "integration_api")
            else self.sync_scheduler.sync_now()
        )
        message = "Sync completed:\n"
        for name, count in results.items():
            if count >= 0:
                message += f"  {name}: {count} items\n"
            else:
                message += f"  {name}: Error\n"
        try:
            self._write_integration_output(
                json.dumps({"sync_results": results}, indent=2)
            )
        except Exception:
            # Defensive: the GUI output box should not block sync notifications
            pass
        messagebox.showinfo("Sync Complete", message)
        self.refresh_integrations_list()

    def on_sync_selected_integration(self):
        """Sync the selected integration."""
        sel = self.integrations_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an integration to sync.")
            return

        name = sel[0]
        key = self._resolve_integration_slug(name)
        if hasattr(self, "integration_api"):
            results = self.integration_api.call_action(key, action="sync")
            count = results.get(key, -1)
        else:
            results = self.sync_scheduler.sync_now(key)
            count = results.get(key, -1)
        try:
            self._write_integration_output(
                json.dumps({"sync_results": results}, indent=2)
            )
        except Exception:
            pass
        if count >= 0:
            messagebox.showinfo("Sync Complete", f"{name}: {count} items synced.")
        else:
            messagebox.showerror("Sync Error", f"Failed to sync {name}.")
        self.refresh_integrations_list()

    def on_preview_integration_data(self):
        """Preview data from the selected integration and surface it in the GUI."""

        sel = self.integrations_tree.selection()
        if not sel:
            messagebox.showinfo(
                "No Selection", "Please select an integration to preview."
            )
            return

        display_name = sel[0]
        slug = self._resolve_integration_slug(display_name)
        file_path = None

        if slug in {"excel", "word", "calendar"}:
            filetypes = [("All files", "*.*")]
            if slug == "excel":
                filetypes = [("Excel", "*.xlsx *.xls")]
            elif slug == "word":
                filetypes = [("Word", "*.docx *.doc")]
            elif slug == "calendar":
                filetypes = [("iCalendar", "*.ics")]
            file_path = filedialog.askopenfilename(
                title="Select a file to preview",
                filetypes=filetypes,
            )
            if not file_path:
                return

        try:
            preview_text = preview_for_integration(slug, file_path=file_path)
        except IntegrationPreviewError as exc:
            messagebox.showerror("Preview Error", str(exc))
            return
        except Exception as exc:  # pragma: no cover - defensive for unexpected errors
            messagebox.showerror("Preview Error", f"Unable to preview data: {exc}")
            return

        self._write_integration_output(preview_text)
        messagebox.showinfo("Preview Complete", f"Updated preview for {display_name}.")

    def on_integration_target_change(self, event=None):
        """Refresh the available actions when the target changes."""
        if not hasattr(self, "integration_api_action_combo"):
            return

        actions = self.integration_api.integration_actions().get(
            self.integration_api_target_var.get(), []
        )
        values = [action.get("name") for action in actions] or ["status", "sync"]
        self.integration_api_action_combo.configure(values=values)
        if self.integration_api_action_var.get() not in values:
            self.integration_api_action_var.set(values[0])

    def on_call_integration_api(self):
        target = self.integration_api_target_var.get()
        action = self.integration_api_action_var.get()
        options: Dict[str, Any] = {}
        field_defs = getattr(self, "integration_action_field_definitions", {})
        for key, var in getattr(self, "integration_action_field_vars", {}).items():
            value = var.get()
            placeholder = field_defs.get(key, {}).get("placeholder")
            if value and value != placeholder:
                options[key] = value
        options_raw = self.integration_api_options_var.get().strip()
        options = None

        if options_raw:
            try:
                options = json.loads(options_raw)
            except json.JSONDecodeError:
                messagebox.showerror(
                    "Invalid Options",
                    'Options must be valid JSON (e.g., {"limit": 10}).',
                )
                return
        try:
            result = self.integration_api.call_action(
                target, action=action, options=options
            )
            text = json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as exc:
            text = f"Error: {exc}"

        if hasattr(self, "integration_api_output"):
            self.integration_api_output.config(state="normal")
            self.integration_api_output.delete("1.0", "end")
            self.integration_api_output.insert("1.0", text)
            self.integration_api_output.config(state="disabled")

    def _on_integration_target_change(self, event=None):
        target = self.integration_api_target_var.get()
        actions = self._get_integration_actions_for_target(target)
        self.integration_api_action_combo.configure(values=actions)
        if actions:
            self.integration_api_action_var.set(actions[0])
        self._render_integration_action_fields(
            target, self.integration_api_action_var.get()
        )

    def _on_integration_action_change(self, event=None):
        target = self.integration_api_target_var.get()
        action = self.integration_api_action_var.get()
        self._render_integration_action_fields(target, action)

    def _get_integration_actions_for_target(self, target: str) -> list[str]:
        base_actions = ["status", "sync", "actions"]
        if target == "all":
            return base_actions

        actions = (
            list(self.integration_actions_metadata.get(target, {}).keys())
            if hasattr(self, "integration_actions_metadata")
            else []
        )
        # Always include core actions for consistency
        for action in base_actions:
            if action not in actions:
                actions.append(action)
        return actions

    def _render_integration_action_fields(self, target: str, action: str):
        for child in self.integration_action_fields_frame.winfo_children():
            child.destroy()

        metadata = {}
        if hasattr(self, "integration_actions_metadata"):
            metadata = self.integration_actions_metadata.get(target, {}).get(action, {})

        fields = metadata.get("fields", []) if metadata else []
        self.integration_action_field_vars = {}
        self.integration_action_field_definitions: Dict[str, Dict[str, Any]] = {}

        if not fields:
            ttk.Label(
                self.integration_action_fields_frame,
                text="No options required for this action",
            ).grid(row=0, column=0, sticky="w", padx=4, pady=2)
            return

        for idx, field in enumerate(fields):
            label = ttk.Label(
                self.integration_action_fields_frame,
                text=f"{field.get('label', field['name'])}:",
            )
            label.grid(row=idx, column=0, sticky="e", padx=4, pady=2)

            var = tk.StringVar()
            self.integration_action_field_vars[field["name"]] = var
            self.integration_action_field_definitions[field["name"]] = field
            ftype = field.get("type", "text")
            choices = field.get("choices", [])

            if ftype == "select" and choices:
                entry = ttk.Combobox(
                    self.integration_action_fields_frame,
                    textvariable=var,
                    values=choices,
                    state="readonly",
                )
            else:
                entry = ttk.Entry(
                    self.integration_action_fields_frame, textvariable=var
                )
                placeholder = field.get("placeholder")
                if placeholder:
                    var.set(placeholder)

            entry.grid(row=idx, column=1, sticky="w", padx=4, pady=2)

    # ---------- Analytics Tab ----------

    def _build_analytics_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.analytics_frame = ttkb.Frame(self.notebook)
        else:
            self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="📊 Analytics")

        self.analytics_frame.columnconfigure(0, weight=1)
        self.analytics_frame.rowconfigure(0, weight=1)

        # Main container with scrollable text
        if TTKBOOTSTRAP_AVAILABLE:
            main_container = ttkb.Frame(self.analytics_frame)
        else:
            main_container = ttk.Frame(self.analytics_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Header
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(
                main_container,
                text="Analytics & Reports",
                bootstyle="primary",
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 2,
                    "bold",
                ),
            )
        else:
            header = ttk.Label(
                main_container,
                text="Analytics & Reports",
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 2,
                    "bold",
                ),
            )
        header.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Text widget for displaying analytics
        text_frame = ttk.Frame(main_container)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.analytics_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Courier", 10),
            bg="#f5f5f5" if not TTKBOOTSTRAP_AVAILABLE else None,
        )
        self.analytics_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.analytics_text.yview
        )
        self.analytics_text.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Buttons
        if TTKBOOTSTRAP_AVAILABLE:
            btn_frame = ttkb.Frame(main_container)
        else:
            btn_frame = ttk.Frame(main_container)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        if TTKBOOTSTRAP_AVAILABLE:
            refresh_btn = ttkb.Button(
                btn_frame,
                text="🔄 Refresh",
                command=self.refresh_analytics,
                bootstyle="primary",
            )
            export_btn = ttkb.Button(
                btn_frame,
                text="💾 Export Report",
                command=self.on_export_analytics_report,
                bootstyle="info-outline",
            )
        else:
            refresh_btn = ttk.Button(
                btn_frame, text="Refresh", command=self.refresh_analytics
            )
            export_btn = ttk.Button(
                btn_frame, text="Export Report", command=self.on_export_analytics_report
            )

        refresh_btn.grid(row=0, column=0, padx=4)
        export_btn.grid(row=0, column=1, padx=4)

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(refresh_btn, text="Refresh analytics data")
            ToolTip(export_btn, text="Export report to text file")

    def refresh_analytics(self):
        """Refresh the analytics display."""
        if not hasattr(self, "analytics_text"):
            return

        self.analytics_text.delete("1.0", "end")

        try:
            # Get all analytics data
            task_stats = get_task_completion_stats(self.state_obj)
            project_stats = get_project_stats(self.state_obj)
            time_stats = get_time_tracking_stats(self.state_obj)
            productivity = get_productivity_metrics(self.state_obj)
            deadline_reminders = get_deadline_reminders(self.state_obj, days_ahead=7)
            workload = get_workload_balance(self.state_obj)
            project_health = get_project_health(self.state_obj)
            suggestions = get_smart_prioritization_suggestions(self.state_obj)

            # Build display text
            lines = []
            lines.append("=" * 70)
            lines.append("ASSISTANT HUB ANALYTICS REPORT")
            lines.append("=" * 70)
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

            # Task Statistics
            lines.append("TASK STATISTICS")
            lines.append("-" * 70)
            lines.append(f"Total Tasks: {task_stats['total']}")
            lines.append(f"  ✓ Done: {task_stats['done']}")
            lines.append(f"  ⟳ In Progress: {task_stats['in_progress']}")
            lines.append(f"  ☐ TODO: {task_stats['todo']}")
            lines.append(f"  ⛔ Blocked: {task_stats['blocked']}")
            lines.append(f"Completion Rate: {task_stats['completion_rate']}%")
            lines.append("")

            # Project Statistics
            lines.append("PROJECT STATISTICS")
            lines.append("-" * 70)
            for project_name, stats in sorted(
                project_stats.items(), key=lambda x: x[1]["total"], reverse=True
            ):
                lines.append(f"{project_name}:")
                lines.append(
                    f"  Total: {stats['total']}, Done: {stats['done']}, Completion: {stats['completion_rate']}%"
                )
            lines.append("")

            # Time Tracking
            lines.append("TIME TRACKING")
            lines.append("-" * 70)
            lines.append(
                f"Estimated: {time_stats['estimated_hours']} hours ({time_stats['total_estimated_minutes']} minutes)"
            )
            lines.append(
                f"Logged: {time_stats['logged_hours']} hours ({time_stats['total_logged_minutes']} minutes)"
            )
            lines.append(f"Tasks with time data: {time_stats['tasks_with_time']}")
            if time_stats["total_estimated_minutes"] > 0:
                variance = (
                    (
                        time_stats["total_logged_minutes"]
                        - time_stats["total_estimated_minutes"]
                    )
                    / time_stats["total_estimated_minutes"]
                ) * 100
                lines.append(f"Time variance: {variance:+.1f}%")
            lines.append("")

            # Productivity Metrics
            lines.append("PRODUCTIVITY METRICS")
            lines.append("-" * 70)
            lines.append(f"Completion Rate: {productivity['completion_rate']}%")
            lines.append(f"Tasks Completed: {productivity['tasks_completed']}")
            lines.append(f"Tasks In Progress: {productivity['tasks_in_progress']}")
            lines.append(
                f"Total Time Logged: {productivity['total_time_logged_hours']} hours"
            )
            lines.append(
                f"Average Time per Task: {productivity['average_time_per_task_minutes']} minutes"
            )
            lines.append("")

            # Deadline Reminders
            if deadline_reminders:
                lines.append("DEADLINE REMINDERS (Next 7 Days)")
                lines.append("-" * 70)
                for reminder in deadline_reminders[:10]:  # Top 10
                    task = reminder["task"]
                    urgency = reminder["urgency"].upper()
                    days = reminder["days_until"]
                    lines.append(
                        f"[{urgency}] Task #{task.id}: {task.title[:50]} - {days} day(s) until due"
                    )
                lines.append("")

            # Workload Balance
            lines.append("WORKLOAD BALANCE")
            lines.append("-" * 70)
            for persona, data in workload.items():
                status = "⚠️ OVERLOADED" if data["overloaded"] else "✓ OK"
                lines.append(f"{persona}: {status}")
                lines.append(
                    f"  Tasks: {data['task_count']}, Est. Hours: {data['estimated_hours']}, Logged: {data['logged_hours']}"
                )
                lines.append(f"  High Priority: {data['high_priority_count']}")
            lines.append("")

            # Project Health
            lines.append("PROJECT HEALTH")
            lines.append("-" * 70)
            for project_name, health in sorted(
                project_health.items(), key=lambda x: x[1]["health_score"]
            ):
                status_icon = (
                    "✓"
                    if health["health_status"] == "healthy"
                    else "⚠"
                    if health["health_status"] == "warning"
                    else "✗"
                )
                lines.append(
                    f"{status_icon} {project_name}: {health['health_status'].upper()} (Score: {health['health_score']})"
                )
                lines.append(
                    f"  Total: {health['total_tasks']}, Completed: {health['completed']}, Blocked: {health['blocked']}, Overdue: {health['overdue']}"
                )
            lines.append("")

            # Smart Suggestions
            if suggestions:
                lines.append("SMART SUGGESTIONS")
                lines.append("-" * 70)
                for suggestion in suggestions[:10]:  # Top 10
                    priority = suggestion["priority"].upper()
                    lines.append(f"[{priority}] {suggestion['message']}")
                lines.append("")

            # Display the report
            self.analytics_text.insert("1.0", "\n".join(lines))
            self.analytics_text.see("1.0")

        except Exception as e:
            self.analytics_text.insert("1.0", f"Error generating analytics: {e}")

    def on_export_analytics_report(self):
        """Export analytics report to a text file."""
        try:
            report = generate_report(self.state_obj)
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            )
            if filename:
                with open(filename, "w") as f:
                    f.write(report)
                messagebox.showinfo("Export", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")

    # ---------- Templates Tab ----------

    def _build_templates_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.templates_frame = ttkb.Frame(self.notebook)
        else:
            self.templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.templates_frame, text="📋 Templates")

        self.templates_frame.columnconfigure(0, weight=1)
        self.templates_frame.rowconfigure(0, weight=1)

        # Main container
        if TTKBOOTSTRAP_AVAILABLE:
            main_container = ttkb.Frame(self.templates_frame)
        else:
            main_container = ttk.Frame(self.templates_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.rowconfigure(1, weight=1)

        # Header
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(
                main_container,
                text="Task Templates",
                bootstyle="primary",
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 2,
                    "bold",
                ),
            )
        else:
            header = ttk.Label(
                main_container,
                text="Task Templates",
                font=(
                    self.base_font.actual("family"),
                    self.base_font.actual("size") + 2,
                    "bold",
                ),
            )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Left: Template list
        list_frame = ttk.Frame(main_container)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 4))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("name", "project", "priority")
        self.templates_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.templates_tree.heading("name", text="TEMPLATE NAME")
        self.templates_tree.heading("project", text="PROJECT")
        self.templates_tree.heading("priority", text="PRIORITY")

        self.templates_tree.column("name", width=150)
        self.templates_tree.column("project", width=100)
        self.templates_tree.column("priority", width=80)

        self.templates_tree.grid(row=0, column=0, sticky="nsew")
        self.templates_tree.bind("<<TreeviewSelect>>", self.on_template_select)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.templates_tree.yview
        )
        self.templates_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Right: Template details form
        if TTKBOOTSTRAP_AVAILABLE:
            form_frame = ttkb.Labelframe(
                main_container, text="Template Details", bootstyle="info"
            )
        else:
            form_frame = ttk.LabelFrame(main_container, text="Template Details")
        form_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 0))
        form_frame.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(form_frame, text="Name:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.template_name_var = tk.StringVar()
        template_name_entry = ttk.Entry(form_frame, textvariable=self.template_name_var)
        template_name_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(form_frame, text="Title:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.template_title_var = tk.StringVar()
        template_title_entry = ttk.Entry(
            form_frame, textvariable=self.template_title_var
        )
        template_title_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(form_frame, text="Project:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.template_project_var = tk.StringVar()
        template_project_combo = ttk.Combobox(
            form_frame, textvariable=self.template_project_var, state="readonly"
        )
        template_project_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=4)
        self.template_project_combo = template_project_combo

        row += 1
        ttk.Label(form_frame, text="Priority:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.template_priority_var = tk.StringVar()
        template_priority_combo = ttk.Combobox(
            form_frame,
            textvariable=self.template_priority_var,
            values=PRIORITY_OPTIONS,
            state="readonly",
        )
        template_priority_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(form_frame, text="Time Est. (min):").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        self.template_time_estimated_var = tk.StringVar()
        template_time_entry = ttk.Entry(
            form_frame, textvariable=self.template_time_estimated_var
        )
        template_time_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(form_frame, text="Notes:").grid(
            row=row, column=0, sticky="ne", padx=4, pady=4
        )
        self.template_notes_text = tk.Text(form_frame, height=6, wrap="word")
        self.template_notes_text.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        # Buttons
        if TTKBOOTSTRAP_AVAILABLE:
            btn_frame = ttkb.Frame(main_container)
        else:
            btn_frame = ttk.Frame(main_container)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        if TTKBOOTSTRAP_AVAILABLE:
            new_btn = ttkb.Button(
                btn_frame,
                text="➕ New",
                command=self.on_new_template,
                bootstyle="success-outline",
            )
            save_btn = ttkb.Button(
                btn_frame,
                text="💾 Save",
                command=self.on_save_template,
                bootstyle="primary",
            )
            delete_btn = ttkb.Button(
                btn_frame,
                text="🗑️ Delete",
                command=self.on_delete_template,
                bootstyle="danger-outline",
            )
            create_task_btn = ttkb.Button(
                btn_frame,
                text="✅ Create Task",
                command=self.on_create_task_from_template,
                bootstyle="info",
            )
            refresh_btn = ttkb.Button(
                btn_frame,
                text="🔄 Refresh",
                command=self.refresh_templates_list,
                bootstyle="secondary-outline",
            )
        else:
            new_btn = ttk.Button(btn_frame, text="New", command=self.on_new_template)
            save_btn = ttk.Button(btn_frame, text="Save", command=self.on_save_template)
            delete_btn = ttk.Button(
                btn_frame, text="Delete", command=self.on_delete_template
            )
            create_task_btn = ttk.Button(
                btn_frame, text="Create Task", command=self.on_create_task_from_template
            )
            refresh_btn = ttk.Button(
                btn_frame, text="Refresh", command=self.refresh_templates_list
            )

        new_btn.grid(row=0, column=0, padx=4)
        save_btn.grid(row=0, column=1, padx=4)
        delete_btn.grid(row=0, column=2, padx=4)
        create_task_btn.grid(row=0, column=3, padx=4)
        refresh_btn.grid(row=0, column=4, padx=4)

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(new_btn, text="Create a new template")
            ToolTip(save_btn, text="Save the current template")
            ToolTip(delete_btn, text="Delete the selected template")
            ToolTip(create_task_btn, text="Create a task from this template")
            ToolTip(refresh_btn, text="Refresh the templates list")

        self.current_template_id = None

    def refresh_templates_list(self):
        """Refresh the templates list display."""
        if not hasattr(self, "templates_tree"):
            return

        for row in self.templates_tree.get_children():
            self.templates_tree.delete(row)

        templates = load_templates(self.conn)
        for template in templates:
            self.templates_tree.insert(
                "",
                "end",
                iid=template.id,
                values=(template.name, template.project or "", template.priority or ""),
            )

        # Update project combo
        if hasattr(self, "template_project_combo"):
            projects = [p.name for p in self.state_obj.projects]
            self.template_project_combo["values"] = projects

    def on_template_select(self, event=None):
        """Handle template selection."""
        sel = self.templates_tree.selection()
        if not sel:
            self.current_template_id = None
            return

        template_id = sel[0]
        templates = load_templates(self.conn)
        template = next((t for t in templates if t.id == template_id), None)

        if template:
            self.current_template_id = template.id
            self.template_name_var.set(template.name)
            self.template_title_var.set(template.title or "")
            self.template_project_var.set(template.project or "")
            self.template_priority_var.set(template.priority or "")
            self.template_time_estimated_var.set(str(template.time_estimated or ""))
            self.template_notes_text.delete("1.0", "end")
            self.template_notes_text.insert("1.0", template.notes or "")

    def on_new_template(self):
        """Create a new template."""
        self.current_template_id = None
        self.template_name_var.set("")
        self.template_title_var.set("")
        self.template_project_var.set("")
        self.template_priority_var.set("")
        self.template_time_estimated_var.set("")
        self.template_notes_text.delete("1.0", "end")
        self.templates_tree.selection_remove(self.templates_tree.selection())

    def on_save_template(self):
        """Save the current template."""
        name = self.template_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Template name is required.")
            return

        template = TaskTemplate(
            id=self.current_template_id or str(uuid.uuid4()),
            name=name,
            title=self.template_title_var.get().strip() or None,
            project=self.template_project_var.get().strip() or None,
            priority=self.template_priority_var.get().strip() or None,
            time_estimated=int(self.template_time_estimated_var.get())
            if self.template_time_estimated_var.get().strip()
            else None,
            notes=self.template_notes_text.get("1.0", "end").strip() or None,
        )

        save_template(self.conn, template)
        self.refresh_templates_list()
        messagebox.showinfo("Success", "Template saved.")

    def on_delete_template(self):
        """Delete the selected template."""
        if not self.current_template_id:
            messagebox.showinfo("No Selection", "Please select a template to delete.")
            return

        if messagebox.askyesno("Confirm", "Delete this template?"):
            delete_template(self.conn, self.current_template_id)
            self.on_new_template()
            self.refresh_templates_list()
            messagebox.showinfo("Success", "Template deleted.")

    def on_create_task_from_template(self):
        """Create a task from the selected template."""
        if not self.current_template_id:
            messagebox.showinfo(
                "No Selection", "Please select a template to create a task from."
            )
            return

        try:
            task = create_task_from_template(
                self.conn, self.current_template_id, owner=self.state_obj.active_persona
            )
            self.refresh_task_list()
            self.refresh_dashboard()
            messagebox.showinfo("Success", f"Task created: {task.title}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create task: {e}")

    # ---------- Settings Tab ----------

    def _build_settings_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.settings_frame = ttkb.Frame(self.notebook)
        else:
            self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")

        self.settings_frame.columnconfigure(1, weight=1)

        row = 0
        if TTKBOOTSTRAP_AVAILABLE:
            ttkb.Label(self.settings_frame, text="Theme:", bootstyle="primary").grid(
                row=row, column=0, sticky="e", padx=8, pady=8
            )
            self.theme_var = tk.StringVar(value=self.settings.theme)
            # Provide more theme options with ttkbootstrap
            theme_values = ["plain", "light", "dark"]
            # Map to ttkbootstrap themes for better names
            theme_combo = ttkb.Combobox(
                self.settings_frame,
                textvariable=self.theme_var,
                values=theme_values,
                state="readonly",
                bootstyle="primary",
            )
        else:
            ttk.Label(self.settings_frame, text="Theme:").grid(
                row=row, column=0, sticky="e", padx=8, pady=8
            )
            self.theme_var = tk.StringVar(value=self.settings.theme)
            theme_combo = ttk.Combobox(
                self.settings_frame,
                textvariable=self.theme_var,
                values=["plain", "light", "dark"],
                state="readonly",
            )
        theme_combo.grid(row=row, column=1, sticky="w", padx=8, pady=8)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(
                theme_combo,
                text="Choose UI theme: plain (cosmo), light (litera), or dark (darkly)",
            )

        row += 1
        ttk.Label(self.settings_frame, text="Default View:").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        self.default_view_var = tk.StringVar(value=self.settings.default_view)
        defview_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.default_view_var,
            values=["dashboard", "tasks", "projects"],
            state="readonly",
        )
        defview_combo.grid(row=row, column=1, sticky="w", padx=8, pady=8)

        row += 1
        ttk.Label(self.settings_frame, text="Font Scale:").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        self.font_scale_var = tk.StringVar(value=self.settings.font_scale)
        font_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.font_scale_var,
            values=["small", "medium", "large"],
            state="readonly",
        )
        font_combo.grid(row=row, column=1, sticky="w", padx=8, pady=8)

        row += 1
        self.show_sys_var = tk.BooleanVar(value=self.settings.show_system_status)
        show_sys_check = ttk.Checkbutton(
            self.settings_frame,
            text="Show system status panel on dashboard",
            variable=self.show_sys_var,
        )
        show_sys_check.grid(row=row, column=1, sticky="w", padx=8, pady=8)

        row += 1
        ttk.Label(self.settings_frame, text="AI change approvals:").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        self.approval_mode_var = tk.StringVar(
            value=self.settings.change_permission_mode
        )
        approval_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.approval_mode_var,
            values=["ask_when_unsure", "ask", "auto"],
            state="readonly",
        )
        approval_combo.grid(row=row, column=1, sticky="w", padx=8, pady=8)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(
                approval_combo,
                text="Choose when the AI should pause for approval before running commands",
            )

        row += 1
        if TTKBOOTSTRAP_AVAILABLE:
            pref_box = ttkb.Labelframe(
                self.settings_frame, text="📊 Data Preferences", bootstyle="info"
            )
        else:
            pref_box = ttk.LabelFrame(self.settings_frame, text="Data Preferences")
        pref_box.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        pref_box.columnconfigure(0, weight=1)
        pref_box.columnconfigure(1, weight=1)
        pref_labels = [
            ("notes", "Notes & Knowledge"),
            ("calendar", "Calendar Events"),
            ("mail", "Email / Messages"),
            ("files", "Files & Attachments"),
        ]
        self.data_pref_vars: Dict[str, tk.BooleanVar] = {}
        for idx, (key, label) in enumerate(pref_labels):
            var = tk.BooleanVar(
                value=self.settings.data_preferences.get(
                    key, DEFAULT_FETCH_PREFERENCES.get(key, True)
                )
            )
            chk = ttk.Checkbutton(pref_box, text=label, variable=var)
            chk.grid(row=idx // 2, column=idx % 2, sticky="w", padx=8, pady=4)
            self.data_pref_vars[key] = var

        row += 1
        if TTKBOOTSTRAP_AVAILABLE:
            export_import_box = ttkb.Labelframe(
                self.settings_frame, text="💾 Export & Import", bootstyle="secondary"
            )
        else:
            export_import_box = ttk.LabelFrame(
                self.settings_frame, text="Export & Import"
            )
        export_import_box.grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=8
        )
        export_import_box.columnconfigure(0, weight=1)
        export_import_box.columnconfigure(1, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            export_tasks_csv_btn = ttkb.Button(
                export_import_box,
                text="📥 Export Tasks (CSV)",
                command=lambda: self.on_export_tasks("csv"),
                bootstyle="info-outline",
            )
            export_tasks_json_btn = ttkb.Button(
                export_import_box,
                text="📥 Export Tasks (JSON)",
                command=lambda: self.on_export_tasks("json"),
                bootstyle="info-outline",
            )
            export_projects_btn = ttkb.Button(
                export_import_box,
                text="📥 Export Projects",
                command=self.on_export_projects,
                bootstyle="info-outline",
            )
            export_backup_btn = ttkb.Button(
                export_import_box,
                text="💾 Full Backup",
                command=self.on_export_backup,
                bootstyle="success-outline",
            )
            import_tasks_btn = ttkb.Button(
                export_import_box,
                text="📤 Import Tasks",
                command=self.on_import_tasks,
                bootstyle="warning-outline",
            )
        else:
            export_tasks_csv_btn = ttk.Button(
                export_import_box,
                text="Export Tasks (CSV)",
                command=lambda: self.on_export_tasks("csv"),
            )
            export_tasks_json_btn = ttk.Button(
                export_import_box,
                text="Export Tasks (JSON)",
                command=lambda: self.on_export_tasks("json"),
            )
            export_projects_btn = ttk.Button(
                export_import_box,
                text="Export Projects",
                command=self.on_export_projects,
            )
            export_backup_btn = ttk.Button(
                export_import_box, text="Full Backup", command=self.on_export_backup
            )
            import_tasks_btn = ttk.Button(
                export_import_box, text="Import Tasks", command=self.on_import_tasks
            )

        export_tasks_csv_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        export_tasks_json_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        export_projects_btn.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        export_backup_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        import_tasks_btn.grid(
            row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew"
        )

        row += 1
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(
                self.settings_frame,
                text="💾 Save Settings",
                command=self.on_save_settings,
                bootstyle="success",
            )
        else:
            save_btn = ttk.Button(
                self.settings_frame, text="Save Settings", command=self.on_save_settings
            )
        save_btn.grid(row=row, column=1, sticky="w", padx=8, pady=8)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(save_btn, text="Save all settings and apply changes")

    def on_save_settings(self):
        self.settings.theme = self.theme_var.get()
        self.settings.default_view = self.default_view_var.get()
        self.settings.show_system_status = self.show_sys_var.get()
        self.settings.font_scale = self.font_scale_var.get()
        self.settings.data_preferences = {
            k: var.get() for k, var in self.data_pref_vars.items()
        }
        self.settings.change_permission_mode = self.approval_mode_var.get()
        self.settings.auto_overwrite = self.settings.change_permission_mode == "auto"
        save_settings(self.conn, self.settings)

        # Apply theme change if ttkbootstrap is available
        if TTKBOOTSTRAP_AVAILABLE:
            theme_map = {"plain": "cosmo", "light": "litera", "dark": "darkly"}
            theme = theme_map.get(self.settings.theme, "cosmo")
            self.style.theme_use(theme)
        else:
            self._configure_style()
        self.refresh_dashboard()
        messagebox.showinfo("Settings", "Settings saved.")

    def on_export_tasks(self, format_type: str):
        """Export tasks to CSV or JSON file."""
        try:
            if format_type == "csv":
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                )
                if filename:
                    export_tasks_to_csv(self.conn, filename)
                    messagebox.showinfo("Export", f"Tasks exported to {filename}")
            elif format_type == "json":
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialfile=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                )
                if filename:
                    export_tasks_to_json(self.conn, filename)
                    messagebox.showinfo("Export", f"Tasks exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export tasks: {e}")

    def on_export_projects(self):
        """Export projects to JSON file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"projects_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )
            if filename:
                export_projects_to_json(self.conn, filename)
                messagebox.showinfo("Export", f"Projects exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export projects: {e}")

    def on_export_backup(self):
        """Export full database backup to JSON file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )
            if filename:
                export_full_backup(self.conn, filename)
                messagebox.showinfo("Export", f"Full backup exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export backup: {e}")

    def on_import_tasks(self):
        """Import tasks from CSV or JSON file."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*"),
                ]
            )
            if filename:
                imported = 0
                if filename.endswith(".csv"):
                    imported = import_tasks_from_csv(self.conn, filename)
                elif filename.endswith(".json"):
                    imported = import_tasks_from_json(self.conn, filename)
                else:
                    messagebox.showwarning(
                        "Import Error", "Please select a CSV or JSON file."
                    )
                    return

                if imported > 0:
                    messagebox.showinfo(
                        "Import", f"Successfully imported {imported} task(s)."
                    )
                    self.refresh_all()
                else:
                    messagebox.showwarning(
                        "Import",
                        "No tasks were imported. Please check the file format.",
                    )
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import tasks: {e}")

    # ---------- Global ----------

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_task_list()
        self.refresh_project_list()
        self.refresh_chat_history()
        if hasattr(self, "refresh_integrations_list"):
            self.refresh_integrations_list()
        if hasattr(self, "refresh_analytics"):
            self.refresh_analytics()
        if hasattr(self, "refresh_templates_list"):
            self.refresh_templates_list()
        if hasattr(self, "refresh_change_log"):
            self.refresh_change_log()

    def _apply_default_view(self):
        mapping = {
            "dashboard": 0,
            "tasks": 1,
            "projects": 2,
        }
        idx = mapping.get(self.settings.default_view, 0)
        try:
            self.notebook.select(idx)
        except tk.TclError:
            pass

    def on_close(self):
        save_active_persona(self.conn, self.state_obj)
        save_settings(self.conn, self.settings)
        if self.api_server:
            try:
                self.api_server.shutdown()
            except Exception:
                pass
        self.conn.close()
        self.destroy()


def run_gui():
    app = AssistantGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
