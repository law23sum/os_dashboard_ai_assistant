"""Shared catalog of command metadata for the Tools experience.

The Tkinter GUI, FastAPI backends, and the new React/Electron clients
consume the same command definitions so that quick actions stay aligned
regardless of platform.
"""

from __future__ import annotations

from typing import Dict, List

SPEC_SHEET_COMMANDS: List[Dict[str, str]] = [
    {
        "label": "Clone repository",
        "command": "git clone https://github.com/yourusername/os-dashboard-ai-assistant.git",
        "description": "Clone the AI OS repo from GitHub.",
    },
    {
        "label": "Setup script",
        "command": "python tools/bootstrap.py",
        "description": "Run bootstrap script to initialize the project from source.",
    },
    {
        "label": "Install dependencies",
        "command": "pip install -r requirements.txt",
        "description": "Install Python dependencies from requirements.txt.",
    },
    {
        "label": "Run application (CLI)",
        "command": "python start_ui.py",
        "description": "Launch the unified desktop/web UI launcher.",
    },
    {
        "label": "Run main app",
        "command": "python main.py",
        "description": "Launch the core application entrypoint.",
    },
    {
        "label": "Launch GUI dashboard",
        "command": "python_os assistant_hub_gui/main.py",
        "description": "Start the GUI dashboard (spec lists python_os alias twice).",
    },
    {
        "label": "Docker dev (basic)",
        "command": "docker-compose up -d",
        "description": "Bring up the basic development Docker stack.",
    },
    {
        "label": "Docker full stack",
        "command": "docker-compose --profile full up -d",
        "description": "Start the full production stack with monitoring.",
    },
    {
        "label": "Docker GUI profile",
        "command": "docker-compose --profile gui up -d",
        "description": "Launch the GUI-enabled Docker profile.",
    },
    {
        "label": "Create credentials dir",
        "command": "mkdir -p config/credentials",
        "description": "Create configuration credentials directory.",
    },
    {
        "label": "Copy config template",
        "command": "cp config/config.yaml config/config.local.yaml",
        "description": "Copy base config to local override file.",
    },
    {
        "label": "Run tests (pytest)",
        "command": "pytest tests/",
        "description": "Execute full pytest suite (listed twice in spec).",
    },
    {
        "label": "Security dashboard",
        "command": "python security_monitor.py dashboard",
        "description": "Open security monitor dashboard view.",
    },
    {
        "label": "Compliance (GDPR)",
        "command": "python security_monitor.py compliance gdpr",
        "description": "Run GDPR compliance assessment routine.",
    },
    {
        "label": "Analyze threats (auth.log)",
        "command": "python security_monitor.py analyze-threats /var/log/auth.log",
        "description": "Analyze authentication log for threats.",
    },
    {
        "label": "Security incidents",
        "command": "python security_monitor.py incidents",
        "description": "Check security incidents dashboard.",
    },
    {
        "label": "Audit logs (user, 7d)",
        "command": 'python security_monitor.py audit --user "username" --days 7',
        "description": "View audit logs for a user over the last 7 days.",
    },
    {
        "label": "Analyze threats (access.log)",
        "command": "python security_monitor.py analyze-threats access.log",
        "description": "Analyze access.log for threats (spec example).",
    },
    {
        "label": "Plugins: list",
        "command": "python plugin_manager.py list",
        "description": "List available marketplace plugins.",
    },
    {
        "label": "Plugins: search weather",
        "command": 'python plugin_manager.py list --query "weather" --type integration',
        "description": "Search plugins filtered by keyword and type.",
    },
    {
        "label": "Plugins: show weather",
        "command": "python plugin_manager.py show weather-integration",
        "description": "Show detailed info for weather-integration plugin.",
    },
    {
        "label": "Plugins: install weather",
        "command": "python plugin_manager.py install weather-integration",
        "description": "Install the weather-integration plugin.",
    },
    {
        "label": "Plugins: install versioned",
        "command": "python plugin_manager.py install weather-integration --version 1.0.0",
        "description": "Install a specific plugin version.",
    },
    {
        "label": "Plugins: uninstall weather",
        "command": "python plugin_manager.py uninstall weather-integration",
        "description": "Uninstall the weather-integration plugin.",
    },
    {
        "label": "Plugins: stats",
        "command": "python plugin_manager.py stats",
        "description": "View marketplace statistics.",
    },
    {
        "label": "Compile modules",
        "command": "python -m compileall assistant_hub",
        "description": "Byte-compile the assistant_hub package.",
    },
    {
        "label": "Neural architecture search",
        "command": "python neural_architecture_search.py",
        "description": "Run neural architecture search workflow.",
    },
    {
        "label": "Unit tests (discover)",
        "command": "python -m unittest discover tests",
        "description": "Discover and execute unit tests.",
    },
    {
        "label": "Unit test ai_assistant",
        "command": "python -m unittest tests.test_ai_assistant",
        "description": "Targeted ai_assistant test module.",
    },
    {
        "label": "Unit test database",
        "command": "python -m unittest tests.test_database",
        "description": "Database-specific tests.",
    },
    {
        "label": "Unit test task automation",
        "command": "python -m unittest tests.test_task_automation",
        "description": "Task automation test module.",
    },
    {
        "label": "Unit tests verbose",
        "command": "python -m unittest discover tests -v",
        "description": "Verbose unittest discovery run.",
    },
    {
        "label": "Import smoke test",
        "command": "python -c \"from os_dashboard_orchestrator import OSDashboard; print('Import successful')\"",
        "description": "Quick import verification of OSDashboard.",
    },
    {
        "label": "Build executable (script)",
        "command": "./build.sh",
        "description": "Run helper build script to create executables.",
    },
    {
        "label": "Install PyInstaller",
        "command": "pip install pyinstaller",
        "description": "Install PyInstaller for manual builds.",
    },
    {
        "label": "Build executable (PyInstaller)",
        "command": "python build-executable.py",
        "description": "Build executables manually with PyInstaller.",
    },
]

BASE_BACKEND_CLI = "python assistant_hub_gui/assistant_hub/ui/terminal/cli.py"

BACKEND_CLI_COMMANDS: List[Dict[str, str]] = [
    {
        "label": "CLI: Projects list",
        "command": f"{BASE_BACKEND_CLI} projects list",
        "description": "List all projects via CLI backend.",
    },
    {
        "label": "CLI: Projects create sample",
        "command": f"{BASE_BACKEND_CLI} projects create gui-sample-project",
        "description": "Create a sample project to verify CLI wiring.",
    },
    {
        "label": "CLI: History (20 entries)",
        "command": f"{BASE_BACKEND_CLI} history --limit 20",
        "description": "Show recent actions from git/agents.",
    },
    {
        "label": "CLI: History (Aria, 10)",
        "command": f"{BASE_BACKEND_CLI} history --agent Aria --limit 10",
        "description": "Filter history by Aria agent.",
    },
    {
        "label": "CLI: Excel summarize sample",
        "command": f'{BASE_BACKEND_CLI} excel summarize "assistant_hub_gui/documents/Samples/Operational Metrics Workbook.xlsx" --sheet "Sheet1" --agent AIC',
        "description": "Summarize bundled sample workbook (Sheet1) with AIC.",
    },
    {
        "label": "CLI: Word rewrite sample",
        "command": f'{BASE_BACKEND_CLI} word rewrite "assistant_hub_gui/documents/Samples/Governed Brief Template.docx" --agent Aria',
        "description": "Rewrite bundled sample doc with Aria agent.",
    },
    {
        "label": "CLI: OneNote list notebooks",
        "command": f"{BASE_BACKEND_CLI} onenote list-notebooks",
        "description": "List notebooks (requires OneNote auth).",
    },
]

BACKEND_CLI_TEMPLATES: List[Dict[str, str]] = [
    {
        "label": "Template: Projects view <id>",
        "command": f"{BASE_BACKEND_CLI} projects view <project_id>",
        "description": "Replace <project_id> then hit Run.",
    },
    {
        "label": "Template: Word draft",
        "command": f"{BASE_BACKEND_CLI} word draft --project proj-osdash --template <template_name> --agent Aria",
        "description": "Set template/project as needed, then Run.",
    },
    {
        "label": "Template: Word rewrite (custom)",
        "command": f'{BASE_BACKEND_CLI} word rewrite "<path_to_docx>" --agent Aria',
        "description": "Point to your docx before running.",
    },
    {
        "label": "Template: Excel summarize (custom)",
        "command": f'{BASE_BACKEND_CLI} excel summarize "<path_to_excel>" --sheet Sheet1 --agent AIC',
        "description": "Set your workbook path + sheet.",
    },
    {
        "label": "Template: OneNote list sections",
        "command": f"{BASE_BACKEND_CLI} onenote list-sections <notebook_id>",
        "description": "Insert OneNote notebook ID.",
    },
    {
        "label": "Template: OneNote list pages",
        "command": f"{BASE_BACKEND_CLI} onenote list-pages <section_id>",
        "description": "Insert OneNote section ID.",
    },
    {
        "label": "Template: OneNote clean section",
        "command": f"{BASE_BACKEND_CLI} onenote clean-section <section_id> --agent AIC",
        "description": "Add section ID before running clean.",
    },
    {
        "label": "Template: OneNote summarize page",
        "command": f"{BASE_BACKEND_CLI} onenote summarize-page <page_id> --agent Aria",
        "description": "Add OneNote page ID before running summary.",
    },
]


def command_catalog() -> Dict[str, List[Dict[str, str]]]:
    """Return catalog in a JSON-serializable format."""

    return {
        "spec_sheet": SPEC_SHEET_COMMANDS,
        "backend_cli": BACKEND_CLI_COMMANDS,
        "templates": BACKEND_CLI_TEMPLATES,
    }
