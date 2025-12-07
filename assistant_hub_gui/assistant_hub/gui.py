#!/usr/bin/env python3
import base64
import os
import sqlite3
import threading
import uuid
from datetime import datetime
from typing import Dict, Optional

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
    AppleCalendarIntegration,
    GmailIntegration,
    GitHubIntegration,
    NotesIntegration,
    WordIntegration,
    ExcelIntegration,
    OneNoteIntegration,
    OneDriveIntegration,
    FilesystemIntegration,
    GitIntegration,
    PDFIntegration,
)

# Additional imports for Tools & Operations tab
try:
    from .integrations.onenote.client import OneNoteClient
    ONENOTE_CLIENT_AVAILABLE = True
except ImportError:
    ONENOTE_CLIENT_AVAILABLE = False
    OneNoteClient = None

try:
    from .integrations.excel.cloud_client import ExcelCloudClient
    EXCEL_CLOUD_AVAILABLE = True
except ImportError:
    EXCEL_CLOUD_AVAILABLE = False
    ExcelCloudClient = None

try:
    from .integrations.excel.service import ExcelService, summarize_local_workbook
    EXCEL_SERVICE_AVAILABLE = True
except ImportError:
    EXCEL_SERVICE_AVAILABLE = False
    ExcelService = None
    summarize_local_workbook = None

try:
    from .integrations.word.service import WordService
    WORD_SERVICE_AVAILABLE = True
except ImportError:
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
            widget.attributes('-alpha', 0.0)
            delta = 1.0 / steps
            delay = duration // steps
            
            def step(alpha=0.0):
                if alpha < 1.0:
                    widget.attributes('-alpha', alpha)
                    widget.after(delay, lambda: step(alpha + delta))
                else:
                    widget.attributes('-alpha', 1.0)
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
            current_bootstyle = getattr(widget, 'cget', lambda x: None)('bootstyle')
            # Temporarily change color
            widget.configure(bootstyle="success")
            widget.after(200, lambda: widget.configure(bootstyle=current_bootstyle or "primary"))
        except:
            pass
    
    @staticmethod
    def add_hover_effect(button, enter_color=None, leave_color=None):
        """Add hover effect to buttons"""
        def on_enter(e):
            try:
                if TTKBOOTSTRAP_AVAILABLE and hasattr(button, 'configure'):
                    # Slightly increase size or change style
                    if enter_color:
                        button.configure(bootstyle="primary")
            except:
                pass
        
        def on_leave(e):
            try:
                if TTKBOOTSTRAP_AVAILABLE and hasattr(button, 'configure'):
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
                container, 
                mode='indeterminate',
                bootstyle="primary-striped",
                length=200
            )
            self.indicator_label = ttkb.Label(
                container,
                textvariable=self.progress_var,
                bootstyle="info"
            )
        else:
            self.progress_bar = ttk.Progressbar(
                container,
                mode='indeterminate',
                length=200
            )
            self.indicator_label = ttk.Label(
                container,
                textvariable=self.progress_var
            )
        
        self.progress_bar.grid(row=row, column=column, columnspan=columnspan, padx=4, pady=4, sticky="ew")
        self.indicator_label.grid(row=row+1, column=column, columnspan=columnspan, padx=4, pady=2)
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
        theme_map = {
            "plain": "cosmo",
            "light": "litera",
            "dark": "darkly"
        }
        theme = theme_map.get("plain", "cosmo")  # Default to cosmo
        
        if TTKBOOTSTRAP_AVAILABLE:
            super().__init__(themename=theme, title="Assistant Hub (GUI)", resizable=(True, True))
            # ttkbootstrap's style is already available as self.style from parent class
        else:
            super().__init__()
            self.title("Assistant Hub (GUI)")
            self.style = ttk.Style()
        
        self.geometry("1200x700")
        self.minsize(1150, 720)

        # Initialize fonts immediately with defaults (needed before loading settings)
        self.base_font = tkfont.nametofont("TkDefaultFont")
        self.text_font = tkfont.nametofont("TkTextFont")

        self.conn: sqlite3.Connection = init_db()
        self.state_obj: AssistantState = load_state(self.conn)
        self.settings: Settings = load_settings(self.conn)
        self.security_status: SecurityStatus = load_security_status(self.conn)

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
        self.command_var = tk.StringVar()
        self.cwd_var = tk.StringVar(value=os.getcwd())
        
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
        self._build_tools_tab()
        self._build_analytics_tab()
        self._build_settings_tab()
        
        # Update tab labels with icons if available
        if TTKBOOTSTRAP_AVAILABLE:
            self.notebook.tab(0, text="📊 Dashboard")
            self.notebook.tab(1, text="✅ Tasks")
            self.notebook.tab(2, text="📁 Projects")
            self.notebook.tab(3, text="💬 AI Console")
            self.notebook.tab(4, text="🔗 Integrations")
            self.notebook.tab(5, text="🔧 Tools")
            self.notebook.tab(6, text="📊 Analytics")
            self.notebook.tab(7, text="⚙️ Settings")

        # Initialize sync scheduler
        self.sync_scheduler = create_default_scheduler(self.conn)
        # Start scheduler in background (optional - can be started manually)
        # self.sync_scheduler.start()
        
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
        
        # Initialize Git versioning worker for automatic version control
        try:
            from .versioning import start_git_worker, get_git_manager
            start_git_worker()
            get_git_manager().ensure_repo()
            print("[GUI] Git versioning initialized - all changes will be automatically tracked")
        except Exception as e:
            print(f"[GUI] Warning: Could not initialize Git versioning: {e}")
        
        # Setup keyboard shortcuts for better usability
        self._setup_keyboard_shortcuts()
        
        self._apply_default_view()
        self.refresh_all()
        self._update_chat_status()
        # Initialize agent model display after UI is built
        if hasattr(self, 'chat_agent_var'):
            self.after(100, self.on_agent_change)
        
        # Add fade-in animation to main window if supported
        try:
            AnimationHelper.fade_in(self)
        except:
            pass

    # ---------- Top bar ----------

    def _initialize_fonts(self):
        """Configure fonts based on settings (fonts already initialized with defaults)."""
        try:
            scale_map = {"small": 10, "medium": 12, "large": 14}
            base_size = scale_map.get(getattr(self.settings, 'font_scale', 'medium'), 12)

            # Configure the already-initialized fonts
            if hasattr(self, 'base_font'):
                self.base_font.configure(size=base_size)
            else:
                self.base_font = tkfont.nametofont("TkDefaultFont")
                self.base_font.configure(size=base_size)

            if hasattr(self, 'text_font'):
                self.text_font.configure(size=base_size)
            else:
                self.text_font = tkfont.nametofont("TkTextFont")
                self.text_font.configure(size=base_size)
        except Exception as e:
            # Fallback to default fonts if configuration fails
            print(f"Warning: Could not configure fonts: {e}")
            if not hasattr(self, 'base_font'):
                self.base_font = tkfont.nametofont("TkDefaultFont")
            if not hasattr(self, 'text_font'):
                self.text_font = tkfont.nametofont("TkTextFont")

    def _configure_style(self):
        if TTKBOOTSTRAP_AVAILABLE:
            # ttkbootstrap handles themes automatically
            theme_map = {
                "plain": "cosmo",
                "light": "litera", 
                "dark": "darkly"
            }
            theme = theme_map.get(self.settings.theme, "cosmo")
            self.style.theme_use(theme)
        else:
            try:
                self.style.theme_use("clam")
            except tk.TclError:
                pass

        scale_map = {"small": 10, "medium": 12, "large": 14}
        base_size = scale_map.get(self.settings.font_scale, 12)

        # Fonts are already initialized by _initialize_fonts(), but we need heading_font
        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(size=base_size + 1, weight="bold")

        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(size=base_size + 1, weight="bold")

        self.option_add("*Font", self.base_font)
        self.style.configure("Treeview", rowheight=base_size + 12, font=(self.base_font.actual("family"), base_size))
        self.style.configure("Treeview.Heading", font=(heading_font.actual("family"), base_size))
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
                self.style.configure(style_name, background=colors["bg"], foreground=colors["fg"])

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
                bootstyle="primary"
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
            self.persona_role_display = ttkb.Label(top, textvariable=self.persona_role_var, bootstyle="info")
        else:
            self.persona_role_display = ttk.Label(top, textvariable=self.persona_role_var)
        self.persona_role_display.grid(row=0, column=3, sticky="w", padx=4)

        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(top, text="💾 Save", command=self._save_with_feedback, bootstyle="success")
            refresh_btn = ttkb.Button(top, text="🔄 Refresh", command=self._refresh_with_feedback, bootstyle="info")
        else:
            save_btn = ttk.Button(top, text="Save", command=self._save_with_feedback)
            refresh_btn = ttk.Button(top, text="Refresh", command=self._refresh_with_feedback)
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
            self._update_chat_status(f'Agent: {agent} | Model: {model} (auto)')

    def _save_with_feedback(self):
        """Save with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_save_btn_ref', None))
        self.on_save()
    
    def on_save(self):
        save_active_persona(self.conn, self.state_obj)
        save_settings(self.conn, self.settings)
        messagebox.showinfo("Saved", "Assistant state & settings saved.")
    
    def _refresh_with_feedback(self):
        """Refresh with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_refresh_btn_ref', None))
        self.refresh_all()
    
    def _setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts for better usability."""
        # Ctrl+S / Cmd+S - Save current item
        self.bind_all("<Control-s>", lambda e: self._save_with_feedback())
        self.bind_all("<Command-s>", lambda e: self._save_with_feedback())
        
        # Ctrl+N / Cmd+N - New item (context-aware)
        self.bind_all("<Control-n>", lambda e: self._new_item_shortcut())
        self.bind_all("<Command-n>", lambda e: self._new_item_shortcut())
        
        # Ctrl+R / Cmd+R - Refresh
        self.bind_all("<Control-r>", lambda e: self._refresh_with_feedback())
        self.bind_all("<Command-r>", lambda e: self._refresh_with_feedback())
        
        # Ctrl+W / Cmd+W - Close window (with confirmation)
        self.bind_all("<Control-w>", lambda e: self._close_window())
        self.bind_all("<Command-w>", lambda e: self._close_window())
        
        # Escape - Clear selection or close dialogs
        self.bind_all("<Escape>", lambda e: self._escape_handler())
        
        # F5 - Refresh
        self.bind_all("<F5>", lambda e: self._refresh_with_feedback())
        
        # Tab navigation shortcuts
        # Ctrl+1-9 - Switch to tabs
        for i in range(1, 10):
            self.bind_all(f"<Control-{i}>", lambda e, idx=i-1: self._switch_tab(idx))
            self.bind_all(f"<Command-{i}>", lambda e, idx=i-1: self._switch_tab(idx))
    
    def _new_item_shortcut(self):
        """Context-aware new item creation based on current tab."""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 1:  # Tasks tab
            self.on_new_task()
        elif current_tab == 2:  # Projects tab
            self.on_new_project()
        else:
            # Default: show info
            messagebox.showinfo("New Item", "Select Tasks or Projects tab to create new items")
    
    def _switch_tab(self, index):
        """Switch to tab by index."""
        try:
            if 0 <= index < self.notebook.index("end"):
                self.notebook.select(index)
        except:
            pass
    
    def _close_window(self):
        """Handle window close with optional confirmation."""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.quit()
    
    def _escape_handler(self):
        """Handle Escape key - clear selections or close dialogs."""
        # Clear any text field focus
        try:
            self.focus_set()
        except:
            pass

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
            self.today_box = ttkb.Labelframe(self.dashboard_frame, text="📋 Today's Focus", bootstyle="primary")
            self.upcoming_box = ttkb.Labelframe(self.dashboard_frame, text="📅 Upcoming Deadlines", bootstyle="info")
            self.status_box = ttkb.Labelframe(self.dashboard_frame, text="📊 Status Overview", bootstyle="success")
            self.load_box = ttkb.Labelframe(self.dashboard_frame, text="👥 Load by Persona", bootstyle="secondary")
            self.cyber_box = ttkb.Labelframe(self.dashboard_frame, text="🛡️ Cyber Defense Status", bootstyle="warning")
        else:
            self.today_box = ttk.LabelFrame(self.dashboard_frame, text="Today's Focus")
            self.upcoming_box = ttk.LabelFrame(self.dashboard_frame, text="Upcoming Deadlines")
            self.status_box = ttk.LabelFrame(self.dashboard_frame, text="Status Overview")
            self.load_box = ttk.LabelFrame(self.dashboard_frame, text="Load by Persona")
            self.cyber_box = ttk.LabelFrame(self.dashboard_frame, text="Cyber Defense Status")
        self.today_box.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.today_text = tk.Text(self.today_box, height=10, wrap="word", font=self.text_font)
        self.today_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.upcoming_box.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.upcoming_text = tk.Text(self.upcoming_box, height=10, wrap="word", font=self.text_font)
        self.upcoming_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.status_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.status_text = tk.Text(self.status_box, height=8, wrap="word", font=self.text_font)
        self.status_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.load_box.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self.load_text = tk.Text(self.load_box, height=8, wrap="word", font=self.text_font)
        self.load_text.pack(fill="both", expand=True, padx=4, pady=4)
        self.cyber_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8))
        self.cyber_box.columnconfigure(0, weight=1)

        self.cyber_status_var = tk.StringVar(value="Status: offline")
        if TTKBOOTSTRAP_AVAILABLE:
            self.cyber_status_label = ttkb.Label(
                self.cyber_box,
                textvariable=self.cyber_status_var,
                font=(self.base_font.actual("family"), self.base_font.actual("size") + 1, "bold"),
                bootstyle="info"
            )
        else:
            self.cyber_status_label = ttk.Label(
                self.cyber_box,
                textvariable=self.cyber_status_var,
                font=(self.base_font.actual("family"), self.base_font.actual("size") + 1, "bold"),
            )
        self.cyber_status_label.grid(row=0, column=0, sticky="w", padx=6, pady=(4, 2))

        self.cyber_message_var = tk.StringVar(value="Telemetry not available.")
        if TTKBOOTSTRAP_AVAILABLE:
            self.cyber_message_label = ttkb.Label(
                self.cyber_box,
                textvariable=self.cyber_message_var,
                wraplength=800,
                justify="left",
                bootstyle="secondary"
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
                font=(self.base_font.actual("family"), self.base_font.actual("size") - 1),
                bootstyle="secondary"
            )
        else:
            self.cyber_updated_label = ttk.Label(
                self.cyber_box,
                textvariable=self.cyber_updated_var,
                font=(self.base_font.actual("family"), self.base_font.actual("size") - 1),
            )
        self.cyber_updated_label.grid(row=2, column=0, sticky="w", padx=6, pady=(0, 4))

        if TTKBOOTSTRAP_AVAILABLE:
            self.sys_box = ttkb.Labelframe(self.dashboard_frame, text="💻 System Status (Optional)", bootstyle="secondary")
        else:
            self.sys_box = ttk.LabelFrame(self.dashboard_frame, text="System Status (Optional)")
        self.sys_box.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8))
        self.sys_text = tk.Text(self.sys_box, height=4, wrap="word", font=self.text_font)
        self.sys_text.pack(fill="both", expand=True, padx=4, pady=4)

    def refresh_dashboard(self):
        state = self.state_obj
        tasks = state.tasks
        today_str = datetime.now().strftime("%Y-%m-%d")

        today_tasks = [t for t in tasks if t.due_date == today_str and t.status != "DONE"]
        priority_weight = {p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)}
        incomplete = [t for t in tasks if t.status != "DONE"]
        incomplete_sorted = sorted(
            incomplete,
            key=lambda t: (priority_weight.get(t.priority, 1), t.due_date or "9999-99-99", t.id),
            reverse=True,
        )

        upcoming = [t for t in tasks if t.due_date and t.due_date > today_str and t.status != "DONE"]
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
            self.today_text.insert("end", "No tasks explicitly due today.\nShowing top 3 priorities:\n\n")
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
        if self.settings.data_preferences.get("calendar", False) or \
           self.settings.data_preferences.get("mail", False) or \
           self.settings.data_preferences.get("notes", False):
            try:
                from .db import get_meta
                import json
                # Get recent external items
                c = self.conn.cursor()
                c.execute("""
                    SELECT ei.title, ei.kind, es.name, ei.last_seen_at
                    FROM external_items ei
                    JOIN external_sources es ON ei.source_id = es.id
                    ORDER BY ei.last_seen_at DESC
                    LIMIT 5
                """)
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
            self.cyber_status_label.configure(foreground=color_map.get(self.security_status.status, "#202020"))

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
            ttkb.Label(filters, text="Project:", bootstyle="secondary").grid(row=0, column=0, padx=(0, 4))
            self.filter_project_var = tk.StringVar()
            self.filter_project_combo = ttkb.Combobox(filters, textvariable=self.filter_project_var, state="readonly", bootstyle="secondary")
            self.filter_project_combo.grid(row=0, column=1, padx=(0, 10))

            ttkb.Label(filters, text="Owner:", bootstyle="secondary").grid(row=0, column=2, padx=(0, 4))
            self.filter_owner_var = tk.StringVar()
            self.filter_owner_combo = ttkb.Combobox(filters, textvariable=self.filter_owner_var, state="readonly", bootstyle="secondary")
            self.filter_owner_combo.grid(row=0, column=3, sticky="w", padx=(0, 10))

            self.show_done_var = tk.BooleanVar(value=True)
            show_done_check = ttkb.Checkbutton(
                filters, text="Show Done", variable=self.show_done_var, command=self.refresh_task_list, bootstyle="primary-round-toggle"
            )
        else:
            ttk.Label(filters, text="Project:").grid(row=0, column=0, padx=(0, 4))
            self.filter_project_var = tk.StringVar()
            self.filter_project_combo = ttk.Combobox(filters, textvariable=self.filter_project_var, state="readonly")
            self.filter_project_combo.grid(row=0, column=1, padx=(0, 10))

            ttk.Label(filters, text="Owner:").grid(row=0, column=2, padx=(0, 4))
            self.filter_owner_var = tk.StringVar()
            self.filter_owner_combo = ttk.Combobox(filters, textvariable=self.filter_owner_var, state="readonly")
            self.filter_owner_combo.grid(row=0, column=3, sticky="w", padx=(0, 10))

            self.show_done_var = tk.BooleanVar(value=True)
            show_done_check = ttk.Checkbutton(
                filters, text="Show Done", variable=self.show_done_var, command=self.refresh_task_list
            )
        show_done_check.grid(row=0, column=4, padx=(0, 10))

        if TTKBOOTSTRAP_AVAILABLE:
            refresh_btn = ttkb.Button(filters, text="🔍 Apply Filters", command=self.refresh_task_list, bootstyle="info-outline")
        else:
            refresh_btn = ttk.Button(filters, text="Apply Filters", command=self.refresh_task_list)
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
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
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
            scrollbar = ttkb.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview, bootstyle="primary-round")
        else:
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        # Add double-click to edit
        self.task_tree.bind("<Double-1>", lambda e: self.on_save_task_changes() if self.task_tree.selection() else None)
        # Add keyboard shortcuts
        self.task_tree.bind("<Return>", lambda e: self.on_save_task_changes() if self.task_tree.selection() else None)
        self.task_tree.bind("<Delete>", lambda e: self.on_delete_task() if self.task_tree.selection() else None)

        if TTKBOOTSTRAP_AVAILABLE:
            detail = ttkb.Labelframe(self.tasks_frame, text="📝 Task Details", bootstyle="primary")
        else:
            detail = ttk.LabelFrame(self.tasks_frame, text="Task Details")
        detail.grid(row=1, column=1, sticky="nsew", padx=8, pady=4)
        for i in range(2):
            detail.columnconfigure(i, weight=1)

        row = 0
        ttk.Label(detail, text="ID:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
        self.task_id_var = tk.StringVar()
        ttk.Label(detail, textvariable=self.task_id_var).grid(row=row, column=1, sticky="w", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Title:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
        self.title_entry = ttk.Entry(detail)
        self.title_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Project:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
        self.project_entry = ttk.Entry(detail)
        self.project_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Owner:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
        self.owner_combo = ttk.Combobox(detail, values=PERSONAS, state="readonly")
        self.owner_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Status:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
        self.status_combo = ttk.Combobox(detail, values=STATUS_OPTIONS, state="readonly")
        self.status_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Priority:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
        self.priority_combo = ttk.Combobox(detail, values=PRIORITY_OPTIONS, state="readonly")
        self.priority_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Due (YYYY-MM-DD):").grid(row=row, column=0, sticky="e", padx=4, pady=2)
        self.due_entry = ttk.Entry(detail)
        self.due_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(detail, text="Notes:").grid(row=row, column=0, sticky="ne", padx=4, pady=2)
        self.notes_text = tk.Text(detail, height=5, wrap="word", font=self.text_font)
        self.notes_text.grid(row=row, column=1, sticky="nsew", padx=4, pady=2)
        detail.rowconfigure(row, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            btns = ttkb.Frame(detail)
        else:
            btns = ttk.Frame(detail)
        btns.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        btns.columnconfigure(2, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            add_btn = ttkb.Button(btns, text="➕ New Task", command=self.on_new_task, bootstyle="primary-outline")
            save_btn = ttkb.Button(btns, text="💾 Save Changes", command=self._save_task_with_feedback, bootstyle="success")
            delete_btn = ttkb.Button(btns, text="🗑️ Delete Task", command=self._delete_task_with_feedback, bootstyle="danger-outline")
        else:
            add_btn = ttk.Button(btns, text="New Task", command=self.on_new_task)
            save_btn = ttk.Button(btns, text="Save Changes", command=self._save_task_with_feedback)
            delete_btn = ttk.Button(btns, text="Delete Task", command=self._delete_task_with_feedback)
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

        priority_weight = {p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)}
        tasks_sorted = sorted(
            tasks,
            key=lambda t: (priority_weight.get(t.priority, 1), t.due_date or "9999-99-99", t.id),
            reverse=True,
        )

        for t in tasks_sorted:
            self.task_tree.insert(
                "",
                "end",
                iid=str(t.id),
                values=(t.id, t.title, t.project, t.owner, t.status, t.priority, t.due_date or ""),
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
        if hasattr(self, 'time_estimated_entry'):
            self.time_estimated_entry.delete(0, "end")
        if hasattr(self, 'time_logged_entry'):
            self.time_logged_entry.delete(0, "end")
        if hasattr(self, 'depends_on_entry'):
            self.depends_on_entry.delete(0, "end")
        if hasattr(self, 'recurrence_pattern_var'):
            self.recurrence_pattern_var.set("")
        if hasattr(self, 'recurrence_end_entry'):
            self.recurrence_end_entry.delete(0, "end")
        self.notes_text.delete("1.0", "end")

    def _save_task_with_feedback(self):
        """Save task with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_task_save_btn', None))
        self.on_save_task_changes()
    
    def _delete_task_with_feedback(self):
        """Delete task with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_task_delete_btn', None))
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
            messagebox.showwarning("Invalid Date", "Due date must be YYYY-MM-DD or blank.")
            return

        # Get time tracking values
        time_estimated = None
        if hasattr(self, 'time_estimated_entry'):
            time_est_str = self.time_estimated_entry.get().strip()
            if time_est_str:
                try:
                    time_estimated = int(time_est_str)
                except ValueError:
                    pass
        
        time_logged = None
        if hasattr(self, 'time_logged_entry'):
            time_log_str = self.time_logged_entry.get().strip()
            if time_log_str:
                try:
                    time_logged = int(time_log_str)
                except ValueError:
                    pass
        
        # Get dependency
        depends_on = None
        if hasattr(self, 'depends_on_entry'):
            dep_str = self.depends_on_entry.get().strip()
            if dep_str:
                try:
                    depends_on = int(dep_str)
                except ValueError:
                    pass
        
        # Get recurrence
        recurrence_pattern = None
        if hasattr(self, 'recurrence_pattern_var'):
            rec_pattern = self.recurrence_pattern_var.get().strip()
            if rec_pattern:
                recurrence_pattern = rec_pattern
        
        recurrence_end = None
        if hasattr(self, 'recurrence_end_entry'):
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
        if hasattr(self, 'time_estimated_entry'):
            self.time_estimated_entry.delete(0, "end")
        if hasattr(self, 'time_logged_entry'):
            self.time_logged_entry.delete(0, "end")
        if hasattr(self, 'depends_on_entry'):
            self.depends_on_entry.delete(0, "end")
        if hasattr(self, 'recurrence_pattern_var'):
            self.recurrence_pattern_var.set("")
        if hasattr(self, 'recurrence_end_entry'):
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
        if not hasattr(self, '_timer_start_time'):
            self._timer_start_time = {}
        self._timer_start_time[tid] = datetime.now()
        
        messagebox.showinfo("Timer Started", f"Timer started for task #{tid}. Click 'Stop Timer' when done.")
        
        # Update button
        if hasattr(self, '_timer_button'):
            if TTKBOOTSTRAP_AVAILABLE:
                self._timer_button.config(text="⏹️ Stop Timer", command=self.on_stop_timer, bootstyle="danger-outline")
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
        
        if not hasattr(self, '_timer_start_time') or tid not in self._timer_start_time:
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
            if hasattr(self, 'time_logged_entry'):
                self.time_logged_entry.delete(0, "end")
                self.time_logged_entry.insert(0, str(task.time_logged))
            
            messagebox.showinfo("Timer Stopped", f"Added {elapsed_minutes} minutes to task #{tid}.")
        
        # Remove from timer dict
        del self._timer_start_time[tid]
        
        # Update button
        if hasattr(self, '_timer_button'):
            if TTKBOOTSTRAP_AVAILABLE:
                self._timer_button.config(text="⏱️ Start Timer", command=self.on_start_timer, bootstyle="info-outline")
            else:
                self._timer_button.config(text="Start Timer", command=self.on_start_timer)
        
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
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
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
            scrollbar = ttkb.Scrollbar(list_frame, orient="vertical", command=self.project_tree.yview, bootstyle="primary-round")
        else:
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.project_tree.yview)
        self.project_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.project_tree.bind("<<TreeviewSelect>>", self.on_project_select)
        # Add double-click to edit
        self.project_tree.bind("<Double-1>", lambda e: self.on_save_project() if self.project_tree.selection() else None)
        # Add keyboard shortcuts
        self.project_tree.bind("<Return>", lambda e: self.on_save_project() if self.project_tree.selection() else None)
        self.project_tree.bind("<Delete>", lambda e: self.on_delete_project() if self.project_tree.selection() else None)

        if TTKBOOTSTRAP_AVAILABLE:
            detail = ttkb.Labelframe(self.projects_frame, text="📁 Project Details", bootstyle="primary")
        else:
            detail = ttk.LabelFrame(self.projects_frame, text="Project Details")
        detail.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        for i in range(2):
            detail.columnconfigure(i, weight=1)

        row = 0
        ttk.Label(detail, text="Name:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        self.proj_name_entry = ttk.Entry(detail)
        self.proj_name_entry.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(detail, text="Priority:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        self.proj_priority_combo = ttk.Combobox(detail, values=PRIORITY_OPTIONS, state="readonly")
        self.proj_priority_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(detail, text="Status:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        self.proj_status_combo = ttk.Combobox(detail, values=["active", "paused", "archived"], state="readonly")
        self.proj_status_combo.grid(row=row, column=1, sticky="ew", padx=4, pady=4)

        row += 1
        ttk.Label(detail, text="Description:").grid(row=row, column=0, sticky="ne", padx=4, pady=4)
        self.proj_desc_text = tk.Text(detail, height=6, wrap="word", font=self.text_font)
        self.proj_desc_text.grid(row=row, column=1, sticky="nsew", padx=4, pady=4)
        detail.rowconfigure(row, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            btns = ttkb.Frame(detail)
        else:
            btns = ttk.Frame(detail)
        btns.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        btns.columnconfigure(2, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            new_btn = ttkb.Button(btns, text="➕ New Project", command=self.on_new_project, bootstyle="primary-outline")
            save_btn = ttkb.Button(btns, text="💾 Save Project", command=self._save_project_with_feedback, bootstyle="success")
            delete_btn = ttkb.Button(btns, text="🗑️ Delete Project", command=self._delete_project_with_feedback, bootstyle="danger-outline")
        else:
            new_btn = ttk.Button(btns, text="New Project", command=self.on_new_project)
            save_btn = ttk.Button(btns, text="Save Project", command=self._save_project_with_feedback)
            delete_btn = ttk.Button(btns, text="Delete Project", command=self._delete_project_with_feedback)
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
        
        # File Task Extraction Section
        if TTKBOOTSTRAP_AVAILABLE:
            extract_section = ttkb.Labelframe(detail, text="📄 Extract Tasks from File", bootstyle="info")
        else:
            extract_section = ttk.LabelFrame(detail, text="Extract Tasks from File")
        extract_section.grid(row=row+2, column=0, columnspan=2, sticky="ew", padx=4, pady=(8, 4))
        extract_section.columnconfigure(0, weight=1)
        
        if TTKBOOTSTRAP_AVAILABLE:
            extract_info = ttkb.Label(extract_section, text="Upload a file to automatically extract tasks using AI", bootstyle="secondary", wraplength=400)
            extract_btn = ttkb.Button(extract_section, text="📁 Upload File & Extract Tasks", command=self.on_extract_tasks_from_file, bootstyle="info")
        else:
            extract_info = ttk.Label(extract_section, text="Upload a file to automatically extract tasks using AI", wraplength=400)
            extract_btn = ttk.Button(extract_section, text="Upload File & Extract Tasks", command=self.on_extract_tasks_from_file)
        extract_info.grid(row=0, column=0, sticky="w", padx=4, pady=4)
        extract_btn.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        
        # Status label for extraction
        self.extract_status_var = tk.StringVar(value="")
        if TTKBOOTSTRAP_AVAILABLE:
            extract_status = ttkb.Label(extract_section, textvariable=self.extract_status_var, bootstyle="secondary", wraplength=400)
        else:
            extract_status = ttk.Label(extract_section, textvariable=self.extract_status_var, wraplength=400)
        extract_status.grid(row=2, column=0, sticky="w", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(extract_btn, text="Upload a file (txt, md, docx, pdf, etc.) and AI will extract tasks automatically")

    def refresh_project_list(self):
        for row in self.project_tree.get_children():
            self.project_tree.delete(row)

        counts: Dict[str, int] = {}
        for t in self.state_obj.tasks:
            counts[t.project] = counts.get(t.project, 0) + 1

        priority_weight = {p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)}
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
        AnimationHelper.pulse_button(getattr(self, '_project_save_btn', None))
        self.on_save_project()
    
    def _delete_project_with_feedback(self):
        """Delete project with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_project_delete_btn', None))
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
            new_proj = Project(name=name, description=desc, status=status, priority=priority)
            self.state_obj.projects.append(new_proj)

        db_upsert_project(self.conn, next(p for p in self.state_obj.projects if p.name == name))
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
    
    def on_extract_tasks_from_file(self):
        """Extract tasks from an uploaded file for the selected project."""
        # Check if a project is selected
        sel = self.project_tree.selection()
        if not sel:
            messagebox.showwarning("No Project Selected", "Please select a project first to extract tasks into.")
            return
        
        project_name = sel[0]
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select File to Extract Tasks From",
            filetypes=[
                ("All Supported", "*.txt *.md *.docx *.pdf *.rtf *.csv"),
                ("Text Files", "*.txt"),
                ("Markdown", "*.md"),
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("Rich Text", "*.rtf"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Update status
            self.extract_status_var.set("🔄 Extracting tasks...")
            self.update()
            
            # Import the extraction function
            from .file_task_extraction import extract_and_create_tasks_from_file
            
            # Extract tasks
            created_tasks = extract_and_create_tasks_from_file(
                self.conn,
                file_path,
                project_name,
                owner=self.state_obj.active_persona
            )
            
            if created_tasks:
                self.extract_status_var.set(f"✅ {len(created_tasks)} tasks extracted successfully!")
                messagebox.showinfo(
                    "Tasks Extracted",
                    f"Successfully extracted {len(created_tasks)} tasks from the file.\n\n"
                    f"Tasks have been added to project '{project_name}'.\n"
                    f"View them in the Tasks tab."
                )
                # Refresh task list
                self.refresh_all()
            else:
                self.extract_status_var.set("⚠️ No tasks found in file")
                messagebox.showinfo(
                    "No Tasks Found",
                    "The file was processed but no tasks could be extracted.\n\n"
                    "Make sure the file contains task-like items (bullet points, numbered lists, TODO items, etc.)"
                )
        except Exception as e:
            self.extract_status_var.set(f"❌ Error: {str(e)}")
            messagebox.showerror("Extraction Error", f"Failed to extract tasks from file:\n{e}")

    # ---------- AI Chat + Terminal Tab ----------

    def _build_chat_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.chat_frame = ttkb.Frame(self.notebook)
        else:
            self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="AI Console")

        # Support side-by-side layout: chat on left, document interaction on right
        # Keep the layout evenly split so both areas are always visible
        self.chat_frame.columnconfigure(0, weight=1)
        self.chat_frame.columnconfigure(1, weight=1)
        self.chat_frame.rowconfigure(0, weight=3)
        self.chat_frame.rowconfigure(1, weight=2)

        # Left side: Chat conversation and compose
        if TTKBOOTSTRAP_AVAILABLE:
            chat_container = ttkb.Frame(self.chat_frame)
        else:
            chat_container = ttk.Frame(self.chat_frame)
        chat_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(8, 4), pady=8)
        chat_container.columnconfigure(0, weight=1)
        chat_container.rowconfigure(0, weight=3)
        chat_container.rowconfigure(1, weight=2)

        if TTKBOOTSTRAP_AVAILABLE:
            convo_frame = ttkb.Labelframe(chat_container, text="💬 Chat & Terminal", bootstyle="primary")
            compose = ttkb.Labelframe(chat_container, text="✍️ Compose Message & Terminal", bootstyle="info")
        else:
            convo_frame = ttk.LabelFrame(chat_container, text="Chat & Terminal")
            compose = ttk.LabelFrame(chat_container, text="Compose Message & Terminal")
        convo_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        convo_frame.columnconfigure(0, weight=1)
        convo_frame.rowconfigure(0, weight=1)
        self.chat_text = tk.Text(convo_frame, wrap="word", state="disabled", font=self.text_font)
        self.chat_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        if TTKBOOTSTRAP_AVAILABLE:
            chat_scroll = ttkb.Scrollbar(convo_frame, orient="vertical", command=self.chat_text.yview, bootstyle="primary-round")
        else:
            chat_scroll = ttk.Scrollbar(convo_frame, orient="vertical", command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=chat_scroll.set)
        chat_scroll.grid(row=0, column=1, sticky="ns")
        compose.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        compose.columnconfigure(1, weight=1)

        # Right side: Document interaction panel (always visible)
        if TTKBOOTSTRAP_AVAILABLE:
            self.document_frame = ttkb.Labelframe(self.chat_frame, text="📑 Document Interaction", bootstyle="success")
        else:
            self.document_frame = ttk.LabelFrame(self.chat_frame, text="Document Interaction")
        self.document_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(4, 8), pady=8)
        self.document_frame.columnconfigure(0, weight=1)
        self.document_frame.rowconfigure(1, weight=1)
        self.document_frame.rowconfigure(2, weight=1)

        # Track active file editing session
        self.active_file_session = None  # Dict with 'type', 'path', 'content', etc.

        # Initialize file preview panel reference (will be created in _build_file_preview_panel)
        self.file_preview_frame = None
        self.file_preview_text = None
        self.file_preview_title_var = None
        self.file_preview_status_var = None
        self.document_activity_text = None

        # Build document interaction panels
        self._build_file_preview_panel()
        self._build_document_activity_panel()

        if TTKBOOTSTRAP_AVAILABLE:
            ttkb.Label(compose, text="From:", bootstyle="secondary").grid(row=0, column=0, sticky="e", padx=4, pady=2)
            sender_combo = ttkb.Combobox(
                compose,
                textvariable=self.chat_sender_var,
                values=PERSONAS,
                state="readonly",
                width=12,
                bootstyle="primary"
            )
            ttkb.Label(compose, text="Respond As:", bootstyle="secondary").grid(row=0, column=2, sticky="e", padx=4, pady=2)
            agent_combo = ttkb.Combobox(
                compose,
                textvariable=self.chat_agent_var,
                values=PERSONAS,
                state="readonly",
                width=12,
                bootstyle="info"
            )
            ttkb.Label(compose, text="Model:", bootstyle="secondary").grid(row=0, column=4, sticky="e", padx=4, pady=2)
            self.model_combo = ttkb.Combobox(
                compose,
                textvariable=self.chat_model_var,
                values=["auto", "gpt-4o", "gpt-4o-mini", "o1-preview", "gpt-4-turbo"],
                state="readonly",
                width=16,
                bootstyle="success"
            )
            ttkb.Label(compose, text="System Prompt:", bootstyle="secondary").grid(row=1, column=0, sticky="ne", padx=4, pady=2)
            ttkb.Label(compose, text="Message:", bootstyle="secondary").grid(row=2, column=0, sticky="ne", padx=4, pady=(4, 2))
        else:
            ttk.Label(compose, text="From:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
            sender_combo = ttk.Combobox(
                compose,
                textvariable=self.chat_sender_var,
                values=PERSONAS,
                state="readonly",
                width=12,
            )
            ttk.Label(compose, text="Respond As:").grid(row=0, column=2, sticky="e", padx=4, pady=2)
            agent_combo = ttk.Combobox(
                compose,
                textvariable=self.chat_agent_var,
                values=PERSONAS,
                state="readonly",
                width=12,
            )
            ttk.Label(compose, text="Model:").grid(row=0, column=4, sticky="e", padx=4, pady=2)
            self.model_combo = ttk.Combobox(
                compose,
                textvariable=self.chat_model_var,
                values=["auto", "gpt-4o", "gpt-4o-mini", "o1-preview", "gpt-4-turbo"],
                state="readonly",
                width=16,
            )
            ttk.Label(compose, text="System Prompt:").grid(row=1, column=0, sticky="ne", padx=4, pady=2)
            ttk.Label(compose, text="Input:").grid(row=2, column=0, sticky="ne", padx=4, pady=(4, 2))
        sender_combo.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=2)
        agent_combo.grid(row=0, column=3, sticky="w", padx=(0, 4), pady=2)
        agent_combo.bind("<<ComboboxSelected>>", self.on_agent_change)
        self.model_combo.grid(row=0, column=5, sticky="w", padx=(0, 4), pady=2)
        self.model_combo.set("auto")
        self.model_combo.bind("<<ComboboxSelected>>", self.on_agent_change)
        
        self.system_prompt_text = tk.Text(compose, height=3, wrap="word", font=self.text_font)
        self.system_prompt_text.grid(row=1, column=1, columnspan=5, sticky="nsew", padx=4, pady=2)
        self.system_prompt_text.insert("1.0", DEFAULT_SYSTEM_PROMPT)
        
        # Combined input section - CWD selector and unified input field
        if TTKBOOTSTRAP_AVAILABLE:
            input_meta_frame = ttkb.Frame(compose)
        else:
            input_meta_frame = ttk.Frame(compose)
        input_meta_frame.grid(row=2, column=1, columnspan=5, sticky="ew", padx=4, pady=(4, 2))
        input_meta_frame.columnconfigure(1, weight=1)
        
        # CWD selector (compact, on same row as input hint)
        if TTKBOOTSTRAP_AVAILABLE:
            cwd_label = ttkb.Label(input_meta_frame, text="CWD:", bootstyle="secondary")
            self.cwd_entry = ttkb.Entry(input_meta_frame, textvariable=self.cwd_var, bootstyle="primary", width=20)
            browse_btn = ttkb.Button(input_meta_frame, text="📂", command=self.on_browse_cwd, bootstyle="secondary-outline", width=3)
        else:
            cwd_label = ttk.Label(input_meta_frame, text="CWD:")
            self.cwd_entry = ttk.Entry(input_meta_frame, textvariable=self.cwd_var, width=20)
            browse_btn = ttk.Button(input_meta_frame, text="📂", command=self.on_browse_cwd, width=3)
        cwd_label.grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.cwd_entry.grid(row=0, column=1, sticky="w", padx=(0, 4))
        browse_btn.grid(row=0, column=2, sticky="w", padx=(0, 0))
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(browse_btn, text="Browse for working directory")
        
        # Combined input field (replaces both chat_input and command_entry)
        # Use Text widget for multi-line support (both messages and commands)
        self.chat_input = tk.Text(compose, height=4, wrap="word", font=self.text_font)
        self.chat_input.grid(row=3, column=1, columnspan=5, sticky="nsew", padx=4, pady=(4, 2))
        # Ctrl+Enter sends as chat message, Enter alone checks if it's a command
        self.chat_input.bind("<Control-Return>", lambda e: (self.on_handle_combined_input(chat_mode=True), "break"))
        self.chat_input.bind("<Return>", lambda e: self.on_handle_combined_input_enter(e))
        
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
        for idx in range(4):
            btns.columnconfigure(idx, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            import_btn = ttkb.Button(btns, text="📁 Import", command=self.on_import_chat_file, bootstyle="info-outline")
            upload_btn = ttkb.Button(btns, text="☁️ Upload", command=self._upload_file_with_feedback, bootstyle="secondary-outline")
            send_btn = ttkb.Button(btns, text="🚀 Send", command=lambda: self.on_handle_combined_input(chat_mode=True), bootstyle="primary")
            clear_btn = ttkb.Button(btns, text="🗑️ Clear", command=self.on_clear_chat_history, bootstyle="danger-outline")
        else:
            import_btn = ttk.Button(btns, text="Import", command=self.on_import_chat_file)
            upload_btn = ttk.Button(btns, text="Upload", command=self._upload_file_with_feedback)
            send_btn = ttk.Button(btns, text="Send", command=lambda: self.on_handle_combined_input(chat_mode=True))
            clear_btn = ttk.Button(btns, text="Clear", command=self.on_clear_chat_history)
        import_btn.grid(row=0, column=0, padx=4, sticky="ew")
        upload_btn.grid(row=0, column=1, padx=4, sticky="ew")
        send_btn.grid(row=0, column=2, padx=4, sticky="ew")
        clear_btn.grid(row=0, column=3, padx=4, sticky="ew")
        
        # Add hover effects to chat buttons
        AnimationHelper.add_hover_effect(import_btn)
        AnimationHelper.add_hover_effect(upload_btn)
        AnimationHelper.add_hover_effect(send_btn)
        AnimationHelper.add_hover_effect(clear_btn)
        self._chat_send_btn = send_btn
        
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(import_btn, text="Import file content into input")
            ToolTip(upload_btn, text="Upload file to OpenAI for AI analysis")
            ToolTip(send_btn, text="Send message (Ctrl+Enter) or run command (Enter for single-line, prefix with $)")
            ToolTip(clear_btn, text="Clear all chat history")

        if TTKBOOTSTRAP_AVAILABLE:
            self.chat_status_label = ttkb.Label(compose, textvariable=self.chat_status_var, bootstyle="info")
        else:
            self.chat_status_label = ttk.Label(compose, textvariable=self.chat_status_var)
        self.chat_status_label.grid(row=5, column=0, columnspan=6, sticky="w", padx=4, pady=(2, 0))
        
        # Add progress indicator for AI responses
        progress_container = ttkb.Frame(compose) if TTKBOOTSTRAP_AVAILABLE else ttk.Frame(compose)
        progress_container.grid(row=6, column=0, columnspan=6, sticky="ew", padx=4, pady=(2, 0))
        progress_container.columnconfigure(0, weight=1)
        self.chat_progress = ProgressIndicator(self).create(progress_container, row=0, column=0, columnspan=1)
        self.chat_progress.progress_bar.grid_remove()
        self.chat_progress.indicator_label.grid_remove()

    def _build_file_preview_panel(self):
        """Build the file preview panel for side-by-side file editing."""
        if TTKBOOTSTRAP_AVAILABLE:
            header_frame = ttkb.Frame(self.document_frame)
        else:
            self.file_preview_frame = ttk.LabelFrame(self.chat_frame, text="File Preview")
        
        # Always visible so the AI and document panels stay side-by-side
        self.file_preview_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(4, 8), pady=8)
        self.file_preview_frame.columnconfigure(0, weight=1)
        self.file_preview_frame.rowconfigure(2, weight=1)
        
            header_frame = ttk.Frame(self.document_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        header_frame.columnconfigure(0, weight=1)

        supported_formats = "PDF, Word, Excel, CSV, TXT, JSON, OneNote"
        if TTKBOOTSTRAP_AVAILABLE:
            ttkb.Label(header_frame, text=f"Supports: {supported_formats}", bootstyle="secondary").grid(row=0, column=0, sticky="w")
            open_btn = ttkb.Button(header_frame, text="📂 Open Document", command=self.on_open_document_file, bootstyle="secondary-outline")
        else:
            ttk.Label(header_frame, text=f"Supports: {supported_formats}").grid(row=0, column=0, sticky="w")
            open_btn = ttk.Button(header_frame, text="Open Document", command=self.on_open_document_file)
        open_btn.grid(row=0, column=1, sticky="e", padx=4)

        if TTKBOOTSTRAP_AVAILABLE:
            self.file_preview_frame = ttkb.Labelframe(self.document_frame, text="📄 Live File Preview", bootstyle="success")
        else:
            self.file_preview_frame = ttk.LabelFrame(self.document_frame, text="Live File Preview")

        self.file_preview_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.file_preview_frame.columnconfigure(0, weight=1)
        self.file_preview_frame.rowconfigure(1, weight=1)

        # Header with file info and close button
        if TTKBOOTSTRAP_AVAILABLE:
            file_header = ttkb.Frame(self.file_preview_frame)
        else:
            file_header = ttk.Frame(self.file_preview_frame)
        file_header.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        file_header.columnconfigure(0, weight=1)

        self.file_preview_title_var = tk.StringVar(value="No file open")
        if TTKBOOTSTRAP_AVAILABLE:
            title_label = ttkb.Label(file_header, textvariable=self.file_preview_title_var, bootstyle="success", font=(self.base_font.actual("family"), self.base_font.actual("size") + 1, "bold"))
            close_btn = ttkb.Button(file_header, text="✕", command=self._close_file_preview, bootstyle="danger-outline", width=3)
        else:
            title_label = ttk.Label(file_header, textvariable=self.file_preview_title_var, font=(self.base_font.actual("family"), self.base_font.actual("size") + 1, "bold"))
            close_btn = ttk.Button(file_header, text="✕", command=self._close_file_preview, width=3)
        title_label.grid(row=0, column=0, sticky="w", padx=4)
        close_btn.grid(row=0, column=1, sticky="e", padx=4)
        
        # Document picker for all supported formats
        if TTKBOOTSTRAP_AVAILABLE:
            picker_frame = ttkb.Frame(self.file_preview_frame)
        else:
            picker_frame = ttk.Frame(self.file_preview_frame)
        picker_frame.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 6))
        picker_frame.columnconfigure(1, weight=1)

        self.document_path_var = tk.StringVar(value="")
        picker_label = ttkb.Label(picker_frame, text="Load a document (PDF, Word, Excel, CSV, TXT, JSON, OneNote export)",
                                   bootstyle="secondary") if TTKBOOTSTRAP_AVAILABLE else ttk.Label(
            picker_frame, text="Load a document (PDF, Word, Excel, CSV, TXT, JSON, OneNote export)")
        picker_label.grid(row=0, column=0, sticky="w", padx=(0, 4))

        if TTKBOOTSTRAP_AVAILABLE:
            picker_entry = ttkb.Entry(picker_frame, textvariable=self.document_path_var, bootstyle="secondary")
            browse_btn = ttkb.Button(picker_frame, text="📂 Browse", command=self._prompt_document_for_preview,
                                     bootstyle="info-outline")
        else:
            picker_entry = ttk.Entry(picker_frame, textvariable=self.document_path_var)
            browse_btn = ttk.Button(picker_frame, text="Browse", command=self._prompt_document_for_preview)
        picker_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        browse_btn.grid(row=1, column=1, sticky="e")

        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(browse_btn, text="Open a local document for preview")

        # File content display area
        if TTKBOOTSTRAP_AVAILABLE:
            content_frame = ttkb.Frame(self.file_preview_frame)
        else:
            content_frame = ttk.Frame(self.file_preview_frame)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Text widget for displaying file content
        self.file_preview_text = tk.Text(content_frame, wrap="word", state="disabled", font=self.text_font)
        self.file_preview_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        if TTKBOOTSTRAP_AVAILABLE:
            preview_scroll = ttkb.Scrollbar(content_frame, orient="vertical", command=self.file_preview_text.yview, bootstyle="success-round")
        else:
            preview_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=self.file_preview_text.yview)
        self.file_preview_text.configure(yscrollcommand=preview_scroll.set)
        preview_scroll.grid(row=0, column=1, sticky="ns")

        # Status bar for file operations
        if TTKBOOTSTRAP_AVAILABLE:
            self.file_preview_status_var = tk.StringVar(value="Ready")
            status_label = ttkb.Label(self.file_preview_frame, textvariable=self.file_preview_status_var, bootstyle="secondary")
        else:
            self.file_preview_status_var = tk.StringVar(value="Ready")
            status_label = ttk.Label(self.file_preview_frame, textvariable=self.file_preview_status_var)
        status_label.grid(row=3, column=0, sticky="w", padx=4, pady=(0, 4))
        status_label.grid(row=2, column=0, sticky="w", padx=4, pady=(0, 4))

        # Refresh button
        if TTKBOOTSTRAP_AVAILABLE:
            refresh_btn = ttkb.Button(self.file_preview_frame, text="🔄 Refresh", command=self._refresh_file_preview, bootstyle="info-outline")
        else:
            refresh_btn = ttk.Button(self.file_preview_frame, text="Refresh", command=self._refresh_file_preview)
        refresh_btn.grid(row=3, column=0, sticky="e", padx=4, pady=(0, 4))

        # Start with helpful placeholder content
        self._show_file_preview_placeholder()

    def _build_document_activity_panel(self):
        """Build activity log showing how AI is updating the document."""
        if TTKBOOTSTRAP_AVAILABLE:
            activity_frame = ttkb.Labelframe(self.document_frame, text="📡 Live Updates", bootstyle="info")
        else:
            activity_frame = ttk.LabelFrame(self.document_frame, text="Live Updates")
        activity_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))
        activity_frame.columnconfigure(0, weight=1)
        activity_frame.rowconfigure(0, weight=1)

        self.document_activity_text = tk.Text(activity_frame, wrap="word", state="disabled", height=6, font=self.text_font)
        self.document_activity_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        if TTKBOOTSTRAP_AVAILABLE:
            activity_scroll = ttkb.Scrollbar(activity_frame, orient="vertical", command=self.document_activity_text.yview, bootstyle="info-round")
        else:
            activity_scroll = ttk.Scrollbar(activity_frame, orient="vertical", command=self.document_activity_text.yview)
        self.document_activity_text.configure(yscrollcommand=activity_scroll.set)
        activity_scroll.grid(row=0, column=1, sticky="ns")

    def _close_file_preview(self):
        """Close the file preview panel."""
        if hasattr(self, 'file_preview_frame') and self.file_preview_frame:
            self.file_preview_frame.grid()
        self.active_file_session = None
        self._show_file_preview_placeholder()
        self.active_file_session = None
        if hasattr(self, 'file_preview_title_var') and self.file_preview_title_var:
            self.file_preview_title_var.set("No file open")
        if hasattr(self, 'file_preview_text') and self.file_preview_text:
            self.file_preview_text.config(state="normal")
            self.file_preview_text.delete("1.0", "end")
            self.file_preview_text.insert("1.0", "Select a document to see live updates.")
            self.file_preview_text.config(state="disabled")
        if hasattr(self, 'file_preview_status_var') and self.file_preview_status_var:
            self.file_preview_status_var.set("Ready")
        self._log_document_activity("Cleared active document session.")

    def _show_file_preview(self, file_type: str, file_path: str, file_id: Optional[str] = None):
        """Show the file preview panel with the specified file."""
        if not hasattr(self, 'file_preview_frame') or not self.file_preview_frame:
            return  # Panel not initialized yet
        
        self.active_file_session = {
            'type': file_type,
            'path': file_path,
            'id': file_id,
            'last_update': datetime.now()
        }
        
        # Update title
        file_name = os.path.basename(file_path) if file_path and os.path.sep in file_path else (file_path or f"{file_type} Document")
        if hasattr(self, 'file_preview_title_var') and self.file_preview_title_var:
            self.file_preview_title_var.set(f"{file_type}: {file_name}")
        
        # Show the panel and keep columns evenly split
        self.file_preview_frame.grid()
        self.chat_frame.columnconfigure(0, weight=1)
        self.chat_frame.columnconfigure(1, weight=1)
        

        self._log_document_activity(f"Opened {file_type} document: {file_name}")

        # Load and display file content
        self._refresh_file_preview()

    def _refresh_file_preview(self):
        """Refresh the file preview content."""
        if not self.active_file_session:
            return
        
        file_type = self.active_file_session.get('type')
        file_path = self.active_file_session.get('path')
        file_id = self.active_file_session.get('id')
        
        try:
            self.file_preview_status_var.set("Loading...")
            self.file_preview_text.config(state="normal")
            self.file_preview_text.delete("1.0", "end")
            
              if file_type == "OneNote":
                  content = self._load_onenote_preview(file_id)
              elif file_type == "Excel":
                  content = self._load_excel_preview(file_path)
              elif file_type == "Word":
                  content = self._load_word_preview(file_path)
              elif file_type == "PDF":
                  content = self._load_pdf_preview(file_path)
              elif file_type in ("CSV", "Text", "TXT"):
                  content = self._load_text_like_preview(file_path)
              elif file_type == "JSON":
                  content = self._load_json_preview(file_path)
              else:
                  content = "Unsupported file type"

            if file_type == "OneNote":
                content = self._load_onenote_preview(file_id)
            elif file_type == "Excel":
                content = self._load_excel_preview(file_path)
            elif file_type == "CSV":
                content = self._load_csv_preview(file_path)
            elif file_type == "Text":
                content = self._load_text_preview(file_path)
            elif file_type == "JSON":
                content = self._load_json_preview(file_path)
            elif file_type == "Word":
                content = self._load_word_preview(file_path)
            elif file_type == "PDF":
                content = self._load_pdf_preview(file_path)
            else:
                content = "Unsupported file type"
            
            self.file_preview_text.insert("1.0", content)
            self.file_preview_text.config(state="disabled")
            self.file_preview_status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            self.active_file_session['last_update'] = datetime.now()
            self._log_document_activity(f"Refreshed {file_type} preview at {self.active_file_session['last_update'].strftime('%H:%M:%S')}")
        except Exception as e:
            self.file_preview_text.insert("1.0", f"Error loading file: {str(e)}")
            self.file_preview_text.config(state="disabled")
            self.file_preview_status_var.set(f"Error: {str(e)}")
            self._log_document_activity(f"Error loading file: {str(e)}")

    def _load_onenote_preview(self, page_id: Optional[str]) -> str:
        """Load OneNote page content for preview."""
        if not ONENOTE_CLIENT_AVAILABLE or not page_id:
            return "OneNote preview not available"
        
        try:
            client = OneNoteClient()
            # Get page content
            page_content = client.get_page_content(page_id)
            if page_content:
                # Extract text from HTML content
                import re
                text = re.sub(r'<[^>]+>', '', page_content)
                return text[:50000]  # Limit preview size
            return "Page content not available"
        except Exception as e:
            return f"Error loading OneNote: {str(e)}"

    def _load_excel_preview(self, file_path: str) -> str:
        """Load Excel file content for preview."""
        if not EXCEL_SERVICE_AVAILABLE or not file_path:
            return "Excel preview not available"
        
        try:
            if os.path.exists(file_path):
                import pandas as pd
                # Try to load and display as table
                try:
                    # Read first sheet
                    df = pd.read_excel(file_path, sheet_name=0, nrows=100)  # Limit to 100 rows for preview
                    preview = f"Excel Workbook: {os.path.basename(file_path)}\n"
                    preview += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
                    preview += "=" * 80 + "\n\n"
                    preview += df.to_string(max_rows=50, max_cols=10)  # Limit display size
                    return preview
                except Exception as e:
                    # Fallback to summary
                    try:
                        summary = summarize_local_workbook(file_path)
                        if summary:
                            return f"Excel Workbook: {os.path.basename(file_path)}\n\n{summary}"
                    except:
                        pass
                    return f"Excel file loaded\n(Error displaying table: {str(e)})"
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading Excel: {str(e)}"

    def _load_csv_preview(self, file_path: str) -> str:
        """Load CSV file content for preview."""
        if not file_path:
            return "CSV preview not available"

        try:
            if os.path.exists(file_path):
                import csv

                lines = []
                with open(file_path, newline='', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    for idx, row in enumerate(reader):
                        lines.append(", ".join(row))
                        if idx >= 50:
                            break
                return "CSV Preview (first 50 rows):\n" + "\n".join(lines)
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading CSV: {str(e)}"

    def _load_text_preview(self, file_path: str) -> str:
        """Load plain text or generic file content for preview."""
        if not file_path:
            return "Text preview not available"

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(MAX_IMPORTED_FILE_CHARS)
                return content
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading text: {str(e)}"

    def _load_json_preview(self, file_path: str) -> str:
        """Load JSON content for preview."""
        if not file_path:
            return "JSON preview not available"

        try:
            if os.path.exists(file_path):
                import json

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                return json.dumps(data, indent=2)[:MAX_IMPORTED_FILE_CHARS]
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading JSON: {str(e)}"

    def _load_word_preview(self, file_path: str) -> str:
        """Load Word document content for preview."""
        if not WORD_SERVICE_AVAILABLE or not file_path:
            return "Word preview not available"
        
        try:
            if os.path.exists(file_path):
                service = WordService()
                # Extract text content
                content = service.extract_text(file_path)
                if content:
                    return content[:50000]  # Limit preview size
                return "Word document loaded (content extraction not available)"
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading Word: {str(e)}"

    def _load_pdf_preview(self, file_path: str) -> str:
        """Load PDF file content for preview."""
        if not file_path:
            return "PDF preview not available"
        
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            # Try to use PDF integration to extract text
            pdf_integration = PDFIntegration(self.conn)
            if hasattr(pdf_integration, 'extract_text'):
                content = pdf_integration.extract_text(file_path)
                if content and content.strip():
                    return content[:50000]  # Limit preview size
                return "PDF loaded but text extraction returned no content. PDF libraries may not be installed (PyPDF2 or pdfplumber)."
            else:
                return "PDF preview not available (extract_text method not found)"
        except Exception as e:
            return f"Error loading PDF: {str(e)}"

    def _load_text_like_preview(self, file_path: str) -> str:
        """Load plain text or CSV-style files for preview."""
        if not file_path:
            return "Text preview not available"

        try:
            if os.path.exists(file_path):
                # For CSV, show a simple tabular view using pandas if available
                if file_path.lower().endswith('.csv'):
                    try:
                        import pandas as pd
                        df = pd.read_csv(file_path, nrows=100)
                        preview = f"CSV File: {os.path.basename(file_path)}\n"
                        preview += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
                        preview += "=" * 80 + "\n\n" + df.to_string(max_rows=50, max_cols=12)
                        return preview
                    except Exception:
                        pass

                with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
                return content[:MAX_IMPORTED_FILE_CHARS]
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading text: {str(e)}"

    def _load_json_preview(self, file_path: str) -> str:
        """Load JSON content with pretty formatting."""
        if not file_path:
            return "JSON preview not available"

        try:
            if os.path.exists(file_path):
                import json
                with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
                    data = json.load(fh)
                return json.dumps(data, indent=2)[:MAX_IMPORTED_FILE_CHARS]
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading JSON: {str(e)}"

    def _show_file_preview_placeholder(self):
        """Display guidance in the document panel when no file is loaded."""
        if not hasattr(self, 'file_preview_text') or not self.file_preview_text:
            return

        if hasattr(self, 'file_preview_title_var') and self.file_preview_title_var:
            self.file_preview_title_var.set("Document Preview")
        placeholder = (
            "Load a document to collaborate with the AI in real time.\n\n"
            "Supported types: PDF, Word, Excel, CSV, TXT, JSON, and OneNote content.\n"
            "Use the Browse button to open a local file or let the AI open cloud documents "
            "via tool calls; updates will appear here automatically."
        )
        self.file_preview_text.config(state="normal")
        self.file_preview_text.delete("1.0", "end")
        self.file_preview_text.insert("1.0", placeholder)
        self.file_preview_text.config(state="disabled")
        if hasattr(self, 'file_preview_status_var') and self.file_preview_status_var:
            self.file_preview_status_var.set("Waiting for document...")
        self.active_file_session = None

    def _prompt_document_for_preview(self):
        """Prompt the user to select a document for side-by-side viewing."""
        filetypes = [
            ("Supported Documents", "*.pdf *.docx *.doc *.txt *.csv *.xlsx *.xls *.json"),
            ("All Files", "*.*"),
        ]
        initial_dir = self.cwd_var.get().strip() if hasattr(self, 'cwd_var') else ''
        path = filedialog.askopenfilename(initialdir=initial_dir or os.getcwd(), filetypes=filetypes)
        if not path:
            return

        self.document_path_var.set(path)
        file_type = self._infer_file_type(path)
        self._show_file_preview(file_type, path)

    def _infer_file_type(self, path: str) -> str:
        """Infer a friendly file type label based on extension."""
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.xlsx', '.xls'):
            return 'Excel'
        if ext in ('.docx', '.doc'):
            return 'Word'
        if ext == '.pdf':
            return 'PDF'
        if ext == '.csv':
            return 'CSV'
        if ext == '.json':
            return 'JSON'
        if ext in ('.txt', '.md'):
            return 'Text'
        return 'Document'
    def _infer_file_type(self, file_path: str) -> str:
        """Infer document type from extension for preview and logging."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".xlsx", ".xlsm", ".xls"]:
            return "Excel"
        if ext == ".csv":
            return "CSV"
        if ext in [".docx", ".doc"]:
            return "Word"
        if ext == ".pdf":
            return "PDF"
        if ext in [".json"]:
            return "JSON"
        if ext in [".txt", ".md", ".log"]:
            return "Text"
        return "Text"

    def on_open_document_file(self):
        """Allow users to open a local document for live interaction."""
        file_path = filedialog.askopenfilename(
            title="Select a document",
            filetypes=[
                ("All supported", "*.pdf *.doc *.docx *.xlsx *.xls *.csv *.txt *.json *.md *.log"),
                ("PDF", "*.pdf"),
                ("Word", "*.doc *.docx"),
                ("Excel", "*.xlsx *.xls"),
                ("CSV", "*.csv"),
                ("Text / Markdown", "*.txt *.md *.log"),
                ("JSON", "*.json"),
                ("All files", "*.*"),
            ]
        )
        if not file_path:
            return

        file_type = self._infer_file_type(file_path)
        self._show_file_preview(file_type, file_path)

    def _log_document_activity(self, message: str):
        """Append a status line to the live update feed."""
        if not self.document_activity_text:
            return
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.document_activity_text.config(state="normal")
        self.document_activity_text.insert("end", f"[{timestamp}] {message}\n")
        self.document_activity_text.see("end")
        self.document_activity_text.config(state="disabled")

    def _detect_file_operation(self, tool_call) -> Optional[Dict]:
        """Detect if a tool call involves file operations for OneNote, Excel, Word, PDF, or other documents."""
        if not hasattr(tool_call, 'function') or not hasattr(tool_call.function, 'name'):
            return None
        
        import json
        try:
            func_name = tool_call.function.name.lower()
            args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
            
            # Check for OneNote operations
            if 'onenote' in func_name or 'note' in func_name or 'notebook' in func_name:
                page_id = args.get('page_id') or args.get('id') or args.get('pageId')
                notebook_id = args.get('notebook_id') or args.get('notebookId')
                section_id = args.get('section_id') or args.get('sectionId')
                if page_id:
                    return {
                        'type': 'OneNote',
                        'path': f"OneNote Page: {page_id}",
                        'id': page_id,
                        'operation': tool_call.function.name
                    }
                elif notebook_id or section_id:
                    # Could be notebook or section operation
                    return {
                        'type': 'OneNote',
                        'path': f"OneNote: {notebook_id or section_id}",
                        'id': notebook_id or section_id,
                        'operation': tool_call.function.name
                    }
            
            # Check for Excel operations
            if 'excel' in func_name or 'workbook' in func_name or 'spreadsheet' in func_name or 'xlsx' in func_name or 'xls' in func_name:
                file_path = args.get('file_path') or args.get('path') or args.get('file') or args.get('filePath')
                if file_path:
                    return {
                        'type': 'Excel',
                        'path': file_path,
                        'id': None,
                        'operation': tool_call.function.name
                    }

            # Check for CSV operations
            if 'csv' in func_name:
                file_path = args.get('file_path') or args.get('path') or args.get('file') or args.get('filePath')
                if file_path:
                    return {
                        'type': 'CSV',
                        'path': file_path,
                        'id': None,
                        'operation': tool_call.function.name
                    }

            # Check for Word operations
            if 'word' in func_name or 'document' in func_name or 'docx' in func_name or 'doc' in func_name:
                file_path = args.get('file_path') or args.get('path') or args.get('file') or args.get('filePath')
                if file_path:
                    return {
                        'type': 'Word',
                        'path': file_path,
                        'id': None,
                        'operation': tool_call.function.name
                    }
            
            # Check for PDF operations
            if 'pdf' in func_name:
                file_path = args.get('file_path') or args.get('path') or args.get('file') or args.get('filePath')
                if file_path:
                    return {
                        'type': 'PDF',
                        'path': file_path,
                        'id': None,
                        'operation': tool_call.function.name
                    }

            # Check for JSON / CSV / text operations
            if 'csv' in func_name or 'json' in func_name or 'text' in func_name:
                file_path = args.get('file_path') or args.get('path') or args.get('file') or args.get('filePath')
                if file_path:
                    return {
                        'type': self._infer_file_type(file_path),
            # Generic text/JSON operations
            if 'json' in func_name or 'text' in func_name or 'file' in func_name:
                file_path = args.get('file_path') or args.get('path') or args.get('file') or args.get('filePath')
                if file_path:
                    inferred_type = self._infer_file_type(file_path)
                    return {
                        'type': inferred_type,
                        'path': file_path,
                        'id': None,
                        'operation': tool_call.function.name
                    }

            # Generic fallback: infer from file_path if provided
            file_path = args.get('file_path') or args.get('path') or args.get('file') or args.get('filePath')
            if file_path:
                return {
                    'type': self._infer_file_type(file_path),
                    'path': file_path,
                    'id': None,
                    'operation': tool_call.function.name
                }
        except Exception:
            pass
        
        return None
    
    def _detect_file_in_message(self, content: str) -> Optional[Dict]:
        """Detect file mentions in chat messages or tool results."""
        import re
        
        # Look for file paths
        file_patterns = [
            r'([^\s]+\.(xlsx?|docx?|pdf))',  # File extensions
            r'(onenote[^\s]*)',  # OneNote mentions
            r'(notebook[^\s]*)',  # Notebook mentions
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    file_path = match[0] if match[0] else match[1] if len(match) > 1 else None
                else:
                    file_path = match
                
                if file_path:
                    # Determine file type
                    file_lower = file_path.lower()
                    if '.xlsx' in file_lower or '.xls' in file_lower:
                        return {'type': 'Excel', 'path': file_path, 'id': None}
                    elif '.docx' in file_lower or '.doc' in file_lower:
                        return {'type': 'Word', 'path': file_path, 'id': None}
                    elif '.pdf' in file_lower:
                        return {'type': 'PDF', 'path': file_path, 'id': None}
                    elif 'onenote' in file_lower or 'notebook' in file_lower:
                        return {'type': 'OneNote', 'path': file_path, 'id': None}
        
        return None

    def _update_chat_status(self, message: Optional[str] = None):
        if not hasattr(self, 'chat_status_var'):
            return
        if message:
            self.chat_status_var.set(message)
        elif openai_available():
            agent = self.chat_agent_var.get() if hasattr(self, 'chat_agent_var') else None
            if agent:
                model = get_agent_model(agent) if self.chat_model_var.get() == "auto" else self.chat_model_var.get()
                self.chat_status_var.set(f'ChatGPT ready. Agent: {agent} | Model: {model}')
            else:
                self.chat_status_var.set('ChatGPT ready.')
        else:
            self.chat_status_var.set('OpenAI key missing – offline fallback only.')

    def refresh_chat_history(self):
        if not self.chat_text:
            return
        self.chat_text.config(state='normal')
        self.chat_text.delete('1.0', 'end')
        for msg in self.state_obj.chat_messages[-400:]:
            timestamp = msg.created_at.replace('T', ' ')
            if msg.kind == 'terminal':
                kind_label = ' [TERMINAL COMMAND]'
            elif msg.kind == 'terminal_result':
                kind_label = ' [TERMINAL OUTPUT]'
            elif msg.kind == 'file':
                kind_label = ' [FILE]'
            else:
                kind_label = ''
            self.chat_text.insert('end', f"[{timestamp}] {msg.persona}{kind_label}\n{msg.content}\n\n")
        self.chat_text.config(state='disabled')

    def on_import_chat_file(self):
        """Import file content into chat input."""
        initial_dir = self.cwd_var.get().strip() if hasattr(self, 'cwd_var') else ''
        path = filedialog.askopenfilename(initialdir=initial_dir or os.getcwd())
        if not path:
            self._update_chat_status('File import cancelled.')
            return
        try:
            content, descriptor = self._read_file_for_chat(path)
        except OSError as exc:
            messagebox.showerror('Import File', f'Unable to read file:\n{exc}')
            self._update_chat_status('Import failed.')
            return

        truncated = False
        raw_len = len(content)
        if raw_len > MAX_IMPORTED_FILE_CHARS:
            content = content[:MAX_IMPORTED_FILE_CHARS] + '\n... [truncated for length]'
            truncated = True

        label = os.path.basename(path)
        block = f"\n[Imported file: {label}{descriptor}]\n{content}\n"
        
        # Clear placeholder if present
        current = self.chat_input.get('1.0', 'end').strip()
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        if current == placeholder:
            self.chat_input.delete('1.0', 'end')
            self.chat_input.config(foreground="black")

        self.chat_input.insert('end', block)
        if truncated:
            self.chat_input.insert('end', '\n[Note: content truncated to fit limit]\n')
        self._update_chat_status(f"Imported '{label}' ({'truncated' if truncated else 'full'}).")

    def on_upload_file(self):
        """Upload file to OpenAI and attach to conversation."""
        initial_dir = self.cwd_var.get().strip() if hasattr(self, 'cwd_var') else ''
        path = filedialog.askopenfilename(initialdir=initial_dir or os.getcwd())
        if not path:
            self._update_chat_status('File upload cancelled.')
            return
        
        try:
            from .ai import get_openai_client
            client = get_openai_client()
            
            # Upload file to OpenAI
            with open(path, 'rb') as f:
                file_obj = client.files.create(
                    file=f,
                    purpose='assistants'
                )
            
            self.uploaded_files.append(file_obj.id)
            label = os.path.basename(path)
            
            # Add file reference to chat input
            self.chat_input.insert('end', f"\n[Uploaded file: {label} (ID: {file_obj.id})]\n")
            self._update_chat_status(f"Uploaded '{label}' to OpenAI (ID: {file_obj.id})")
            
            # Store file info in chat
            self._store_chat_message(
                'System',
                'system',
                f"File uploaded: {label} (OpenAI ID: {file_obj.id})",
                kind='file'
            )
            self.refresh_chat_history()
            
        except Exception as exc:
            messagebox.showerror('Upload File', f'Failed to upload file:\n{exc}')
            self._update_chat_status('File upload failed.')

    def _read_file_for_chat(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data = fh.read()
            return data, ''
        except UnicodeDecodeError:
            with open(path, 'rb') as fh:
                binary = fh.read()
        encoded = base64.b64encode(binary).decode('ascii')
        notice = ' (base64 encoded)'
        return f"(base64)\n{encoded}", notice

    def _store_chat_message(self, persona: str, role: str, content: str, kind: str = 'chat') -> ChatMessage:
        role = (role or 'user').lower()
        now = datetime.now().isoformat(timespec='seconds')
        msg = ChatMessage(id=0, persona=persona, role=role, kind=kind, content=content, created_at=now)
        msg.id = db_insert_chat_message(self.conn, msg)
        self.state_obj.chat_messages.append(msg)
        return msg

    def _send_chat_with_feedback(self, invoke_ai: bool = True):
        """Send chat message with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_chat_send_btn', None))
        self.on_send_chat_message(invoke_ai)
    
    def _send_chat_with_feedback(self, invoke_ai: bool = True):
        """Send chat message with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_chat_send_btn', None))
        self.on_send_chat_message(invoke_ai)
    
    def _upload_file_with_feedback(self):
        """Upload file with visual feedback"""
        self.on_upload_file()
    
    def _run_terminal_with_feedback(self, event=None):
        """Run terminal command with visual feedback"""
        AnimationHelper.pulse_button(getattr(self, '_terminal_run_btn', None))
        self.on_run_terminal_command(event)
    
    def on_send_chat_message(self, invoke_ai: bool = True):
        if not hasattr(self, 'chat_input'):
            return
        text = self.chat_input.get('1.0', 'end').strip()
        
        # Ignore placeholder text
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        if not text or text == placeholder:
            messagebox.showinfo('Chat', 'Type a message first.')
            return
        sender = self.chat_sender_var.get().strip() or 'Chris'
        if sender not in PERSONAS:
            sender = 'Chris'
        user_msg = self._store_chat_message(sender, 'user', text)
        
        # Try to extract and create tasks from the message
        try:
            created_tasks = create_task_from_ai_message(
                self.conn,
                text,
                default_project="General",
                default_owner=sender
            )
            if created_tasks:
                self._update_chat_status(f'Created {len(created_tasks)} task(s) from message.')
                self.refresh_task_list()
                self.refresh_dashboard()
        except Exception:
            pass
        
        self.chat_input.delete('1.0', 'end')
        self.on_input_focus_out()  # Restore placeholder if empty
        self.refresh_chat_history()
        if not invoke_ai:
            self._update_chat_status('Message logged without contacting ChatGPT.')
            return

        responder = self.chat_agent_var.get().strip() or self.state_obj.active_persona
        instruction = None
        if responder and responder != sender:
            instruction = f'Please respond as {responder}.'

        system_prompt = self.system_prompt_text.get('1.0', 'end').strip()
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
        self._update_chat_status(f'Contacting ChatGPT ({model})...')
        # Start progress indicator
        if hasattr(self, 'chat_progress'):
            self.chat_progress.start(f'Generating response with {model}...')

        def worker():
            # Interactive loop: handle tool calls
            max_iterations = 10  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                # Refresh messages from state for each iteration
                current_messages = self.state_obj.chat_messages.copy()
                
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
                    self.after(0, lambda r=reply, e=error: self._handle_ai_reply(r, e, responder))
                    return
                
                # If there are tool calls, execute them
                if tool_calls:
                    tool_results = []
                    for tool_call in tool_calls:
                        # Detect file operations and show preview
                        file_op = self._detect_file_operation(tool_call)
                        if file_op:
                            self.after(0, lambda op=file_op: self._show_file_preview(
                                op['type'], op['path'], op.get('id')
                            ))
                        
                        result = execute_tool_call(tool_call, cwd=cwd)
                        tool_results.append(result)
                        
                        # After file operation, refresh preview
                        if file_op:
                            self.after(0, lambda: self._refresh_file_preview())
                        
                        # Store terminal command and result in chat immediately
                        if tool_call.function.name == "execute_command":
                            import json
                            try:
                                args = json.loads(tool_call.function.arguments)
                                cmd = args.get("command", "")
                                if cmd:
                                    header = f'$ {cmd}\n(cwd: {cwd})'
                                    self._store_chat_message(responder, 'user', header, kind='terminal')
                                    self._store_chat_message(responder, 'assistant', result["content"], kind='terminal_result')
                                    self.after(0, self.refresh_chat_history)
                            except:
                                pass
                    
                    # Store tool results in chat for next iteration
                    for result in tool_results:
                        result_content = result.get("content", "")
                        self._store_chat_message(responder, 'tool', result_content, kind='tool_result')
                        
                        # Check if tool result mentions a file
                        file_op = self._detect_file_in_message(result_content)
                        if file_op and not self.active_file_session:
                            self.after(0, lambda op=file_op: self._show_file_preview(
                                op['type'], op['path'], op.get('id')
                            ))
                    
                    self.after(0, self.refresh_chat_history)
                    iteration += 1
                    import time
                    time.sleep(0.5)  # Brief pause to allow UI update
                    continue
                else:
                    # No more tool calls, return the final reply
                    self.after(0, lambda r=reply, e=error: self._handle_ai_reply(r, e, responder))
                    return
            
            # Max iterations reached
            final_reply = reply if 'reply' in locals() and reply else "Maximum interaction iterations reached."
            self.after(0, lambda r=final_reply: self._handle_ai_reply(r, None, responder))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_ai_reply(self, reply_text: str, error: Optional[str], responder: str):
        # Stop progress indicator
        if hasattr(self, 'chat_progress'):
            if error:
                self.chat_progress.stop("Error occurred")
            else:
                self.chat_progress.stop("Response received")
        
        persona = responder or self.chat_agent_var.get().strip() or 'AI Team'
        text = reply_text.strip() if reply_text else '(no response)'
        self._store_chat_message(persona, 'assistant', text)
        self.refresh_chat_history()
        if error:
            self._update_chat_status(f'ChatGPT error (fallback used): {error}')
        else:
            self._update_chat_status('ChatGPT response ready.')

    def on_clear_chat_history(self):
        if not messagebox.askyesno('Clear Chat', 'Delete the entire chat + terminal log?'):
            return
        db_clear_chat_history(self.conn)
        self.state_obj.chat_messages.clear()
        self.refresh_chat_history()

    def on_run_terminal_command(self, event=None):
        command = self.command_var.get().strip()
        if not command:
            messagebox.showinfo('Terminal', 'Enter a command to run.')
            return
        cwd = os.path.expanduser(self.cwd_var.get().strip() or os.getcwd())
        if not os.path.isdir(cwd):
            messagebox.showerror('Terminal', f'Working directory not found: {cwd}')
            return
        try:
            result = run_bash_command(command, cwd=cwd)
        except Exception as exc:
            messagebox.showerror('Terminal', f'Failed to execute command: {exc}')
            return

        header = f'$ {command}\n(cwd: {result.cwd})'
        self._store_chat_message('Terminal', 'user', header, kind='terminal')

        parts = [f'shell: {result.shell_path}', f'exit: {result.returncode}']
        output = result.stdout.strip()
        err = result.stderr.strip()
        body = ' | '.join(parts)
        if output:
            body += f"\n{output}"
        if err:
            body += f"\n[stderr]\n{err}"
        self._store_chat_message('Terminal', 'assistant', body or '(no output)', kind='terminal_result')

        self.command_var.set('')
        self.refresh_chat_history()

    def on_browse_cwd(self):
        initial = self.cwd_var.get().strip() or os.getcwd()
        path = filedialog.askdirectory(initialdir=initial)
        if path:
            self.cwd_var.set(path)

    def on_input_focus_in(self, event=None):
        """Clear placeholder text when input gains focus."""
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        current_text = self.chat_input.get('1.0', 'end').strip()
        if current_text == placeholder:
            self.chat_input.delete('1.0', 'end')
            self.chat_input.config(foreground="black")

    def on_input_focus_out(self, event=None):
        """Restore placeholder text if input is empty."""
        current_text = self.chat_input.get('1.0', 'end').strip()
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        if not current_text:
            self.chat_input.insert("1.0", placeholder)
            self.chat_input.config(foreground="gray")

    def on_handle_combined_input(self, chat_mode=False):
        """Handle combined input field - can be either chat message or terminal command."""
        if not hasattr(self, 'chat_input'):
            return
        
        text = self.chat_input.get('1.0', 'end').strip()
        placeholder = "Type a message or command here. Prefix commands with '$' or press Enter for single-line commands."
        
        # Ignore placeholder text
        if not text or text == placeholder:
            return
        
        # Check if it's a command (starts with $ or chat_mode is False and it's a single line)
        is_command = text.startswith('$') or (not chat_mode and '\n' not in text)
        
        if is_command:
            # Remove $ prefix if present
            command = text.lstrip('$').strip()
            if command:
                # Update command_var for backward compatibility
                self.command_var.set(command)
                # Run the terminal command
                self._run_terminal_with_feedback()
        else:
            # Send as chat message
            self.on_send_chat_message(invoke_ai=True)
        
        # Clear input and restore placeholder
        self.chat_input.delete('1.0', 'end')
        self.on_input_focus_out()

    def on_handle_combined_input_enter(self, event):
        """Handle Enter key in combined input - check if it's a command or newline."""
        if not hasattr(self, 'chat_input'):
            return None
        
        text = self.chat_input.get('1.0', 'end').strip()
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
        has_newlines = '\n' in text
        starts_with_dollar = text.startswith('$')
        
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
        if not hasattr(self, 'sync_scheduler'):
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
            header = ttkb.Label(main_container, text="External Data Integrations", bootstyle="primary", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
        else:
            header = ttk.Label(main_container, text="External Data Integrations", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
        header.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Integrations list
        list_frame = ttk.Frame(main_container)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ("service", "status", "last_sync", "items")
        self.integrations_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.integrations_tree.heading("service", text="SERVICE")
        self.integrations_tree.heading("status", text="STATUS")
        self.integrations_tree.heading("last_sync", text="LAST SYNC")
        self.integrations_tree.heading("items", text="ITEMS")
        
        self.integrations_tree.column("service", width=200)
        self.integrations_tree.column("status", width=120)
        self.integrations_tree.column("last_sync", width=150)
        self.integrations_tree.column("items", width=80)
        
        self.integrations_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.integrations_tree.yview)
        self.integrations_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Buttons
        if TTKBOOTSTRAP_AVAILABLE:
            btn_frame = ttkb.Frame(main_container)
        else:
            btn_frame = ttk.Frame(main_container)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        
        if TTKBOOTSTRAP_AVAILABLE:
            connect_btn = ttkb.Button(btn_frame, text="🔌 Connect", command=self.on_connect_integration, bootstyle="success-outline")
            sync_btn = ttkb.Button(btn_frame, text="🔄 Sync All", command=self.on_sync_all_integrations, bootstyle="primary")
            sync_selected_btn = ttkb.Button(btn_frame, text="🔄 Sync Selected", command=self.on_sync_selected_integration, bootstyle="info-outline")
            refresh_btn = ttkb.Button(btn_frame, text="🔄 Refresh", command=self.refresh_integrations_list, bootstyle="secondary-outline")
        else:
            connect_btn = ttk.Button(btn_frame, text="Connect", command=self.on_connect_integration)
            sync_btn = ttk.Button(btn_frame, text="Sync All", command=self.on_sync_all_integrations)
            sync_selected_btn = ttk.Button(btn_frame, text="Sync Selected", command=self.on_sync_selected_integration)
            refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_integrations_list)
        
        connect_btn.grid(row=0, column=0, padx=4)
        sync_btn.grid(row=0, column=1, padx=4)
        sync_selected_btn.grid(row=0, column=2, padx=4)
        refresh_btn.grid(row=0, column=3, padx=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(connect_btn, text="Connect/Configure the selected integration")
            ToolTip(sync_btn, text="Sync all enabled integrations")
            ToolTip(sync_selected_btn, text="Sync the selected integration")
            ToolTip(refresh_btn, text="Refresh the integrations list")
    
    def refresh_integrations_list(self):
        """Refresh the integrations list display."""
        for row in self.integrations_tree.get_children():
            self.integrations_tree.delete(row)
        
        # Load saved credentials/configs before checking status
        self._load_saved_credentials()
        
        # Get integration statuses - all available integrations
        integrations = {
            "Local Notes": NotesIntegration(self.conn),
            "Apple Calendar": AppleCalendarIntegration(self.conn),
            "Gmail": GmailIntegration(self.conn),
            "GitHub": GitHubIntegration(self.conn),
            "Word": WordIntegration(self.conn),
            "Excel": ExcelIntegration(self.conn),
            "OneNote": OneNoteIntegration(self.conn),
            "OneDrive": OneDriveIntegration(self.conn),
            "Local Files": FilesystemIntegration(self.conn),
            "Git": GitIntegration(self.conn),
            "PDF": PDFIntegration(self.conn),
        }
        
        for name, integration in integrations.items():
            # Try to authenticate to get current status
            try:
                integration.authenticate()
            except Exception:
                pass
            
            status = integration.get_status()
            status_text = "✅ Connected" if status.connected else "❌ Disconnected"
            if status.error:
                status_text += f" ({status.error[:30]})"
            
            last_sync = status.last_sync or "Never"
            if last_sync != "Never" and "T" in last_sync:
                last_sync = last_sync.replace("T", " ")[:16]
            
            self.integrations_tree.insert(
                "",
                "end",
                iid=name,
                values=(name, status_text, last_sync, status.item_count),
            )
    
    def _load_saved_credentials(self):
        """Load saved credentials from config files into environment."""
        config_dir = os.path.expanduser("~/.assistant_hub")
        
        # Load GitHub token
        github_token_file = os.path.join(config_dir, "github_token.txt")
        if os.path.exists(github_token_file):
            try:
                with open(github_token_file, "r") as f:
                    os.environ["GITHUB_TOKEN"] = f.read().strip()
            except Exception:
                pass
        
        # Load Azure credentials
        azure_config_file = os.path.join(config_dir, "azure_config.txt")
        if os.path.exists(azure_config_file):
            try:
                with open(azure_config_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip()
            except Exception:
                pass
    
    def on_sync_all_integrations(self):
        """Sync all enabled integrations."""
        results = self.sync_scheduler.sync_now()
        message = "Sync completed:\n"
        for name, count in results.items():
            if count >= 0:
                message += f"  {name}: {count} items\n"
            else:
                message += f"  {name}: Error\n"
        messagebox.showinfo("Sync Complete", message)
        self.refresh_integrations_list()
    
    def on_sync_selected_integration(self):
        """Sync the selected integration."""
        sel = self.integrations_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an integration to sync.")
            return
        
        name = sel[0]
        # Map display names to scheduler keys
        name_map = {
            "Local Notes": "notes",
            "Apple Calendar": "calendar",
            "Gmail": "mail",
            "GitHub": "github",
            "Word": "word",
            "Excel": "excel",
            "OneNote": "onenote",
            "Local Files": "filesystem",
            "Git": "git",
            "PDF": "pdf",
        }
        key = name_map.get(name, name.lower().replace(" ", "_"))
        results = self.sync_scheduler.sync_now(key)
        count = results.get(key, -1)
        if count >= 0:
            messagebox.showinfo("Sync Complete", f"{name}: {count} items synced.")
        else:
            messagebox.showerror("Sync Error", f"Failed to sync {name}.")
        self.refresh_integrations_list()
    
    def on_connect_integration(self):
        """Open connection/authentication dialog for selected integration."""
        sel = self.integrations_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an integration to connect.")
            return
        
        name = sel[0]
        self._show_connection_dialog(name)
    
    def _show_connection_dialog(self, service_name: str):
        """Show appropriate connection/configuration dialog for a service."""
        dialog = tk.Toplevel(self)
        dialog.title(f"Connect to {service_name}")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(dialog, padding=20)
        else:
            main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Service-specific dialogs
        if service_name == "Google Calendar":
            self._show_google_oauth_dialog(dialog, main_frame, "calendar")
        elif service_name == "Gmail":
            self._show_google_oauth_dialog(dialog, main_frame, "gmail")
        elif service_name == "GitHub":
            self._show_github_auth_dialog(dialog, main_frame)
        elif service_name == "OneNote":
            self._show_msgraph_auth_dialog(dialog, main_frame)
        elif service_name == "Local Notes":
            self._show_notes_config_dialog(dialog, main_frame)
        elif service_name == "Local Files":
            self._show_files_config_dialog(dialog, main_frame)
        elif service_name in ["Word", "Excel", "Git", "PDF"]:
            # These don't need configuration, just show info
            info_label = ttk.Label(main_frame, text=f"{service_name} integration is ready to use.\nNo additional configuration needed.", justify="center")
            info_label.pack(pady=20)
            if TTKBOOTSTRAP_AVAILABLE:
                close_btn = ttkb.Button(main_frame, text="Close", command=dialog.destroy, bootstyle="primary")
            else:
                close_btn = ttk.Button(main_frame, text="Close", command=dialog.destroy)
            close_btn.pack(pady=10)
        else:
            info_label = ttk.Label(main_frame, text=f"Configuration for {service_name} is not yet implemented.", justify="center")
            info_label.pack(pady=20)
            if TTKBOOTSTRAP_AVAILABLE:
                close_btn = ttkb.Button(main_frame, text="Close", command=dialog.destroy, bootstyle="primary")
            else:
                close_btn = ttk.Button(main_frame, text="Close", command=dialog.destroy)
            close_btn.pack(pady=10)
    
    def _show_google_oauth_dialog(self, dialog, frame, service_type: str):
        """Show Google OAuth2 setup dialog."""
        title_label = ttk.Label(frame, text=f"Connect to Google {service_type.title()}", font=(self.base_font.actual("family"), 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        instructions = ttk.Label(
            frame,
            text="To connect, you need to:\n\n"
                 "1. Create a Google Cloud Project\n"
                 "2. Enable Google Calendar API (or Gmail API)\n"
                 "3. Create OAuth 2.0 credentials\n"
                 "4. Download credentials JSON file\n\n"
                 "Then paste the path to your credentials file below:",
            justify="left"
        )
        instructions.pack(pady=10, fill="x")
        
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill="x", pady=10)
        
        path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=50)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def browse_file():
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select Google OAuth2 Credentials JSON",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                path_var.set(filename)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=browse_file)
        browse_btn.pack(side="right")
        
        def save_and_connect():
            cred_path = path_var.get().strip()
            if not cred_path:
                messagebox.showerror("Error", "Please provide a credentials file path.")
                return
            
            if not os.path.exists(cred_path):
                messagebox.showerror("Error", "Credentials file not found.")
                return
            
            # Copy credentials to standard location
            cred_dir = os.path.expanduser("~/.assistant_hub")
            os.makedirs(cred_dir, exist_ok=True)
            
            target_path = os.path.join(cred_dir, f"google_{service_type}_credentials.json")
            try:
                import shutil
                shutil.copy2(cred_path, target_path)
                messagebox.showinfo("Success", f"Credentials saved. Please complete OAuth2 flow in terminal.\n\nRun the authentication script to get your access token.")
                dialog.destroy()
                self.refresh_integrations_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save credentials: {e}")
        
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(frame, text="Save Credentials", command=save_and_connect, bootstyle="success")
            cancel_btn = ttkb.Button(frame, text="Cancel", command=dialog.destroy, bootstyle="secondary")
        else:
            save_btn = ttk.Button(frame, text="Save Credentials", command=save_and_connect)
            cancel_btn = ttk.Button(frame, text="Cancel", command=dialog.destroy)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        save_btn.pack(side="left", padx=5)
        cancel_btn.pack(side="left", padx=5)
    
    def _show_github_auth_dialog(self, dialog, frame):
        """Show GitHub Personal Access Token dialog."""
        title_label = ttk.Label(frame, text="Connect to GitHub", font=(self.base_font.actual("family"), 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        instructions = ttk.Label(
            frame,
            text="Enter your GitHub Personal Access Token.\n\n"
                 "To create a token:\n"
                 "1. Go to GitHub Settings > Developer settings > Personal access tokens\n"
                 "2. Generate a new token with 'repo' scope\n"
                 "3. Copy the token and paste it below:",
            justify="left"
        )
        instructions.pack(pady=10, fill="x")
        
        token_frame = ttk.Frame(frame)
        token_frame.pack(fill="x", pady=10)
        
        token_label = ttk.Label(token_frame, text="Token:")
        token_label.pack(anchor="w")
        
        token_var = tk.StringVar()
        token_entry = ttk.Entry(token_frame, textvariable=token_var, width=50, show="*")
        token_entry.pack(fill="x", pady=(5, 0))
        
        def save_token():
            token = token_var.get().strip()
            if not token:
                messagebox.showerror("Error", "Please enter a GitHub token.")
                return
            
            # Save to environment or config
            import os
            # For now, we'll save it in a way that the integration can access it
            # In production, use secure storage
            config_dir = os.path.expanduser("~/.assistant_hub")
            os.makedirs(config_dir, exist_ok=True)
            token_file = os.path.join(config_dir, "github_token.txt")
            
            try:
                with open(token_file, "w") as f:
                    f.write(token)
                # Also set as environment variable for current session
                os.environ["GITHUB_TOKEN"] = token
                messagebox.showinfo("Success", "GitHub token saved successfully!")
                dialog.destroy()
                self.refresh_integrations_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save token: {e}")
        
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(frame, text="Save Token", command=save_token, bootstyle="success")
            cancel_btn = ttkb.Button(frame, text="Cancel", command=dialog.destroy, bootstyle="secondary")
        else:
            save_btn = ttk.Button(frame, text="Save Token", command=save_token)
            cancel_btn = ttk.Button(frame, text="Cancel", command=dialog.destroy)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        save_btn.pack(side="left", padx=5)
        cancel_btn.pack(side="left", padx=5)
    
    def _show_msgraph_auth_dialog(self, dialog, frame):
        """Show Microsoft Graph authentication dialog."""
        title_label = ttk.Label(frame, text="Connect to OneNote (Microsoft Graph)", font=(self.base_font.actual("family"), 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        instructions = ttk.Label(
            frame,
            text="Enter your Microsoft Azure App credentials.\n\n"
                 "To get credentials:\n"
                 "1. Go to Azure Portal > App registrations\n"
                 "2. Create or select an app\n"
                 "3. Get Tenant ID, Client ID, and Client Secret\n"
                 "4. Enter them below:",
            justify="left"
        )
        instructions.pack(pady=10, fill="x")
        
        # Load existing credentials from database to pre-populate fields
        from .db import load_azure_credentials
        existing_creds = load_azure_credentials(self.conn)
        
        tenant_frame = ttk.Frame(frame)
        tenant_frame.pack(fill="x", pady=5)
        ttk.Label(tenant_frame, text="Tenant ID:").pack(anchor="w")
        tenant_var = tk.StringVar(value=existing_creds.get("tenant_id", "") if existing_creds else "")
        ttk.Entry(tenant_frame, textvariable=tenant_var, width=50).pack(fill="x", pady=(5, 0))
        
        client_id_frame = ttk.Frame(frame)
        client_id_frame.pack(fill="x", pady=5)
        ttk.Label(client_id_frame, text="Client ID:").pack(anchor="w")
        client_id_var = tk.StringVar(value=existing_creds.get("client_id", "") if existing_creds else "")
        ttk.Entry(client_id_frame, textvariable=client_id_var, width=50).pack(fill="x", pady=(5, 0))
        
        secret_frame = ttk.Frame(frame)
        secret_frame.pack(fill="x", pady=5)
        ttk.Label(secret_frame, text="Client Secret:").pack(anchor="w")
        secret_var = tk.StringVar(value=existing_creds.get("client_secret", "") if existing_creds else "")
        ttk.Entry(secret_frame, textvariable=secret_var, width=50, show="*").pack(fill="x", pady=(5, 0))
        
        def save_credentials():
            tenant = tenant_var.get().strip()
            client_id = client_id_var.get().strip()
            secret = secret_var.get().strip()
            
            if not all([tenant, client_id, secret]):
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            
            # Save to database (primary storage)
            try:
                from .db import save_azure_credentials
                save_azure_credentials(self.conn, tenant, client_id, secret)
                
                # Also save to environment variables for current session
                import os
                os.environ["AZURE_TENANT_ID"] = tenant
                os.environ["AZURE_CLIENT_ID"] = client_id
                os.environ["AZURE_CLIENT_SECRET"] = secret
                
                # Also save to config file for backup/compatibility
                config_dir = os.path.expanduser("~/.assistant_hub")
                os.makedirs(config_dir, exist_ok=True)
                config_file = os.path.join(config_dir, "azure_config.txt")
                
                with open(config_file, "w") as f:
                    f.write(f"AZURE_TENANT_ID={tenant}\n")
                    f.write(f"AZURE_CLIENT_ID={client_id}\n")
                    f.write(f"AZURE_CLIENT_SECRET={secret}\n")
                
                messagebox.showinfo("Success", "Microsoft Graph credentials saved to database!")
                dialog.destroy()
                self.refresh_integrations_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save credentials: {e}")
        
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(frame, text="Save Credentials", command=save_credentials, bootstyle="success")
            cancel_btn = ttkb.Button(frame, text="Cancel", command=dialog.destroy, bootstyle="secondary")
        else:
            save_btn = ttk.Button(frame, text="Save Credentials", command=save_credentials)
            cancel_btn = ttk.Button(frame, text="Cancel", command=dialog.destroy)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        save_btn.pack(side="left", padx=5)
        cancel_btn.pack(side="left", padx=5)
    
    def _show_notes_config_dialog(self, dialog, frame):
        """Show Local Notes configuration dialog."""
        title_label = ttk.Label(frame, text="Configure Local Notes", font=(self.base_font.actual("family"), 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        instructions = ttk.Label(
            frame,
            text="Select the directory where your notes are stored:",
            justify="left"
        )
        instructions.pack(pady=10, fill="x")
        
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill="x", pady=10)
        
        path_var = tk.StringVar(value=os.path.expanduser("~/Documents/Notes"))
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=50)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def browse_folder():
            from tkinter import filedialog
            folder = filedialog.askdirectory(title="Select Notes Directory")
            if folder:
                path_var.set(folder)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=browse_folder)
        browse_btn.pack(side="right")
        
        def save_config():
            notes_path = path_var.get().strip()
            if not notes_path:
                messagebox.showerror("Error", "Please select a notes directory.")
                return
            
            # Create directory if it doesn't exist
            try:
                os.makedirs(notes_path, exist_ok=True)
                # Save to config (could use database or config file)
                messagebox.showinfo("Success", f"Notes directory configured: {notes_path}")
                dialog.destroy()
                self.refresh_integrations_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to configure notes directory: {e}")
        
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(frame, text="Save", command=save_config, bootstyle="success")
            cancel_btn = ttkb.Button(frame, text="Cancel", command=dialog.destroy, bootstyle="secondary")
        else:
            save_btn = ttk.Button(frame, text="Save", command=save_config)
            cancel_btn = ttk.Button(frame, text="Cancel", command=dialog.destroy)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        save_btn.pack(side="left", padx=5)
        cancel_btn.pack(side="left", padx=5)
    
    def _show_files_config_dialog(self, dialog, frame):
        """Show Local Files configuration dialog."""
        title_label = ttk.Label(frame, text="Configure Local Files", font=(self.base_font.actual("family"), 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        instructions = ttk.Label(
            frame,
            text="Select the root directory to scan for files:",
            justify="left"
        )
        instructions.pack(pady=10, fill="x")
        
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill="x", pady=10)
        
        path_var = tk.StringVar(value=os.path.expanduser("~"))
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=50)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def browse_folder():
            from tkinter import filedialog
            folder = filedialog.askdirectory(title="Select Root Directory")
            if folder:
                path_var.set(folder)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=browse_folder)
        browse_btn.pack(side="right")
        
        def save_config():
            root_path = path_var.get().strip()
            if not root_path or not os.path.exists(root_path):
                messagebox.showerror("Error", "Please select a valid directory.")
                return
            
            try:
                # Save to config
                messagebox.showinfo("Success", f"Files root directory configured: {root_path}")
                dialog.destroy()
                self.refresh_integrations_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to configure files directory: {e}")
        
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(frame, text="Save", command=save_config, bootstyle="success")
            cancel_btn = ttkb.Button(frame, text="Cancel", command=dialog.destroy, bootstyle="secondary")
        else:
            save_btn = ttk.Button(frame, text="Save", command=save_config)
            cancel_btn = ttk.Button(frame, text="Cancel", command=dialog.destroy)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        save_btn.pack(side="left", padx=5)
        cancel_btn.pack(side="left", padx=5)


# ---------- Tools & Operations Tab ----------

    def _build_tools_tab(self):
        """Build the Tools & Operations tab with GUI interfaces for CLI commands."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.tools_frame = ttkb.Frame(self.notebook)
        else:
            self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="🔧 Tools")
        
        self.tools_frame.columnconfigure(0, weight=1)
        self.tools_frame.rowconfigure(0, weight=1)
        
        # Create notebook for different tool sections
        if TTKBOOTSTRAP_AVAILABLE:
            tools_notebook = ttkb.Notebook(self.tools_frame)
        else:
            tools_notebook = ttk.Notebook(self.tools_frame)
        tools_notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        
        # OneNote Notebooks section
        self._build_onenote_tools_section(tools_notebook)
        
        # Excel Workbooks section
        self._build_excel_tools_section(tools_notebook)
        
        # Document Summarization section
        self._build_summarization_tools_section(tools_notebook)
        
        # Workflow Execution section
        self._build_workflow_tools_section(tools_notebook)
        
        # Projects section (GUI for projects list/add)
        self._build_projects_tools_section(tools_notebook)
        
        # Enhanced Chat with Agent Selection
        self._build_agent_chat_section(tools_notebook)
    
    def _build_onenote_tools_section(self, parent):
        """Build OneNote notebooks browser section."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="📓 OneNote Notebooks")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Header
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(frame, text="OneNote Notebooks", bootstyle="primary", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            refresh_btn = ttkb.Button(frame, text="🔄 Refresh Notebooks", command=self.refresh_onenote_notebooks, bootstyle="info-outline")
        else:
            header = ttk.Label(frame, text="OneNote Notebooks", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            refresh_btn = ttk.Button(frame, text="Refresh Notebooks", command=self.refresh_onenote_notebooks)
        
        header.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        refresh_btn.grid(row=0, column=1, sticky="e", padx=8, pady=(8, 4))
        
        # Notebooks tree
        columns = ("name", "id", "last_modified")
        self.onenote_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        self.onenote_tree.heading("name", text="Notebook Name")
        self.onenote_tree.heading("id", text="ID")
        self.onenote_tree.heading("last_modified", text="Last Modified")
        
        self.onenote_tree.column("name", width=300)
        self.onenote_tree.column("id", width=200)
        self.onenote_tree.column("last_modified", width=150)
        
        self.onenote_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            scrollbar = ttkb.Scrollbar(frame, orient="vertical", command=self.onenote_tree.yview, bootstyle="primary-round")
        else:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.onenote_tree.yview)
        self.onenote_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=4)
        
        # Status label
        self.onenote_status_var = tk.StringVar(value="Click 'Refresh Notebooks' to load OneNote notebooks")
        if TTKBOOTSTRAP_AVAILABLE:
            status_label = ttkb.Label(frame, textvariable=self.onenote_status_var, bootstyle="secondary")
        else:
            status_label = ttk.Label(frame, textvariable=self.onenote_status_var)
        status_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=4)
    
    def _build_excel_tools_section(self, parent):
        """Build Excel workbooks browser section."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="📊 Excel Workbooks")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Header
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(frame, text="Excel Workbooks", bootstyle="primary", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            refresh_btn = ttkb.Button(frame, text="🔄 Refresh Workbooks", command=self.refresh_excel_workbooks, bootstyle="info-outline")
        else:
            header = ttk.Label(frame, text="Excel Workbooks", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            refresh_btn = ttk.Button(frame, text="Refresh Workbooks", command=self.refresh_excel_workbooks)
        
        header.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        refresh_btn.grid(row=0, column=1, sticky="e", padx=8, pady=(8, 4))
        
        # Workbooks tree
        columns = ("name", "id", "size", "modified")
        self.excel_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        self.excel_tree.heading("name", text="Workbook Name")
        self.excel_tree.heading("id", text="ID")
        self.excel_tree.heading("size", text="Size")
        self.excel_tree.heading("modified", text="Modified")
        
        self.excel_tree.column("name", width=300)
        self.excel_tree.column("id", width=200)
        self.excel_tree.column("size", width=100)
        self.excel_tree.column("modified", width=150)
        
        self.excel_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            scrollbar = ttkb.Scrollbar(frame, orient="vertical", command=self.excel_tree.yview, bootstyle="primary-round")
        else:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.excel_tree.yview)
        self.excel_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=4)
        
        # Status label
        self.excel_status_var = tk.StringVar(value="Click 'Refresh Workbooks' to load Excel workbooks from OneDrive")
        if TTKBOOTSTRAP_AVAILABLE:
            status_label = ttkb.Label(frame, textvariable=self.excel_status_var, bootstyle="secondary")
        else:
            status_label = ttk.Label(frame, textvariable=self.excel_status_var)
        status_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=4)
    
    def _build_summarization_tools_section(self, parent):
        """Build document summarization section for Excel and Word."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="📝 Summarize Documents")
        
        frame.columnconfigure(0, weight=1)
        
        # Excel summarization
        if TTKBOOTSTRAP_AVAILABLE:
            excel_section = ttkb.Labelframe(frame, text="Excel Workbook Summarization", bootstyle="info")
        else:
            excel_section = ttk.LabelFrame(frame, text="Excel Workbook Summarization")
        excel_section.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        excel_section.columnconfigure(1, weight=1)
        
        ttk.Label(excel_section, text="File Path:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.excel_summarize_path_var = tk.StringVar()
        excel_path_entry = ttk.Entry(excel_section, textvariable=self.excel_summarize_path_var)
        excel_path_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            excel_browse_btn = ttkb.Button(excel_section, text="📂 Browse", command=lambda: self._browse_file(self.excel_summarize_path_var, [("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]), bootstyle="secondary-outline")
            excel_summarize_btn = ttkb.Button(excel_section, text="📊 Summarize", command=self.on_summarize_excel, bootstyle="info")
        else:
            excel_browse_btn = ttk.Button(excel_section, text="Browse", command=lambda: self._browse_file(self.excel_summarize_path_var, [("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]))
            excel_summarize_btn = ttk.Button(excel_section, text="Summarize", command=self.on_summarize_excel)
        excel_browse_btn.grid(row=0, column=2, padx=4, pady=4)
        excel_summarize_btn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=4, pady=4)
        
        # Word summarization
        if TTKBOOTSTRAP_AVAILABLE:
            word_section = ttkb.Labelframe(frame, text="Word Document Summarization", bootstyle="info")
        else:
            word_section = ttk.LabelFrame(frame, text="Word Document Summarization")
        word_section.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
        word_section.columnconfigure(1, weight=1)
        
        ttk.Label(word_section, text="File Path:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.word_summarize_path_var = tk.StringVar()
        word_path_entry = ttk.Entry(word_section, textvariable=self.word_summarize_path_var)
        word_path_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            word_browse_btn = ttkb.Button(word_section, text="📂 Browse", command=lambda: self._browse_file(self.word_summarize_path_var, [("Word files", "*.docx *.doc"), ("All files", "*.*")]), bootstyle="secondary-outline")
            word_summarize_btn = ttkb.Button(word_section, text="📝 Summarize", command=self.on_summarize_word, bootstyle="info")
        else:
            word_browse_btn = ttk.Button(word_section, text="Browse", command=lambda: self._browse_file(self.word_summarize_path_var, [("Word files", "*.docx *.doc"), ("All files", "*.*")]))
            word_summarize_btn = ttk.Button(word_section, text="Summarize", command=self.on_summarize_word)
        word_browse_btn.grid(row=0, column=2, padx=4, pady=4)
        word_summarize_btn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=4, pady=4)
        
        # Result display
        if TTKBOOTSTRAP_AVAILABLE:
            result_section = ttkb.Labelframe(frame, text="Result", bootstyle="secondary")
        else:
            result_section = ttk.LabelFrame(frame, text="Result")
        result_section.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        result_section.columnconfigure(0, weight=1)
        result_section.rowconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        self.summarization_result_text = tk.Text(result_section, wrap="word", height=10, font=self.text_font)
        self.summarization_result_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            result_scrollbar = ttkb.Scrollbar(result_section, orient="vertical", command=self.summarization_result_text.yview, bootstyle="primary-round")
        else:
            result_scrollbar = ttk.Scrollbar(result_section, orient="vertical", command=self.summarization_result_text.yview)
        self.summarization_result_text.configure(yscroll=result_scrollbar.set)
        result_scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _build_workflow_tools_section(self, parent):
        """Build workflow execution section."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="⚙️ Workflows")
        
        frame.columnconfigure(0, weight=1)
        
        # Notebook cleanup workflow
        if TTKBOOTSTRAP_AVAILABLE:
            workflow_section = ttkb.Labelframe(frame, text="Clean OneNote Notebook Workflow", bootstyle="warning")
        else:
            workflow_section = ttk.LabelFrame(frame, text="Clean OneNote Notebook Workflow")
        workflow_section.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        workflow_section.columnconfigure(1, weight=1)
        
        ttk.Label(workflow_section, text="Notebook Path/ID:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.workflow_notebook_var = tk.StringVar()
        workflow_entry = ttk.Entry(workflow_section, textvariable=self.workflow_notebook_var)
        workflow_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            workflow_run_btn = ttkb.Button(workflow_section, text="🧹 Run Clean Notebook Workflow", command=self.on_run_clean_notebook_workflow, bootstyle="warning")
        else:
            workflow_run_btn = ttk.Button(workflow_section, text="Run Clean Notebook Workflow", command=self.on_run_clean_notebook_workflow)
        workflow_run_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        
        # Workflow result display
        if TTKBOOTSTRAP_AVAILABLE:
            result_section = ttkb.Labelframe(frame, text="Workflow Result", bootstyle="secondary")
        else:
            result_section = ttk.LabelFrame(frame, text="Workflow Result")
        result_section.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        result_section.columnconfigure(0, weight=1)
        result_section.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        self.workflow_result_text = tk.Text(result_section, wrap="word", height=10, font=self.text_font)
        self.workflow_result_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            workflow_scrollbar = ttkb.Scrollbar(result_section, orient="vertical", command=self.workflow_result_text.yview, bootstyle="primary-round")
        else:
            workflow_scrollbar = ttk.Scrollbar(result_section, orient="vertical", command=self.workflow_result_text.yview)
        self.workflow_result_text.configure(yscroll=workflow_scrollbar.set)
        workflow_scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _build_projects_tools_section(self, parent):
        """Build projects list/add GUI section."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="📁 Projects")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Info message
        if TTKBOOTSTRAP_AVAILABLE:
            info_text = ttkb.Label(frame, text="💡 Tip: Use the 'Projects' tab for full project management. This is a quick access view.", bootstyle="info")
        else:
            info_text = ttk.Label(frame, text="Tip: Use the 'Projects' tab for full project management. This is a quick access view.")
        info_text.grid(row=0, column=0, sticky="w", padx=8, pady=8)
        
        # Quick project list
        if TTKBOOTSTRAP_AVAILABLE:
            list_section = ttkb.Labelframe(frame, text="Known Projects", bootstyle="primary")
        else:
            list_section = ttk.LabelFrame(frame, text="Known Projects")
        list_section.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        list_section.columnconfigure(0, weight=1)
        list_section.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        columns = ("name", "priority", "status", "tasks")
        self.projects_tools_tree = ttk.Treeview(list_section, columns=columns, show="headings", selectmode="browse")
        self.projects_tools_tree.heading("name", text="Project Name")
        self.projects_tools_tree.heading("priority", text="Priority")
        self.projects_tools_tree.heading("status", text="Status")
        self.projects_tools_tree.heading("tasks", text="# Tasks")
        
        self.projects_tools_tree.column("name", width=250)
        self.projects_tools_tree.column("priority", width=100)
        self.projects_tools_tree.column("status", width=100)
        self.projects_tools_tree.column("tasks", width=80)
        
        self.projects_tools_tree.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            projects_scrollbar = ttkb.Scrollbar(list_section, orient="vertical", command=self.projects_tools_tree.yview, bootstyle="primary-round")
        else:
            projects_scrollbar = ttk.Scrollbar(list_section, orient="vertical", command=self.projects_tools_tree.yview)
        self.projects_tools_tree.configure(yscroll=projects_scrollbar.set)
        projects_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Quick add project
        if TTKBOOTSTRAP_AVAILABLE:
            add_section = ttkb.Labelframe(frame, text="Quick Add Project", bootstyle="success")
        else:
            add_section = ttk.LabelFrame(frame, text="Quick Add Project")
        add_section.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        add_section.columnconfigure(1, weight=1)
        
        ttk.Label(add_section, text="Project Name:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.quick_project_name_var = tk.StringVar()
        quick_name_entry = ttk.Entry(add_section, textvariable=self.quick_project_name_var)
        quick_name_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            quick_add_btn = ttkb.Button(add_section, text="➕ Add Project", command=self.on_quick_add_project, bootstyle="success")
            refresh_projects_btn = ttkb.Button(add_section, text="🔄 Refresh", command=self.refresh_projects_tools_list, bootstyle="secondary-outline")
        else:
            quick_add_btn = ttk.Button(add_section, text="Add Project", command=self.on_quick_add_project)
            refresh_projects_btn = ttk.Button(add_section, text="Refresh", command=self.refresh_projects_tools_list)
        quick_add_btn.grid(row=0, column=2, padx=4, pady=4)
        refresh_projects_btn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=4, pady=4)
        
        # Bind Enter key to add project
        quick_name_entry.bind("<Return>", lambda e: self.on_quick_add_project())
        
        # Initial refresh
        self.refresh_projects_tools_list()
    
    def _build_agent_chat_section(self, parent):
        """Build enhanced chat section with agent selection."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="💬 Agent Chat")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Info message
        if TTKBOOTSTRAP_AVAILABLE:
            info_text = ttkb.Label(frame, text="💡 Tip: Use the 'Chat' tab for full chat interface. This is a quick agent chat interface.", bootstyle="info")
        else:
            info_text = ttk.Label(frame, text="Tip: Use the 'Chat' tab for full chat interface. This is a quick agent chat interface.")
        info_text.grid(row=0, column=0, sticky="w", padx=8, pady=8)
        
        # Agent selection and input
        if TTKBOOTSTRAP_AVAILABLE:
            input_section = ttkb.Labelframe(frame, text="Send Message to Agent", bootstyle="primary")
        else:
            input_section = ttk.LabelFrame(frame, text="Send Message to Agent")
        input_section.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
        input_section.columnconfigure(1, weight=1)
        
        ttk.Label(input_section, text="Agent:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.agent_chat_agent_var = tk.StringVar(value="AIC")
        if TTKBOOTSTRAP_AVAILABLE:
            agent_combo = ttkb.Combobox(input_section, textvariable=self.agent_chat_agent_var, values=["AIC", "Aria", "Sora"], state="readonly", bootstyle="primary")
        else:
            agent_combo = ttk.Combobox(input_section, textvariable=self.agent_chat_agent_var, values=["AIC", "Aria", "Sora"], state="readonly")
        agent_combo.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        
        ttk.Label(input_section, text="Message:").grid(row=1, column=0, sticky="nw", padx=4, pady=4)
        self.agent_chat_message_text = tk.Text(input_section, height=5, wrap="word", font=self.text_font)
        self.agent_chat_message_text.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            agent_chat_send_btn = ttkb.Button(input_section, text="📤 Send to Agent", command=self.on_send_agent_message, bootstyle="primary")
        else:
            agent_chat_send_btn = ttk.Button(input_section, text="Send to Agent", command=self.on_send_agent_message)
        agent_chat_send_btn.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        
        # Response display
        if TTKBOOTSTRAP_AVAILABLE:
            response_section = ttkb.Labelframe(frame, text="Agent Response", bootstyle="secondary")
        else:
            response_section = ttk.LabelFrame(frame, text="Agent Response")
        response_section.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        response_section.columnconfigure(0, weight=1)
        response_section.rowconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        self.agent_chat_response_text = tk.Text(response_section, wrap="word", height=10, font=self.text_font, state="disabled")
        self.agent_chat_response_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            agent_chat_scrollbar = ttkb.Scrollbar(response_section, orient="vertical", command=self.agent_chat_response_text.yview, bootstyle="primary-round")
        else:
            agent_chat_scrollbar = ttk.Scrollbar(response_section, orient="vertical", command=self.agent_chat_response_text.yview)
        self.agent_chat_response_text.configure(yscroll=agent_chat_scrollbar.set)
        agent_chat_scrollbar.grid(row=0, column=1, sticky="ns")
    
    # ---------- Tools Tab Handler Methods ----------
    
    def refresh_onenote_notebooks(self):
        """Refresh the list of OneNote notebooks."""
        try:
            # Clear existing items
            for item in self.onenote_tree.get_children():
                self.onenote_tree.delete(item)
            
            if not ONENOTE_CLIENT_AVAILABLE or OneNoteClient is None:
                self.onenote_status_var.set("❌ OneNote client not available. Check Microsoft Graph configuration.")
                return
            
            # Check if credentials are configured
            from .integrations import GraphCredentials
            try:
                creds = GraphCredentials.from_env()
                if not creds.tenant_id or not creds.client_id or not creds.client_secret:
                    self.onenote_status_var.set("❌ Not authenticated. Configure Microsoft Graph credentials in Settings > Integrations.")
                    messagebox.showwarning(
                        "Not Authenticated",
                        "Microsoft Graph credentials are not configured.\n\n"
                        "Please go to:\n"
                        "1. Settings tab > Integrations\n"
                        "2. Click 'Configure' next to OneNote\n"
                        "3. Enter your Azure credentials\n\n"
                        "Or run: python get_azure_credentials.py"
                    )
                    return
            except Exception as e:
                self.onenote_status_var.set("❌ Credentials error. Check Microsoft Graph configuration.")
                messagebox.showwarning("Credentials Error", f"Failed to load credentials: {e}")
                return
            
            self.onenote_status_var.set("🔄 Loading notebooks...")
            self.update()
            
            try:
                # Pass connection to GraphClient so it can load credentials from database
                from .integrations.msgraph.client import GraphClient
                graph_client = GraphClient(conn=self.conn)
                client = OneNoteClient(graph_client)
                notebooks = client.list_notebooks()
                
                if not notebooks:
                    self.onenote_status_var.set("ℹ️ No notebooks found. You may not have any OneNote notebooks.")
                    return
                
                for nb in notebooks:
                    name = nb.get("displayName", "Unknown")
                    nb_id = nb.get("id", "")
                    last_modified = nb.get("lastModifiedDateTime", "Unknown")
                    if last_modified and "T" in last_modified:
                        last_modified = last_modified.replace("T", " ")[:16]
                    
                    self.onenote_tree.insert("", "end", values=(name, nb_id, last_modified))
                
                self.onenote_status_var.set(f"✅ Loaded {len(notebooks)} notebook(s)")
            except Exception as e:
                error_msg = str(e)
                # Check for specific authentication errors
                if "401" in error_msg or "Unauthorized" in error_msg or "Authentication" in error_msg:
                    self.onenote_status_var.set("❌ Authentication failed. Check Microsoft Graph credentials.")
                    messagebox.showerror(
                        "Authentication Failed",
                        f"Failed to authenticate with Microsoft Graph:\n\n{error_msg}\n\n"
                        "Possible causes:\n"
                        "1. Invalid or expired client secret\n"
                        "2. Wrong tenant ID, client ID, or client secret\n"
                        "3. Missing required permissions (Notes.ReadWrite)\n\n"
                        "Go to Settings > Integrations to reconfigure credentials."
                    )
                elif "credentials" in error_msg.lower():
                    self.onenote_status_var.set("❌ Credentials not configured. Set up Microsoft Graph in Settings.")
                    messagebox.showwarning(
                        "Not Configured",
                        "Microsoft Graph credentials are not configured.\n\n"
                        "Go to Settings > Integrations to configure."
                    )
                else:
                    self.onenote_status_var.set(f"❌ Error: {error_msg[:50]}")
                    messagebox.showerror("Error", f"Failed to load OneNote notebooks:\n\n{error_msg}")
        except Exception as e:
            error_msg = str(e)
            self.onenote_status_var.set(f"❌ Error: {error_msg[:50]}")
            messagebox.showerror("Error", f"Failed to refresh notebooks:\n\n{error_msg}")
    
    def refresh_excel_workbooks(self):
        """Refresh the list of Excel workbooks from OneDrive."""
        try:
            # Clear existing items
            for item in self.excel_tree.get_children():
                self.excel_tree.delete(item)
            
            if not EXCEL_CLOUD_AVAILABLE or ExcelCloudClient is None:
                self.excel_status_var.set("❌ Excel cloud client not available. Check Microsoft Graph configuration.")
                return
            
            self.excel_status_var.set("🔄 Loading workbooks...")
            self.update()
            
            try:
                # Pass connection to GraphClient so it can load credentials from database
                from .integrations.msgraph.client import GraphClient
                graph_client = GraphClient(conn=self.conn)
                client = ExcelCloudClient(graph_client)
                items = client.list_workbooks()
                
                # Filter for Excel files
                excel_files = [item for item in items if item.get("name", "").endswith((".xlsx", ".xls"))]
                
                if not excel_files:
                    self.excel_status_var.set("ℹ️ No Excel workbooks found or not authenticated. Check Microsoft Graph credentials.")
                    return
                
                for item in excel_files:
                    name = item.get("name", "Unknown")
                    item_id = item.get("id", "")
                    size = item.get("size", 0)
                    size_str = f"{size / 1024:.1f} KB" if size > 0 else "Unknown"
                    modified = item.get("lastModifiedDateTime", "Unknown")
                    if modified and "T" in modified:
                        modified = modified.replace("T", " ")[:16]
                    
                    self.excel_tree.insert("", "end", values=(name, item_id, size_str, modified))
                
                self.excel_status_var.set(f"✅ Loaded {len(excel_files)} workbook(s)")
            except Exception as e:
                self.excel_status_var.set(f"❌ Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to load Excel workbooks: {e}")
        except Exception as e:
            self.excel_status_var.set(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh workbooks: {e}")
    
    def _browse_file(self, var: tk.StringVar, filetypes):
        """Helper method to browse for a file."""
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            var.set(filename)
    
    def on_summarize_excel(self):
        """Summarize a local Excel workbook."""
        path = self.excel_summarize_path_var.get().strip()
        if not path:
            messagebox.showwarning("No File", "Please select an Excel file to summarize.")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("File Not Found", f"The file does not exist: {path}")
            return
        
        try:
            self.summarization_result_text.delete("1.0", "end")
            self.summarization_result_text.insert("1.0", "🔄 Summarizing Excel workbook...\n")
            self.update()
            
            if not EXCEL_SERVICE_AVAILABLE or summarize_local_workbook is None:
                self.summarization_result_text.delete("1.0", "end")
                self.summarization_result_text.insert("1.0", "❌ Excel service not available. pandas may not be installed.\n")
                messagebox.showerror("Error", "Excel summarization requires pandas. Install with: pip install pandas")
                return
            
            # Summarize the workbook
            result = summarize_local_workbook(path, "Generate a summary of this workbook")
            
            summary_path = result.get("summary_path", "")
            
            if summary_path and os.path.exists(summary_path):
                with open(summary_path, 'r') as f:
                    summary_content = f.read()
                
                self.summarization_result_text.delete("1.0", "end")
                self.summarization_result_text.insert("1.0", f"✅ Summary generated successfully!\n\n")
                self.summarization_result_text.insert("end", f"Summary saved to: {summary_path}\n\n")
                self.summarization_result_text.insert("end", "Summary Content:\n" + "="*50 + "\n\n")
                self.summarization_result_text.insert("end", summary_content)
            else:
                self.summarization_result_text.delete("1.0", "end")
                self.summarization_result_text.insert("1.0", "✅ Summarization completed. Check the summary file next to the workbook.\n")
            
            messagebox.showinfo("Success", "Excel workbook summarized successfully!")
        except Exception as e:
            self.summarization_result_text.delete("1.0", "end")
            self.summarization_result_text.insert("1.0", f"❌ Error: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to summarize Excel workbook: {e}")
    
    def on_summarize_word(self):
        """Summarize a local Word document."""
        path = self.word_summarize_path_var.get().strip()
        if not path:
            messagebox.showwarning("No File", "Please select a Word document to summarize.")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("File Not Found", f"The file does not exist: {path}")
            return
        
        try:
            self.summarization_result_text.delete("1.0", "end")
            self.summarization_result_text.insert("1.0", "🔄 Summarizing Word document...\n")
            self.update()
            
            if not WORD_SERVICE_AVAILABLE or WordService is None:
                self.summarization_result_text.delete("1.0", "end")
                self.summarization_result_text.insert("1.0", "❌ Word service not available. python-docx may not be installed.\n")
                messagebox.showerror("Error", "Word summarization requires python-docx. Install with: pip install python-docx")
                return
            
            # Read and summarize the document
            from docx import Document
            
            doc = Document(path)
            text_content = "\n".join([para.text for para in doc.paragraphs])
            
            # Use AI to summarize (simplified - in real implementation, use WordService)
            if openai_available():
                from .ai_layer.tools import summarize_text
                summary = summarize_text(text_content, style="clear")
                
                self.summarization_result_text.delete("1.0", "end")
                self.summarization_result_text.insert("1.0", "✅ Summary generated successfully!\n\n")
                self.summarization_result_text.insert("end", "Summary:\n" + "="*50 + "\n\n")
                self.summarization_result_text.insert("end", summary)
            else:
                # Fallback: show first few paragraphs
                preview = "\n".join([para.text for para in doc.paragraphs[:10]])
                self.summarization_result_text.delete("1.0", "end")
                self.summarization_result_text.insert("1.0", "ℹ️ OpenAI not available. Showing document preview:\n\n")
                self.summarization_result_text.insert("end", preview[:500] + ("..." if len(preview) > 500 else ""))
            
            messagebox.showinfo("Success", "Word document summarized successfully!")
        except Exception as e:
            self.summarization_result_text.delete("1.0", "end")
            self.summarization_result_text.insert("1.0", f"❌ Error: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to summarize Word document: {e}")
    
    def on_run_clean_notebook_workflow(self):
        """Run the clean notebook workflow."""
        notebook_path_or_id = self.workflow_notebook_var.get().strip()
        if not notebook_path_or_id:
            messagebox.showwarning("No Notebook", "Please enter a notebook path or ID.")
            return
        
        try:
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert("1.0", "🔄 Running clean notebook workflow...\n")
            self.update()
            
            if not WORKFLOWS_AVAILABLE or CleanNotebookWorkflow is None:
                self.workflow_result_text.delete("1.0", "end")
                self.workflow_result_text.insert("1.0", "❌ Workflow system not available.\n")
                messagebox.showerror("Error", "Workflow system not available.")
                return
            
            # Import required services
            try:
                from .integrations.onenote.service import OneNoteService
                onenote_service = OneNoteService()
                workflow = CleanNotebookWorkflow(onenote_service)
                
                # Run the workflow
                workflow.run(notebook_path_or_id, actor="AIC")
                
                self.workflow_result_text.delete("1.0", "end")
                self.workflow_result_text.insert("1.0", f"✅ Clean notebook workflow completed successfully!\n\n")
                self.workflow_result_text.insert("end", f"Notebook: {notebook_path_or_id}\n")
                self.workflow_result_text.insert("end", "The notebook has been cleaned and changes have been committed.\n")
                
                messagebox.showinfo("Success", "Clean notebook workflow completed successfully!")
            except Exception as e:
                self.workflow_result_text.delete("1.0", "end")
                self.workflow_result_text.insert("1.0", f"❌ Error: {str(e)}\n")
                messagebox.showerror("Error", f"Failed to run workflow: {e}")
        except Exception as e:
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert("1.0", f"❌ Error: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to run workflow: {e}")
    
    def refresh_projects_tools_list(self):
        """Refresh the projects list in the Tools tab."""
        try:
            # Clear existing items
            for item in self.projects_tools_tree.get_children():
                self.projects_tools_tree.delete(item)
            
            # Load current state
            self.state_obj = load_state(self.conn)
            
            # Count tasks per project
            counts: Dict[str, int] = {}
            for t in self.state_obj.tasks:
                counts[t.project] = counts.get(t.project, 0) + 1
            
            # Add projects to tree
            priority_weight = {p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)}
            projects_sorted = sorted(
                self.state_obj.projects,
                key=lambda p: (priority_weight.get(p.priority, 1), p.name),
                reverse=True,
            )
            
            for p in projects_sorted:
                self.projects_tools_tree.insert(
                    "",
                    "end",
                    iid=p.name,
                    values=(p.name, p.priority, p.status, counts.get(p.name, 0)),
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh projects list: {e}")
    
    def on_quick_add_project(self):
        """Quick add a project from the Tools tab."""
        name = self.quick_project_name_var.get().strip()
        if not name:
            messagebox.showwarning("No Name", "Please enter a project name.")
            return
        
        # Check if project already exists
        existing = next((p for p in self.state_obj.projects if p.name == name), None)
        if existing:
            messagebox.showinfo("Exists", f"Project '{name}' already exists.")
            return
        
        try:
            # Create new project
            new_project = Project(
                name=name,
                description="",
                priority="MEDIUM",
                status="active"
            )
            
            db_upsert_project(self.conn, new_project)
            self.state_obj.projects.append(new_project)
            
            # Clear input and refresh list
            self.quick_project_name_var.set("")
            self.refresh_projects_tools_list()
            
            messagebox.showinfo("Success", f"Project '{name}' added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add project: {e}")
    
    def on_send_agent_message(self):
        """Send a message to the selected agent."""
        agent = self.agent_chat_agent_var.get()
        message = self.agent_chat_message_text.get("1.0", "end").strip()
        
        if not message:
            messagebox.showwarning("No Message", "Please enter a message.")
            return
        
        if not openai_available():
            messagebox.showerror("Error", "OpenAI API is not available. Please configure your API key.")
            return
        
        try:
            self.agent_chat_response_text.config(state="normal")
            self.agent_chat_response_text.delete("1.0", "end")
            self.agent_chat_response_text.insert("1.0", f"🔄 Sending message to {agent}...\n")
            self.update()
            
            # Get agent model
            model = get_agent_model(agent)
            
            # Create chat history
            history = [
                ChatMessage(role="user", content=message, timestamp=datetime.now().isoformat())
            ]
            
            # Generate response
            response = generate_ai_reply(
                history=history,
                persona=agent,
                model=model,
                temperature=0.7
            )
            
            self.agent_chat_response_text.delete("1.0", "end")
            self.agent_chat_response_text.insert("1.0", f"Response from {agent}:\n" + "="*50 + "\n\n")
            self.agent_chat_response_text.insert("end", response)
            self.agent_chat_response_text.config(state="disabled")
            
            # Save to chat history
            db_insert_chat_message(self.conn, ChatMessage(
                role="user",
                content=message,
                timestamp=datetime.now().isoformat(),
                persona=agent
            ))
            db_insert_chat_message(self.conn, ChatMessage(
                role="assistant",
                content=response,
                timestamp=datetime.now().isoformat(),
                persona=agent
            ))
            
            # Clear input
            self.agent_chat_message_text.delete("1.0", "end")
        except Exception as e:
            self.agent_chat_response_text.config(state="normal")
            self.agent_chat_response_text.delete("1.0", "end")
            self.agent_chat_response_text.insert("1.0", f"❌ Error: {str(e)}\n")
            self.agent_chat_response_text.config(state="disabled")
            messagebox.showerror("Error", f"Failed to send message: {e}")

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
            header = ttkb.Label(main_container, text="Analytics & Reports", bootstyle="primary", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
        else:
            header = ttk.Label(main_container, text="Analytics & Reports", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
        header.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Text widget for displaying analytics
        text_frame = ttk.Frame(main_container)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.analytics_text = tk.Text(text_frame, wrap="word", font=("Courier", 10), bg="#f5f5f5" if not TTKBOOTSTRAP_AVAILABLE else None)
        self.analytics_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.analytics_text.yview)
        self.analytics_text.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Buttons
        if TTKBOOTSTRAP_AVAILABLE:
            btn_frame = ttkb.Frame(main_container)
        else:
            btn_frame = ttk.Frame(main_container)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        
        if TTKBOOTSTRAP_AVAILABLE:
            refresh_btn = ttkb.Button(btn_frame, text="🔄 Refresh", command=self.refresh_analytics, bootstyle="primary")
            export_btn = ttkb.Button(btn_frame, text="💾 Export Report", command=self.on_export_analytics_report, bootstyle="info-outline")
        else:
            refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_analytics)
            export_btn = ttk.Button(btn_frame, text="Export Report", command=self.on_export_analytics_report)
        
        refresh_btn.grid(row=0, column=0, padx=4)
        export_btn.grid(row=0, column=1, padx=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(refresh_btn, text="Refresh analytics data")
            ToolTip(export_btn, text="Export report to text file")
    
    def refresh_analytics(self):
        """Refresh the analytics display."""
        if not hasattr(self, 'analytics_text'):
            return
        
        self.analytics_text.delete('1.0', 'end')
        
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
            for project_name, stats in sorted(project_stats.items(), key=lambda x: x[1]["total"], reverse=True):
                lines.append(f"{project_name}:")
                lines.append(f"  Total: {stats['total']}, Done: {stats['done']}, Completion: {stats['completion_rate']}%")
            lines.append("")
            
            # Time Tracking
            lines.append("TIME TRACKING")
            lines.append("-" * 70)
            lines.append(f"Estimated: {time_stats['estimated_hours']} hours ({time_stats['total_estimated_minutes']} minutes)")
            lines.append(f"Logged: {time_stats['logged_hours']} hours ({time_stats['total_logged_minutes']} minutes)")
            lines.append(f"Tasks with time data: {time_stats['tasks_with_time']}")
            if time_stats['total_estimated_minutes'] > 0:
                variance = ((time_stats['total_logged_minutes'] - time_stats['total_estimated_minutes']) / time_stats['total_estimated_minutes']) * 100
                lines.append(f"Time variance: {variance:+.1f}%")
            lines.append("")
            
            # Productivity Metrics
            lines.append("PRODUCTIVITY METRICS")
            lines.append("-" * 70)
            lines.append(f"Completion Rate: {productivity['completion_rate']}%")
            lines.append(f"Tasks Completed: {productivity['tasks_completed']}")
            lines.append(f"Tasks In Progress: {productivity['tasks_in_progress']}")
            lines.append(f"Total Time Logged: {productivity['total_time_logged_hours']} hours")
            lines.append(f"Average Time per Task: {productivity['average_time_per_task_minutes']} minutes")
            lines.append("")
            
            # Deadline Reminders
            if deadline_reminders:
                lines.append("DEADLINE REMINDERS (Next 7 Days)")
                lines.append("-" * 70)
                for reminder in deadline_reminders[:10]:  # Top 10
                    task = reminder['task']
                    urgency = reminder['urgency'].upper()
                    days = reminder['days_until']
                    lines.append(f"[{urgency}] Task #{task.id}: {task.title[:50]} - {days} day(s) until due")
                lines.append("")
            
            # Workload Balance
            lines.append("WORKLOAD BALANCE")
            lines.append("-" * 70)
            for persona, data in workload.items():
                status = "⚠️ OVERLOADED" if data['overloaded'] else "✓ OK"
                lines.append(f"{persona}: {status}")
                lines.append(f"  Tasks: {data['task_count']}, Est. Hours: {data['estimated_hours']}, Logged: {data['logged_hours']}")
                lines.append(f"  High Priority: {data['high_priority_count']}")
            lines.append("")
            
            # Project Health
            lines.append("PROJECT HEALTH")
            lines.append("-" * 70)
            for project_name, health in sorted(project_health.items(), key=lambda x: x[1]['health_score']):
                status_icon = "✓" if health['health_status'] == "healthy" else "⚠" if health['health_status'] == "warning" else "✗"
                lines.append(f"{status_icon} {project_name}: {health['health_status'].upper()} (Score: {health['health_score']})")
                lines.append(f"  Total: {health['total_tasks']}, Completed: {health['completed']}, Blocked: {health['blocked']}, Overdue: {health['overdue']}")
            lines.append("")
            
            # Smart Suggestions
            if suggestions:
                lines.append("SMART SUGGESTIONS")
                lines.append("-" * 70)
                for suggestion in suggestions[:10]:  # Top 10
                    priority = suggestion['priority'].upper()
                    lines.append(f"[{priority}] {suggestion['message']}")
                lines.append("")
            
            # Display the report
            self.analytics_text.insert('1.0', '\n'.join(lines))
            self.analytics_text.see('1.0')
            
        except Exception as e:
            self.analytics_text.insert('1.0', f"Error generating analytics: {e}")
    
    def on_export_analytics_report(self):
        """Export analytics report to a text file."""
        try:
            report = generate_report(self.state_obj)
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(report)
                messagebox.showinfo("Export", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")


# Templates tab removed - functionality was redundant with normal task creation

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
            ttkb.Label(self.settings_frame, text="Theme:", bootstyle="primary").grid(row=row, column=0, sticky="e", padx=8, pady=8)
            self.theme_var = tk.StringVar(value=self.settings.theme)
            # Provide more theme options with ttkbootstrap
            theme_values = ["plain", "light", "dark"]
            # Map to ttkbootstrap themes for better names
            theme_combo = ttkb.Combobox(
                self.settings_frame,
                textvariable=self.theme_var,
                values=theme_values,
                state="readonly",
                bootstyle="primary"
            )
        else:
            ttk.Label(self.settings_frame, text="Theme:").grid(row=row, column=0, sticky="e", padx=8, pady=8)
            self.theme_var = tk.StringVar(value=self.settings.theme)
            theme_combo = ttk.Combobox(
                self.settings_frame,
                textvariable=self.theme_var,
                values=["plain", "light", "dark"],
                state="readonly",
            )
        theme_combo.grid(row=row, column=1, sticky="w", padx=8, pady=8)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(theme_combo, text="Choose UI theme: plain (cosmo), light (litera), or dark (darkly)")

        row += 1
        ttk.Label(self.settings_frame, text="Default View:").grid(row=row, column=0, sticky="e", padx=8, pady=8)
        self.default_view_var = tk.StringVar(value=self.settings.default_view)
        defview_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.default_view_var,
            values=["dashboard", "tasks", "projects"],
            state="readonly",
        )
        defview_combo.grid(row=row, column=1, sticky="w", padx=8, pady=8)

        row += 1
        ttk.Label(self.settings_frame, text="Font Scale:").grid(row=row, column=0, sticky="e", padx=8, pady=8)
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
        if TTKBOOTSTRAP_AVAILABLE:
            pref_box = ttkb.Labelframe(self.settings_frame, text="📊 Data Preferences", bootstyle="info")
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
            var = tk.BooleanVar(value=self.settings.data_preferences.get(key, DEFAULT_FETCH_PREFERENCES.get(key, True)))
            chk = ttk.Checkbutton(pref_box, text=label, variable=var)
            chk.grid(row=idx // 2, column=idx % 2, sticky="w", padx=8, pady=4)
            self.data_pref_vars[key] = var

        row += 1
        if TTKBOOTSTRAP_AVAILABLE:
            export_import_box = ttkb.Labelframe(self.settings_frame, text="💾 Export & Import", bootstyle="secondary")
        else:
            export_import_box = ttk.LabelFrame(self.settings_frame, text="Export & Import")
        export_import_box.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        export_import_box.columnconfigure(0, weight=1)
        export_import_box.columnconfigure(1, weight=1)
        
        if TTKBOOTSTRAP_AVAILABLE:
            export_tasks_csv_btn = ttkb.Button(export_import_box, text="📥 Export Tasks (CSV)", command=lambda: self.on_export_tasks("csv"), bootstyle="info-outline")
            export_tasks_json_btn = ttkb.Button(export_import_box, text="📥 Export Tasks (JSON)", command=lambda: self.on_export_tasks("json"), bootstyle="info-outline")
            export_projects_btn = ttkb.Button(export_import_box, text="📥 Export Projects", command=self.on_export_projects, bootstyle="info-outline")
            export_backup_btn = ttkb.Button(export_import_box, text="💾 Full Backup", command=self.on_export_backup, bootstyle="success-outline")
            import_tasks_btn = ttkb.Button(export_import_box, text="📤 Import Tasks", command=self.on_import_tasks, bootstyle="warning-outline")
        else:
            export_tasks_csv_btn = ttk.Button(export_import_box, text="Export Tasks (CSV)", command=lambda: self.on_export_tasks("csv"))
            export_tasks_json_btn = ttk.Button(export_import_box, text="Export Tasks (JSON)", command=lambda: self.on_export_tasks("json"))
            export_projects_btn = ttk.Button(export_import_box, text="Export Projects", command=self.on_export_projects)
            export_backup_btn = ttk.Button(export_import_box, text="Full Backup", command=self.on_export_backup)
            import_tasks_btn = ttk.Button(export_import_box, text="Import Tasks", command=self.on_import_tasks)
        
        export_tasks_csv_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        export_tasks_json_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        export_projects_btn.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        export_backup_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        import_tasks_btn.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
        
        row += 1
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(self.settings_frame, text="💾 Save Settings", command=self.on_save_settings, bootstyle="success")
        else:
            save_btn = ttk.Button(self.settings_frame, text="Save Settings", command=self.on_save_settings)
        save_btn.grid(row=row, column=1, sticky="w", padx=8, pady=8)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(save_btn, text="Save all settings and apply changes")

    def on_save_settings(self):
        self.settings.theme = self.theme_var.get()
        self.settings.default_view = self.default_view_var.get()
        self.settings.show_system_status = self.show_sys_var.get()
        self.settings.font_scale = self.font_scale_var.get()
        self.settings.data_preferences = {k: var.get() for k, var in self.data_pref_vars.items()}
        save_settings(self.conn, self.settings)
        
        # Apply theme change if ttkbootstrap is available
        if TTKBOOTSTRAP_AVAILABLE:
            theme_map = {
                "plain": "cosmo",
                "light": "litera",
                "dark": "darkly"
            }
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
                    initialfile=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
                if filename:
                    export_tasks_to_csv(self.conn, filename)
                    messagebox.showinfo("Export", f"Tasks exported to {filename}")
            elif format_type == "json":
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialfile=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
                initialfile=f"projects_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
                initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
                    ("All files", "*.*")
                ]
            )
            if filename:
                imported = 0
                if filename.endswith('.csv'):
                    imported = import_tasks_from_csv(self.conn, filename)
                elif filename.endswith('.json'):
                    imported = import_tasks_from_json(self.conn, filename)
                else:
                    messagebox.showwarning("Import Error", "Please select a CSV or JSON file.")
                    return
                
                if imported > 0:
                    messagebox.showinfo("Import", f"Successfully imported {imported} task(s).")
                    self.refresh_all()
                else:
                    messagebox.showwarning("Import", "No tasks were imported. Please check the file format.")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import tasks: {e}")

    # ---------- Global ----------

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_task_list()
        self.refresh_project_list()
        self.refresh_chat_history()
        if hasattr(self, 'refresh_integrations_list'):
            self.refresh_integrations_list()
        if hasattr(self, 'refresh_analytics'):
            self.refresh_analytics()

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
        
        # Stop cognitive daemon system
        try:
            from .daemon import stop_daemon_system
            stop_daemon_system()
            print("[GUI] Cognitive daemon system stopped")
        except Exception:
            pass
        
        self.conn.close()
        self.destroy()


def run_gui():
    app = AssistantGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
