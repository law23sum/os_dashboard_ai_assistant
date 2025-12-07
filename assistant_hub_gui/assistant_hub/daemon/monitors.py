"""Monitors that detect opportunities for automation.

These monitors run continuously, noticing what needs to be done
before humans even realize it.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3

from ..db import AssistantState, Settings, Task, Project


class BaseMonitor:
    """Base class for all monitors."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def check(self, state: AssistantState, settings: Settings) -> List[Dict[str, Any]]:
        """Check for opportunities and return findings."""
        raise NotImplementedError


class DocumentMonitor(BaseMonitor):
    """Monitors for missing or needed documents."""
    
    def check(self, state: AssistantState, settings: Settings) -> List[Dict[str, Any]]:
        """Check for missing documents that should exist."""
        findings = []
        
        # Check projects for missing documentation
        for project in state.projects:
            project_docs_path = Path(f"documents/projects/{project.name}")
            
            # Check for missing project brief
            brief_path = project_docs_path / f"{project.name}_brief.docx"
            if not brief_path.exists() and project.status == "active":
                findings.append({
                    "type": "missing_document",
                    "severity": "medium",
                    "project": project.name,
                    "document_type": "project_brief",
                    "suggested_path": str(brief_path),
                    "reason": f"Active project '{project.name}' lacks a project brief",
                })
            
            # Check for missing progress report
            report_path = project_docs_path / f"{project.name}_progress.docx"
            if report_path.exists():
                # Check if report is outdated (older than 7 days)
                mtime = datetime.fromtimestamp(report_path.stat().st_mtime)
                if (datetime.now() - mtime).days > 7:
                    findings.append({
                        "type": "outdated_document",
                        "severity": "low",
                        "project": project.name,
                        "document_type": "progress_report",
                        "path": str(report_path),
                        "days_old": (datetime.now() - mtime).days,
                        "reason": f"Progress report for '{project.name}' is {(datetime.now() - mtime).days} days old",
                    })
        
        return findings


class TaskMonitor(BaseMonitor):
    """Monitors tasks for automation opportunities."""
    
    def check(self, state: AssistantState, settings: Settings) -> List[Dict[str, Any]]:
        """Check tasks for things that need attention."""
        findings = []
        today = datetime.now().date()
        
        for task in state.tasks:
            # Check for high-priority tasks with no progress
            if (task.status == "TODO" and 
                task.priority in ["HIGH", "CRITICAL"] and
                task.due_date):
                try:
                    due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    days_until = (due_date - today).days
                    
                    if days_until <= 3 and days_until >= 0:
                        findings.append({
                            "type": "urgent_task",
                            "severity": "high",
                            "task_id": task.id,
                            "task_title": task.title,
                            "days_until_due": days_until,
                            "reason": f"Task '{task.title}' is due in {days_until} days",
                        })
                except Exception:
                    pass
            
            # Check for tasks that should have documents but don't
            if task.status == "IN_PROGRESS" and task.project:
                doc_path = Path(f"documents/tasks/{task.project}/{task.id}_{task.title}.docx")
                if not doc_path.exists():
                    findings.append({
                        "type": "task_needs_documentation",
                        "severity": "low",
                        "task_id": task.id,
                        "task_title": task.title,
                        "project": task.project,
                        "suggested_path": str(doc_path),
                        "reason": f"Task '{task.title}' is in progress but has no documentation",
                    })
        
        return findings


class IntegrationMonitor(BaseMonitor):
    """Monitors integrations for sync opportunities."""
    
    def check(self, state: AssistantState, settings: Settings) -> List[Dict[str, Any]]:
        """Check integrations for items that need syncing."""
        findings = []
        
        # This would check external_items table for staleness
        # For now, return empty findings
        # In full implementation, would check last sync times, etc.
        
        return findings


class FileSystemMonitor(BaseMonitor):
    """Monitors file system for changes and opportunities."""
    
    def check(self, state: AssistantState, settings: Settings) -> List[Dict[str, Any]]:
        """Monitor file system for automation opportunities."""
        findings = []
        
        # Check for new files that should be processed
        documents_dir = Path("documents")
        if documents_dir.exists():
            for file_path in documents_dir.rglob("*.docx"):
                # Check if file was modified recently (within last hour)
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if (datetime.now() - mtime).total_seconds() < 3600:
                    findings.append({
                        "type": "new_document",
                        "severity": "info",
                        "path": str(file_path),
                        "modified_time": mtime.isoformat(),
                        "reason": f"New or recently modified document: {file_path.name}",
                    })
        
        return findings


class OutdatedContentMonitor(BaseMonitor):
    """Monitors for outdated content that needs updating."""
    
    def check(self, state: AssistantState, settings: Settings) -> List[Dict[str, Any]]:
        """Check for content that's become outdated."""
        findings = []
        
        # Check project descriptions that might be stale
        for project in state.projects:
            if project.status == "active":
                # Check if project has many completed tasks but description hasn't been updated
                project_tasks = [t for t in state.tasks if t.project == project.name]
                completed = len([t for t in project_tasks if t.status == "DONE"])
                total = len(project_tasks)
                
                if total > 0 and completed > 0:
                    completion_ratio = completed / total
                    if completion_ratio > 0.5:  # More than 50% complete
                        findings.append({
                            "type": "project_progress_update_needed",
                            "severity": "low",
                            "project": project.name,
                            "completion_ratio": completion_ratio,
                            "completed_tasks": completed,
                            "total_tasks": total,
                            "reason": f"Project '{project.name}' is {completion_ratio*100:.0f}% complete - description may need updating",
                        })
        
        return findings


