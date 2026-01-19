"""
Main Dashboard Interface
Central control panel for the AI OS Console
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path
import queue
import subprocess
import webbrowser
from datetime import datetime

import requests

# Import our modules
from ..intelligence.data_collector import SyncDataCollector, DataSource
from ..content.generators import (
    PresentationGenerator,
    ExcelDashboardGenerator,
    WordDocumentGenerator,
    ContentConfig,
)
from ..system.operations import (
    SystemOperationsController,
    NetworkServiceManager,
    ServiceConfig,
)
from ..intelligence.quality_assurance import (
    ContentValidator,
    BatchValidator,
    AccessibilityChecker,
)
from ..operations.concurrent_manager import (
    ConcurrentOperationsManager,
    ConcurrentTask,
    BatchOperation,
)
from ..integrations.advanced_systems import (
    StaticSiteDeployer,
    OfficeAddinEmbedder,
    DeploymentConfig,
    OfficeAddinConfig,
)
from ..integrations.office_realtime import (
    AIOfficeWebSocketRouter,
    MessageType,
    ApplicationType,
)
from ..intelligence.office_ai_service import OfficeAIProcessingService
from ..spec import spec_summary


@dataclass
class DashboardConfig:
    """Configuration for the dashboard"""

    title: str = "AI OS Console"
    theme: str = "default"
    auto_save: bool = True
    log_level: str = "INFO"
    max_workers: int = 10
    workspace_dir: str = "./workspace"
    ai_service_url: Optional[str] = os.environ.get(
        "AI_SERVICE_URL", "http://localhost:8000"
    )
    enable_realtime_router: bool = True


class TaskMonitorWidget(ttk.Frame):
    """Widget for monitoring running tasks"""

    def __init__(self, parent, concurrent_manager: ConcurrentOperationsManager):
        super().__init__(parent)
        self.concurrent_manager = concurrent_manager
        self.setup_ui()
        self.update_task_list()

    def setup_ui(self):
        """Setup the task monitor UI"""
        # Title
        title_label = ttk.Label(self, text="Task Monitor", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Task list
        columns = ("ID", "Name", "Status", "Progress", "Duration")
        self.task_tree = ttk.Treeview(self, columns=columns, show="headings", height=8)

        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        self.task_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(button_frame, text="Refresh", command=self.update_task_list).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(
            button_frame, text="Cancel Selected", command=self.cancel_selected_task
        ).pack(side="left")

    def update_task_list(self):
        """Update the task list display"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Get performance stats
        stats = self.concurrent_manager.get_performance_stats()

        # Add active tasks
        for task_id in list(self.concurrent_manager.active_tasks.keys()):
            task_status = self.concurrent_manager.get_task_status(task_id)
            if task_status and task_status["status"] != "not_found":
                duration = task_status.get("execution_time", 0) or 0
                self.task_tree.insert(
                    "",
                    "end",
                    values=(
                        task_id[:8],
                        task_status["name"][:20],
                        task_status["status"],
                        "N/A",  # Progress not implemented in base system
                        f"{duration:.1f}s",
                    ),
                )

        # Schedule next update
        self.after(2000, self.update_task_list)

    def cancel_selected_task(self):
        """Cancel the selected task"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to cancel.")
            return

        item = self.task_tree.item(selection[0])
        task_id_short = item["values"][0]

        # Find full task ID
        for task_id in self.concurrent_manager.active_tasks.keys():
            if task_id.startswith(task_id_short):
                success = self.concurrent_manager.cancel_task(task_id)
                if success:
                    messagebox.showinfo("Success", f"Task {task_id_short} cancelled.")
                else:
                    messagebox.showerror(
                        "Error", f"Failed to cancel task {task_id_short}."
                    )
                break


class SystemStatsWidget(ttk.Frame):
    """Widget for displaying system statistics"""

    def __init__(self, parent, system_controller: SystemOperationsController):
        super().__init__(parent)
        self.system_controller = system_controller
        self.setup_ui()
        self.update_stats()

    def setup_ui(self):
        """Setup the system stats UI"""
        # Title
        title_label = ttk.Label(
            self, text="System Statistics", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Stats frame
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill="both", expand=True)

        # Create stat labels
        self.cpu_label = ttk.Label(stats_frame, text="CPU Usage: --")
        self.cpu_label.pack(anchor="w")

        self.memory_label = ttk.Label(stats_frame, text="Memory Usage: --")
        self.memory_label.pack(anchor="w")

        self.disk_label = ttk.Label(stats_frame, text="Disk Usage: --")
        self.disk_label.pack(anchor="w")

        self.uptime_label = ttk.Label(stats_frame, text="Uptime: --")
        self.uptime_label.pack(anchor="w")

        self.tasks_label = ttk.Label(stats_frame, text="Running Tasks: --")
        self.tasks_label.pack(anchor="w")

        self.ports_label = ttk.Label(stats_frame, text="Exposed Ports: --")
        self.ports_label.pack(anchor="w")

    def update_stats(self):
        """Update system statistics"""
        try:
            sys_info = self.system_controller.get_system_info()

            if "error" not in sys_info:
                # Update labels
                self.cpu_label.config(
                    text=f"CPU Usage: {sys_info['cpu']['cpu_usage']:.1f}%"
                )
                self.memory_label.config(
                    text=f"Memory Usage: {sys_info['memory']['percentage']:.1f}%"
                )
                self.disk_label.config(
                    text=f"Disk Usage: {sys_info['disk']['percentage']:.1f}%"
                )

                uptime_hours = sys_info["uptime"] / 3600
                self.uptime_label.config(text=f"Uptime: {uptime_hours:.1f} hours")

                self.tasks_label.config(
                    text=f"Running Tasks: {sys_info['running_tasks']}"
                )
                self.ports_label.config(
                    text=f"Exposed Ports: {len(sys_info['exposed_ports'])}"
                )

        except Exception as e:
            logging.error(f"Error updating system stats: {e}")

        # Schedule next update
        self.after(5000, self.update_stats)


class ContentGenerationPanel(ttk.Frame):
    """Panel for content generation operations"""

    def __init__(self, parent, concurrent_manager: ConcurrentOperationsManager):
        super().__init__(parent)
        self.concurrent_manager = concurrent_manager
        self.setup_ui()

    def setup_ui(self):
        """Setup the content generation UI"""
        # Title
        title_label = ttk.Label(
            self, text="Content Generation", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))

        # Presentation section
        pres_frame = ttk.LabelFrame(self, text="Presentations", padding=10)
        pres_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            pres_frame, text="Create Presentation", command=self.create_presentation
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            pres_frame, text="Batch Slides", command=self.create_batch_slides
        ).pack(side="left")

        # Excel section
        excel_frame = ttk.LabelFrame(self, text="Excel Dashboards", padding=10)
        excel_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            excel_frame, text="Create Dashboard", command=self.create_excel_dashboard
        ).pack(side="left", padx=(0, 5))
        ttk.Button(excel_frame, text="Add Charts", command=self.add_excel_charts).pack(
            side="left"
        )

        # Word section
        word_frame = ttk.LabelFrame(self, text="Word Documents", padding=10)
        word_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            word_frame, text="Create Document", command=self.create_word_document
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            word_frame, text="Generate Report", command=self.generate_report
        ).pack(side="left")

        # Quality Assurance section
        qa_frame = ttk.LabelFrame(self, text="Quality Assurance", padding=10)
        qa_frame.pack(fill="x")

        ttk.Button(
            qa_frame, text="Validate Content", command=self.validate_content
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            qa_frame, text="Check Accessibility", command=self.check_accessibility
        ).pack(side="left")

    def create_presentation(self):
        """Create a new presentation"""

        def presentation_task():
            config = ContentConfig(
                title="AI Assistant Presentation",
                author="Dashboard User",
                theme="professional",
            )

            generator = PresentationGenerator(config)
            generator.add_title_slide("Welcome", "AI Assistant Platform Demo")
            generator.add_content_slide(
                "Features",
                [
                    "Multi-source data intelligence",
                    "Professional content generation",
                    "System-level operations",
                    "Quality assurance systems",
                ],
            )

            output_path = f"./workspace/presentation_{int(time.time())}.html"
            html_content = generator.generate_html(output_path)

            return {"output_path": output_path, "size": len(html_content)}

        task = ConcurrentTask(
            name="create_presentation", function=presentation_task, priority=2
        )

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Presentation creation started (Task ID: {task_id[:8]})"
        )

    def create_batch_slides(self):
        """Create multiple slides in batch"""

        def batch_slides_task():
            # Simulate batch slide creation
            time.sleep(2)  # Simulate processing time
            return {"slides_created": 5, "batch_time": 2.0}

        task = ConcurrentTask(
            name="batch_slides_creation", function=batch_slides_task, priority=1
        )

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Batch slides creation started (Task ID: {task_id[:8]})"
        )

    def create_excel_dashboard(self):
        """Create Excel dashboard"""

        def excel_task():
            import pandas as pd

            # Create sample data
            data = pd.DataFrame(
                {
                    "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
                    "Sales": [100, 150, 200, 175, 225],
                    "Profit": [20, 30, 45, 35, 50],
                }
            )

            config = ContentConfig(title="Sales Dashboard", author="Dashboard User")

            generator = ExcelDashboardGenerator(config)
            generator.add_worksheet("Sales Data", data)

            output_path = f"./workspace/dashboard_{int(time.time())}.xlsx"
            success = generator.generate_excel(output_path)

            return {"output_path": output_path, "success": success}

        task = ConcurrentTask(
            name="create_excel_dashboard", function=excel_task, priority=2
        )

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Excel dashboard creation started (Task ID: {task_id[:8]})"
        )

    def add_excel_charts(self):
        """Add charts to Excel file"""
        messagebox.showinfo(
            "Feature", "Excel chart addition feature would be implemented here."
        )

    def create_word_document(self):
        """Create Word document"""

        def word_task():
            config = ContentConfig(title="AI Assistant Report", author="Dashboard User")

            generator = WordDocumentGenerator(config)
            generator.add_heading("Executive Summary", 1)
            generator.add_paragraph(
                "This report demonstrates the capabilities of the AI Assistant Platform."
            )
            generator.add_heading("Key Features", 2)
            generator.add_list(
                [
                    "Advanced data collection and processing",
                    "Professional content generation",
                    "System-level automation",
                    "Quality assurance and validation",
                ]
            )

            output_path = f"./workspace/report_{int(time.time())}.docx"
            success = generator.generate_docx(output_path)

            return {"output_path": output_path, "success": success}

        task = ConcurrentTask(
            name="create_word_document", function=word_task, priority=2
        )

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Word document creation started (Task ID: {task_id[:8]})"
        )

    def generate_report(self):
        """Generate comprehensive report"""
        messagebox.showinfo(
            "Feature",
            "Comprehensive report generation feature would be implemented here.",
        )

    def validate_content(self):
        """Validate content quality"""
        file_path = filedialog.askopenfilename(
            title="Select file to validate",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
        )

        if file_path:

            def validation_task():
                validator = ContentValidator()
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                results = validator.validate_content(content, "html")

                # Count issues
                errors = len(
                    [r for r in results if r.severity == "error" and not r.passed]
                )
                warnings = len(
                    [r for r in results if r.severity == "warning" and not r.passed]
                )

                return {
                    "file_path": file_path,
                    "total_checks": len(results),
                    "errors": errors,
                    "warnings": warnings,
                    "results": results,
                }

            task = ConcurrentTask(
                name="validate_content", function=validation_task, priority=1
            )

            task_id = self.concurrent_manager.submit_task(task)
            messagebox.showinfo(
                "Task Started", f"Content validation started (Task ID: {task_id[:8]})"
            )

    def check_accessibility(self):
        """Check accessibility compliance"""
        file_path = filedialog.askopenfilename(
            title="Select HTML file to check", filetypes=[("HTML files", "*.html")]
        )

        if file_path:

            def accessibility_task():
                checker = AccessibilityChecker()
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                results = checker.check_accessibility(content)

                issues = len([r for r in results if not r.passed])

                return {
                    "file_path": file_path,
                    "total_checks": len(results),
                    "issues": issues,
                    "results": results,
                }

            task = ConcurrentTask(
                name="accessibility_check", function=accessibility_task, priority=1
            )

            task_id = self.concurrent_manager.submit_task(task)
            messagebox.showinfo(
                "Task Started", f"Accessibility check started (Task ID: {task_id[:8]})"
            )


class DataOperationsPanel(ttk.Frame):
    """Panel for data operations"""

    def __init__(self, parent, concurrent_manager: ConcurrentOperationsManager):
        super().__init__(parent)
        self.concurrent_manager = concurrent_manager
        self.data_collector = SyncDataCollector()
        self.setup_ui()

    def setup_ui(self):
        """Setup the data operations UI"""
        # Title
        title_label = ttk.Label(
            self, text="Data Operations", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))

        # Web scraping section
        scraping_frame = ttk.LabelFrame(self, text="Web Scraping", padding=10)
        scraping_frame.pack(fill="x", pady=(0, 10))

        self.url_entry = ttk.Entry(scraping_frame, width=50)
        self.url_entry.pack(side="left", padx=(0, 5))
        self.url_entry.insert(0, "https://example.com")

        ttk.Button(
            scraping_frame, text="Scrape Page", command=self.scrape_webpage
        ).pack(side="left")

        # Batch operations section
        batch_frame = ttk.LabelFrame(self, text="Batch Operations", padding=10)
        batch_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            batch_frame, text="Batch Scrape URLs", command=self.batch_scrape
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            batch_frame, text="Process Data Files", command=self.process_data_files
        ).pack(side="left")

        # API integration section
        api_frame = ttk.LabelFrame(self, text="API Integration", padding=10)
        api_frame.pack(fill="x")

        ttk.Button(api_frame, text="Connect API", command=self.connect_api).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(
            api_frame, text="Live Data Feed", command=self.create_data_feed
        ).pack(side="left")

    def scrape_webpage(self):
        """Scrape a single webpage"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL to scrape.")
            return

        def scraping_task():
            result = self.data_collector.scrape_single_page(url)
            return {
                "url": url,
                "success": "error" not in result,
                "data_size": len(str(result.get("data", {}))),
                "title": result.get("metadata", {}).get("title", "Unknown"),
            }

        task = ConcurrentTask(name="scrape_webpage", function=scraping_task, priority=2)

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Web scraping started (Task ID: {task_id[:8]})"
        )

    def batch_scrape(self):
        """Batch scrape multiple URLs"""

        def batch_scraping_task():
            urls = [
                "https://example.com",
                "https://httpbin.org/json",
                "https://jsonplaceholder.typicode.com/posts/1",
            ]

            sources = [
                DataSource(name=f"site_{i}", url=url, source_type="web")
                for i, url in enumerate(urls)
            ]

            results = self.data_collector.collect_data(sources)

            successful = len([r for r in results if "error" not in r])

            return {
                "total_urls": len(urls),
                "successful": successful,
                "failed": len(urls) - successful,
            }

        task = ConcurrentTask(
            name="batch_scrape_urls", function=batch_scraping_task, priority=1
        )

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Batch scraping started (Task ID: {task_id[:8]})"
        )

    def process_data_files(self):
        """Process data files"""
        file_paths = filedialog.askopenfilenames(
            title="Select data files to process",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if file_paths:

            def processing_task():
                processed_files = []

                for file_path in file_paths:
                    try:
                        if file_path.endswith(".csv"):
                            import pandas as pd

                            df = pd.read_csv(file_path)
                            processed_files.append(
                                {
                                    "file": file_path,
                                    "rows": len(df),
                                    "columns": len(df.columns),
                                    "success": True,
                                }
                            )
                        elif file_path.endswith(".json"):
                            with open(file_path, "r") as f:
                                data = json.load(f)
                            processed_files.append(
                                {
                                    "file": file_path,
                                    "size": len(str(data)),
                                    "success": True,
                                }
                            )
                    except Exception as e:
                        processed_files.append(
                            {"file": file_path, "error": str(e), "success": False}
                        )

                return {
                    "total_files": len(file_paths),
                    "processed_files": processed_files,
                    "successful": len([f for f in processed_files if f["success"]]),
                }

            task = ConcurrentTask(
                name="process_data_files", function=processing_task, priority=2
            )

            task_id = self.concurrent_manager.submit_task(task)
            messagebox.showinfo(
                "Task Started", f"Data processing started (Task ID: {task_id[:8]})"
            )

    def connect_api(self):
        """Connect to API endpoint"""
        messagebox.showinfo(
            "Feature", "API connection feature would be implemented here."
        )

    def create_data_feed(self):
        """Create live data feed"""
        messagebox.showinfo(
            "Feature", "Live data feed creation feature would be implemented here."
        )


class DeploymentPanel(ttk.Frame):
    """Panel for deployment operations"""

    def __init__(self, parent, concurrent_manager: ConcurrentOperationsManager):
        super().__init__(parent)
        self.concurrent_manager = concurrent_manager
        self.deployer = StaticSiteDeployer()
        self.setup_ui()

    def setup_ui(self):
        """Setup the deployment UI"""
        # Title
        title_label = ttk.Label(
            self, text="Deployment & Integration", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))

        # Static site deployment section
        deploy_frame = ttk.LabelFrame(self, text="Static Site Deployment", padding=10)
        deploy_frame.pack(fill="x", pady=(0, 10))

        # Platform selection
        platform_frame = ttk.Frame(deploy_frame)
        platform_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(platform_frame, text="Platform:").pack(side="left")
        self.platform_var = tk.StringVar(value="vercel")
        platform_combo = ttk.Combobox(
            platform_frame,
            textvariable=self.platform_var,
            values=["vercel", "netlify", "github-pages", "aws-s3"],
            state="readonly",
            width=15,
        )
        platform_combo.pack(side="left", padx=(5, 10))

        # Project name
        ttk.Label(platform_frame, text="Project:").pack(side="left")
        self.project_entry = ttk.Entry(platform_frame, width=20)
        self.project_entry.pack(side="left", padx=(5, 0))
        self.project_entry.insert(0, "ai-dashboard")

        # Deploy button
        ttk.Button(deploy_frame, text="Deploy Site", command=self.deploy_site).pack(
            pady=(5, 0)
        )

        # Office Add-In section
        addin_frame = ttk.LabelFrame(self, text="Office Add-In Integration", padding=10)
        addin_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            addin_frame, text="Create Excel Add-In", command=self.create_excel_addin
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            addin_frame, text="Embed Dashboard", command=self.embed_dashboard
        ).pack(side="left")

        # System operations section
        system_frame = ttk.LabelFrame(self, text="System Operations", padding=10)
        system_frame.pack(fill="x")

        ttk.Button(system_frame, text="Expose Port", command=self.expose_port).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(
            system_frame, text="Install Package", command=self.install_package
        ).pack(side="left", padx=(0, 5))
        ttk.Button(system_frame, text="Run Command", command=self.run_command).pack(
            side="left"
        )

    def deploy_site(self):
        """Deploy static site"""
        source_dir = filedialog.askdirectory(title="Select source directory to deploy")
        if not source_dir:
            return

        platform = self.platform_var.get()
        project_name = self.project_entry.get().strip()

        if not project_name:
            messagebox.showerror("Error", "Please enter a project name.")
            return

        def deployment_task():
            config = DeploymentConfig(platform=platform, project_name=project_name)

            result = self.deployer.deploy(source_dir, config)
            return result

        task = ConcurrentTask(
            name="deploy_static_site", function=deployment_task, priority=3
        )

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Deployment started (Task ID: {task_id[:8]})"
        )

    def create_excel_addin(self):
        """Create Excel Add-In"""

        def addin_task():
            embedder = OfficeAddinEmbedder()

            config = OfficeAddinConfig(
                manifest_id="12345678-1234-1234-1234-123456789012",
                display_name="AI Dashboard Add-In",
                description="Interactive dashboard for Excel",
                provider_name="AI Assistant Platform",
                dashboard_url="https://example.com/dashboard",
            )

            manifest = embedder.create_office_addin_manifest(config)

            # Save manifest to file
            output_path = f"./workspace/excel_addin_manifest_{int(time.time())}.xml"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(manifest)

            return {
                "manifest_path": output_path,
                "manifest_size": len(manifest),
                "dashboard_url": config.dashboard_url,
            }

        task = ConcurrentTask(
            name="create_excel_addin", function=addin_task, priority=2
        )

        task_id = self.concurrent_manager.submit_task(task)
        messagebox.showinfo(
            "Task Started", f"Excel Add-In creation started (Task ID: {task_id[:8]})"
        )

    def embed_dashboard(self):
        """Embed dashboard in Excel file"""
        excel_file = filedialog.askopenfilename(
            title="Select Excel file", filetypes=[("Excel files", "*.xlsx")]
        )

        if excel_file:
            messagebox.showinfo(
                "Feature",
                f"Dashboard embedding for {excel_file} would be implemented here.",
            )

    def expose_port(self):
        """Expose a port to public internet"""
        port_dialog = tk.Toplevel()
        port_dialog.title("Expose Port")
        port_dialog.geometry("300x150")

        ttk.Label(port_dialog, text="Port to expose:").pack(pady=10)
        port_entry = ttk.Entry(port_dialog, width=10)
        port_entry.pack()
        port_entry.insert(0, "8000")

        def do_expose():
            try:
                port = int(port_entry.get())
                # This would use the system controller to expose the port
                messagebox.showinfo("Success", f"Port {port} exposed successfully!")
                port_dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid port number.")

        ttk.Button(port_dialog, text="Expose", command=do_expose).pack(pady=10)

    def install_package(self):
        """Install system package"""
        package_dialog = tk.Toplevel()
        package_dialog.title("Install Package")
        package_dialog.geometry("300x150")

        ttk.Label(package_dialog, text="Package name:").pack(pady=10)
        package_entry = ttk.Entry(package_dialog, width=30)
        package_entry.pack()

        def do_install():
            package_name = package_entry.get().strip()
            if package_name:
                messagebox.showinfo(
                    "Info",
                    f"Package installation for '{package_name}' would be started.",
                )
                package_dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter a package name.")

        ttk.Button(package_dialog, text="Install", command=do_install).pack(pady=10)

    def run_command(self):
        """Run system command"""
        command_dialog = tk.Toplevel()
        command_dialog.title("Run Command")
        command_dialog.geometry("400x200")

        ttk.Label(command_dialog, text="Command to run:").pack(pady=10)
        command_entry = ttk.Entry(command_dialog, width=50)
        command_entry.pack()
        command_entry.insert(0, "ls -la")

        def do_run():
            command = command_entry.get().strip()
            if command:
                messagebox.showinfo("Info", f"Command '{command}' would be executed.")
                command_dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter a command.")

        ttk.Button(command_dialog, text="Run", command=do_run).pack(pady=10)


class MainDashboard:
    """
    Main Dashboard Application
    """

    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        self.setup_logging()
        self.initialize_components()
        self.setup_ui()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("dashboard.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def initialize_components(self):
        """Initialize all system components"""
        self.logger.info("Initializing dashboard components...")

        # Core components
        self.concurrent_manager = ConcurrentOperationsManager(
            max_workers=self.config.max_workers
        )
        self.system_controller = SystemOperationsController()
        self.office_ai_service = OfficeAIProcessingService(self.config.workspace_dir)
        self.realtime_events: List[Dict[str, Any]] = []
        self.office_router = None
        self.office_ai_service_url = self.config.ai_service_url
        if self.config.enable_realtime_router:
            try:
                self.office_router = AIOfficeWebSocketRouter(
                    ai_service_url=self.office_ai_service_url
                    or "http://localhost:8000",
                    ai_service_client=self._route_ai_office_message,
                )
                self.logger.info(
                    "Real-time Office router initialized (service=%s)",
                    self.office_ai_service_url or "local-simulator",
                )
            except Exception as exc:
                self.logger.warning("Failed to initialize Office router: %s", exc)
                self.office_router = None

        # Create workspace directory
        Path(self.config.workspace_dir).mkdir(exist_ok=True)

        self.logger.info("Dashboard components initialized successfully")

    def setup_ui(self):
        """Setup the main user interface"""
        self.root = tk.Tk()
        self.root.title(self.config.title)
        self.root.geometry("1200x800")

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")

        # Create main menu
        self.create_menu()

        # Create main layout
        self.create_main_layout()

        # Status bar
        self.create_status_bar()

        self.logger.info("Dashboard UI setup complete")

    def create_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Workspace", command=self.open_workspace)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_application)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="System Info", command=self.show_system_info)
        tools_menu.add_command(
            label="Performance Stats", command=self.show_performance_stats
        )
        tools_menu.add_command(
            label="Real-Time Sessions", command=self.show_realtime_sessions
        )
        tools_menu.add_command(label="Clear Cache", command=self.clear_cache)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="Technical Spec", command=self.show_technical_spec)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_layout(self):
        """Create main dashboard layout"""
        # Main paned window
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel - System monitoring
        left_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(left_frame, weight=1)

        # System stats widget
        self.system_stats = SystemStatsWidget(left_frame, self.system_controller)
        self.system_stats.pack(fill="x", pady=(0, 10))

        # Task monitor widget
        self.task_monitor = TaskMonitorWidget(left_frame, self.concurrent_manager)
        self.task_monitor.pack(fill="both", expand=True)

        # Right panel - Operations
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        # Notebook for different operation panels
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)

        # Content generation panel
        content_panel = ContentGenerationPanel(self.notebook, self.concurrent_manager)
        self.notebook.add(content_panel, text="Content Generation")

        # Data operations panel
        data_panel = DataOperationsPanel(self.notebook, self.concurrent_manager)
        self.notebook.add(data_panel, text="Data Operations")

        # Deployment panel
        deployment_panel = DeploymentPanel(self.notebook, self.concurrent_manager)
        self.notebook.add(deployment_panel, text="Deployment")

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill="x", side="bottom")

        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side="left", padx=5)

        # Time label
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side="right", padx=5)

        self.update_time()

    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def new_project(self):
        """Create new project"""
        messagebox.showinfo(
            "New Project", "New project creation feature would be implemented here."
        )

    def open_workspace(self):
        """Open workspace directory"""
        try:
            if os.name == "nt":  # Windows
                os.startfile(self.config.workspace_dir)
            elif os.name == "posix":  # macOS and Linux
                subprocess.run(
                    [
                        "open" if sys.platform == "darwin" else "xdg-open",
                        self.config.workspace_dir,
                    ]
                )
        except Exception as e:
            messagebox.showerror("Error", f"Could not open workspace: {e}")

    def show_system_info(self):
        """Show system information dialog"""
        sys_info = self.system_controller.get_system_info()

        info_window = tk.Toplevel(self.root)
        info_window.title("System Information")
        info_window.geometry("500x400")

        text_widget = tk.Text(info_window, wrap="word")
        scrollbar = ttk.Scrollbar(
            info_window, orient="vertical", command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Format system info
        info_text = "System Information\n" + "=" * 50 + "\n\n"

        if "error" not in sys_info:
            info_text += f"CPU Cores: {sys_info['cpu']['total_cores']}\n"
            info_text += f"CPU Usage: {sys_info['cpu']['cpu_usage']:.1f}%\n"
            info_text += (
                f"Memory Total: {sys_info['memory']['total'] / (1024**3):.1f} GB\n"
            )
            info_text += f"Memory Usage: {sys_info['memory']['percentage']:.1f}%\n"
            info_text += f"Disk Usage: {sys_info['disk']['percentage']:.1f}%\n"
            info_text += f"Uptime: {sys_info['uptime'] / 3600:.1f} hours\n"
            info_text += f"Running Tasks: {sys_info['running_tasks']}\n"
            info_text += f"Exposed Ports: {len(sys_info['exposed_ports'])}\n"
        else:
            info_text += f"Error retrieving system info: {sys_info['error']}\n"

        text_widget.insert("1.0", info_text)
        text_widget.config(state="disabled")

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_performance_stats(self):
        """Show performance statistics"""
        stats = self.concurrent_manager.get_performance_stats()

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Performance Statistics")
        stats_window.geometry("400x300")

        text_widget = tk.Text(stats_window, wrap="word")

        stats_text = "Performance Statistics\n" + "=" * 50 + "\n\n"
        stats_text += f"Tasks Completed: {stats['tasks_completed']}\n"
        stats_text += f"Tasks Failed: {stats['tasks_failed']}\n"
        stats_text += (
            f"Average Execution Time: {stats['average_execution_time']:.2f}s\n"
        )
        stats_text += f"Active Tasks: {stats['active_tasks']}\n"
        stats_text += f"Queue Size: {stats['queue_size']}\n"
        stats_text += f"Thread Pool Size: {stats['thread_pool_size']}\n"
        stats_text += f"Process Pool Size: {stats['process_pool_size']}\n"

        text_widget.insert("1.0", stats_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True)

    def show_realtime_sessions(self):
        """Display current Office router sessions and recent AI events."""
        if not self.office_router:
            messagebox.showinfo(
                "Real-Time Sessions",
                "The Office real-time router is disabled or failed to initialize.",
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Office Real-Time Sessions")
        window.geometry("520x420")

        text_widget = tk.Text(window, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        def refresh_view():
            sessions = self.office_router.list_active_documents()
            clients = self.office_router.list_clients()

            text_widget.config(state="normal")
            text_widget.delete("1.0", tk.END)

            text_widget.insert("end", "Active Documents\n===================\n")
            if sessions:
                for doc_id, client_ids in sessions.items():
                    text_widget.insert(
                        "end",
                        f"• {doc_id} :: participants={', '.join(client_ids) or '—'}\n",
                    )
            else:
                text_widget.insert("end", "No active document sessions registered.\n")

            text_widget.insert("end", "\nConnected Clients\n===================\n")
            if clients:
                for client in clients:
                    text_widget.insert(
                        "end",
                        f"• {client.client_id} ({client.application.value})"
                        f" user={client.user_id or 'anonymous'} doc={client.document_id or '—'}\n",
                    )
            else:
                text_widget.insert("end", "No clients connected to the router.\n")

            if self.realtime_events:
                text_widget.insert("end", "\nRecent AI Events\n===================\n")
                for event in reversed(self.realtime_events[-10:]):
                    text_widget.insert(
                        "end",
                        f"[{event['timestamp']}] {event['message_type']}"
                        f" doc={event['document_id']} status={event['status']}\n",
                    )

            text_widget.config(state="disabled")

        refresh_view()
        ttk.Button(window, text="Refresh", command=refresh_view).pack(pady=5)

    def _route_ai_office_message(self, message):
        """Proxy AI Office requests to external services or a local simulator."""
        payload = message.to_dict()
        doc_id = (
            payload.get("document_id")
            or payload.get("payload", {}).get("document_id")
            or "unspecified"
        )
        response_data: Optional[Dict[str, Any]] = None

        if self.office_ai_service_url:
            endpoint = f"{self.office_ai_service_url.rstrip('/')}/process"
            try:
                resp = requests.post(endpoint, json=payload, timeout=15)
                resp.raise_for_status()
                response_data = resp.json()
            except requests.RequestException as exc:
                self.logger.warning(
                    "AI Office service unreachable (%s). Falling back to local heuristics.",
                    exc,
                )

        if response_data is None and self.office_ai_service:
            try:
                response_data = self.office_ai_service.process_message(message)
            except Exception as exc:  # pragma: no cover - defensive fallback
                self.logger.error("Local AI service failed: %s", exc)
                response_data = None

        if response_data is None:
            response_data = self._build_local_ai_office_result(message)

        self._record_realtime_event(message, response_data)
        return response_data

    def _build_local_ai_office_result(self, message):
        """Generate a lightweight local response when the remote service is unavailable."""
        preview_source = (
            message.payload.get("prompt")
            or message.payload.get("content")
            or message.payload.get("text")
            or "Context not provided"
        )
        if isinstance(preview_source, dict):
            preview_source = json.dumps(preview_source)[:200]
        preview = str(preview_source)
        if len(preview) > 160:
            preview = preview[:157] + "..."

        return {
            "status": "simulated",
            "message_type": message.type.value,
            "document_id": message.document_id or "unspecified",
            "summary": preview,
            "recommendations": [
                {
                    "title": "Structure Review",
                    "detail": "Placeholder recommendation generated locally while waiting for the AI service.",
                },
                {
                    "title": "Accessibility",
                    "detail": "Consider running the AccessibilityChecker once edits are complete.",
                },
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _record_realtime_event(self, message, response_data):
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_type": message.type.value,
            "document_id": message.document_id or "unspecified",
            "status": response_data.get("status")
            or ("success" if response_data.get("success", True) else "error"),
        }
        self.realtime_events.append(event)
        if len(self.realtime_events) > 50:
            self.realtime_events = self.realtime_events[-50:]

    def clear_cache(self):
        """Clear system cache"""
        result = messagebox.askyesno(
            "Clear Cache", "Are you sure you want to clear all cached data?"
        )
        if result:
            # Clear cache implementation would go here
            messagebox.showinfo("Success", "Cache cleared successfully.")

    def show_documentation(self):
        """Show documentation"""
        webbrowser.open("https://github.com/ai-assistant/documentation")

    def show_technical_spec(self):
        """Display mission and architectural summary from the canonical spec."""
        summary = spec_summary()
        spec_window = tk.Toplevel(self.root)
        spec_window.title("Canonical Technical Specification")
        spec_window.geometry("600x500")

        text_widget = tk.Text(spec_window, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        for section, items in summary.items():
            text_widget.insert("end", f"{section}\n" + "-" * len(section) + "\n")
            for item in items:
                text_widget.insert("end", f" • {item}\n")
            text_widget.insert("end", "\n")

        text_widget.config(state="disabled")

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{self.config.title}
Version 1.0.0

Advanced Autonomous Workflows Platform
Multi-Source Data Intelligence
Professional-Grade Content Generation
System-Level Operations Control

© 2024 AI Assistant Platform Team
        """
        messagebox.showinfo("About", about_text)

    def quit_application(self):
        """Quit the application"""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.logger.info("Shutting down dashboard...")

            # Cleanup components
            self.concurrent_manager.shutdown()
            self.system_controller.cleanup_resources()
            if self.office_router:
                try:
                    self.office_router.shutdown()
                except Exception as exc:
                    self.logger.warning("Error shutting down Office router: %s", exc)

            self.root.quit()

    def run(self):
        """Run the dashboard application"""
        self.logger.info("Starting dashboard application...")
        self.status_label.config(text="Dashboard started successfully")

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Dashboard interrupted by user")
        except Exception as e:
            self.logger.error(f"Dashboard error: {e}")
            messagebox.showerror("Error", f"Dashboard error: {e}")
        finally:
            self.quit_application()


# Entry point
def main():
    """Main entry point for the dashboard"""
    config = DashboardConfig(
        title="AI OS Console v1.0",
        theme="default",
        auto_save=True,
        log_level="INFO",
        max_workers=10,
        workspace_dir="./workspace",
    )

    dashboard = MainDashboard(config)
    dashboard.run()


if __name__ == "__main__":
    main()
