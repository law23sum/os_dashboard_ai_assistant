"""Extract tasks from uploaded files using AI."""

import os
import json
import re
from typing import List, Dict, Optional
from datetime import datetime

from .db import Task, db_insert_task, PERSONAS, PRIORITY_OPTIONS
from .ai import openai_available, get_openai_client


def extract_tasks_from_file_content(
    file_content: str,
    file_name: str,
    project_name: str,
    owner: str = "Chris"
) -> List[Task]:
    """Extract tasks from file content using AI."""
    
    if not openai_available():
        # Fallback to simple text extraction
        return _extract_tasks_simple(file_content, project_name, owner)
    
    # Create a prompt for AI to extract tasks
    prompt = f"""Analyze the following document and extract all tasks, action items, or to-do items. 
Return them as a JSON array of objects, each with:
- "title": the task title
- "sequence": the order/sequence number (1, 2, 3, etc.)
- "priority": one of {PRIORITY_OPTIONS} (default to MEDIUM)
- "notes": any additional context or details
- "depends_on_sequence": (optional) sequence number of a task this depends on

Document name: {file_name}
Project: {project_name}

Document content:
{file_content[:8000]}  # Limit content size

Return ONLY valid JSON array, no other text."""

    try:
        # Use AI to extract tasks
        messages = [
            {
                "role": "system",
                "content": "You are a task extraction assistant. Extract tasks from documents and return them as a JSON array. Always return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for extraction
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )
        
        reply_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        json_text = _extract_json_from_response(reply_text)
        
        if json_text:
            tasks_data = json.loads(json_text)
            return _create_tasks_from_ai_response(tasks_data, project_name, owner)
        else:
            # Fallback to simple extraction
            return _extract_tasks_simple(file_content, project_name, owner)
            
    except Exception as e:
        # Fallback to simple extraction on error
        return _extract_tasks_simple(file_content, project_name, owner)


def _extract_json_from_response(text: str) -> Optional[str]:
    """Extract JSON from AI response, handling markdown code blocks."""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Try to find JSON array
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    # Try to parse the whole text as JSON
    try:
        json.loads(text)
        return text
    except:
        return None


def _create_tasks_from_ai_response(
    tasks_data: List[Dict],
    project_name: str,
    owner: str
) -> List[Task]:
    """Create Task objects from AI-extracted data."""
    tasks = []
    
    # Sort by sequence number
    sorted_tasks = sorted(tasks_data, key=lambda x: x.get("sequence", 999))
    
    for i, task_data in enumerate(sorted_tasks):
        title = task_data.get("title", "").strip()
        if not title:
            continue
        
        sequence = task_data.get("sequence", i + 1)
        priority = task_data.get("priority", "MEDIUM")
        if priority not in PRIORITY_OPTIONS:
            priority = "MEDIUM"
        
        notes = task_data.get("notes", "")
        if notes:
            notes = f"Sequence: {sequence}\n{notes}"
        else:
            notes = f"Sequence: {sequence}"
        
        # Dependencies will be handled after all tasks are created
        depends_on_sequence = task_data.get("depends_on_sequence")
        
        task = Task(
            id=0,  # Will be set after insertion
            title=title,
            project=project_name,
            status="TODO",
            priority=priority,
            due_date="",
            notes=notes,
            owner=owner,
            created_at=datetime.now().isoformat(timespec="seconds"),
            depends_on=None,  # Will be set later if needed
            recurrence_pattern=None,
            recurrence_end=None,
            time_estimated=None,
            time_logged=None,
            template_id=None,
        )
        
        # Store sequence for dependency resolution
        task._temp_sequence = sequence
        task._temp_depends_on_sequence = depends_on_sequence
        
        tasks.append(task)
    
    return tasks


def _extract_tasks_simple(
    content: str,
    project_name: str,
    owner: str
) -> List[Task]:
    """Simple fallback task extraction using regex patterns."""
    tasks = []
    
    # Patterns for common task indicators
    patterns = [
        r'(?:^|\n)\s*[-*•]\s+(.+?)(?:\n|$)',
        r'(?:^|\n)\s*\d+[\.)]\s+(.+?)(?:\n|$)',
        r'(?:^|\n)\s*(?:TODO|TASK|ACTION):\s*(.+?)(?:\n|$)',
        r'(?:^|\n)\s*(?:Step|Phase|Stage)\s+\d+[\.:]?\s+(.+?)(?:\n|$)',
    ]
    
    found_items = []
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            task_text = match.group(1).strip()
            if len(task_text) > 3 and task_text not in found_items:
                found_items.append(task_text)
    
    # Create tasks in order
    for i, task_text in enumerate(found_items):
        task = Task(
            id=0,
            title=task_text[:200],  # Limit title length
            project=project_name,
            status="TODO",
            priority="MEDIUM",
            due_date="",
            notes=f"Extracted from file (sequence: {i + 1})",
            owner=owner,
            created_at=datetime.now().isoformat(timespec="seconds"),
            depends_on=None,
            recurrence_pattern=None,
            recurrence_end=None,
            time_estimated=None,
            time_logged=None,
            template_id=None,
        )
        tasks.append(task)
    
    return tasks


def extract_and_create_tasks_from_file(
    conn,
    file_path: str,
    project_name: str,
    owner: str = "Chris"
) -> List[Task]:
    """Extract tasks from a file and create them in the database."""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try binary read for non-text files
        with open(file_path, 'rb') as f:
            content = f.read()
            # For binary files, we can't extract text tasks
            return []
    except Exception as e:
        return []
    
    file_name = os.path.basename(file_path)
    
    # Extract tasks
    tasks = extract_tasks_from_file_content(content, file_name, project_name, owner)
    
    if not tasks:
        return []
    
    # Insert tasks into database in sequence order
    created_tasks = []
    sequence_to_id = {}
    
    # First pass: insert all tasks and map sequences
    for task in tasks:
        # Get temp sequence before removing
        temp_seq = getattr(task, '_temp_sequence', None)
        temp_dep = getattr(task, '_temp_depends_on_sequence', None)
        
        # Remove temp attributes before insertion
        if hasattr(task, '_temp_sequence'):
            delattr(task, '_temp_sequence')
        if hasattr(task, '_temp_depends_on_sequence'):
            delattr(task, '_temp_depends_on_sequence')
        
        task.id = db_insert_task(conn, task)
        created_tasks.append(task)
        
        # Map sequence to task ID for dependency resolution
        if temp_seq:
            sequence_to_id[temp_seq] = task.id
    
    # Second pass: update dependencies based on sequence numbers
    from .db import db_update_task
    for task in created_tasks:
        # Check if this task should depend on a previous task
        # We'll use sequential dependencies: each task depends on the previous one
        task_index = created_tasks.index(task)
        if task_index > 0:
            # Make each task depend on the previous one to maintain sequence
            task.depends_on = created_tasks[task_index - 1].id
            db_update_task(conn, task)
    
    return created_tasks

