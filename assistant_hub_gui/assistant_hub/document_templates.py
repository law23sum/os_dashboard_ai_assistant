"""Document templates system for common workflows."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

import sqlite3
from .db import init_db, DB_FILE


@dataclass
class DocumentTemplate:
    """A document template for common workflows."""
    id: int
    name: str
    category: str  # "project", "meeting", "report", "proposal", etc.
    content: str  # Template content with placeholders
    description: str = ""
    placeholders: Optional[str] = None  # JSON array of placeholder names


def init_templates_table(conn: sqlite3.Connection):
    """Initialize the document_templates table if it doesn't exist."""
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS document_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            description TEXT,
            placeholders TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()


def create_default_templates(conn: sqlite3.Connection):
    """Create default document templates."""
    init_templates_table(conn)
    
    templates = [
        {
            "name": "Project Brief",
            "category": "project",
            "description": "Standard project brief template",
            "content": """# {project_name} - Project Brief

## Overview
{project_overview}

## Objectives
{objectives}

## Scope
{scope}

## Timeline
- Start Date: {start_date}
- Target Completion: {end_date}

## Resources
{resources}

## Success Criteria
{success_criteria}

## Risks
{risks}

## Next Steps
{next_steps}
""",
            "placeholders": ["project_name", "project_overview", "objectives", "scope", 
                           "start_date", "end_date", "resources", "success_criteria", "risks", "next_steps"]
        },
        {
            "name": "Meeting Notes",
            "category": "meeting",
            "description": "Standard meeting notes template",
            "content": """# Meeting Notes - {meeting_title}

**Date:** {date}
**Attendees:** {attendees}
**Location:** {location}

## Agenda
{agenda}

## Discussion Points
{discussion_points}

## Decisions Made
{decisions}

## Action Items
{action_items}

## Next Meeting
{next_meeting}
""",
            "placeholders": ["meeting_title", "date", "attendees", "location", "agenda",
                           "discussion_points", "decisions", "action_items", "next_meeting"]
        },
        {
            "name": "Progress Report",
            "category": "report",
            "description": "Weekly/monthly progress report template",
            "content": """# {project_name} - Progress Report

**Period:** {period}
**Report Date:** {report_date}

## Executive Summary
{executive_summary}

## Completed This Period
{completed}

## In Progress
{in_progress}

## Blockers & Issues
{blockers}

## Upcoming Work
{upcoming}

## Metrics
- Completion Rate: {completion_rate}%
- Tasks Completed: {tasks_completed}
- Tasks Remaining: {tasks_remaining}

## Next Steps
{next_steps}
""",
            "placeholders": ["project_name", "period", "report_date", "executive_summary",
                           "completed", "in_progress", "blockers", "upcoming", 
                           "completion_rate", "tasks_completed", "tasks_remaining", "next_steps"]
        },
        {
            "name": "Proposal Template",
            "category": "proposal",
            "description": "Project proposal template",
            "content": """# {proposal_title}

## Executive Summary
{executive_summary}

## Problem Statement
{problem_statement}

## Proposed Solution
{proposed_solution}

## Benefits
{benefits}

## Implementation Plan
{implementation_plan}

## Timeline
{timeline}

## Budget
{budget}

## Risks & Mitigation
{risks}

## Conclusion
{conclusion}
""",
            "placeholders": ["proposal_title", "executive_summary", "problem_statement",
                           "proposed_solution", "benefits", "implementation_plan", 
                           "timeline", "budget", "risks", "conclusion"]
        }
    ]
    
    c = conn.cursor()
    for template in templates:
        import json
        placeholders_json = json.dumps(template["placeholders"])
        created_at = datetime.now().isoformat(timespec="seconds")
        
        # Check if template already exists
        c.execute("SELECT id FROM document_templates WHERE name = ?", (template["name"],))
        if c.fetchone():
            continue
        
        c.execute("""
            INSERT INTO document_templates (name, category, content, description, placeholders, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (template["name"], template["category"], template["content"], 
              template["description"], placeholders_json, created_at))
    
    conn.commit()


def get_templates(conn: sqlite3.Connection, category: Optional[str] = None) -> List[DocumentTemplate]:
    """Get all document templates, optionally filtered by category."""
    init_templates_table(conn)
    
    c = conn.cursor()
    if category:
        c.execute("""
            SELECT id, name, category, content, description, placeholders
            FROM document_templates
            WHERE category = ?
            ORDER BY name
        """, (category,))
    else:
        c.execute("""
            SELECT id, name, category, content, description, placeholders
            FROM document_templates
            ORDER BY category, name
        """)
    
    templates = []
    for row in c.fetchall():
        placeholders = None
        if row["placeholders"]:
            import json
            try:
                placeholders = json.loads(row["placeholders"])
            except Exception:
                pass
        
        templates.append(DocumentTemplate(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            content=row["content"],
            description=row["description"] or "",
            placeholders=placeholders
        ))
    
    return templates


def get_template(conn: sqlite3.Connection, template_id: int) -> Optional[DocumentTemplate]:
    """Get a specific template by ID."""
    init_templates_table(conn)
    
    c = conn.cursor()
    c.execute("""
        SELECT id, name, category, content, description, placeholders
        FROM document_templates
        WHERE id = ?
    """, (template_id,))
    
    row = c.fetchone()
    if not row:
        return None
    
    placeholders = None
    if row["placeholders"]:
        import json
        try:
            placeholders = json.loads(row["placeholders"])
        except Exception:
            pass
    
    return DocumentTemplate(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        content=row["content"],
        description=row["description"] or "",
        placeholders=placeholders
    )


def create_template(
    conn: sqlite3.Connection,
    name: str,
    category: str,
    content: str,
    description: str = "",
    placeholders: Optional[List[str]] = None
) -> int:
    """Create a new document template."""
    init_templates_table(conn)
    
    c = conn.cursor()
    placeholders_json = None
    if placeholders:
        import json
        placeholders_json = json.dumps(placeholders)
    
    created_at = datetime.now().isoformat(timespec="seconds")
    
    c.execute("""
        INSERT INTO document_templates (name, category, content, description, placeholders, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, content, description, placeholders_json, created_at))
    
    conn.commit()
    return c.lastrowid


def render_template(template: DocumentTemplate, values: Dict[str, str]) -> str:
    """Render a template with provided values."""
    content = template.content
    
    # Replace placeholders
    for key, value in values.items():
        placeholder = "{" + key + "}"
        content = content.replace(placeholder, str(value))
    
    # Replace any remaining placeholders with empty string
    import re
    content = re.sub(r'\{[^}]+\}', '', content)
    
    return content

