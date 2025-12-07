"""Document templates system for generating structured documents."""

import sqlite3
import uuid
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DocumentTemplate:
    """A template for generating documents."""
    id: str
    name: str
    category: str
    content: str
    created_at: str
    updated_at: Optional[str] = None


# Default templates
DEFAULT_TEMPLATES = {
    "project_brief": {
        "name": "Project Brief",
        "category": "project",
        "content": """# {project_name}

## Overview
{overview}

## Objectives
{objectives}

## Scope
{scope}

## Timeline
{timeline}

## Resources
{resources}

## Risks
{risks}

## Success Criteria
{success_criteria}
"""
    },
    "meeting_notes": {
        "name": "Meeting Notes",
        "category": "meeting",
        "content": """# Meeting Notes - {meeting_title}

**Date:** {date}
**Attendees:** {attendees}
**Location:** {location}

## Agenda
{agenda}

## Discussion
{discussion}

## Decisions
{decisions}

## Action Items
{action_items}

## Next Steps
{next_steps}
"""
    },
    "progress_report": {
        "name": "Progress Report",
        "category": "report",
        "content": """# Progress Report - {project_name}

**Period:** {period}
**Date:** {date}

## Executive Summary
{executive_summary}

## Completed Work
{completed_work}

## In Progress
{in_progress}

## Blockers
{blockers}

## Metrics
{metrics}

## Next Period Goals
{next_goals}
"""
    },
    "proposal": {
        "name": "Proposal Template",
        "category": "proposal",
        "content": """# {proposal_title}

**Date:** {date}
**Prepared by:** {author}

## Problem Statement
{problem_statement}

## Proposed Solution
{solution}

## Benefits
{benefits}

## Implementation Plan
{implementation_plan}

## Timeline
{timeline}

## Resources Required
{resources}

## Risks and Mitigation
{risks}

## Conclusion
{conclusion}
"""
    }
}


def initialize_default_templates(conn: sqlite3.Connection):
    """Initialize default templates in the database."""
    for template_id, template_data in DEFAULT_TEMPLATES.items():
        # Check if template already exists
        c = conn.cursor()
        c.execute("SELECT id FROM document_templates WHERE id = ?", (template_id,))
        if c.fetchone():
            continue  # Skip if already exists
        
        # Insert default template
        created_at = datetime.now().isoformat(timespec="seconds")
        c.execute("""
            INSERT INTO document_templates (id, name, category, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            template_id,
            template_data["name"],
            template_data["category"],
            template_data["content"],
            created_at
        ))
    
    conn.commit()


def get_templates(conn: sqlite3.Connection, category: Optional[str] = None) -> List[DocumentTemplate]:
    """Get all templates, optionally filtered by category.
    
    Args:
        conn: Database connection
        category: Optional category filter
    
    Returns:
        List of DocumentTemplate objects
    """
    c = conn.cursor()
    
    if category:
        c.execute("""
            SELECT id, name, category, content, created_at, updated_at
            FROM document_templates
            WHERE category = ?
            ORDER BY name
        """, (category,))
    else:
        c.execute("""
            SELECT id, name, category, content, created_at, updated_at
            FROM document_templates
            ORDER BY category, name
        """)
    
    rows = c.fetchall()
    templates = []
    for row in rows:
        templates.append(DocumentTemplate(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row.get("updated_at")
        ))
    
    return templates


def get_template(conn: sqlite3.Connection, template_id: str) -> Optional[DocumentTemplate]:
    """Get a specific template by ID."""
    c = conn.cursor()
    c.execute("""
        SELECT id, name, category, content, created_at, updated_at
        FROM document_templates
        WHERE id = ?
    """, (template_id,))
    
    row = c.fetchone()
    if not row:
        return None
    
    return DocumentTemplate(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        content=row["content"],
        created_at=row["created_at"],
        updated_at=row.get("updated_at")
    )


def create_template(
    conn: sqlite3.Connection,
    name: str,
    category: str,
    content: str,
    template_id: Optional[str] = None
) -> str:
    """Create a new template.
    
    Args:
        conn: Database connection
        name: Template name
        category: Template category
        content: Template content with {placeholders}
        template_id: Optional custom ID (auto-generated if not provided)
    
    Returns:
        Template ID
    """
    if template_id is None:
        template_id = str(uuid.uuid4())
    
    created_at = datetime.now().isoformat(timespec="seconds")
    
    c = conn.cursor()
    c.execute("""
        INSERT INTO document_templates (id, name, category, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (template_id, name, category, content, created_at))
    
    conn.commit()
    return template_id


def update_template(
    conn: sqlite3.Connection,
    template_id: str,
    name: Optional[str] = None,
    category: Optional[str] = None,
    content: Optional[str] = None
) -> bool:
    """Update an existing template."""
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    
    if not updates:
        return False
    
    updated_at = datetime.now().isoformat(timespec="seconds")
    updates.append("updated_at = ?")
    params.append(updated_at)
    params.append(template_id)
    
    c = conn.cursor()
    c.execute(f"""
        UPDATE document_templates
        SET {', '.join(updates)}
        WHERE id = ?
    """, params)
    
    conn.commit()
    return c.rowcount > 0


def delete_template(conn: sqlite3.Connection, template_id: str) -> bool:
    """Delete a template."""
    c = conn.cursor()
    c.execute("DELETE FROM document_templates WHERE id = ?", (template_id,))
    conn.commit()
    return c.rowcount > 0


def render_template(template: DocumentTemplate, values: Dict[str, str]) -> str:
    """Render a template with provided values.
    
    Args:
        template: DocumentTemplate object
        values: Dict mapping placeholder names to values
    
    Returns:
        Rendered document as string
    """
    content = template.content
    
    # Find all placeholders in the template
    placeholders = re.findall(r'\{(\w+)\}', content)
    
    # Replace placeholders with values
    for placeholder in placeholders:
        value = values.get(placeholder, f"{{{{ {placeholder} }}}}")  # Keep placeholder if not found
        content = content.replace(f"{{{placeholder}}}", str(value))
    
    return content


def get_template_placeholders(template: DocumentTemplate) -> List[str]:
    """Extract all placeholder names from a template."""
    placeholders = re.findall(r'\{(\w+)\}', template.content)
    return list(set(placeholders))  # Remove duplicates


def get_categories(conn: sqlite3.Connection) -> List[str]:
    """Get all unique template categories."""
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM document_templates ORDER BY category")
    rows = c.fetchall()
    return [row["category"] for row in rows]


