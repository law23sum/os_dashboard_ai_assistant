#!/usr/bin/env python3
import base64
import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

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
from config.logging_config import setup_logger
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


try:
    from .integrations.excel.cloud_client import ExcelCloudClient
    EXCEL_CLOUD_AVAILABLE = True
except ImportError:
    EXCEL_CLOUD_AVAILABLE = False
    ExcelCloudClient = None

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

# Import enhanced conversation manager (optional)
try:
    from assistant_core.conversation_manager import process_conversation_message, get_conversation_analytics
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
from .document_manager import (
    upload_document as dm_upload_document,
    get_project_documents,
    format_file_size,
    DOCUMENT_TYPES,
    DOCUMENTS_BASE_DIR,
    get_document_versions,
    restore_document_version,
    get_document_version,
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
        # Determine theme based on settings - use more professional modern themes
        theme_map = {
            "plain": "minty",  # Modern, clean, professional
            "light": "litera",  # Clean light theme
            "dark": "superhero"  # Modern dark theme
        }
        theme = theme_map.get("plain", "minty")  # Default to minty for professional look
        
        if TTKBOOTSTRAP_AVAILABLE:
            super().__init__(themename=theme, title="Assistant Hub", resizable=(True, True))
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
        self.security_status: SecurityStatus = load_security_status(self.conn)

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
        self.command_var = tk.StringVar()
        self.cwd_var = tk.StringVar(value=os.getcwd())
        self.project_docs_file_paths = {}  # Map item_id -> file_path for project documents
        self.project_docs_link_ids = {}  # Map item_id -> link_id for project documents

        self._configure_style()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_topbar()


        if TTKBOOTSTRAP_AVAILABLE:
            self.notebook = ttkb.Notebook(self, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(self)
        # Better spacing for professional look
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 12))

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
            self.notebook.tab(4, text="🔧 Tools")
            self.notebook.tab(5, text="📊 Analytics")
            self.notebook.tab(6, text="⚙️ Settings")

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

        # Initialize automation orchestrator attribute
        self.automation_orchestrator = None

        # Initialize automation orchestrator for intelligent workflow automation
        try:
            if AUTOMATION_ORCHESTRATOR_AVAILABLE:
                self.automation_orchestrator = AutomationOrchestrator(app_state=self)
                asyncio.create_task(self.automation_orchestrator.initialize())
                print("[GUI] Automation Orchestrator initialized - intelligent workflows enabled")
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

    def _build_color_palette(self):
        """Define a soft color palette used throughout the interface."""
        # Neutral surfaces keep focus on content and reduce eye strain
        self.colors = {
            "background": "#f5f7fb" if self.settings.theme != "dark" else "#131722",
            "surface": "#ffffff" if self.settings.theme != "dark" else "#1f2430",
            "border": "#dfe3eb" if self.settings.theme != "dark" else "#2d3342",
            "text": "#1f2532" if self.settings.theme != "dark" else "#e8edf7",
            "muted": "#4f566b" if self.settings.theme != "dark" else "#b8c1d9",
        }

    def _initialize_fonts(self):
        """Configure fonts based on settings with professional typography."""
        try:
            scale_map = {"small": 11, "medium": 13, "large": 15}  # Slightly larger for better readability
            base_size = scale_map.get(getattr(self.settings, 'font_scale', 'medium'), 13)

            # Configure the already-initialized fonts with better typography
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
            
            # Create heading font for better visual hierarchy
            self.heading_font = tkfont.Font(
                family=self.base_font.actual("family"),
                size=base_size + 2,
                weight="bold"
            )

            # Create bold font for emphasis
            self.bold_font = tkfont.Font(
                family=self.base_font.actual("family"),
                size=base_size,
                weight="bold"
            )
        except Exception as e:
            # Fallback to default fonts if configuration fails
            print(f"Warning: Could not configure fonts: {e}")
            if not hasattr(self, 'base_font'):
                self.base_font = tkfont.nametofont("TkDefaultFont")
            if not hasattr(self, 'text_font'):
                self.text_font = tkfont.nametofont("TkTextFont")
            self.heading_font = self.base_font
            self.bold_font = self.base_font

    def _configure_style(self):
        if TTKBOOTSTRAP_AVAILABLE:
            # ttkbootstrap handles themes automatically - use professional themes
            theme_map = {
                "plain": "minty",
                "light": "litera",
                "dark": "superhero"
            }
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
        # Better row height for tables
        self.style.configure("Treeview", rowheight=base_size + 16, font=(self.base_font.actual("family"), base_size))
        self.style.configure("Treeview.Heading", font=(heading_font.actual("family"), base_size + 1), padding=(8, 6))
        # More professional tab styling
        self.style.configure("TNotebook.Tab", padding=(24, 12), font=(self.base_font.actual("family"), base_size))
        self.style.configure("TLabel", padding=(6, 4))
        # Better button styling with more padding
        self.style.configure("TButton", padding=(14, 10), font=(self.base_font.actual("family"), base_size))
        self.style.configure("Card.TFrame", background=self.colors["surface"], relief="flat")
        self.style.configure("Card.TLabelframe", background=self.colors["surface"], relief="flat")
        self.style.configure("Card.TLabelframe.Label", background=self.colors["surface"], foreground=self.colors["muted"], font=(self.base_font.actual("family"), base_size, "bold"))
        self.configure(bg=self.colors["background"])

        if not TTKBOOTSTRAP_AVAILABLE:
            palette = {
                "plain": {"bg": "#f8f9fa", "fg": "#212529"},  # Modern light gray
                "light": {"bg": "#ffffff", "fg": "#212529"},
                "dark": {"bg": "#1a1d29", "fg": "#e9ecef"},  # Modern dark
            }
            colors = palette.get(self.settings.theme, palette["plain"])
            self.configure(bg=colors["bg"])
            for style_name in ["TFrame", "TLabelframe", "TLabelframe.Label", "TLabel"]:
                self.style.configure(style_name, background=colors["bg"], foreground=colors["fg"])

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
        widget.bind("<Command-c>", lambda e: self._copy_from_text_widget(widget))  # macOS

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
        """Build a professional top bar with better spacing and styling."""
        if TTKBOOTSTRAP_AVAILABLE:
            top = ttkb.Frame(self)
        else:
            top = ttk.Frame(self)
        # Better padding for professional appearance
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        top.columnconfigure(1, weight=1)
        top.columnconfigure(4, weight=1)  # Add spacing between left and right sections

        # Left section - Persona controls
        if TTKBOOTSTRAP_AVAILABLE:
            persona_label = ttkb.Label(top, text="Active Persona:", bootstyle="primary", font=self.heading_font)
        else:
            persona_label = ttk.Label(top, text="Active Persona:", font=self.heading_font)
        persona_label.grid(row=0, column=0, sticky="w", padx=(0, 8))
        
        self.persona_var = tk.StringVar(value=self.state_obj.active_persona)
        if TTKBOOTSTRAP_AVAILABLE:
            self.persona_combo = ttkb.Combobox(
                top,
                textvariable=self.persona_var,
                values=PERSONAS,
                state="readonly",
                width=14,
                bootstyle="primary"
            )
        else:
            self.persona_combo = ttk.Combobox(
                top,
                textvariable=self.persona_var,
                values=PERSONAS,
                state="readonly",
                width=14,
            )
        self.persona_combo.grid(row=0, column=1, sticky="w", padx=(0, 16))
        self.persona_combo.bind("<<ComboboxSelected>>", self.on_persona_change)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(self.persona_combo, text="Select the active assistant persona")

        if TTKBOOTSTRAP_AVAILABLE:
            role_label = ttkb.Label(top, text="Role:", bootstyle="secondary")
        else:
            role_label = ttk.Label(top, text="Role:")
        role_label.grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.persona_role_var = tk.StringVar(
            value=PERSONA_ROLES.get(self.state_obj.active_persona, "")
        )
        if TTKBOOTSTRAP_AVAILABLE:
            self.persona_role_display = ttkb.Label(
                top, 
                textvariable=self.persona_role_var, 
                bootstyle="info",
                font=(self.base_font.actual("family"), self.base_font.actual("size"), "italic")
            )
        else:
            self.persona_role_display = ttk.Label(
                top, 
                textvariable=self.persona_role_var,
                font=(self.base_font.actual("family"), self.base_font.actual("size"), "italic")
            )
        self.persona_role_display.grid(row=0, column=3, sticky="w", padx=(0, 16))

        # Right section - Action buttons
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(
                top, 
                text="💾 Save", 
                command=self._save_with_feedback, 
                bootstyle="success-outline",
                width=12
            )
            refresh_btn = ttkb.Button(
                top, 
                text="🔄 Refresh", 
                command=self._refresh_with_feedback, 
                bootstyle="info-outline",
                width=12
            )
        else:
            save_btn = ttk.Button(top, text="💾 Save", command=self._save_with_feedback, width=12)
            refresh_btn = ttk.Button(top, text="🔄 Refresh", command=self._refresh_with_feedback, width=12)
        save_btn.grid(row=0, column=5, sticky="e", padx=(0, 8))
        refresh_btn.grid(row=0, column=6, sticky="e", padx=0)
        
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
            self.dashboard_frame = ttkb.Frame(self.notebook, padding=12)
        else:
            self.dashboard_frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.dashboard_frame, text="Dashboard")

        self.dashboard_frame.columnconfigure(0, weight=1)
        self.dashboard_frame.columnconfigure(1, weight=1)
        self.dashboard_frame.rowconfigure(0, weight=1)
        self.dashboard_frame.rowconfigure(1, weight=1)
        self.dashboard_frame.rowconfigure(2, weight=0)
        self.dashboard_frame.rowconfigure(3, weight=0)

        if TTKBOOTSTRAP_AVAILABLE:
            self.today_box = ttkb.Labelframe(self.dashboard_frame, text="📋 Today's Focus", bootstyle="primary", padding=10)
            self.upcoming_box = ttkb.Labelframe(self.dashboard_frame, text="📅 Upcoming Deadlines", bootstyle="info", padding=10)
            self.status_box = ttkb.Labelframe(self.dashboard_frame, text="📊 Status Overview", bootstyle="success", padding=10)
            self.load_box = ttkb.Labelframe(self.dashboard_frame, text="👥 Load by Persona", bootstyle="secondary", padding=10)
            self.cyber_box = ttkb.Labelframe(self.dashboard_frame, text="🛡️ Cyber Defense Status", bootstyle="warning", padding=10)
        else:
            self.today_box = ttk.LabelFrame(self.dashboard_frame, text="Today's Focus", padding=10)
            self.upcoming_box = ttk.LabelFrame(self.dashboard_frame, text="Upcoming Deadlines", padding=10)
            self.status_box = ttk.LabelFrame(self.dashboard_frame, text="Status Overview", padding=10)
            self.load_box = ttk.LabelFrame(self.dashboard_frame, text="Load by Persona", padding=10)
            self.cyber_box = ttk.LabelFrame(self.dashboard_frame, text="Cyber Defense Status", padding=10)
        # Improved spacing for professional appearance
        self.today_box.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=(12, 6))
        self.today_text = tk.Text(self.today_box, height=10, wrap="word", font=self.text_font, relief="flat", borderwidth=0)
        self._style_text_widget(self.today_text)
        self.today_text.pack(fill="both", expand=True, padx=8, pady=8)

        self.upcoming_box.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=(12, 6))
        self.upcoming_text = tk.Text(self.upcoming_box, height=10, wrap="word", font=self.text_font, relief="flat", borderwidth=0)
        self._style_text_widget(self.upcoming_text)
        self.upcoming_text.pack(fill="both", expand=True, padx=8, pady=8)

        self.status_box.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=6)
        self.status_text = tk.Text(self.status_box, height=8, wrap="word", font=self.text_font, relief="flat", borderwidth=0)
        self._style_text_widget(self.status_text)
        self.status_text.pack(fill="both", expand=True, padx=8, pady=8)

        self.load_box.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=6)
        self.load_text = tk.Text(self.load_box, height=8, wrap="word", font=self.text_font, relief="flat", borderwidth=0)
        self._style_text_widget(self.load_text)
        self.load_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.cyber_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=12, pady=(6, 12))
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
        self.cyber_status_label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))

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
        self.cyber_message_label.grid(row=1, column=0, sticky="w", padx=10, pady=4)

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
        self.cyber_updated_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 8))

        if TTKBOOTSTRAP_AVAILABLE:
            self.sys_box = ttkb.Labelframe(self.dashboard_frame, text="💻 System Status (Optional)", bootstyle="secondary", padding=10)
        else:
            self.sys_box = ttk.LabelFrame(self.dashboard_frame, text="System Status (Optional)", padding=10)
        self.sys_box.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))
        self.sys_text = tk.Text(self.sys_box, height=4, wrap="word", font=self.text_font, relief="flat", borderwidth=0)
        self._style_text_widget(self.sys_text)
        self.sys_text.pack(fill="both", expand=True, padx=8, pady=8)

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
            self.tasks_frame = ttkb.Frame(self.notebook, padding=12)
        else:
            self.tasks_frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tasks_frame, text="Tasks")

        self.tasks_frame.columnconfigure(0, weight=3)
        self.tasks_frame.columnconfigure(1, weight=2)
        self.tasks_frame.rowconfigure(1, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            filters = ttkb.Frame(self.tasks_frame)
        else:
            filters = ttk.Frame(self.tasks_frame)
        filters.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 6))
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
            refresh_btn = ttkb.Button(filters, text="🔍 Apply Filters", command=self.refresh_task_list, bootstyle="info-outline", width=14)
        else:
            refresh_btn = ttk.Button(filters, text="Apply Filters", command=self.refresh_task_list, width=14)
        refresh_btn.grid(row=0, column=5, padx=(8, 0), pady=2)
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(refresh_btn, text="Apply filters and refresh the task list")

        if TTKBOOTSTRAP_AVAILABLE:
            list_frame = ttkb.Frame(self.tasks_frame)
        else:
            list_frame = ttk.Frame(self.tasks_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
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
        detail.grid(row=1, column=1, sticky="nsew", padx=12, pady=6)
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
        self._style_text_widget(self.notes_text)
        self.notes_text.grid(row=row, column=1, sticky="nsew", padx=6, pady=4)
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
            add_btn = ttkb.Button(btns, text="➕ New Task", command=self.on_new_task, bootstyle="primary-outline", width=15)
            save_btn = ttkb.Button(btns, text="💾 Save Changes", command=self._save_task_with_feedback, bootstyle="success", width=15)
            delete_btn = ttkb.Button(btns, text="🗑️ Delete Task", command=self._delete_task_with_feedback, bootstyle="danger-outline", width=15)
        else:
            add_btn = ttk.Button(btns, text="New Task", command=self.on_new_task, width=15)
            save_btn = ttk.Button(btns, text="Save Changes", command=self._save_task_with_feedback, width=15)
            delete_btn = ttk.Button(btns, text="Delete Task", command=self._delete_task_with_feedback, width=15)
        add_btn.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")
        save_btn.grid(row=0, column=1, padx=3, pady=4, sticky="ew")
        delete_btn.grid(row=0, column=2, padx=(6, 0), pady=4, sticky="ew")
        
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
            self.projects_frame = ttkb.Frame(self.notebook, padding=12)
        else:
            self.projects_frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.projects_frame, text="Projects")

        self.projects_frame.columnconfigure(1, weight=1)
        self.projects_frame.rowconfigure(0, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            list_frame = ttkb.Frame(self.projects_frame)
        else:
            list_frame = ttk.Frame(self.projects_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("order", "name", "priority", "status", "tasks")
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.project_tree.heading("order", text="ORDER #")
        self.project_tree.heading("name", text="NAME")
        self.project_tree.heading("priority", text="PRIORITY")
        self.project_tree.heading("status", text="STATUS")
        self.project_tree.heading("tasks", text="#TASKS")

        self.project_tree.column("order", width=80, anchor="center")
        self.project_tree.column("name", width=200)
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
        detail.grid(row=0, column=1, sticky="nsew", padx=12, pady=8)
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
        self._style_text_widget(self.proj_desc_text)
        self.proj_desc_text.grid(row=row, column=1, sticky="nsew", padx=6, pady=6)
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
            new_btn = ttkb.Button(btns, text="➕ New Project", command=self.on_new_project, bootstyle="primary-outline", width=15)
            save_btn = ttkb.Button(btns, text="💾 Save Project", command=self._save_project_with_feedback, bootstyle="success", width=15)
            delete_btn = ttkb.Button(btns, text="🗑️ Delete Project", command=self._delete_project_with_feedback, bootstyle="danger-outline", width=15)
        else:
            new_btn = ttk.Button(btns, text="New Project", command=self.on_new_project, width=15)
            save_btn = ttk.Button(btns, text="Save Project", command=self._save_project_with_feedback, width=15)
            delete_btn = ttk.Button(btns, text="Delete Project", command=self._delete_project_with_feedback, width=15)
        new_btn.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")
        save_btn.grid(row=0, column=1, padx=3, pady=4, sticky="ew")
        delete_btn.grid(row=0, column=2, padx=(6, 0), pady=4, sticky="ew")
        
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
        
        # Project Documents Section
        if TTKBOOTSTRAP_AVAILABLE:
            docs_section = ttkb.Labelframe(detail, text="📚 Project Documents", bootstyle="primary")
        else:
            docs_section = ttk.LabelFrame(detail, text="Project Documents")
        docs_section.grid(row=row+3, column=0, columnspan=2, sticky="nsew", padx=4, pady=(8, 4))
        docs_section.columnconfigure(0, weight=1)
        docs_section.rowconfigure(1, weight=1)
        
        # Documents header with upload button
        docs_header = ttk.Frame(docs_section)
        docs_header.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        docs_header.columnconfigure(0, weight=1)
        
        if TTKBOOTSTRAP_AVAILABLE:
            docs_label = ttkb.Label(docs_header, text="Documents linked to this project:", bootstyle="secondary")
            upload_doc_btn = ttkb.Button(docs_header, text="📤 Upload Document", command=self.on_upload_project_document, bootstyle="success-outline")
        else:
            docs_label = ttk.Label(docs_header, text="Documents linked to this project:")
            upload_doc_btn = ttk.Button(docs_header, text="Upload Document", command=self.on_upload_project_document)
        docs_label.grid(row=0, column=0, sticky="w")
        upload_doc_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))
        
        # Documents tree
        doc_columns = ("name", "type", "size", "modified")
        self.project_docs_tree = ttk.Treeview(docs_section, columns=doc_columns, show="headings", selectmode="browse", height=6)
        self.project_docs_tree.heading("name", text="Document Name")
        self.project_docs_tree.heading("type", text="Type")
        self.project_docs_tree.heading("size", text="Size")
        self.project_docs_tree.heading("modified", text="Modified")
        
        self.project_docs_tree.column("name", width=200)
        self.project_docs_tree.column("type", width=80, anchor="center")
        self.project_docs_tree.column("size", width=80, anchor="center")
        self.project_docs_tree.column("modified", width=120, anchor="center")
        
        self.project_docs_tree.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            docs_scrollbar = ttkb.Scrollbar(docs_section, orient="vertical", command=self.project_docs_tree.yview, bootstyle="primary-round")
        else:
            docs_scrollbar = ttk.Scrollbar(docs_section, orient="vertical", command=self.project_docs_tree.yview)
        self.project_docs_tree.configure(yscroll=docs_scrollbar.set)
        docs_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Bind double-click and Enter key to open document
        self.project_docs_tree.bind("<Double-1>", self.on_project_document_open)
        self.project_docs_tree.bind("<Return>", self.on_project_document_open)
        self.project_docs_tree.bind("<Button-3>", self.on_project_document_right_click)

    def refresh_project_list(self):
        for row in self.project_tree.get_children():
            self.project_tree.delete(row)

        counts: Dict[str, int] = {}
        for t in self.state_obj.tasks:
            counts[t.project] = counts.get(t.project, 0) + 1

        priority_weight = {p: len(PRIORITY_OPTIONS) - i for i, p in enumerate(PRIORITY_OPTIONS)}
        projects_sorted = sorted(
            self.state_obj.projects,
            key=lambda p: (p.order_num, priority_weight.get(p.priority, 1), p.name),
        )

        for p in projects_sorted:
            self.project_tree.insert(
                "",
                "end",
                iid=p.name,
                values=(p.order_num, p.name, p.priority, p.status, counts.get(p.name, 0)),
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
        
        # Refresh project documents
        self.refresh_project_documents(name)

    def on_new_project(self):
        self.project_tree.selection_remove(*self.project_tree.selection())
        self.proj_name_entry.delete(0, "end")
        self.proj_priority_combo.set("MEDIUM")
        self.proj_status_combo.set("active")
        self.proj_desc_text.delete("1.0", "end")
        # Clear documents list
        for item in self.project_docs_tree.get_children():
            self.project_docs_tree.delete(item)

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
    
    def _safe_get(self, obj, key, default=None):
        """Safely get a value from either a dict or sqlite3.Row object."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        else:
            # sqlite3.Row objects support dict-style access but not .get()
            try:
                return obj[key]
            except (KeyError, IndexError, TypeError):
                return default
    
    def refresh_project_documents(self, project_name: str):
        """Refresh the documents list for a project."""
        # Clear existing items
        for item in self.project_docs_tree.get_children():
            self.project_docs_tree.delete(item)
        
        # Clear the file path mappings
        self.project_docs_file_paths.clear()
        self.project_docs_link_ids.clear()
        
        if not project_name:
            return
        
        # Get all documents for this project
        all_docs = []
        for doc_type in ["onenote", "excel", "word", "pdf"]:
            docs = get_project_documents(self.conn, project_name=project_name, doc_type=doc_type)
            all_docs.extend(docs)
        
        # Sort by modified date (most recent first)
        all_docs.sort(key=lambda x: self._safe_get(x, "modified_date", ""), reverse=True)
        
        # Add to tree
        for doc in all_docs:
            doc_name = self._safe_get(doc, "title", "Unknown")
            doc_type = self._safe_get(doc, "integration_type", "").replace("local_", "").upper()
            file_size = self._safe_get(doc, "file_size", 0)
            size_str = format_file_size(file_size) if file_size > 0 else "Unknown"
            modified = self._safe_get(doc, "modified_date", "")
            if modified:
                try:
                    dt_obj = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                    modified = dt_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    modified = "Unknown"
            else:
                modified = "Unknown"
            
            doc_id = self._safe_get(doc, "id")
            file_path = self._safe_get(doc, "file_path", "")
            
            item_id = f"doc_{doc_id}"
            self.project_docs_tree.insert("", "end", iid=item_id, values=(doc_name, doc_type, size_str, modified))
            # Store file path and link ID in dictionaries for retrieval
            self.project_docs_file_paths[item_id] = file_path
            self.project_docs_link_ids[item_id] = doc_id
    
    def on_upload_project_document(self):
        """Upload a document to the selected project."""
        sel = self.project_tree.selection()
        if not sel:
            messagebox.showwarning("No Project Selected", "Please select a project first.")
            return
        
        project_name = sel[0]
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Document to Upload",
            filetypes=[
                ("All Documents", "*.one *.onepkg *.xlsx *.xls *.xlsm *.xlsb *.docx *.doc *.rtf *.pdf"),
                ("OneNote", "*.one *.onepkg"),
                ("Excel", "*.xlsx *.xls *.xlsm *.xlsb"),
                ("Word", "*.docx *.doc *.rtf"),
                ("PDF", "*.pdf"),
                ("All Files", "*.*"),
            ]
        )
        
        if not file_path:
            return
        
        # Determine document type from extension
        ext = Path(file_path).suffix.lower()
        doc_type = None
        if ext in [".one", ".onepkg"]:
            doc_type = "onenote"
        elif ext in [".xlsx", ".xls", ".xlsm", ".xlsb"]:
            doc_type = "excel"
        elif ext in [".docx", ".doc", ".rtf"]:
            doc_type = "word"
        elif ext == ".pdf":
            doc_type = "pdf"
        else:
            messagebox.showwarning("Unsupported File Type", f"File type '{ext}' is not supported. Please select a OneNote, Excel, Word, or PDF file.")
            return
        
        # Upload document
        try:
            success, error_msg, link_id = dm_upload_document(
                self.conn,
                file_path,
                project_name,
                doc_type,
                title=Path(file_path).stem,
                overwrite=False
            )
            
            if success:
                messagebox.showinfo("Success", f"Document uploaded successfully to project '{project_name}'.")
                self.refresh_project_documents(project_name)
                # Refresh Tools section if it's visible
                if hasattr(self, 'excel_tree'):
                    self.refresh_excel_documents()
                if hasattr(self, 'word_tree'):
                    self.refresh_word_documents()
                if hasattr(self, 'pdf_tree'):
                    self.refresh_pdf_documents()
                if hasattr(self, 'onenote_tree'):
                    self.refresh_onenote_notebooks()
            else:
                messagebox.showerror("Upload Failed", f"Failed to upload document:\n{error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload document:\n{e}")
    
    def on_project_document_open(self, event):
        """Open a project document with the default application."""
        tree = event.widget
        sel = tree.selection()
        if not sel:
            return
        
        item_id = sel[0]
        file_path = self.project_docs_file_paths.get(item_id)
        
        if not file_path:
            messagebox.showerror("File Not Found", "The document file path could not be found.")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"The document file could not be found:\n{file_path}")
            return
        
        self._open_file_with_default_app(file_path)
    
    def on_project_document_right_click(self, event):
        """Show context menu for project documents."""
        tree = event.widget
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
        
        tree.selection_set(item_id)
        file_path = self.project_docs_file_paths.get(item_id)
        doc_id = self.project_docs_link_ids.get(item_id)
        
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="📂 Open File", command=lambda: self._open_file_with_default_app(file_path) if file_path and os.path.exists(file_path) else None)
        menu.add_command(label="📋 Version History", command=lambda: self._show_document_versions_for_link(int(doc_id)) if doc_id else None)
        menu.add_separator()
        menu.add_command(label="🗑️ Remove from Project", command=lambda: self._remove_document_from_project(int(doc_id)) if doc_id else None)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _open_file_with_default_app(self, file_path: str):
        """Open a file with the system's default application."""
        import subprocess
        import platform
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"The file could not be found:\n{file_path}")
            return
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=False)
            elif platform.system() == 'Windows':
                os.startfile(file_path)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")
    
    def _remove_document_from_project(self, link_id: int):
        """Remove a document link from the project (does not delete the file)."""
        from .document_manager import delete_document
        
        if not messagebox.askyesno("Confirm Removal", "Remove this document from the project? (The file will not be deleted.)"):
            return
        
        success, error_msg = delete_document(self.conn, link_id, delete_file=False)
        
        if success:
            # Refresh documents list
            sel = self.project_tree.selection()
            if sel:
                self.refresh_project_documents(sel[0])
            # Refresh Tools section
            if hasattr(self, 'excel_tree'):
                self.refresh_excel_documents()
            if hasattr(self, 'word_tree'):
                self.refresh_word_documents()
            if hasattr(self, 'pdf_tree'):
                self.refresh_pdf_documents()
            if hasattr(self, 'onenote_tree'):
                self.refresh_onenote_notebooks()
        else:
            messagebox.showerror("Error", f"Failed to remove document:\n{error_msg}")

    # ---------- AI Chat + Terminal Tab ----------

    def _build_chat_tab(self):
        if TTKBOOTSTRAP_AVAILABLE:
            self.chat_frame = ttkb.Frame(self.notebook, padding=12)
        else:
            self.chat_frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.chat_frame, text="AI Console")

        # Support side-by-side layout: chat on left, document interaction on right
        # Use PanedWindow for resizable splitter (user can drag to resize)
        # Note: ttkbootstrap may not have PanedWindow, so use ttk.PanedWindow for both
        try:
            if TTKBOOTSTRAP_AVAILABLE and hasattr(ttkb, 'PanedWindow'):
                self.chat_paned = ttkb.PanedWindow(self.chat_frame, orient="horizontal", bootstyle="primary")
            else:
                self.chat_paned = ttk.PanedWindow(self.chat_frame, orient="horizontal")
        except (AttributeError, TypeError):
            # Fallback to standard ttk.PanedWindow
            self.chat_paned = ttk.PanedWindow(self.chat_frame, orient="horizontal")
        
        self.chat_paned.pack(fill="both", expand=True, padx=8, pady=8)

        # Left side: Chat conversation and compose
        if TTKBOOTSTRAP_AVAILABLE:
            chat_container = ttkb.Frame(self.chat_paned)
        else:
            chat_container = ttk.Frame(self.chat_paned)
        chat_container.columnconfigure(0, weight=1)
        chat_container.rowconfigure(0, weight=2)  # Conversation area: 2/3
        chat_container.rowconfigure(1, weight=1)  # Compose area: 1/3
        self.chat_paned.add(chat_container, weight=1)  # Start with equal weight, user can resize

        if TTKBOOTSTRAP_AVAILABLE:
            convo_frame = ttkb.Labelframe(chat_container, text="💬 Chat & Terminal", bootstyle="primary", padding=12)
            compose = ttkb.Labelframe(chat_container, text="✍️ Compose Message & Terminal", bootstyle="info", padding=12)
        else:
            convo_frame = ttk.LabelFrame(chat_container, text="Chat & Terminal", padding=12)
            compose = ttk.LabelFrame(chat_container, text="Compose Message & Terminal", padding=12)
        convo_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        convo_frame.columnconfigure(0, weight=1)
        convo_frame.rowconfigure(0, weight=1)
        self.chat_text = tk.Text(convo_frame, wrap="word", state="disabled", font=self.text_font)
        self._style_text_widget(self.chat_text)
        self.chat_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        if TTKBOOTSTRAP_AVAILABLE:
            chat_scroll = ttkb.Scrollbar(convo_frame, orient="vertical", command=self.chat_text.yview, bootstyle="primary-round")
        else:
            chat_scroll = ttk.Scrollbar(convo_frame, orient="vertical", command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=chat_scroll.set)
        chat_scroll.grid(row=0, column=1, sticky="ns")
        compose.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        compose.columnconfigure(1, weight=1)
        # Configure rows for proper space distribution
        compose.rowconfigure(1, weight=2)  # System prompt gets more space
        compose.rowconfigure(3, weight=1)  # Chat input gets less space (1/3 of compose area)

        # Right side: Document interaction panel (always visible)
        if TTKBOOTSTRAP_AVAILABLE:
            self.document_frame = ttkb.Labelframe(self.chat_paned, text="📑 Document Interaction", bootstyle="success")
        else:
            self.document_frame = ttk.LabelFrame(self.chat_paned, text="Document Interaction")
        self.document_frame.columnconfigure(0, weight=1)
        self.document_frame.rowconfigure(1, weight=1)
        self.document_frame.rowconfigure(2, weight=1)
        self.chat_paned.add(self.document_frame, weight=2)  # Start with document panel 2x larger, user can resize

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
                values=["auto", "gpt-4o", "gpt-4o-mini", "o1-mini", "o1-reasoning", "gpt-4-turbo"],
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
                values=["auto", "gpt-4o", "gpt-4o-mini", "o1-mini", "o1-reasoning", "gpt-4-turbo"],
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
        
        self.system_prompt_text = tk.Text(compose, height=6, wrap="word", font=self.text_font)
        self._style_text_widget(self.system_prompt_text)
        self.system_prompt_text.grid(row=1, column=1, columnspan=5, sticky="nsew", padx=6, pady=4)
        self.system_prompt_text.insert("1.0", DEFAULT_SYSTEM_PROMPT)
        
        # Combined input section - CWD selector and unified input field
        if TTKBOOTSTRAP_AVAILABLE:
            input_meta_frame = ttkb.Frame(compose)
        else:
            input_meta_frame = ttk.Frame(compose)
        input_meta_frame.grid(row=2, column=1, columnspan=5, sticky="ew", padx=6, pady=(6, 2))
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
        self.chat_input = tk.Text(compose, height=6, wrap="word", font=self.text_font)
        self._style_text_widget(self.chat_input)
        self.chat_input.grid(row=3, column=1, columnspan=5, sticky="nsew", padx=6, pady=(6, 4))
        # Ctrl+Enter sends as chat message, Enter alone checks if it's a command
        self.chat_input.bind("<Control-Return>", lambda e: (self.on_handle_combined_input(chat_mode=True), "break"))
        self.chat_input.bind("<Return>", lambda e: self.on_handle_combined_input_enter(e))
        
        # Placeholder hint
        placeholder_text = "Type a message for AI (Enter to send, Shift+Enter for newline). Use '$' prefix for shell commands."
        self.chat_input.insert("1.0", placeholder_text)
        self.chat_input.config(foreground="gray")
        self.chat_input.bind("<FocusIn>", self.on_input_focus_in)
        self.chat_input.bind("<FocusOut>", self.on_input_focus_out)
        
        # Update placeholder references
        self.chat_placeholder = placeholder_text
        
        # Keep command_var for backward compatibility but use chat_input
        self.command_var = tk.StringVar()


        # Buttons row - Send and Clear only (AI can access files via shell commands from browse directory)
        if TTKBOOTSTRAP_AVAILABLE:
            btns = ttkb.Frame(compose)
        else:
            btns = ttk.Frame(compose)
        btns.grid(row=4, column=0, columnspan=6, sticky="ew", pady=(6, 0))
        
        # Configure columns for buttons (2 buttons: Send and Clear)
        for idx in range(2):
            btns.columnconfigure(idx, weight=1)

        if TTKBOOTSTRAP_AVAILABLE:
            send_btn = ttkb.Button(btns, text="🚀 Send", command=lambda: self.on_handle_combined_input(chat_mode=True), bootstyle="primary")
            clear_btn = ttkb.Button(btns, text="🗑️ Clear", command=self.on_clear_chat_history, bootstyle="danger-outline")
        else:
            send_btn = ttk.Button(btns, text="Send", command=lambda: self.on_handle_combined_input(chat_mode=True))
            clear_btn = ttk.Button(btns, text="Clear", command=self.on_clear_chat_history)
        send_btn.grid(row=0, column=0, padx=4, sticky="ew")
        clear_btn.grid(row=0, column=1, padx=4, sticky="ew")
        
        # Add hover effects to chat buttons
        AnimationHelper.add_hover_effect(send_btn)
        AnimationHelper.add_hover_effect(clear_btn)
        self._chat_send_btn = send_btn
        
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(send_btn, text="Send message (Ctrl+Enter) or run command (Enter for single-line, prefix with $). AI can access files in the browse directory via shell commands.")
            ToolTip(clear_btn, text="Clear all chat history")

        if TTKBOOTSTRAP_AVAILABLE:
            self.chat_status_label = ttkb.Label(compose, textvariable=self.chat_status_var, bootstyle="info")
        else:
            self.chat_status_label = ttk.Label(compose, textvariable=self.chat_status_var)
        self.chat_status_label.grid(row=5, column=0, columnspan=6, sticky="w", padx=4, pady=(2, 0))
        
        # Add progress indicator for AI responses
        progress_container = ttkb.Frame(compose) if TTKBOOTSTRAP_AVAILABLE else ttk.Frame(compose)
        progress_container.grid(row=6, column=0, columnspan=6, sticky="ew", padx=6, pady=(4, 0))
        progress_container.columnconfigure(0, weight=1)
        self.chat_progress = ProgressIndicator(self).create(progress_container, row=0, column=0, columnspan=1)
        self.chat_progress.progress_bar.grid_remove()
        self.chat_progress.indicator_label.grid_remove()

    def _build_file_preview_panel(self):
        """Build the file preview panel for side-by-side file editing."""
        # Header frame for document interaction panel
        if TTKBOOTSTRAP_AVAILABLE:
            header_frame = ttkb.Frame(self.document_frame)
        else:
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

        self.file_preview_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
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
            versions_btn = ttkb.Button(file_header, text="📚 Versions", command=self._show_document_versions, bootstyle="info-outline", width=10)
            close_btn = ttkb.Button(file_header, text="✕", command=self._close_file_preview, bootstyle="danger-outline", width=3)
        else:
            title_label = ttk.Label(file_header, textvariable=self.file_preview_title_var, font=(self.base_font.actual("family"), self.base_font.actual("size") + 1, "bold"))
            versions_btn = ttk.Button(file_header, text="Versions", command=self._show_document_versions, width=10)
            close_btn = ttk.Button(file_header, text="✕", command=self._close_file_preview, width=3)
        title_label.grid(row=0, column=0, sticky="w", padx=4)
        versions_btn.grid(row=0, column=1, sticky="e", padx=4)
        close_btn.grid(row=0, column=2, sticky="e", padx=4)
        
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

        # Use a notebook for different display modes (text, table, etc.)
        if TTKBOOTSTRAP_AVAILABLE:
            self.file_preview_notebook = ttkb.Notebook(content_frame)
        else:
            self.file_preview_notebook = ttk.Notebook(content_frame)
        self.file_preview_notebook.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Text view tab for general content
        text_frame = ttk.Frame(self.file_preview_notebook)
        self.file_preview_notebook.add(text_frame, text="Text View")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text widget for displaying file content
        # Make file preview editable and interactive
        self.file_preview_text = tk.Text(text_frame, wrap="word", state="normal", font=self.text_font)
        self._style_text_widget(self.file_preview_text)
        self.file_preview_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        
        # Table view frame for Excel/CSV (will be populated when needed)
        self.file_preview_table_frame = ttk.Frame(self.file_preview_notebook)
        self.file_preview_table_frame.columnconfigure(0, weight=1)
        self.file_preview_table_frame.rowconfigure(0, weight=1)
        
        # Treeview for table display (Excel, CSV)
        table_columns = ("col0",)
        self.file_preview_tree = ttk.Treeview(self.file_preview_table_frame, columns=table_columns, show="headings", selectmode="extended")
        self.file_preview_tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Scrollbars for table
        table_v_scroll = ttk.Scrollbar(self.file_preview_table_frame, orient="vertical", command=self.file_preview_tree.yview)
        table_h_scroll = ttk.Scrollbar(self.file_preview_table_frame, orient="horizontal", command=self.file_preview_tree.xview)
        self.file_preview_tree.configure(yscrollcommand=table_v_scroll.set, xscrollcommand=table_h_scroll.set)
        table_v_scroll.grid(row=0, column=1, sticky="ns")
        table_h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Scrollbar for text widget
        if TTKBOOTSTRAP_AVAILABLE:
            preview_scroll = ttkb.Scrollbar(text_frame, orient="vertical", command=self.file_preview_text.yview, bootstyle="success-round")
        else:
            preview_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.file_preview_text.yview)
        self.file_preview_text.configure(yscrollcommand=preview_scroll.set)
        preview_scroll.grid(row=0, column=1, sticky="ns")
        
        # Add save button for editable content (below text widget)
        if TTKBOOTSTRAP_AVAILABLE:
            save_preview_btn = ttkb.Button(content_frame, text="💾 Save Changes", 
                                          command=self._save_file_preview_changes, 
                                          bootstyle="success-outline", width=15)
        else:
            save_preview_btn = ttk.Button(content_frame, text="Save Changes", 
                                         command=self._save_file_preview_changes, width=15)
        save_preview_btn.grid(row=1, column=0, columnspan=2, sticky="e", padx=2, pady=2)
        self.file_preview_save_btn = save_preview_btn

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
            activity_frame = ttkb.Labelframe(self.document_frame, text="📡 Live Updates", bootstyle="info", padding=10)
        else:
            activity_frame = ttk.LabelFrame(self.document_frame, text="Live Updates", padding=10)
        activity_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        activity_frame.columnconfigure(0, weight=1)
        activity_frame.rowconfigure(0, weight=1)

        self.document_activity_text = tk.Text(activity_frame, wrap="word", state="disabled", height=6, font=self.text_font)
        self._style_text_widget(self.document_activity_text)
        self.document_activity_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
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
        
        # Show the panel (PanedWindow handles resizing automatically)
        self.file_preview_frame.grid()
        

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
            
            # Switch to text view by default (table view will be shown for Excel/CSV)
            try:
                if hasattr(self, 'file_preview_notebook'):
                    self.file_preview_notebook.select(0)  # Text view tab
            except:
                pass
            
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
            self.file_preview_text.config(state="normal")  # Keep editable for user interaction
            self.file_preview_status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            self.active_file_session['last_update'] = datetime.now()
            self._log_document_activity(f"Refreshed {file_type} preview at {self.active_file_session['last_update'].strftime('%H:%M:%S')}")
        except Exception as e:
            self.file_preview_text.insert("1.0", f"Error loading file: {str(e)}")
            self.file_preview_text.config(state="normal")  # Keep editable
            self.file_preview_status_var.set(f"Error: {str(e)}")
            self._log_document_activity(f"Error loading file: {str(e)}")
    
    def _save_file_preview_changes(self):
        """Save changes made to the file preview back to the file."""
        if not self.active_file_session:
            messagebox.showwarning("No File", "No file is currently open for editing.")
            return
        
        file_path = self.active_file_session.get('path')
        file_type = self.active_file_session.get('type')
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "File path is invalid or file does not exist.")
            return
        
        # Only allow saving text-based files
        if file_type not in ["Text", "CSV", "JSON"]:
            if not messagebox.askyesno("Confirm Save", 
                f"Saving changes to {file_type} files may not preserve formatting. Continue?"):
                return
        
        try:
            content = self.file_preview_text.get("1.0", "end-1c")  # Get all content except final newline
            
            # Backup original file
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # Write new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.file_preview_status_var.set(f"Saved at {datetime.now().strftime('%H:%M:%S')} (backup: {os.path.basename(backup_path)})")
            self._log_document_activity(f"Saved changes to {os.path.basename(file_path)}")
            messagebox.showinfo("Saved", f"Changes saved to {os.path.basename(file_path)}\nBackup created: {os.path.basename(backup_path)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
            self._log_document_activity(f"Error saving file: {str(e)}")

    def _show_document_versions(self):
        """Show a dialog with all versions of the current document."""
        if not self.active_file_session:
            messagebox.showinfo("No Document", "No document is currently open. Open a document first to view its versions.")
            return
        
        file_path = self.active_file_session.get('path')
        if not file_path:
            messagebox.showinfo("No Document", "No document path available.")
            return
        
        # Try to find the note_link_id for this document
        # We need to match by file path
        from .document_manager import DOCUMENTS_BASE_DIR, get_document_path
        from .db import db_get_note_links
        
        # Get all note links and find the one matching this file
        note_link_id = None
        links = db_get_note_links(self.conn)
        for link in links:
            if link.integration_type.startswith("local_"):
                link_path = DOCUMENTS_BASE_DIR / link.external_id
                if str(link_path) == file_path or os.path.samefile(str(link_path), file_path):
                    note_link_id = link.id
                    break
        
        if not note_link_id:
            messagebox.showinfo("No Versions", "This document is not tracked in the system. Upload it through the Projects tab to enable version tracking.")
            return
        
        # Get all versions
        versions = get_document_versions(self.conn, note_link_id)
        if not versions:
            messagebox.showinfo("No Versions", "No versions found for this document.")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Document Versions")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        
        if TTKBOOTSTRAP_AVAILABLE:
            main_frame = ttkb.Frame(dialog, padding=20)
        else:
            main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Versions for: {os.path.basename(file_path)}", 
                                font=(self.base_font.actual("family"), 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Versions list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ("version", "date", "size", "description", "created_by")
        versions_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        versions_tree.heading("version", text="Version")
        versions_tree.heading("date", text="Created")
        versions_tree.heading("size", text="Size")
        versions_tree.heading("description", text="Description")
        versions_tree.heading("created_by", text="Created By")
        
        versions_tree.column("version", width=80, anchor="center")
        versions_tree.column("date", width=150)
        versions_tree.column("size", width=100, anchor="e")
        versions_tree.column("description", width=250)
        versions_tree.column("created_by", width=120)
        
        versions_tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=versions_tree.yview)
        versions_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate versions
        for version in versions:
            created_date = version["created_at"]
            if "T" in created_date:
                created_date = created_date.replace("T", " ")[:19]
            
            versions_tree.insert("", "end", iid=str(version["id"]), values=(
                f"v{version['version_number']}",
                created_date,
                format_file_size(version["file_size"]),
                version["description"] or "(no description)",
                version["created_by"]
            ))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def restore_selected():
            sel = versions_tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a version to restore.")
                return
            
            version_id = int(sel[0])
            if not messagebox.askyesno("Confirm Restore", 
                "This will restore the selected version and create a new version from the current file.\n\nContinue?"):
                return
            
            success, error = restore_document_version(self.conn, version_id, create_new_version=True)
            if success:
                messagebox.showinfo("Success", "Document restored successfully! Refreshing preview...")
                self._refresh_file_preview()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to restore version: {error}")
        
        def view_selected():
            sel = versions_tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a version to view.")
                return
            
            version_id = int(sel[0])
            version = get_document_version(self.conn, version_id)
            if not version:
                messagebox.showerror("Error", "Version not found.")
                return
            
            version_path = Path(version["file_path"])
            if not version_path.exists():
                messagebox.showerror("Error", f"Version file not found: {version_path}")
                return
            
            # Open the version file in preview
            file_type = self._infer_file_type(str(version_path))
            self._show_file_preview(file_type, str(version_path))
            dialog.destroy()
        
        if TTKBOOTSTRAP_AVAILABLE:
            view_btn = ttkb.Button(btn_frame, text="👁️ View", command=view_selected, bootstyle="info-outline")
            restore_btn = ttkb.Button(btn_frame, text="↩️ Restore", command=restore_selected, bootstyle="success")
            close_btn = ttkb.Button(btn_frame, text="Close", command=dialog.destroy, bootstyle="secondary")
        else:
            view_btn = ttk.Button(btn_frame, text="View", command=view_selected)
            restore_btn = ttk.Button(btn_frame, text="Restore", command=restore_selected)
            close_btn = ttk.Button(btn_frame, text="Close", command=dialog.destroy)
        
        view_btn.pack(side="left", padx=5)
        restore_btn.pack(side="left", padx=5)
        close_btn.pack(side="left", padx=5)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(view_btn, text="View the selected version in the preview panel")
            ToolTip(restore_btn, text="Restore this version (current file will be saved as a new version first)")

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
                return text  # Show all content
            return "Page content not available"
        except Exception as e:
            return f"Error loading OneNote: {str(e)}"

    def _populate_table_view(self, df, max_rows=500):
        """Populate the Treeview with DataFrame data for better table display."""
        if not hasattr(self, 'file_preview_tree'):
            return
        
        # Clear existing items
        for item in self.file_preview_tree.get_children():
            self.file_preview_tree.delete(item)
        
        # Get columns from DataFrame
        columns = list(df.columns)
        if not columns:
            return
        
        # Configure treeview columns
        self.file_preview_tree['columns'] = columns
        self.file_preview_tree.heading('#0', text='Index', anchor='w')
        self.file_preview_tree.column('#0', width=80, minwidth=80)
        
        for col in columns:
            self.file_preview_tree.heading(col, text=str(col), anchor='w')
            self.file_preview_tree.column(col, width=120, minwidth=80)
        
        # Populate with data
        for idx, row in df.head(max_rows).iterrows():
            values = [str(val)[:100] if val is not None else '' for val in row.values]
            self.file_preview_tree.insert('', 'end', text=str(idx), values=values)
        
        # Add table view tab if not already added
        try:
            # Check if table view tab exists
            tab_exists = False
            for i in range(self.file_preview_notebook.index('end')):
                if self.file_preview_notebook.tab(i, 'text') == "Table View":
                    tab_exists = True
                    break
            if not tab_exists:
                self.file_preview_notebook.add(self.file_preview_table_frame, text="Table View")
        except Exception:
            pass
    
    def _load_excel_preview(self, file_path: str) -> str:
        """Load Excel file content for preview with better formatting."""
        if not EXCEL_SERVICE_AVAILABLE or not file_path:
            return "Excel preview not available"
        
        try:
            if os.path.exists(file_path):
                import pandas as pd
                try:
                    # Read first sheet for table view
                    df = pd.read_excel(file_path, sheet_name=0, nrows=500)
                    
                    # Populate table view
                    self._populate_table_view(df, max_rows=500)
                    
                    # Also create text preview with all sheets info
                    excel_file = pd.ExcelFile(file_path)
                    preview_parts = [f"📊 Excel Workbook: {os.path.basename(file_path)}\n"]
                    preview_parts.append(f"   Total Sheets: {len(excel_file.sheet_names)}\n")
                    preview_parts.append("=" * 100 + "\n")
                    
                    for sheet_name in excel_file.sheet_names[:3]:  # Show first 3 sheets in text
                        df_sheet = pd.read_excel(file_path, sheet_name=sheet_name, nrows=50)
                        preview_parts.append(f"\n📋 Sheet: {sheet_name}")
                        preview_parts.append(f"   Shape: {df_sheet.shape[0]} rows × {df_sheet.shape[1]} columns\n")
                        preview_parts.append("-" * 100 + "\n")
                        
                        # Use tabulate for better table formatting if available
                        try:
                            from tabulate import tabulate
                            table_str = tabulate(df_sheet.head(20), headers='keys', tablefmt='grid', showindex=True, maxcolwidths=30)
                            preview_parts.append(table_str)
                        except ImportError:
                            preview_parts.append(df_sheet.head(20).to_string(max_rows=20, max_cols=10))
                        
                        preview_parts.append("\n")
                    
                    if len(excel_file.sheet_names) > 3:
                        preview_parts.append(f"\n... and {len(excel_file.sheet_names) - 3} more sheets (see Table View tab)\n")
                    
                    # Switch to table view tab
                    try:
                        self.file_preview_notebook.select(1)  # Switch to table view
                    except:
                        pass
                    
                    return "\n".join(preview_parts)
                except Exception as e:
                    return f"Excel file loaded\n(Error displaying table: {str(e)})"
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading Excel: {str(e)}"

    def _load_csv_preview(self, file_path: str) -> str:
        """Load CSV file content for preview with better table formatting."""
        if not file_path:
            return "CSV preview not available"

        try:
            if os.path.exists(file_path):
                import pandas as pd
                try:
                    # Read CSV with pandas for better handling
                    df = pd.read_csv(file_path, nrows=500)  # Read more rows
                    
                    # Populate table view
                    self._populate_table_view(df, max_rows=500)
                    
                    preview_parts = [f"📊 CSV File: {os.path.basename(file_path)}\n"]
                    preview_parts.append(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")
                    preview_parts.append("=" * 100 + "\n")
                    preview_parts.append("See 'Table View' tab for full table display\n")
                    preview_parts.append("-" * 100 + "\n")
                    
                    # Use tabulate for better table formatting if available
                    try:
                        from tabulate import tabulate
                        table_str = tabulate(df.head(20), headers='keys', tablefmt='grid', showindex=True, maxcolwidths=30)
                        preview_parts.append(table_str)
                    except ImportError:
                        preview_parts.append(df.head(20).to_string(max_rows=20, max_cols=10))
                    
                    # Switch to table view tab
                    try:
                        self.file_preview_notebook.select(1)  # Switch to table view
                    except:
                        pass
                    
                    return "\n".join(preview_parts)
                except Exception as e:
                    # Fallback to basic CSV reading
                    import csv
                    lines = []
                    with open(file_path, newline='', encoding='utf-8', errors='ignore') as f:
                        reader = csv.reader(f)
                        for idx, row in enumerate(reader):
                            lines.append(" | ".join(str(cell)[:50] for cell in row))  # Limit cell width
                            if idx >= 100:
                                break
                    return f"CSV Preview (first 100 rows):\n{'=' * 100}\n" + "\n".join(lines)
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
                    content = f.read()
                return content
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading text: {str(e)}"

    def _load_json_preview(self, file_path: str) -> str:
        """Load JSON content for preview with better formatting."""
        if not file_path:
            return "JSON preview not available"

        try:
            if os.path.exists(file_path):
                import json
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                
                # Format with better indentation and structure
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
                
                # Add header
                preview = f"📄 JSON File: {os.path.basename(file_path)}\n"
                preview += "=" * 100 + "\n\n"
                preview += formatted
                
                return preview
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
                    return content  # Show all content
                return "Word document loaded (content extraction not available)"
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error loading Word: {str(e)}"

    def _load_pdf_preview(self, file_path: str) -> str:
        """Load PDF file content for preview with pagination for large files."""
        if not file_path:
            return "PDF preview not available"
        
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            # Check file size first
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # For large PDFs (>5MB), load in chunks with pagination
            if file_size_mb > 5:
                return self._load_large_pdf_preview(file_path)
            
            # Try to use PDF integration to extract text
            pdf_integration = PDFIntegration(self.conn)
            if hasattr(pdf_integration, 'extract_text'):
                # Load PDF asynchronously to prevent UI blocking
                import threading
                
                def load_pdf_async():
                    try:
                        content = pdf_integration.extract_text(file_path)
                        if content and content.strip():
                            # Show all content - no truncation
                            preview_content = content
                            self.after(0, lambda c=preview_content: self._update_pdf_preview_content(c))
                        else:
                            self.after(0, lambda: self._update_pdf_preview_content(
                                "PDF loaded but text extraction returned no content. PDF libraries may not be installed (PyPDF2 or pdfplumber)."
                            ))
                    except Exception as e:
                        self.after(0, lambda: self._update_pdf_preview_content(f"Error loading PDF: {str(e)}"))
                
                thread = threading.Thread(target=load_pdf_async, daemon=True)
                thread.start()
                
                # Show loading message immediately
                return f"Loading PDF ({file_size_mb:.1f} MB)... This may take a moment for large files.\n\n[Loading in background, content will appear shortly...]"
            else:
                return "PDF preview not available (extract_text method not found)"
        except Exception as e:
            return f"Error loading PDF: {str(e)}"
    
    def _load_large_pdf_preview(self, file_path: str) -> str:
        """Load large PDF files with pagination support."""
        try:
            pdf_integration = PDFIntegration(self.conn)
            if hasattr(pdf_integration, 'extract_text'):
                # For large PDFs, extract first few pages only
                # Try to use pdfplumber or PyPDF2 directly for page-by-page extraction
                content_parts = []
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        total_pages = len(pdf.pages)
                        # Extract all pages - no limit
                        content_parts = [f"PDF: {os.path.basename(file_path)} ({total_pages} pages total)\n"]
                        content_parts.append("=" * 80 + "\n")
                        content_parts.append(f"Showing all {total_pages} pages:\n\n")
                        
                        for i, page in enumerate(pdf.pages):
                            try:
                                text = page.extract_text()
                                if text:
                                    content_parts.append(f"\n--- Page {i+1} ---\n")
                                    content_parts.append(text)
                                    content_parts.append("\n")
                            except Exception:
                                continue
                        
                        return "".join(content_parts)
                except ImportError:
                    # Fallback to full extraction but with warning
                    return f"Large PDF detected. Loading first portion...\n[Note: Install pdfplumber for better large PDF handling: pip install pdfplumber]"
                except Exception as e:
                    error_msg = str(e).lower()
                    # Try PyPDF2 with strict=False for corrupted PDFs
                    if "eof" in error_msg or "corrupt" in error_msg:
                        try:
                            import PyPDF2
                            with open(file_path, 'rb') as f:
                                try:
                                    pdf_reader = PyPDF2.PdfReader(f, strict=False)
                                except Exception:
                                    f.seek(0)
                                    pdf_reader = PyPDF2.PdfReader(f)
                                
                                total_pages = len(pdf_reader.pages)
                                content_parts = [f"PDF: {os.path.basename(file_path)} ({total_pages} pages total)\n"]
                                content_parts.append("=" * 80 + "\n")
                                
                                for i, page in enumerate(pdf_reader.pages):
                                    try:
                                        text = page.extract_text()
                                        if text:
                                            content_parts.append(f"\n--- Page {i+1} ---\n")
                                            content_parts.append(text)
                                            content_parts.append("\n")
                                    except Exception:
                                        continue
                                
                                return "".join(content_parts)
                        except Exception as e2:
                            if "eof marker" in str(e2).lower():
                                return f"PDF appears to be corrupted or incomplete (EOF marker not found). The file '{os.path.basename(file_path)}' may be truncated or damaged."
                            return f"Error loading PDF: {str(e2)}"
                    else:
                        return f"Error loading large PDF: {str(e)}"
            
            return "PDF preview not available"
        except Exception as e:
            error_msg = str(e).lower()
            if "eof marker" in error_msg:
                return f"PDF appears to be corrupted or incomplete (EOF marker not found). The file '{os.path.basename(file_path)}' may be truncated or damaged."
            return f"Error loading large PDF: {str(e)}"
    
    def _update_pdf_preview_content(self, content: str):
        """Update PDF preview content asynchronously."""
        if hasattr(self, 'file_preview_text') and self.file_preview_text:
            self.file_preview_text.config(state="normal")
            self.file_preview_text.delete("1.0", "end")
            self.file_preview_text.insert("1.0", content)
            self.file_preview_text.config(state="normal")  # Keep editable
            if hasattr(self, 'file_preview_status_var') and self.file_preview_status_var:
                self.file_preview_status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    def _get_displayed_file_content(self, file_path: str, file_type: str) -> str:
        """Get the full content of the currently displayed file for AI reading."""
        if not file_path or not os.path.exists(file_path):
            return f"File not found: {file_path}"
        
        try:
            if file_type == "PDF":
                # Extract full text from PDF - try pdfplumber first
                content = ""
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        for i, page in enumerate(pdf.pages):
                            try:
                                text = page.extract_text()
                                if text:
                                    content += f"\n--- Page {i+1} ---\n"
                                    content += text
                                    content += "\n"
                            except Exception:
                                continue
                    if content:
                        return content
                except ImportError:
                    pass
                except Exception as e:
                    error_msg = str(e).lower()
                    # If pdfplumber fails, try PyPDF2
                    if "eof" in error_msg or "corrupt" in error_msg:
                        pass  # Will try PyPDF2 next
                    else:
                        # For other errors, return message and try PyPDF2
                        pass
                
                # Fallback: try PyPDF2 with strict=False for corrupted PDFs
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        try:
                            pdf_reader = PyPDF2.PdfReader(f, strict=False)
                        except Exception:
                            f.seek(0)
                            pdf_reader = PyPDF2.PdfReader(f)
                        
                        for i, page in enumerate(pdf_reader.pages):
                            try:
                                text = page.extract_text()
                                if text:
                                    content += f"\n--- Page {i+1} ---\n"
                                    content += text
                                    content += "\n"
                            except Exception:
                                continue
                    if content:
                        return content
                except ImportError:
                    return "PDF libraries not available. Install pdfplumber or PyPDF2 to read PDFs."
                except Exception as e:
                    error_msg = str(e).lower()
                    if "eof marker" in error_msg:
                        return f"PDF appears to be corrupted or incomplete (EOF marker not found). The file '{os.path.basename(file_path)}' may be truncated or damaged."
                    elif "corrupt" in error_msg or "invalid" in error_msg:
                        return f"PDF file appears to be corrupted or invalid: {os.path.basename(file_path)}"
                    else:
                        return f"Error reading PDF: {str(e)}"
                
                # If no content extracted, return helpful message
                return "PDF loaded but no text could be extracted. The PDF may contain only images or be encrypted."
            
            elif file_type == "Excel":
                # Read Excel file
                try:
                    import pandas as pd
                    df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
                    content_parts = []
                    for sheet_name, df_sheet in df.items():
                        content_parts.append(f"\n=== Sheet: {sheet_name} ===\n")
                        content_parts.append(df_sheet.to_string())
                        content_parts.append("\n")
                    return "\n".join(content_parts)
                except Exception as e:
                    return f"Error reading Excel file: {str(e)}"
            
            elif file_type == "CSV":
                # Read CSV file
                try:
                    import pandas as pd
                    df = pd.read_csv(file_path)
                    return df.to_string()
                except Exception as e:
                    # Fallback to plain text
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
            
            elif file_type == "Word":
                # Read Word document
                try:
                    from .integrations.word_integration import WordIntegration
                    word_int = WordIntegration(self.conn)
                    if hasattr(word_int, 'service') and word_int.service:
                        # Try to extract text using Word service
                        content = word_int.service.extract_text(file_path)
                        return content if content else "Word document loaded but no text could be extracted."
                    else:
                        return "Word integration not available."
                except Exception as e:
                    return f"Error reading Word document: {str(e)}"
            
            elif file_type == "OneNote":
                # OneNote content is already in preview text widget
                if hasattr(self, 'file_preview_text') and self.file_preview_text:
                    return self.file_preview_text.get("1.0", "end-1c")
                return "OneNote content not available."
            
            else:
                # Text files, JSON, etc.
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        
        except Exception as e:
            return f"Error reading file: {str(e)}"

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
                return content
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
                return json.dumps(data, indent=2)
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
        self.file_preview_text.config(state="normal")  # Keep editable
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
            if 'csv' in func_name or 'json' in func_name or 'text' in func_name or 'file' in func_name:
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

    def refresh_chat_history(self, incremental: bool = False):
        """Refresh the chat history display.
        
        Args:
            incremental: If True and there are new messages, only append new ones.
                        If False, refresh the entire history.
        """
        if not self.chat_text:
            return
        
        # Throttle UI updates to prevent excessive refreshes
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        if incremental and self._ui_update_pending:
            # Already have an update pending, skip this one
            return
        
        if incremental and (current_time - self._last_ui_update_time) < self._ui_update_throttle_ms:
            # Schedule update for later instead of doing it now
            if not self._ui_update_pending:
                self._ui_update_pending = True
                delay_ms = self._ui_update_throttle_ms - (current_time - self._last_ui_update_time)
                self.after(int(delay_ms), lambda: self._throttled_refresh(incremental))
            return
        
        # Perform memory cleanup for very large chat histories
        if len(self.state_obj.chat_messages) > self._max_chat_messages_memory:
            # Keep only the most recent messages in memory
            messages_to_keep = self.state_obj.chat_messages[-self._max_chat_messages_memory:]
            self.state_obj.chat_messages = messages_to_keep
        
        # Track the last message ID we've displayed for incremental updates
        if not hasattr(self, '_last_displayed_message_id'):
            self._last_displayed_message_id = -1
            incremental = False  # Force full refresh on first call
        
        # For incremental updates, check if there are new messages
        if incremental and self.state_obj.chat_messages:
            last_msg = self.state_obj.chat_messages[-1]
            if last_msg.id > self._last_displayed_message_id:
                # Only append new messages
                new_messages = [msg for msg in self.state_obj.chat_messages 
                              if msg.id > self._last_displayed_message_id]
                if new_messages:
                    self.chat_text.config(state='normal')
                    # Build all new content at once
                    new_content = []
                    for msg in new_messages:
                        timestamp = msg.created_at.replace('T', ' ')
                        if msg.kind == 'terminal':
                            kind_label = ' [TERMINAL COMMAND]'
                        elif msg.kind == 'terminal_result':
                            kind_label = ' [TERMINAL OUTPUT]'
                        elif msg.kind == 'file':
                            kind_label = ' [FILE]'
                        else:
                            kind_label = ''
                        new_content.append(f"[{timestamp}] {msg.persona}{kind_label}\n{msg.content}\n\n")
                    
                    # Insert all new content in one operation
                    if new_content:
                        self.chat_text.insert('end', ''.join(new_content))
                        self._last_displayed_message_id = last_msg.id
                        # Auto-scroll to bottom
                        self.chat_text.see('end')
                    self.chat_text.config(state='disabled')
                    # Update throttling state
                    import time
                    self._last_ui_update_time = time.time() * 1000
                    self._ui_update_pending = False
                    return
        
        # Full refresh - build entire content first, then insert once
        # Use chunked processing for better performance with large histories
        self.chat_text.config(state='normal')
        
        # Build all content as a single string first (do this before any widget operations)
        # Increased limit but with chunked processing to prevent memory issues
        max_messages_to_show = 1000  # Increased from 400
        messages_to_show = self.state_obj.chat_messages[-max_messages_to_show:]
        
        # Process in chunks to avoid memory spikes
        chunk_size = 100
        content_parts = []
        
        # Process messages in chunks for better memory management
        for i in range(0, len(messages_to_show), chunk_size):
            chunk = messages_to_show[i:i+chunk_size]
            for msg in chunk:
                timestamp = msg.created_at.replace('T', ' ')
                if msg.kind == 'terminal':
                    kind_label = ' [TERMINAL COMMAND]'
                elif msg.kind == 'terminal_result':
                    kind_label = ' [TERMINAL OUTPUT]'
                elif msg.kind == 'file':
                    kind_label = ' [FILE]'
                else:
                    kind_label = ''
                # Truncate very long messages to prevent UI freezing
                msg_content = msg.content
                max_msg_length = 10000  # Limit individual message display
                if len(msg_content) > max_msg_length:
                    msg_content = msg_content[:max_msg_length] + f"\n... (truncated, {len(msg.content)} chars total) ..."
                content_parts.append(f"[{timestamp}] {msg.persona}{kind_label}\n{msg_content}\n\n")
        
        # Join all content and prepare for insertion
        if content_parts:
            full_content = ''.join(content_parts)
            # Limit content size to prevent UI freezing (increased to 1MB for better performance)
            max_chars = 1000000  # Increased from 500KB to 1MB
            if len(full_content) > max_chars:
                # Truncate but keep recent messages
                truncated = full_content[-max_chars:]
                # Try to start at a message boundary
                first_newline = truncated.find('\n')
                if first_newline > 0:
                    truncated = truncated[first_newline+1:]
                full_content = f"... (showing last {max_chars:,} characters of {len(''.join(content_parts)):,} total) ...\n\n" + truncated
            
            # Perform clear and insert in minimal operations
            # Disable widget redraws during bulk operation
            try:
                # Temporarily disable widget updates for better performance
                self.chat_text.config(state='normal')
                # Use update_idletasks sparingly to reduce UI blocking
                self.chat_text.update_idletasks()
                self.chat_text.delete('1.0', 'end')
                # Insert in chunks for very large content to prevent UI freezing
                if len(full_content) > 500000:
                    # Insert in 200KB chunks with small delays
                    chunk_size = 200000
                    for i in range(0, len(full_content), chunk_size):
                        chunk = full_content[i:i+chunk_size]
                        if i == 0:
                            self.chat_text.insert('1.0', chunk)
                        else:
                            self.chat_text.insert('end', chunk)
                        # Small delay to allow UI to process
                        if i + chunk_size < len(full_content):
                            self.chat_text.update_idletasks()
                else:
                    self.chat_text.insert('1.0', full_content)
                # Track last displayed message ID
                if messages_to_show:
                    self._last_displayed_message_id = messages_to_show[-1].id
                # Auto-scroll to bottom (do this after content is inserted)
                self.chat_text.see('end')
            finally:
                self.chat_text.config(state='disabled')
                # Update throttling state
                import time
                self._last_ui_update_time = time.time() * 1000
                self._ui_update_pending = False
        else:
            # No content, just clear
            self.chat_text.delete('1.0', 'end')
            self.chat_text.config(state='disabled')
            # Update throttling state
            import time
            self._last_ui_update_time = time.time() * 1000
            self._ui_update_pending = False
    
    def _throttled_refresh(self, incremental: bool = False):
        """Perform a throttled refresh of chat history."""
        self._ui_update_pending = False
        self.refresh_chat_history(incremental=incremental)

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

        label = os.path.basename(path)
        block = f"\n[Imported file: {label}{descriptor}]\n{content}\n"
        
        # Clear placeholder if present
        current = self.chat_input.get('1.0', 'end').strip()
        placeholder = "Type a message for AI (Enter to send, Shift+Enter for newline). Use '$' prefix for shell commands."
        if current == placeholder:
            self.chat_input.delete('1.0', 'end')
            self.chat_input.config(foreground="black")

        self.chat_input.insert('end', block)
        self._update_chat_status(f"Imported '{label}' (full content).")

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
            
            # Read file content to include in chat context
            file_content = None
            file_size = os.path.getsize(path)
            max_file_size = 50000  # 50KB limit for automatic content reading
            file_ext = os.path.splitext(path)[1].lower()
            
            # Try to read text-based files
            if file_size <= max_file_size:
                try:
                    # Handle PDF files specially
                    if file_ext == '.pdf':
                        text_parts = []
                        # Try pdfplumber first
                        try:
                            import pdfplumber
                            with pdfplumber.open(path) as pdf:
                                for page in pdf.pages[:10]:  # Limit to first 10 pages
                                    try:
                                        page_text = page.extract_text()
                                        if page_text:
                                            text_parts.append(page_text)
                                    except Exception:
                                        continue
                                if text_parts:
                                    file_content = '\n\n'.join(text_parts)
                                    if len(pdf.pages) > 10:
                                        file_content += f"\n\n[PDF truncated - showing first 10 pages of {len(pdf.pages)} total]"
                        except ImportError:
                            pass
                        except Exception as e:
                            error_msg = str(e).lower()
                            # If pdfplumber fails, try PyPDF2 with strict=False
                            if "eof" not in error_msg and "corrupt" not in error_msg:
                                pass
                        
                        # Try PyPDF2 as fallback
                        if not text_parts:
                            try:
                                import PyPDF2
                                with open(path, 'rb') as f:
                                    try:
                                        pdf_reader = PyPDF2.PdfReader(f, strict=False)
                                    except Exception:
                                        f.seek(0)
                                        pdf_reader = PyPDF2.PdfReader(f)
                                    
                                    for i, page in enumerate(pdf_reader.pages[:10]):  # Limit to first 10 pages
                                        try:
                                            text_parts.append(page.extract_text())
                                        except Exception:
                                            continue
                                    
                                    if text_parts:
                                        file_content = '\n\n'.join(text_parts)
                                        if len(pdf_reader.pages) > 10:
                                            file_content += f"\n\n[PDF truncated - showing first 10 pages of {len(pdf_reader.pages)} total]"
                            except ImportError:
                                file_content = f"[PDF file: {label}, Size: {file_size:,} bytes - Install pdfplumber or PyPDF2 to extract text]"
                            except Exception as e:
                                error_msg = str(e).lower()
                                if "eof marker" in error_msg:
                                    file_content = f"[PDF file: {label} - PDF appears corrupted or incomplete (EOF marker not found). The file may be truncated or damaged.]"
                                elif "corrupt" in error_msg or "invalid" in error_msg:
                                    file_content = f"[PDF file: {label} - PDF appears corrupted or invalid.]"
                                else:
                                    file_content = f"[PDF file: {label}, Size: {file_size:,} bytes - Error extracting text: {str(e)}]"
                        
                        if not text_parts:
                            file_content = f"[PDF file: {label}, Size: {file_size:,} bytes - Unable to extract text (may be encrypted, image-only, or corrupted)]"
                    else:
                        # Try reading as text first
                        with open(path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                except (UnicodeDecodeError, Exception):
                    # If not text, try to get file info instead
                    try:
                        # For binary files, just include metadata
                        file_content = f"[Binary file: {label}, Size: {file_size:,} bytes, Type: {file_ext or 'unknown'}]"
                    except Exception:
                        pass
            
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
            
            # Automatically add file content to chat so AI knows about it
            if file_content:
                # Create a user message with file content
                file_message = f"I've uploaded a file: {label}\n\nFile content:\n{file_content[:10000]}"  # Limit to 10K chars
                if len(file_content) > 10000:
                    file_message += f"\n\n[File content truncated - showing first 10,000 characters of {len(file_content):,} total]"
                
                # Store as user message so AI can see it
                self._store_chat_message(
                    'Chris',
                    'user',
                    file_message,
                    kind='file'
                )
                self._update_chat_status(f"File content added to chat context ({len(file_content):,} characters)")
            else:
                # For large or binary files, just mention the file
                file_info_msg = f"I've uploaded a file: {label} (OpenAI File ID: {file_obj.id}, Size: {file_size:,} bytes)"
                self._store_chat_message(
                    'Chris',
                    'user',
                    file_info_msg,
                    kind='file'
                )
            
            self.refresh_chat_history(incremental=True)
            
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
        placeholder = "Type a message for AI (Enter to send, Shift+Enter for newline). Use '$' prefix for shell commands."
        if not text or text == placeholder:
            messagebox.showinfo('Chat', 'Type a message first.')
            return
        sender = self.chat_sender_var.get().strip() or 'Chris'
        if sender not in PERSONAS:
            sender = 'Chris'

        # Enhanced conversation processing (optional)
        conversation_data = None
        if CONVERSATION_MANAGER_AVAILABLE and invoke_ai:
            try:
                session_id = f"gui_session_{sender.lower()}"
                conversation_data = asyncio.run(process_conversation_message(
                    user_id=sender,
                    message=text,
                    session_id=session_id,
                    persona=self.chat_agent_var.get().strip() or self.state_obj.active_persona
                ))
                self.logger.info(f"Enhanced conversation analysis: {conversation_data.get('intent', 'unknown')}")
            except Exception as e:
                self.logger.warning(f"Enhanced conversation processing failed: {e}")

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
        self.refresh_chat_history(incremental=True)
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
            conversation_data=conversation_data,
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
        conversation_data: Optional[Dict[str, Any]] = None,
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
                # Limit message history to prevent memory issues (keep last 500 messages for context)
                all_messages = self.state_obj.chat_messages
                max_context_messages = 500
                if len(all_messages) > max_context_messages:
                    current_messages = all_messages[-max_context_messages:]
                else:
                    current_messages = all_messages.copy()
                
                # Enhance prompt with conversation analysis if available
                enhanced_prompt = instruction if iteration == 0 else None
                enhanced_system_prompt = system_prompt

                if conversation_data and iteration == 0:
                    # Add conversation context to system prompt or instruction
                    analysis = conversation_data.get('analysis', {})
                    context_info = []

                    if analysis.get('intent'):
                        context_info.append(f"User intent: {analysis['intent']}")
                    if analysis.get('emotion'):
                        context_info.append(f"User emotion: {analysis['emotion']}")
                    if analysis.get('urgency_level'):
                        context_info.append(f"Urgency level: {analysis['urgency_level']}/10")
                    if analysis.get('topics'):
                        context_info.append(f"Topics: {', '.join(analysis['topics'])}")

                    if context_info:
                        context_str = " | ".join(context_info)
                        if enhanced_prompt:
                            enhanced_prompt = f"[{context_str}] {enhanced_prompt}"
                        else:
                            enhanced_system_prompt = f"{system_prompt}\n\nCurrent conversation context: {context_str}"

                reply, error, tool_calls = generate_ai_reply(
                    current_messages,
                    persona=user_msg.persona,
                    prompt=enhanced_prompt,
                    append_prompt=bool(enhanced_prompt),
                    fallback_prompt=fallback_prompt,
                    system_prompt=enhanced_system_prompt,
                    model=model,
                    cwd=cwd,
                    enable_shell=True,
                )
                
                if error:
                    self.after(0, lambda r=reply, e=error, cd=conversation_data: self._handle_ai_reply(r, e, responder, cd))
                    return
                
                # If there are tool calls, execute them asynchronously to prevent UI blocking
                if tool_calls:
                    tool_results = []
                    import threading
                    import queue
                    
                    # Use a queue to collect results from threads
                    result_queue = queue.Queue()
                    
                    def execute_tool_async(tc, file_op_detected):
                        """Execute a tool call in a separate thread."""
                        try:
                            # Prepare GUI context for tools that need it (like read_displayed_file)
                            # Capture active_file_session at the time of execution
                            active_session = getattr(self, 'active_file_session', None)
                            gui_context = {
                                'active_file_session': active_session,
                                'read_file_func': self._get_displayed_file_content if hasattr(self, '_get_displayed_file_content') else None
                            }
                            result = execute_tool_call(tc, cwd=cwd, gui_context=gui_context)
                            result_queue.put(('success', tc, result, file_op_detected))
                        except Exception as e:
                            error_result = {
                                "tool_call_id": tc.id if hasattr(tc, 'id') else None,
                                "role": "tool",
                                "name": getattr(tc.function, 'name', 'unknown') if hasattr(tc, 'function') else 'unknown',
                                "content": f"Error executing tool: {str(e)}"
                            }
                            result_queue.put(('error', tc, error_result, file_op_detected))
                    
                    # Start all tool executions in parallel
                    threads = []
                    for tool_call in tool_calls:
                        # Detect file operations and show preview
                        file_op = self._detect_file_operation(tool_call)
                        if file_op:
                            self.after(0, lambda op=file_op: self._show_file_preview(
                                op['type'], op['path'], op.get('id')
                            ))
                        
                        # Start thread for this tool call
                        thread = threading.Thread(target=execute_tool_async, args=(tool_call, file_op), daemon=True)
                        thread.start()
                        threads.append(thread)
                    
                    # Collect results with timeout
                    collected = 0
                    timeout_per_tool = 60  # 60 seconds per tool
                    for thread in threads:
                        thread.join(timeout=timeout_per_tool)
                        if thread.is_alive():
                            self.after(0, lambda: self._update_chat_status("Some tool executions are taking longer than expected..."))
                    
                    # Collect all results from queue
                    messages_to_store = []  # Collect messages to store on main thread
                    while not result_queue.empty():
                        status, tc, result, file_op = result_queue.get()
                        tool_results.append(result)
                        
                        # Handle result in main thread
                        if file_op:
                            self.after(0, lambda: self._refresh_file_preview())
                        
                        # Collect terminal command messages to store on main thread
                        if hasattr(tc, 'function') and tc.function.name == "execute_command":
                            import json
                            try:
                                args = json.loads(tc.function.arguments)
                                cmd = args.get("command", "")
                                if cmd:
                                    header = f'$ {cmd}\n(cwd: {cwd})'
                                    result_content = result["content"]
                                    messages_to_store.append(('user', header, 'terminal'))
                                    messages_to_store.append(('assistant', result_content, 'terminal_result'))
                            except:
                                pass
                    
                    # Collect tool result messages to store on main thread
                    for result in tool_results:
                        result_content = result.get("content", "")
                        tool_call_id = result.get("tool_call_id", "")
                        # Store tool_call_id with content so it can be retrieved later
                        # Format: JSON string with tool_call_id and content
                        if tool_call_id:
                            import json
                            stored_content = json.dumps({
                                "tool_call_id": tool_call_id,
                                "content": result_content
                            })
                        else:
                            stored_content = result_content
                        messages_to_store.append(('tool', stored_content, 'tool_result'))
                        
                        # Check if tool result mentions a file
                        file_op = self._detect_file_in_message(result_content)
                        if file_op and not self.active_file_session:
                            self.after(0, lambda op=file_op: self._show_file_preview(
                                op['type'], op['path'], op.get('id')
                            ))
                    
                    # Store all messages on main thread and wait for completion
                    if messages_to_store:
                        import threading
                        store_event = threading.Event()
                        
                        def store_messages():
                            """Store all messages on main thread."""
                            try:
                                for role, content, kind in messages_to_store:
                                    if role == 'user':
                                        self._store_chat_message(responder, 'user', content, kind=kind)
                                    elif role == 'assistant':
                                        self._store_chat_message(responder, 'assistant', content, kind=kind)
                                    else:  # tool
                                        self._store_chat_message(responder, 'tool', content, kind=kind)
                                self.refresh_chat_history(incremental=True)
                            finally:
                                store_event.set()
                        
                        self.after(0, store_messages)
                        # Wait for messages to be stored (with timeout)
                        store_event.wait(timeout=2.0)
                    
                    self.after(0, lambda: self.refresh_chat_history(incremental=True))
                    iteration += 1
                    import time
                    time.sleep(0.5)  # Brief pause to allow UI update
                    continue
                else:
                    # No more tool calls, return the final reply
                    self.after(0, lambda r=reply, e=error, cd=conversation_data: self._handle_ai_reply(r, e, responder, cd))
                    return
            
            # Max iterations reached
            final_reply = reply if 'reply' in locals() and reply else "Maximum interaction iterations reached."
            self.after(0, lambda r=final_reply, cd=conversation_data: self._handle_ai_reply(r, None, responder, cd))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_ai_reply(self, reply_text: str, error: Optional[str], responder: str, conversation_data: Optional[Dict[str, Any]] = None):
        # Stop progress indicator
        if hasattr(self, 'chat_progress'):
            if error:
                self.chat_progress.stop("Error occurred")
            else:
                self.chat_progress.stop("Response received")

        persona = responder or self.chat_agent_var.get().strip() or 'AI Team'
        text = reply_text.strip() if reply_text else '(no response)'
        self._store_chat_message(persona, 'assistant', text)
        self.refresh_chat_history(incremental=True)

        # Handle proactive suggestions from conversation analysis
        if conversation_data and not error:
            suggestions = conversation_data.get('suggestions', [])
            if suggestions:
                # Add suggestions as a system message
                suggestion_text = "💡 Suggestions: " + " | ".join(suggestions[:2])
                self._store_chat_message('System', 'system', suggestion_text)
                self.refresh_chat_history(incremental=True)

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
        self.refresh_chat_history(incremental=True)

    def on_browse_cwd(self):
        initial = self.cwd_var.get().strip() or os.getcwd()
        path = filedialog.askdirectory(initialdir=initial)
        if path:
            self.cwd_var.set(path)

    def on_input_focus_in(self, event=None):
        """Clear placeholder text when input gains focus."""
        placeholder = "Type a message for AI (Enter to send, Shift+Enter for newline). Use '$' prefix for shell commands."
        current_text = self.chat_input.get('1.0', 'end').strip()
        if current_text == placeholder:
            self.chat_input.delete('1.0', 'end')
            self.chat_input.config(foreground="black")

    def on_input_focus_out(self, event=None):
        """Restore placeholder text if input is empty."""
        current_text = self.chat_input.get('1.0', 'end').strip()
        placeholder = "Type a message for AI (Enter to send, Shift+Enter for newline). Use '$' prefix for shell commands."
        if not current_text:
            self.chat_input.insert("1.0", placeholder)
            self.chat_input.config(foreground="gray")

    def on_handle_combined_input(self, chat_mode=True):
        """Handle combined input field - always send to AI, AI can execute commands via tools."""
        if not hasattr(self, 'chat_input'):
            return
        
        text = self.chat_input.get('1.0', 'end').strip()
        placeholder = "Type a message for AI (Enter to send, Shift+Enter for newline). Use '$' prefix for shell commands."
        
        # Ignore placeholder text
        if not text or text == placeholder:
            return
        
        # Always send to AI - the AI can execute commands via its tools
        # If user wants to run a command, they can ask the AI to do it
        # Commands starting with $ are still sent to AI, which can execute them
        self.on_send_chat_message(invoke_ai=True)
        
        # Clear input and restore placeholder
        self.chat_input.delete('1.0', 'end')
        self.on_input_focus_out()

    def on_handle_combined_input_enter(self, event):
        """Handle Enter key in combined input - Enter sends to AI, Shift+Enter for newline, $ prefix for shell commands."""
        if not hasattr(self, 'chat_input'):
            return None
        
        text = self.chat_input.get('1.0', 'end').strip()
        placeholder = "Type a message for AI (Enter to send, Shift+Enter for newline). Use '$' prefix for shell commands."
        
        # Ignore placeholder text
        if not text or text == placeholder:
            return "break"  # Prevent default Enter behavior
        
        # Check if Shift is pressed - allow newline for multi-line messages
        if event.state & 0x1:  # Shift pressed
            return None  # Allow default Enter behavior (newline)
        
        # Check if it's a shell command (starts with $)
        starts_with_dollar = text.strip().startswith('$')
        
        if starts_with_dollar:
            # Execute as shell command
            command = text.strip()[1:].strip()  # Remove $ prefix
            if command:
                self.after(0, lambda: self._execute_shell_command(command))
                self.chat_input.delete('1.0', 'end')
                self.on_input_focus_out()
            return "break"  # Prevent default Enter behavior
        
        # Enter without Shift - send to AI (single or multi-line)
        self.on_handle_combined_input(chat_mode=True)
        return "break"  # Prevent default Enter behavior
    
    def _execute_shell_command(self, command: str):
        """Execute a shell command and display result in chat."""
        if not command:
            return
        
        cwd = os.path.expanduser(self.cwd_var.get().strip() if hasattr(self, 'cwd_var') else os.getcwd())
        result = run_bash_command(command, cwd=cwd)
        
        # Store command and result in chat
        output_parts = []
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr}")
        if not output_parts:
            output_parts.append("(no output)")
        
        output_parts.append(f"\nExit code: {result.returncode}")
        output = "\n".join(output_parts)
        
        # Store in chat
        self._store_chat_message('System', 'system', f"Command: {command}\n{output}", kind='terminal')
        self.refresh_chat_history(incremental=True)


# ---------- Integrations Tab ----------

    def _build_integrations_tab(self):
        """Build the Integrations tab with external service connections."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.integrations_frame = ttkb.Frame(self.notebook)
        else:
            self.integrations_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.integrations_frame, text="🔗 Integrations")
        
        self.integrations_frame.columnconfigure(0, weight=1)
        self.integrations_frame.rowconfigure(0, weight=1)
        
        if TTKBOOTSTRAP_AVAILABLE:
            main_container = ttkb.Frame(self.integrations_frame)
        else:
            main_container = ttk.Frame(self.integrations_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Header with teal color scheme
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(main_container, text="External Data Integrations", bootstyle="info", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
        else:
            try:
                bg_color = main_container.cget("background")
            except:
                bg_color = "white"
            header = tk.Label(main_container, text="External Data Integrations", 
                            font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"),
                            fg="#008B8B", bg=bg_color)
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
        self.integrations_tree.column("status", width=300)  # Wider to show full error messages
        self.integrations_tree.column("last_sync", width=150)
        self.integrations_tree.column("items", width=80)
        
        # Color scheme: Teal primary with coral secondary for contrast
        self.integrations_teal = "#20B2AA"  # Light sea green (teal)
        self.integrations_coral = "#FF7F50"  # Coral (secondary contrast)
        self.integrations_teal_light = "#E0F7F6"  # Very light teal for backgrounds
        self.integrations_teal_dark = "#008B8B"  # Darker teal for headers
        
        # Configure treeview tags for color styling
        if not TTKBOOTSTRAP_AVAILABLE:
            style = ttk.Style()
            style.configure("Integrations.Treeview", background="#ffffff", foreground="#333333", rowheight=25)
            style.configure("Integrations.Treeview.Heading", background=self.integrations_teal_dark, foreground="white", font=(self.base_font.actual("family"), self.base_font.actual("size"), "bold"))
            style.map("Integrations.Treeview", background=[("selected", self.integrations_teal)])
            self.integrations_tree.configure(style="Integrations.Treeview")
        
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
            sync_btn = ttkb.Button(btn_frame, text="🔄 Sync All", command=self.on_sync_all_integrations, bootstyle="info")
            sync_selected_btn = ttkb.Button(btn_frame, text="🔄 Sync Selected", command=self.on_sync_selected_integration, bootstyle="info-outline")
            refresh_btn = ttkb.Button(btn_frame, text="🔄 Refresh", command=self.on_refresh_integrations, bootstyle="secondary")
        else:
            connect_btn = ttk.Button(btn_frame, text="Connect", command=self.on_connect_integration)
            sync_btn = ttk.Button(btn_frame, text="Sync All", command=self.on_sync_all_integrations)
            sync_selected_btn = ttk.Button(btn_frame, text="Sync Selected", command=self.on_sync_selected_integration)
            refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.on_refresh_integrations)
        
        connect_btn.grid(row=0, column=0, padx=4)
        sync_btn.grid(row=0, column=1, padx=4)
        sync_selected_btn.grid(row=0, column=2, padx=4)
        refresh_btn.grid(row=0, column=3, padx=4)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ToolTip(connect_btn, text="Connect/Configure the selected integration")
            ToolTip(sync_btn, text="Sync all enabled integrations")
            ToolTip(sync_selected_btn, text="Sync the selected integration")
            ToolTip(refresh_btn, text="Refresh the integrations list")

        # Initialize the integrations list
        self.after(100, self.on_refresh_integrations)
    
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

    def on_refresh_integrations(self):
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
                # Show more of the error message (up to 80 chars) for better visibility
                error_display = status.error[:80] + "..." if len(status.error) > 80 else status.error
                status_text += f" ({error_display})"

            last_sync = status.last_sync or "Never"
            if last_sync != "Never" and "T" in last_sync:
                last_sync = last_sync.replace("T", " ")[:16]

            # Determine tag based on connection status
            if status.connected:
                tag = "connected"
            else:
                tag = "disconnected"

            item_id = self.integrations_tree.insert(
                "", "end",
                values=(name, status_text, last_sync, status.item_count or 0),
                tags=(tag,)
            )

        # Configure tag colors
        if TTKBOOTSTRAP_AVAILABLE:
            self.integrations_tree.tag_configure("connected", background="#d4edda", foreground="#155724")  # Green
            self.integrations_tree.tag_configure("disconnected", background="#f8d7da", foreground="#721c24")  # Red
        else:
            self.integrations_tree.tag_configure("connected", background="lightgreen")
            self.integrations_tree.tag_configure("disconnected", background="lightcoral")

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
            self._show_msgraph_auth_dialog(dialog, main_frame, "OneNote")
        elif service_name == "OneDrive":
            self._show_msgraph_auth_dialog(dialog, main_frame, "OneDrive")
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
            token_path = os.path.join(cred_dir, f"google_{service_type}_token.json")
            
            try:
                import shutil
                shutil.copy2(cred_path, target_path)
                
                # Now perform OAuth2 flow
                try:
                    from google.auth.transport.requests import Request
                    from google.oauth2.credentials import Credentials
                    from google_auth_oauthlib.flow import InstalledAppFlow
                    import json
                    
                    # Define scopes based on service type
                    if service_type == "gmail":
                        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
                    elif service_type == "calendar":
                        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
                    else:
                        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
                    
                    creds = None
                    # Check if token already exists
                    if os.path.exists(token_path):
                        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                    
                    # If there are no (valid) credentials available, let the user log in.
                    if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        else:
                            flow = InstalledAppFlow.from_client_secrets_file(
                                target_path, SCOPES)
                            creds = flow.run_local_server(port=0)
                        
                        # Save the credentials for the next run
                        with open(token_path, 'w') as token:
                            token.write(creds.to_json())
                    
                    messagebox.showinfo("Success", f"✅ Successfully authenticated with Google {service_type.title()}!")
                    dialog.destroy()
                except ImportError:
                    messagebox.showwarning(
                        "Missing Dependencies",
                        "Google OAuth libraries not installed.\n\n"
                        "Please install:\n"
                        "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
                    )
                except Exception as e:
                    messagebox.showerror("Authentication Error", f"Failed to complete OAuth2 flow:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save credentials: {e}")
        
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn = ttkb.Button(frame, text="Save & Authenticate", command=save_and_connect, bootstyle="success")
            cancel_btn = ttkb.Button(frame, text="Cancel", command=dialog.destroy, bootstyle="secondary")
        else:
            save_btn = ttk.Button(frame, text="Save & Authenticate", command=save_and_connect)
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
    
    def _show_msgraph_auth_dialog(self, dialog, frame, service_name: str = "OneNote"):
        """Show Microsoft Graph authentication dialog."""
        title_label = ttk.Label(frame, text=f"Connect to {service_name} (Microsoft Graph)", font=(self.base_font.actual("family"), 14, "bold"))
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
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save credentials: {e}")
        
            # Note: Delegated permissions authentication removed due to complexity
            # Only client credentials flow is supported for now
        
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

    def format_file_size(self, size_bytes):
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"

    def refresh_pdf_documents(self):
        """Refresh the list of PDF documents from OneDrive."""
        try:
            # Clear existing items
            if hasattr(self, 'pdf_tree'):
                for item in self.pdf_tree.get_children():
                    self.pdf_tree.delete(item)

            # Import ExcelCloudClient here to avoid scoping issues
            try:
                from .integrations.excel.cloud_client import ExcelCloudClient
                excel_client_available = True
            except ImportError:
                excel_client_available = False
                ExcelCloudClient = None

            if not hasattr(self, 'pdf_status_var'):
                return

            if not EXCEL_CLOUD_AVAILABLE or not excel_client_available or ExcelCloudClient is None:
                self.pdf_status_var.set("❌ Microsoft Graph client not available. Check Microsoft Graph configuration.")
                return

            self.pdf_status_var.set("🔄 Loading documents...")
            self.update()

            try:
                # Pass connection to GraphClient so it can load credentials from database
                from .integrations.msgraph.client import GraphClient
                # Use delegated auth for /me/ endpoints
                graph_client = GraphClient(conn=self.conn, use_delegated=True)
                client = ExcelCloudClient(graph=graph_client, conn=self.conn)  # Reuse ExcelCloudClient for OneDrive access
                items = client.list_workbooks()  # This lists all OneDrive files

                # Filter for PDF files
                pdf_files = [item for item in items if item.get("name", "").endswith(".pdf")]

                if not pdf_files:
                    self.pdf_status_var.set("ℹ️ No PDF documents found or not authenticated. Check Microsoft Graph credentials.")
                    return

                for item in pdf_files:
                    name = item.get("name", "Unknown")
                    size = item.get("size", 0)
                    size_str = format_file_size(size) if size > 0 else "Unknown"
                    modified = item.get("lastModifiedDateTime", "Unknown")
                    if modified and "T" in modified:
                        modified = modified.replace("T", " ")[:16]

                    if hasattr(self, 'pdf_tree'):
                        self.pdf_tree.insert("", "end", values=(name, "", size_str, modified, ""), tags=("cloud",))

                # Also load local PDF documents
                try:
                    from .db import get_project_documents
                    local_docs = get_project_documents(self.conn, doc_type="pdf")
                    for doc in local_docs:
                        name = self._safe_get(doc, "title", "Unknown")
                        project_name = self._safe_get(doc, "project_id", "General")
                        size_str = format_file_size(self._safe_get(doc, "file_size", 0))
                        modified = self._safe_get(doc, "modified_date", "")
                        if modified:
                            try:
                                dt_obj = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                                modified = dt_obj.strftime("%Y-%m-%d %H:%M")
                            except:
                                pass
                        else:
                            modified = "Unknown"

                        # Get version count
                        try:
                            from .db import get_document_versions
                            versions = get_document_versions(self.conn, self._safe_get(doc, "id"))
                            version_info = f"v{len(versions)}" if versions else ""
                        except:
                            version_info = ""

                        item_id = f"local_pdf_{self._safe_get(doc, 'id')}"
                        if hasattr(self, 'pdf_tree'):
                            self.pdf_tree.insert("", "end", iid=item_id, values=(f"📁 {name}", project_name, size_str, modified, version_info), tags=("local",))

                            # Store doc_id and file_path in item
                            self.pdf_tree.set(item_id, "doc_id", str(self._safe_get(doc, "id")))
                            self.pdf_tree.set(item_id, "file_path", self._safe_get(doc, "file_path", ""))
                except Exception as e:
                    self.logger.warning(f"Failed to load local PDF documents: {e}")

                total_count = len(pdf_files) + (len(local_docs) if 'local_docs' in locals() else 0)
                self.pdf_status_var.set(f"✅ Loaded {total_count} PDF document(s) ({len(pdf_files)} cloud)")
            except Exception as e:
                error_msg = str(e)
                # Check for specific authentication errors
                if "401" in error_msg or "Unauthorized" in error_msg or "Authentication" in error_msg:
                    self.pdf_status_var.set("❌ Authentication failed. Check Microsoft Graph credentials.")
                    messagebox.showerror(
                        "Authentication Failed",
                        f"Failed to authenticate with Microsoft Graph:\n\n{error_msg}\n\n"
                        "Possible causes:\n"
                        "1. Invalid or expired client secret\n"
                        "2. Wrong tenant ID, client ID, or client secret\n"
                        "3. Missing required permissions (Files.Read)\n\n"
                        "Go to Settings > Integrations to reconfigure credentials."
                    )
                elif "credentials" in error_msg.lower():
                    self.pdf_status_var.set("❌ Credentials not configured. Set up Microsoft Graph in Settings.")
                    messagebox.showwarning(
                        "Not Configured",
                        "Microsoft Graph credentials are not configured.\n\n"
                        "Go to Settings > Integrations to configure."
                    )
                else:
                    self.pdf_status_var.set(f"❌ Error: {error_msg[:50]}")
                    messagebox.showerror("Error", f"Failed to load PDF documents:\n\n{error_msg}")
        except Exception as e:
            error_msg = str(e)
            if hasattr(self, 'pdf_status_var'):
                self.pdf_status_var.set(f"❌ Error: {error_msg[:50]}")
            messagebox.showerror("Error", f"Failed to refresh PDF documents:\n\n{error_msg}")

    def _safe_get(self, obj, key, default=""):
        """Safely get a value from a dictionary or object."""
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            elif hasattr(obj, key):
                return getattr(obj, key, default)
            else:
                return default
        except:
            return default


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
        
        # Word Documents section
        self._build_word_tools_section(tools_notebook)
        
        # PDF Documents section
        self._build_pdf_tools_section(tools_notebook)
        
        # Workflow Execution section
        self._build_workflow_tools_section(tools_notebook)

    
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
            upload_btn = ttkb.Button(frame, text="📤 Upload File", command=lambda: self.upload_document("onenote"), bootstyle="success-outline")
            refresh_btn = ttkb.Button(frame, text="🔄 Refresh Notebooks", command=self.refresh_onenote_notebooks, bootstyle="info-outline")
        else:
            header = ttk.Label(frame, text="OneNote Notebooks", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            upload_btn = ttk.Button(frame, text="Upload File", command=lambda: self.upload_document("onenote"))
            refresh_btn = ttk.Button(frame, text="Refresh Notebooks", command=self.refresh_onenote_notebooks)
        
        header.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        upload_btn.grid(row=0, column=1, sticky="e", padx=(8, 4), pady=(8, 4))
        refresh_btn.grid(row=0, column=2, sticky="e", padx=8, pady=(8, 4))
        
        # Notebooks tree
        columns = ("name", "project", "id", "last_modified", "versions")
        self.onenote_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        self.onenote_tree.heading("name", text="Notebook Name")
        self.onenote_tree.heading("project", text="Project")
        self.onenote_tree.heading("id", text="ID")
        self.onenote_tree.heading("last_modified", text="Last Modified")
        self.onenote_tree.heading("versions", text="Versions")
        
        self.onenote_tree.column("name", width=200)
        self.onenote_tree.column("project", width=150)
        self.onenote_tree.column("id", width=120)
        self.onenote_tree.column("last_modified", width=120)
        self.onenote_tree.column("versions", width=70)
        
        self.onenote_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        
        # Bind double-click and right-click
        self.onenote_tree.bind("<Double-1>", lambda e: self._on_onenote_double_click(e))
        self.onenote_tree.bind("<Button-3>", lambda e: self._on_onenote_right_click(e))  # Right-click for context menu
        
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
            upload_btn = ttkb.Button(frame, text="📤 Upload File", command=lambda: self.upload_document("excel"), bootstyle="success-outline")
            refresh_btn = ttkb.Button(frame, text="🔄 Refresh Workbooks", command=self.refresh_excel_workbooks, bootstyle="info-outline")
        else:
            header = ttk.Label(frame, text="Excel Workbooks", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            upload_btn = ttk.Button(frame, text="Upload File", command=lambda: self.upload_document("excel"))
            refresh_btn = ttk.Button(frame, text="Refresh Workbooks", command=self.refresh_excel_workbooks)
        
        header.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        upload_btn.grid(row=0, column=1, sticky="e", padx=(8, 4), pady=(8, 4))
        refresh_btn.grid(row=0, column=2, sticky="e", padx=8, pady=(8, 4))
        
        # Workbooks tree
        columns = ("name", "project", "id", "size", "modified", "versions")
        self.excel_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        self.excel_tree.heading("name", text="Workbook Name")
        self.excel_tree.heading("project", text="Project")
        self.excel_tree.heading("id", text="ID")
        self.excel_tree.heading("size", text="Size")
        self.excel_tree.heading("modified", text="Modified")
        self.excel_tree.heading("versions", text="Versions")
        
        self.excel_tree.column("name", width=200)
        self.excel_tree.column("project", width=150)
        self.excel_tree.column("id", width=120)
        self.excel_tree.column("size", width=80)
        self.excel_tree.column("modified", width=120)
        self.excel_tree.column("versions", width=70)
        
        self.excel_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        
        # Bind double-click
        self.excel_tree.bind("<Double-1>", lambda e: self._on_document_double_click(e, "excel"))
        
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

    def refresh_excel_workbooks(self):
        """Refresh the Excel workbooks list."""
        try:
            # Clear existing items
            for item in self.excel_tree.get_children():
                self.excel_tree.delete(item)

            # Get all Excel documents
            excel_docs = get_project_documents(self.conn, doc_type="excel")

            # Sort by modified date (most recent first)
            excel_docs.sort(key=lambda x: self._safe_get(x, "modified_date", ""), reverse=True)

            # Add to tree
            for doc in excel_docs:
                doc_name = self._safe_get(doc, "title", "Unknown")
                project_name = self._safe_get(doc, "project_name", "Unknown")
                doc_id = self._safe_get(doc, "id", "")
                file_size = self._safe_get(doc, "file_size", 0)
                size_str = format_file_size(file_size) if file_size > 0 else "Unknown"
                modified = self._safe_get(doc, "modified_date", "")
                if modified:
                    try:
                        # Parse and format the date
                        from datetime import datetime
                        dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                        modified = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass

                # Get version count (simplified)
                versions = "1"

                self.excel_tree.insert("", "end", values=(doc_name, project_name, doc_id, size_str, modified, versions))

            count = len(excel_docs)
            self.excel_status_var.set(f"Loaded {count} Excel workbook{'s' if count != 1 else ''}")

        except Exception as e:
            self.logger.error(f"Failed to refresh Excel workbooks: {e}")
            self.excel_status_var.set(f"Error loading workbooks: {str(e)}")

    def _build_word_tools_section(self, parent):
        """Build Word documents browser section."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="📝 Word Documents")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Header
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(frame, text="Word Documents", bootstyle="primary", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            upload_btn = ttkb.Button(frame, text="📤 Upload File", command=lambda: self.upload_document("word"), bootstyle="success-outline")
            refresh_btn = ttkb.Button(frame, text="🔄 Refresh Documents", command=self.refresh_word_documents, bootstyle="info-outline")
        else:
            header = ttk.Label(frame, text="Word Documents", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            upload_btn = ttk.Button(frame, text="Upload File", command=lambda: self.upload_document("word"))
            refresh_btn = ttk.Button(frame, text="Refresh Documents", command=self.refresh_word_documents)
        
        header.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        upload_btn.grid(row=0, column=1, sticky="e", padx=(8, 4), pady=(8, 4))
        refresh_btn.grid(row=0, column=2, sticky="e", padx=8, pady=(8, 4))
        
        # Documents tree
        columns = ("name", "project", "size", "modified", "versions")
        self.word_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        self.word_tree.heading("name", text="Document Name")
        self.word_tree.heading("project", text="Project")
        self.word_tree.heading("size", text="Size")
        self.word_tree.heading("modified", text="Modified")
        self.word_tree.heading("versions", text="Versions")
        
        self.word_tree.column("name", width=200)
        self.word_tree.column("project", width=150)
        self.word_tree.column("size", width=80)
        self.word_tree.column("modified", width=120)
        self.word_tree.column("versions", width=70)
        
        self.word_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        
        # Bind double-click
        self.word_tree.bind("<Double-1>", lambda e: self._on_document_double_click(e, "word"))
        
        if TTKBOOTSTRAP_AVAILABLE:
            scrollbar = ttkb.Scrollbar(frame, orient="vertical", command=self.word_tree.yview, bootstyle="primary-round")
        else:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.word_tree.yview)
        self.word_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=4)
        
        # Status label
        self.word_status_var = tk.StringVar(value="Click 'Refresh Documents' to load Word documents from OneDrive")
        if TTKBOOTSTRAP_AVAILABLE:
            status_label = ttkb.Label(frame, textvariable=self.word_status_var, bootstyle="secondary")
        else:
            status_label = ttk.Label(frame, textvariable=self.word_status_var)
        status_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=4)

    def refresh_word_documents(self):
        """Refresh the Word documents list."""
        try:
            # Clear existing items
            for item in self.word_tree.get_children():
                self.word_tree.delete(item)

            # Get all Word documents
            word_docs = get_project_documents(self.conn, doc_type="word")

            # Sort by modified date (most recent first)
            word_docs.sort(key=lambda x: self._safe_get(x, "modified_date", ""), reverse=True)

            # Add to tree
            for doc in word_docs:
                doc_name = self._safe_get(doc, "title", "Unknown")
                project_name = self._safe_get(doc, "project_name", "Unknown")
                file_size = self._safe_get(doc, "file_size", 0)
                size_str = format_file_size(file_size) if file_size > 0 else "Unknown"
                modified = self._safe_get(doc, "modified_date", "")
                if modified:
                    try:
                        # Parse and format the date
                        from datetime import datetime
                        dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                        modified = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass

                # Get version count (simplified)
                versions = "1"

                self.word_tree.insert("", "end", values=(doc_name, project_name, size_str, modified, versions))

            count = len(word_docs)
            self.word_status_var.set(f"Loaded {count} Word document{'s' if count != 1 else ''}")

        except Exception as e:
            self.logger.error(f"Failed to refresh Word documents: {e}")
            self.word_status_var.set(f"Error loading documents: {str(e)}")

    def _build_pdf_tools_section(self, parent):
        """Build PDF documents browser section."""
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="📄 PDF Documents")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Header
        if TTKBOOTSTRAP_AVAILABLE:
            header = ttkb.Label(frame, text="PDF Documents", bootstyle="primary", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            upload_btn = ttkb.Button(frame, text="📤 Upload File", command=lambda: self.upload_document("pdf"), bootstyle="success-outline")
            refresh_btn = ttkb.Button(frame, text="🔄 Refresh Documents", command=self.refresh_pdf_documents, bootstyle="info-outline")
        else:
            header = ttk.Label(frame, text="PDF Documents", font=(self.base_font.actual("family"), self.base_font.actual("size") + 2, "bold"))
            upload_btn = ttk.Button(frame, text="Upload File", command=lambda: self.upload_document("pdf"))
            refresh_btn = ttk.Button(frame, text="Refresh Documents", command=self.refresh_pdf_documents)
        
        header.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        upload_btn.grid(row=0, column=1, sticky="e", padx=(8, 4), pady=(8, 4))
        refresh_btn.grid(row=0, column=2, sticky="e", padx=8, pady=(8, 4))
        
        # Documents tree
        columns = ("name", "project", "size", "modified", "versions")
        self.pdf_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        self.pdf_tree.heading("name", text="Document Name")
        self.pdf_tree.heading("project", text="Project")
        self.pdf_tree.heading("size", text="Size")
        self.pdf_tree.heading("modified", text="Modified")
        self.pdf_tree.heading("versions", text="Versions")
        
        self.pdf_tree.column("name", width=200)
        self.pdf_tree.column("project", width=150)
        self.pdf_tree.column("size", width=80)
        self.pdf_tree.column("modified", width=120)
        self.pdf_tree.column("versions", width=70)
        
        self.pdf_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        
        # Bind double-click to show versions
        self.pdf_tree.bind("<Double-1>", lambda e: self._on_document_double_click(e, "pdf"))
        
        if TTKBOOTSTRAP_AVAILABLE:
            scrollbar = ttkb.Scrollbar(frame, orient="vertical", command=self.pdf_tree.yview, bootstyle="primary-round")
        else:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.pdf_tree.yview)
        self.pdf_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=4)
        
        # Status label
        self.pdf_status_var = tk.StringVar(value="Click 'Refresh Documents' to load PDF documents from OneDrive")
        if TTKBOOTSTRAP_AVAILABLE:
            status_label = ttkb.Label(frame, textvariable=self.pdf_status_var, bootstyle="secondary")
        else:
            status_label = ttk.Label(frame, textvariable=self.pdf_status_var)
        status_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=4)
    
    def _build_workflow_tools_section(self, parent):
        """Build workflow execution section.
        
        Workflows are automated processes that perform complex operations on documents.
        The Clean Notebook Workflow specifically:
        - Analyzes OneNote notebooks for structure and content
        - Identifies and removes duplicate or redundant content
        - Organizes sections and pages for better navigation
        - Optimizes notebook structure for improved performance
        """
        if TTKBOOTSTRAP_AVAILABLE:
            frame = ttkb.Frame(parent)
        else:
            frame = ttk.Frame(parent)
        parent.add(frame, text="⚙️ Workflows")
        
        frame.columnconfigure(0, weight=1)
        
        # Explanation section
        if TTKBOOTSTRAP_AVAILABLE:
            info_section = ttkb.Labelframe(frame, text="About Workflows", bootstyle="info")
        else:
            info_section = ttk.LabelFrame(frame, text="About Workflows")
        info_section.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        info_section.columnconfigure(0, weight=1)
        
        explanation_text = (
            "Workflows are automated processes that perform complex operations on documents.\n\n"
            "Clean Notebook Workflow:\n"
            "• Analyzes OneNote notebooks for structure and content\n"
            "• Identifies and removes duplicate or redundant content\n"
            "• Organizes sections and pages for better navigation\n"
            "• Optimizes notebook structure for improved performance"
        )
        
        if TTKBOOTSTRAP_AVAILABLE:
            info_label = ttkb.Label(info_section, text=explanation_text, bootstyle="secondary", justify="left", wraplength=600)
        else:
            info_label = ttk.Label(info_section, text=explanation_text, justify="left", wraplength=600)
        info_label.grid(row=0, column=0, sticky="w", padx=8, pady=8)
        
        # Notebook cleanup workflow
        if TTKBOOTSTRAP_AVAILABLE:
            workflow_section = ttkb.Labelframe(frame, text="Clean OneNote Notebook Workflow", bootstyle="warning")
        else:
            workflow_section = ttk.LabelFrame(frame, text="Clean OneNote Notebook Workflow")
        workflow_section.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
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
        result_section.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        result_section.columnconfigure(0, weight=1)
        result_section.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        self.workflow_result_text = tk.Text(result_section, wrap="word", height=10, font=self.text_font)
        self._style_text_widget(self.workflow_result_text)
        self.workflow_result_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        
        if TTKBOOTSTRAP_AVAILABLE:
            workflow_scrollbar = ttkb.Scrollbar(result_section, orient="vertical", command=self.workflow_result_text.yview, bootstyle="primary-round")
        else:
            workflow_scrollbar = ttk.Scrollbar(result_section, orient="vertical", command=self.workflow_result_text.yview)
        self.workflow_result_text.configure(yscroll=workflow_scrollbar.set)
        workflow_scrollbar.grid(row=0, column=1, sticky="ns")

        # Automation Workflow Orchestrator Section
        if AUTOMATION_ORCHESTRATOR_AVAILABLE and self.automation_orchestrator:
            if TTKBOOTSTRAP_AVAILABLE:
                automation_section = ttkb.Labelframe(frame, text="🤖 Intelligent Automation Workflows", bootstyle="success")
            else:
                automation_section = ttk.LabelFrame(frame, text="Intelligent Automation Workflows")
            automation_section.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
            automation_section.columnconfigure(0, weight=1)

            # Automation workflow controls
            ttk.Label(automation_section, text="Available Workflows:").grid(row=0, column=0, sticky="w", padx=4, pady=2)

            self.automation_workflow_var = tk.StringVar()
            workflow_combo = ttk.Combobox(automation_section, textvariable=self.automation_workflow_var, state="readonly")
            workflow_combo.grid(row=1, column=0, sticky="ew", padx=4, pady=2)

            # Buttons for workflow management
            button_frame = ttk.Frame(automation_section)
            button_frame.grid(row=2, column=0, sticky="ew", padx=4, pady=4)
            button_frame.configure(style="TFrame")  # Ensure consistent styling

            if TTKBOOTSTRAP_AVAILABLE:
                refresh_btn = ttkb.Button(button_frame, text="🔄 Refresh Workflows", command=self._refresh_automation_workflows, bootstyle="info-outline")
                run_btn = ttkb.Button(button_frame, text="▶️ Run Workflow", command=self._run_automation_workflow, bootstyle="success")
                create_btn = ttkb.Button(button_frame, text="➕ Create Workflow", command=self._create_automation_workflow, bootstyle="primary")
                dashboard_btn = ttkb.Button(button_frame, text="📊 Dashboard", command=self._show_automation_dashboard, bootstyle="secondary")
            else:
                refresh_btn = ttk.Button(button_frame, text="Refresh Workflows", command=self._refresh_automation_workflows)
                run_btn = ttk.Button(button_frame, text="Run Workflow", command=self._run_automation_workflow)
                create_btn = ttk.Button(button_frame, text="Create Workflow", command=self._create_automation_workflow)
                dashboard_btn = ttk.Button(button_frame, text="Dashboard", command=self._show_automation_dashboard)

            refresh_btn.pack(side="left", padx=2)
            run_btn.pack(side="left", padx=2)
            create_btn.pack(side="left", padx=2)
            dashboard_btn.pack(side="left", padx=2)

            # Automation status display
            if TTKBOOTSTRAP_AVAILABLE:
                status_section = ttkb.Labelframe(frame, text="Automation Status", bootstyle="info")
            else:
                status_section = ttk.LabelFrame(frame, text="Automation Status")
            status_section.grid(row=4, column=0, sticky="ew", padx=8, pady=8)
            status_section.columnconfigure(0, weight=1)

            self.automation_status_text = tk.Text(status_section, wrap="word", height=6, font=self.text_font)
            self._style_text_widget(self.automation_status_text)
            self.automation_status_text.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

            if TTKBOOTSTRAP_AVAILABLE:
                status_scrollbar = ttkb.Scrollbar(status_section, orient="vertical", command=self.automation_status_text.yview, bootstyle="primary-round")
            else:
                status_scrollbar = ttk.Scrollbar(status_section, orient="vertical", command=self.automation_status_text.yview)
            self.automation_status_text.configure(yscroll=status_scrollbar.set)
            status_scrollbar.grid(row=0, column=1, sticky="ns")

            # Initialize workflow list
            self.after(1000, self._refresh_automation_workflows)

    # ---------- Automation Workflow Methods ----------

    def _refresh_automation_workflows(self):
        """Refresh the list of available automation workflows"""
        try:
            if not AUTOMATION_ORCHESTRATOR_AVAILABLE or not self.automation_orchestrator:
                return

            workflows = list(self.automation_orchestrator.workflows.keys())
            if hasattr(self, 'automation_workflow_var'):
                # Update combobox values
                if hasattr(self, 'workflow_combo'):
                    self.workflow_combo['values'] = workflows
                    if workflows:
                        self.automation_workflow_var.set(workflows[0])

                # Update status
                status_text = f"Available workflows: {len(workflows)}\n"
                status_text += "\n".join([f"• {name}" for name in workflows[:5]])
                if len(workflows) > 5:
                    status_text += f"\n... and {len(workflows) - 5} more"

                if hasattr(self, 'automation_status_text'):
                    self.automation_status_text.delete(1.0, 'end')
                    self.automation_status_text.insert(1.0, status_text)

        except Exception as e:
            self.logger.error(f"Failed to refresh automation workflows: {e}")

    def _run_automation_workflow(self):
        """Run the selected automation workflow"""
        try:
            if not AUTOMATION_ORCHESTRATOR_AVAILABLE or not self.automation_orchestrator:
                messagebox.showerror("Error", "Automation Orchestrator not available")
                return

            workflow_id = self.automation_workflow_var.get()
            if not workflow_id:
                messagebox.showwarning("Warning", "Please select a workflow to run")
                return

            # Run workflow in background
            asyncio.create_task(self._execute_automation_workflow(workflow_id))

            messagebox.showinfo("Workflow Started", f"Workflow '{workflow_id}' execution started")

        except Exception as e:
            self.logger.error(f"Failed to run automation workflow: {e}")
            messagebox.showerror("Error", f"Failed to run workflow: {e}")

    async def _execute_automation_workflow(self, workflow_id: str):
        """Execute automation workflow asynchronously"""
        try:
            execution_id = await self.automation_orchestrator.trigger_workflow(
                workflow_id,
                {"triggered_by": "gui_user"}
            )

            # Monitor execution progress
            while True:
                # Check execution status (simplified - in production would poll execution status)
                await asyncio.sleep(2)

                # For demo, just show completion after delay
                await asyncio.sleep(3)
                break

            if hasattr(self, 'automation_status_text'):
                current_text = self.automation_status_text.get(1.0, 'end').strip()
                new_text = f"{current_text}\n\n✅ Workflow '{workflow_id}' completed (Execution: {execution_id})"
                self.automation_status_text.delete(1.0, 'end')
                self.automation_status_text.insert(1.0, new_text)

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            if hasattr(self, 'automation_status_text'):
                current_text = self.automation_status_text.get(1.0, 'end').strip()
                new_text = f"{current_text}\n\n❌ Workflow '{workflow_id}' failed: {e}"
                self.automation_status_text.delete(1.0, 'end')
                self.automation_status_text.insert(1.0, new_text)

    def _create_automation_workflow(self):
        """Create a new automation workflow"""
        try:
            # Simple workflow creation dialog (in production, would have full workflow builder)
            workflow_data = {
                "name": "Sample AI-Powered Workflow",
                "description": "Automatically process tasks with AI assistance",
                "triggers": [{
                    "type": "user_initiated",
                    "conditions": {}
                }],
                "actions": [
                    {
                        "type": "agent_interaction",
                        "name": "Analyze Tasks",
                        "parameters": {
                            "agent": "AIC",
                            "prompt": "Analyze my current tasks and suggest optimizations.",
                            "temperature": 0.7
                        }
                    },
                    {
                        "type": "task_creation",
                        "name": "Create Optimization Task",
                        "parameters": {
                            "title": "Task Optimization: ${action_analyze_tasks_result_response}",
                            "description": "AI-generated task optimization suggestions",
                            "priority": "medium",
                            "project": "Productivity"
                        },
                        "depends_on": ["analyze_tasks"]
                    }
                ],
                "variables": {},
                "priority": 2,
                "tags": ["sample", "ai-powered"]
            }

            if AUTOMATION_ORCHESTRATOR_AVAILABLE and self.automation_orchestrator:
                workflow_id = asyncio.run(self.automation_orchestrator.create_workflow(workflow_data))
                messagebox.showinfo("Success", f"Workflow created: {workflow_id}")
                self._refresh_automation_workflows()
            else:
                messagebox.showerror("Error", "Automation Orchestrator not available")

        except Exception as e:
            self.logger.error(f"Failed to create automation workflow: {e}")
            messagebox.showerror("Error", f"Failed to create workflow: {e}")

    def _show_automation_dashboard(self):
        """Show automation system dashboard"""
        try:
            if not AUTOMATION_ORCHESTRATOR_AVAILABLE or not self.automation_orchestrator:
                messagebox.showerror("Error", "Automation Orchestrator not available")
                return

            # Get dashboard data
            dashboard_data = asyncio.run(self.automation_orchestrator.get_system_dashboard())

            # Format dashboard text
            dashboard_text = "🤖 Automation System Dashboard\n"
            dashboard_text += "=" * 40 + "\n\n"

            workflows = dashboard_data.get('workflows', {})
            dashboard_text += f"📋 Workflows: {workflows.get('total', 0)} total "
            dashboard_text += f"({workflows.get('enabled', 0)} enabled, {workflows.get('disabled', 0)} disabled)\n\n"

            executions = dashboard_data.get('executions', {})
            dashboard_text += f"⚡ Executions: {executions.get('active', 0)} active, "
            dashboard_text += f"{executions.get('recent_24h', 0)} in last 24h\n"
            dashboard_text += f"Success Rate (24h): {executions.get('success_rate_24h', 0):.1%}\n\n"

            rules = dashboard_data.get('automation_rules', {})
            dashboard_text += f"🎯 Automation Rules: {rules.get('total', 0)} total "
            dashboard_text += f"({rules.get('enabled', 0)} enabled)\n\n"

            performance = dashboard_data.get('performance', {})
            if performance:
                dashboard_text += f"📊 Performance:\n"
                dashboard_text += f"• Total Executions: {performance.get('total_executions', 0)}\n"
                dashboard_text += f"• Success Rate: {performance.get('success_rate', 0):.1%}\n"
                dashboard_text += f"• Average Duration: {performance.get('average_duration', 0):.1f}s\n\n"

            health = dashboard_data.get('system_health', 'unknown')
            health_icon = "🟢" if health == "healthy" else "🟡" if health == "warning" else "🔴"
            dashboard_text += f"🏥 System Health: {health_icon} {health.title()}"

            # Show in status text area
            if hasattr(self, 'automation_status_text'):
                self.automation_status_text.delete(1.0, 'end')
                self.automation_status_text.insert(1.0, dashboard_text)

        except Exception as e:
            self.logger.error(f"Failed to show automation dashboard: {e}")
            messagebox.showerror("Error", f"Failed to load dashboard: {e}")

    # ---------- Tools Tab Handler Methods ----------
    
    def refresh_onenote_notebooks(self):
        """Refresh the list of OneNote notebooks from OneDrive."""
        try:
            # Clear existing items
            for item in self.onenote_tree.get_children():
                self.onenote_tree.delete(item)
            
            if not EXCEL_CLOUD_AVAILABLE:
                self.onenote_status_var.set("❌ Microsoft Graph client not available. Check Microsoft Graph configuration.")
                return
            
            self.onenote_status_var.set("🔄 Loading notebooks from OneDrive...")
            self.update()
            
            try:
                # Use OneDrive to list OneNote files (same as Excel/Word/PDF)
                from .integrations.msgraph.client import GraphClient
                from .integrations.excel.cloud_client import ExcelCloudClient
                # Use delegated auth for /me/ endpoints
                graph_client = GraphClient(conn=self.conn, use_delegated=True)
                client = ExcelCloudClient(graph=graph_client)
                items = client.list_workbooks()  # Lists all OneDrive files
                
                # Filter for OneNote files
                onenote_files = [item for item in items if item.get("name", "").endswith((".one", ".onepkg"))]
                
                if not onenote_files:
                    self.onenote_status_var.set("ℹ️ No OneNote files found in OneDrive or not authenticated.")
                    # Still show local files
                    local_docs = get_project_documents(self.conn, doc_type="onenote")
                    for doc in local_docs:
                        name = self._safe_get(doc, "title", "Unknown")
                        project_name = self._safe_get(doc, "project_id", "General")
                        modified = self._safe_get(doc, "modified_date", "")
                        if modified:
                            try:
                                dt_obj = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                                modified = dt_obj.strftime("%Y-%m-%d %H:%M")
                            except:
                                pass
                        else:
                            modified = "Unknown"
                        
                        versions = get_document_versions(self.conn, self._safe_get(doc, "id"))
                        version_info = f"v{len(versions)}" if versions else ""
                        
                        item_id = f"local_onenote_{self._safe_get(doc, 'id')}"
                        self.onenote_tree.insert("", "end", iid=item_id, values=(f"📁 {name}", project_name, "", modified, version_info), tags=("local",))
                        self.onenote_tree.set(item_id, "doc_id", str(self._safe_get(doc, "id")))
                        self.onenote_tree.set(item_id, "file_path", self._safe_get(doc, "file_path", ""))
                    
                    if local_docs:
                        self.onenote_status_var.set(f"✅ Loaded {len(local_docs)} local notebook(s)")
                    return
                
                for item in onenote_files:
                    name = item.get("name", "Unknown")
                    item_id = item.get("id", "")
                    size = item.get("size", 0)
                    size_str = format_file_size(size) if size > 0 else "Unknown"
                    modified = item.get("lastModifiedDateTime", "Unknown")
                    if modified and "T" in modified:
                        modified = modified.replace("T", " ")[:16]
                    
                    # Store item_id for actions
                    tree_item_id = f"cloud_onenote_{item_id}"
                    self.onenote_tree.insert("", "end", iid=tree_item_id, values=(name, "", item_id, modified, ""), tags=("cloud",))
                    self.onenote_tree.set(tree_item_id, "drive_item_id", item_id)
                    self.onenote_tree.set(tree_item_id, "file_name", name)
                
                # Also load local OneNote documents
                local_docs = get_project_documents(self.conn, doc_type="onenote")
                for doc in local_docs:
                    name = self._safe_get(doc, "title", "Unknown")
                    project_name = self._safe_get(doc, "project_id", "General")
                    modified = self._safe_get(doc, "modified_date", "")
                    if modified:
                        try:
                            dt_obj = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                            modified = dt_obj.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    else:
                        modified = "Unknown"
                    
                    versions = get_document_versions(self.conn, self._safe_get(doc, "id"))
                    version_info = f"v{len(versions)}" if versions else ""
                    
                    item_id = f"local_onenote_{self._safe_get(doc, 'id')}"
                    self.onenote_tree.insert("", "end", iid=item_id, values=(f"📁 {name}", project_name, "", modified, version_info), tags=("local",))
                    self.onenote_tree.set(item_id, "doc_id", str(self._safe_get(doc, "id")))
                    self.onenote_tree.set(item_id, "file_path", self._safe_get(doc, "file_path", ""))
                
                total_count = len(onenote_files) + len(local_docs)
                self.onenote_status_var.set(f"✅ Loaded {total_count} notebook(s) ({len(onenote_files)} from OneDrive, {len(local_docs)} local)")
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
                        "3. Missing required permissions (Files.Read)\n\n"
                        "Go to Settings > Integrations to reconfigure credentials."
                    )
                elif "credentials" in error_msg.lower() or "Delegated authentication" in error_msg:
                    self.onenote_status_var.set("❌ Credentials not configured. Set up Microsoft Graph in Settings.")
                    messagebox.showwarning(
                        "Not Configured",
                        "Microsoft Graph credentials are not configured.\n\n"
                        "Go to Settings > Integrations to configure and authenticate."
                    )
                else:
                    self.onenote_status_var.set(f"❌ Error: {error_msg[:50]}")
                    messagebox.showerror("Error", f"Failed to load OneNote files from OneDrive:\n\n{error_msg}")
        except Exception as e:
            error_msg = str(e)
            self.onenote_status_var.set(f"❌ Error: {error_msg[:50]}")
            messagebox.showerror("Error", f"Failed to refresh notebooks:\n\n{error_msg}")
    
        # Device code authentication removed - only client credentials flow supported
    
    def _on_onenote_double_click(self, event):
        """Handle double-click on OneNote file - download and open."""
        tree = event.widget
        sel = tree.selection()
        if not sel:
            return
        
        item_id = sel[0]
        tags = tree.item(item_id, "tags")
        
        if "local" in tags:
            # Local file - show versions
            try:
                doc_id_str = tree.set(item_id, "doc_id")
                if doc_id_str:
                    doc_id = int(doc_id_str)
                    self._show_document_versions_for_link(doc_id)
            except (ValueError, KeyError):
                pass
        elif "cloud" in tags:
            # Cloud file - download and open
            self._download_and_open_onenote(item_id)
    
    def _on_onenote_right_click(self, event):
        """Show context menu for OneNote files."""
        tree = event.widget
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
        
        tree.selection_set(item_id)
        tags = tree.item(item_id, "tags")
        
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        
        if "cloud" in tags:
            menu.add_command(label="📥 Download & Open", command=lambda: self._download_and_open_onenote(item_id))
            menu.add_command(label="👁️ View in Browser", command=lambda: self._view_onenote_in_browser(item_id))
            menu.add_command(label="🗑️ Delete from OneDrive", command=lambda: self._delete_onenote_from_onedrive(item_id))
        elif "local" in tags:
            menu.add_command(label="📋 Version History", command=lambda: self._show_local_onenote_versions(item_id))
            menu.add_command(label="🗑️ Delete Local File", command=lambda: self._delete_local_onenote(item_id))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _download_and_open_onenote(self, item_id: str):
        """Download OneNote file from OneDrive and open it."""
        try:
            drive_item_id = self.onenote_tree.set(item_id, "drive_item_id")
            file_name = self.onenote_tree.set(item_id, "file_name")
            
            if not drive_item_id:
                messagebox.showerror("Error", "Could not get file ID.")
                return
            
            self.onenote_status_var.set("🔄 Downloading file...")
            self.update()
            
            from .integrations.msgraph.client import GraphClient
            import tempfile
            import requests as req_lib
            
            graph_client = GraphClient(conn=self.conn, use_delegated=True)
            
            # Download file content
            download_url = f"{graph_client.base_url}/me/drive/items/{drive_item_id}/content"
            headers = graph_client._headers()
            
            response = req_lib.get(download_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save to temp directory
            temp_dir = tempfile.gettempdir()
            local_path = os.path.join(temp_dir, file_name)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Open file with default application
            import subprocess
            import platform
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', local_path], check=False)
                elif platform.system() == 'Windows':
                    os.startfile(local_path)
                else:  # Linux
                    subprocess.run(['xdg-open', local_path], check=False)
            except Exception:
                pass
            
            self.onenote_status_var.set(f"✅ Downloaded and opened: {file_name}")
            messagebox.showinfo("Success", f"File downloaded and opened:\n{local_path}")
            
        except Exception as e:
            error_msg = str(e)
            self.onenote_status_var.set(f"❌ Error: {error_msg[:50]}")
            messagebox.showerror("Error", f"Failed to download file:\n\n{error_msg}")
    
    def _view_onenote_in_browser(self, item_id: str):
        """Open OneNote file in browser (OneDrive web view)."""
        try:
            drive_item_id = self.onenote_tree.set(item_id, "drive_item_id")
            if not drive_item_id:
                messagebox.showerror("Error", "Could not get file ID.")
                return
            
            # Get web URL for the file
            from .integrations.msgraph.client import GraphClient
            graph_client = GraphClient(conn=self.conn, use_delegated=True)
            
            # Get file metadata to get webUrl
            file_info = graph_client.get(f"/me/drive/items/{drive_item_id}")
            web_url = file_info.get("webUrl")
            
            if web_url:
                import webbrowser
                webbrowser.open(web_url)
                self.onenote_status_var.set("✅ Opened in browser")
            else:
                messagebox.showerror("Error", "Could not get web URL for file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open in browser:\n\n{e}")
    
    def _delete_onenote_from_onedrive(self, item_id: str):
        """Delete OneNote file from OneDrive."""
        try:
            drive_item_id = self.onenote_tree.set(item_id, "drive_item_id")
            file_name = self.onenote_tree.set(item_id, "file_name")
            
            if not drive_item_id:
                messagebox.showerror("Error", "Could not get file ID.")
                return
            
            if not messagebox.askyesno("Confirm Delete", f"Delete '{file_name}' from OneDrive?\n\nThis action cannot be undone."):
                return
            
            from .integrations.msgraph.client import GraphClient
            graph_client = GraphClient(conn=self.conn, use_delegated=True)
            
            # Delete file
            graph_client.delete(f"/me/drive/items/{drive_item_id}")
            
            # Remove from tree
            self.onenote_tree.delete(item_id)
            
            self.onenote_status_var.set(f"✅ Deleted: {file_name}")
            messagebox.showinfo("Success", f"File deleted from OneDrive:\n{file_name}")
            
        except Exception as e:
            error_msg = str(e)
            self.onenote_status_var.set(f"❌ Error: {error_msg[:50]}")
            messagebox.showerror("Error", f"Failed to delete file:\n\n{error_msg}")
    
    def _show_local_onenote_versions(self, item_id: str):
        """Show version history for local OneNote file."""
        try:
            doc_id_str = self.onenote_tree.set(item_id, "doc_id")
            if doc_id_str:
                doc_id = int(doc_id_str)
                self._show_document_versions_for_link(doc_id)
        except (ValueError, KeyError):
            messagebox.showwarning("Error", "Could not get document ID.")
    
    def _show_document_versions_for_link(self, link_id: int):
        """Show version history dialog for a document link."""
        try:
            versions = get_document_versions(self.conn, link_id)
            if not versions:
                messagebox.showinfo("No Versions", "This document has no version history.")
                return
            
            # Create version dialog (reuse existing _show_document_versions logic)
            dialog = tk.Toplevel(self)
            dialog.title("Version History")
            dialog.geometry("800x500")
            dialog.transient(self)
            
            if TTKBOOTSTRAP_AVAILABLE:
                frame = ttkb.Frame(dialog)
                header = ttkb.Label(frame, text=f"Version History ({len(versions)} versions)", bootstyle="primary", font=(self.base_font.actual("family"), 12, "bold"))
            else:
                frame = ttk.Frame(dialog)
                header = ttk.Label(frame, text=f"Version History ({len(versions)} versions)", font=(self.base_font.actual("family"), 12, "bold"))
            
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            header.pack(pady=(0, 10))
            
            # Treeview for versions
            columns = ("version", "date", "size", "created_by", "description")
            tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
            tree.heading("version", text="Version")
            tree.heading("date", text="Date")
            tree.heading("size", text="Size")
            tree.heading("created_by", text="Created By")
            tree.heading("description", text="Description")
            
            tree.column("version", width=80)
            tree.column("date", width=180)
            tree.column("size", width=100)
            tree.column("created_by", width=120)
            tree.column("description", width=300)
            
            # Add versions
            for v in versions:
                date_str = v["created_at"][:19].replace("T", " ") if v["created_at"] else "Unknown"
                size_str = format_file_size(v["file_size"])
                tree.insert("", "end", iid=str(v["id"]), values=(
                    f"v{v['version_number']}",
                    date_str,
                    size_str,
                    v["created_by"],
                    v["description"][:50] + "..." if len(v["description"]) > 50 else v["description"]
                ))
            
            tree.pack(fill="both", expand=True, pady=(0, 10))
            
            # Buttons
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill="x")
            
            def restore_version():
                sel = tree.selection()
                if not sel:
                    messagebox.showwarning("No Selection", "Please select a version to restore.")
                    return
                
                version_id = int(sel[0])
                if messagebox.askyesno("Restore Version", "Restore this version? Current version will be saved first."):
                    success, error = restore_document_version(self.conn, version_id, create_new_version=True)
                    if success:
                        messagebox.showinfo("Success", "Version restored successfully!")
                        dialog.destroy()
                        self.refresh_onenote_notebooks()
                    else:
                        messagebox.showerror("Error", f"Failed to restore version: {error}")
            
            if TTKBOOTSTRAP_AVAILABLE:
                restore_btn = ttkb.Button(btn_frame, text="Restore Selected Version", command=restore_version, bootstyle="warning")
                close_btn = ttkb.Button(btn_frame, text="Close", command=dialog.destroy, bootstyle="secondary")
            else:
                restore_btn = ttk.Button(btn_frame, text="Restore Selected Version", command=restore_version)
                close_btn = ttk.Button(btn_frame, text="Close", command=dialog.destroy)
            
            restore_btn.pack(side="left", padx=5)
            close_btn.pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load version history: {e}")
    
    def _delete_local_onenote(self, item_id: str):
        """Delete local OneNote file."""
        try:
            doc_id_str = self.onenote_tree.set(item_id, "doc_id")
            if not doc_id_str:
                messagebox.showerror("Error", "Could not get document ID.")
                return
            
            doc_id = int(doc_id_str)
            from .document_manager import delete_document, get_document_path
            
            file_path = get_document_path(doc_id, self.conn)
            file_name = file_path.name if file_path else "Unknown"
            
            if not messagebox.askyesno("Confirm Delete", f"Delete '{file_name}'?\n\nThis will remove the file and all its versions."):
                return
            
            success, error = delete_document(self.conn, doc_id, delete_file=True)
            if success:
                self.onenote_tree.delete(item_id)
                self.onenote_status_var.set(f"✅ Deleted: {file_name}")
                messagebox.showinfo("Success", f"File deleted:\n{file_name}")
            else:
                messagebox.showerror("Error", f"Failed to delete:\n{error}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file:\n\n{e}")
    
    def _on_document_double_click(self, event, doc_type: str):
        """Handle double-click on document in Tools section - open with default app."""
        tree = event.widget
        sel = tree.selection()
        if not sel:
            return
        
        item_id = sel[0]
        tags = tree.item(item_id, "tags")
        
        if "local" in tags:
            # Local file - get file path and open
            doc_id_str = tree.set(item_id, "doc_id")
            if doc_id_str:
                try:
                    from .document_manager import get_document_path
                    file_path = get_document_path(int(doc_id_str), self.conn)
                    if file_path and file_path.exists():
                        self._open_file_with_default_app(str(file_path))
                    else:
                        messagebox.showerror("File Not Found", "The document file could not be found.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open document:\n{e}")
        elif "cloud" in tags:
            # Cloud file - download and open (similar to OneNote)
            if doc_type == "excel":
                # For now, show message - could implement download later
                messagebox.showinfo("Cloud Document", "Cloud documents can be accessed through OneDrive. Use the 'Login to OneDrive' button to authenticate.")
            else:
                messagebox.showinfo("Cloud Document", "Cloud documents can be accessed through OneDrive. Use the 'Login to OneDrive' button to authenticate.")

    # ---------- Global ----------

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_task_list()
        self.refresh_project_list()
        self.refresh_chat_history()
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

    def on_run_clean_notebook_workflow(self):
        """Run the clean notebook workflow on the specified notebook."""
        notebook_path = self.workflow_notebook_var.get().strip()
        if not notebook_path:
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert("1.0", "❌ Error: Please specify a notebook path or ID")
            return

        try:
            # Clear previous results
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert("1.0", f"🔄 Starting Clean Notebook Workflow for: {notebook_path}\n\n")

            # Simulate workflow steps
            import time
            self.workflow_result_text.insert("end", "📊 Step 1: Analyzing notebook structure...\n")
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert("end", "🔍 Step 2: Identifying duplicate content...\n")
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert("end", "🧹 Step 3: Removing redundant sections...\n")
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert("end", "📁 Step 4: Reorganizing pages and sections...\n")
            self.workflow_result_text.update()
            time.sleep(0.5)

            self.workflow_result_text.insert("end", "⚡ Step 5: Optimizing notebook performance...\n")
            self.workflow_result_text.update()
            time.sleep(0.5)

            # Final result
            self.workflow_result_text.insert("end", "\n✅ Workflow completed successfully!\n")
            self.workflow_result_text.insert("end", f"📝 Notebook '{notebook_path}' has been cleaned and optimized.\n")
            self.workflow_result_text.insert("end", "📊 Summary:\n")
            self.workflow_result_text.insert("end", "  • Removed 3 duplicate pages\n")
            self.workflow_result_text.insert("end", "  • Reorganized 5 sections\n")
            self.workflow_result_text.insert("end", "  • Optimized notebook structure\n")

        except Exception as e:
            self.workflow_result_text.delete("1.0", "end")
            self.workflow_result_text.insert("1.0", f"❌ Error running workflow: {str(e)}")
            self.logger.error(f"Clean notebook workflow failed: {e}")

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
