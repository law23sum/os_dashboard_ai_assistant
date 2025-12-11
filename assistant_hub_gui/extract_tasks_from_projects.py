#!/usr/bin/env python3
"""Extract tasks from project descriptions and create Task entries in the database."""

import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from assistant_hub.db import (
    init_db,
    load_state,
    db_insert_task,
    Task,
    PRIORITY_OPTIONS,
    STATUS_OPTIONS,
)


def parse_tasks_from_description(description: str) -> list[str]:
    """Extract task items from a project description."""
    tasks = []

    # Look for "Next Tasks:" section
    next_tasks_match = re.search(
        r"Next Tasks:\s*\n(.*?)(?:\n\n|\nDeliverables:|$)",
        description,
        re.DOTALL | re.IGNORECASE,
    )
    if next_tasks_match:
        tasks_text = next_tasks_match.group(1)
        # Split by lines starting with "-"
        current_task = None
        for line in tasks_text.split("\n"):
            line = line.strip()
            if line.startswith("-"):
                # Save previous task if exists
                if current_task:
                    tasks.append(current_task)
                # Start new task
                current_task = line[1:].strip()
            elif current_task and line:
                # Continuation of previous task
                current_task += " " + line
        # Don't forget the last task
        if current_task:
            tasks.append(current_task)

    return tasks


def expand_task(task_text: str, project_name: str) -> list[str]:
    """Break down a task into more granular, explicit sub-tasks."""
    task_lower = task_text.lower()
    expanded = []

    # Handle parenthetical lists like "(AND / OR / EXCEPT / RESONATE / COLLAPSE / etc.)"
    # These should stay as part of the main task, not split
    if re.search(r"\([^)]*/\s*[^)]*\)", task_text):
        # Keep as single task - it's a list of options/examples
        return [task_text]

    # Handle tasks with multiple items separated by "/" (but not in parentheses)
    if " / " in task_text and "(" not in task_text:
        parts = [p.strip() for p in task_text.split(" / ")]
        # Only split if parts are substantial (more than 2 words each)
        if all(len(p.split()) >= 2 for p in parts if p):
            for part in parts:
                if part and len(part.split()) >= 2:
                    expanded.append(part)
            if expanded:
                return expanded

    # Handle enumeration patterns like "1. X, 2. Y, 3. Z"
    enum_items = re.findall(r"(\d+)\.\s*([^,\n]+)", task_text)
    if len(enum_items) > 1:
        for num, item in enum_items:
            item = item.strip()
            if item:
                expanded.append(item)
        if expanded:
            return expanded

    # Handle tasks with "and" that should be split (but be careful)
    # Only split if both parts are substantial
    if " and " in task_text:
        # Don't split if it's a list like "locked, beating, amplifying, and cancelling"
        if re.search(r",\s*\w+\s*,\s*\w+\s*,\s*and\s+\w+", task_text):
            return [task_text]  # Keep as single task

        # Check if it's a list pattern like "X, Y, and Z"
        list_match = re.search(r"([^,]+),\s*([^,]+)(?:,\s*and\s*([^,]+))?", task_text)
        if list_match:
            parts = [p.strip() for p in task_text.split(",")]
            # Clean up "and" from last part
            cleaned_parts = []
            for part in parts:
                part = re.sub(r"^\s*and\s+", "", part.strip())
                # Only split if part is substantial (at least 3 words or has a verb)
                verbs = [
                    "define",
                    "specify",
                    "build",
                    "create",
                    "implement",
                    "design",
                    "encode",
                    "derive",
                    "prove",
                    "show",
                    "test",
                    "catalogue",
                    "assign",
                    "map",
                    "demonstrate",
                    "relate",
                    "connect",
                    "finalize",
                    "lock",
                    "note",
                    "classify",
                    "characterize",
                    "formalize",
                ]
                has_verb = any(verb in part.lower() for verb in verbs)
                if part and (len(part.split()) >= 3 or has_verb):
                    cleaned_parts.append(part)
            if len(cleaned_parts) > 1:
                return cleaned_parts

        # Simple "X and Y" pattern - only split if both are substantial
        parts = task_text.split(" and ", 1)
        if len(parts) == 2:
            part1, part2 = parts[0].strip(), parts[1].strip()
            # Only split if both parts are substantial and have verbs
            verbs = [
                "define",
                "specify",
                "build",
                "create",
                "implement",
                "design",
                "encode",
                "derive",
                "prove",
                "show",
                "test",
                "catalogue",
                "assign",
                "map",
                "demonstrate",
                "relate",
                "connect",
                "finalize",
                "lock",
                "note",
                "classify",
                "characterize",
                "formalize",
            ]
            has_verb1 = any(verb in part1.lower() for verb in verbs)
            has_verb2 = any(verb in part2.lower() for verb in verbs)
            # Both parts must be substantial (at least 3 words each)
            if (
                has_verb1
                and has_verb2
                and len(part1.split()) >= 3
                and len(part2.split()) >= 3
            ):
                return [part1, part2]

    # Handle semicolon-separated tasks
    if ";" in task_text:
        parts = [p.strip() for p in task_text.split(";")]
        if len(parts) > 1 and all(len(p.split()) >= 3 for p in parts if p):
            return [p for p in parts if p]

    # Handle "then" or "and then" separators
    if " then " in task_lower or " and then " in task_lower:
        parts = re.split(r"\s+then\s+|\s+and then\s+", task_text, flags=re.IGNORECASE)
        if len(parts) > 1 and all(
            len(p.strip().split()) >= 3 for p in parts if p.strip()
        ):
            return [p.strip() for p in parts if p.strip()]

    # Default: return as single task
    return [task_text]


def create_granular_tasks(
    project_name: str, description: str, priority: str
) -> list[Task]:
    """Create granular, explicit tasks from a project description."""
    raw_tasks = parse_tasks_from_description(description)
    all_tasks = []

    for raw_task in raw_tasks:
        # Expand into granular tasks
        expanded = expand_task(raw_task, project_name)

        for task_text in expanded:
            # Make task more explicit
            explicit_task = make_explicit(task_text, project_name)

            # Skip if task is None (incomplete/invalid)
            if explicit_task is None:
                continue

            # Create task object
            task = Task(
                id=0,
                title=explicit_task,
                project=project_name,
                status="TODO",
                priority=priority,
                due_date="",
                notes=f"Extracted from project: {project_name}\nOriginal: {raw_task}",
                owner="AIC",  # Default to AIC for extracted tasks
                created_at=datetime.now().isoformat(timespec="seconds"),
            )
            all_tasks.append(task)

    return all_tasks


def make_explicit(task_text: str, project_name: str) -> str:
    """Make a task more explicit and actionable."""
    task = task_text.strip()

    # Expand abbreviations first
    task = task.replace("TRF", "Theoretical Reasoning Framework")
    task = task.replace("AIC", "AIC daemon framework")
    task = task.replace("MPIS", "Mathematical Phenomena Interpretation System")

    # Remove redundant patterns
    task = re.sub(
        r"define and specify mathematical define",
        "define and specify mathematical",
        task,
        flags=re.IGNORECASE,
    )
    task = re.sub(
        r"define and specify define", "define and specify", task, flags=re.IGNORECASE
    )
    task = re.sub(
        r"characterize and document locked\.",
        "Characterize and document locked patterns.",
        task,
        flags=re.IGNORECASE,
    )
    task = re.sub(
        r"characterize and document cancelling",
        "Characterize and document cancelling patterns",
        task,
        flags=re.IGNORECASE,
    )

    # Fix incomplete tasks
    if task.strip() in [
        "locked.",
        "cancelling patterns.",
        "equation set.",
        "canon volume.",
        "operations.",
        "operators.",
        "relations.",
        "y.",
        "t).",
    ]:
        return None  # Skip these incomplete tasks

    # Make verbs more explicit (but check if already explicit)
    verb_replacements = {
        r"^finalize\s+": "Finalize and document ",
        r"^define\s+": "Define and specify ",
        r"^specify\s+": "Specify and document ",
        r"^build\s+": "Build and implement ",
        r"^create\s+": "Create and document ",
        r"^encode\s+": "Encode and test ",
        r"^derive\s+": "Derive and verify ",
        r"^prove\s+": "Prove and document ",
        r"^show\s+": "Show and demonstrate ",
        r"^test\s+": "Test and validate ",
        r"^map\s+": "Map and document ",
        r"^classify\s+": "Classify and organize ",
        r"^catalogue\s+": "Catalogue and organize ",
        r"^assign\s+": "Assign and document ",
        r"^connect\s+": "Connect and verify ",
        r"^relate\s+": "Relate and document ",
        r"^characterize\s+": "Characterize and document ",
        r"^formalize\s+": "Formalize and verify ",
        r"^design\s+": "Design and document ",
        r"^implement\s+": "Implement and test ",
    }

    # Only apply if task doesn't already have explicit verb
    task_lower = task.lower()
    if not any(
        phrase in task_lower
        for phrase in [
            " and document",
            " and specify",
            " and implement",
            " and test",
            " and verify",
            " and demonstrate",
        ]
    ):
        for pattern, replacement in verb_replacements.items():
            if re.match(pattern, task, re.IGNORECASE):
                task = re.sub(pattern, replacement, task, flags=re.IGNORECASE)
                break

    # Add context from project name if task is too vague
    if len(task.split()) < 4:
        project_short = (
            project_name.split(".")[1].strip() if "." in project_name else project_name
        )
        if "framework" in project_name.lower():
            if "framework" not in task.lower():
                task = f"{task} for {project_short}"
        elif "mathematics" in project_name.lower() or "math" in project_name.lower():
            if "mathematical" not in task.lower() and "math" not in task.lower():
                task = f"{task} in {project_short}"

    # Ensure task ends with proper punctuation
    if not task.endswith((".", "!", "?")):
        task += "."

    return task


def ensure_unique_tasks(
    new_tasks: list[Task], existing_tasks: list[Task]
) -> list[Task]:
    """Filter out tasks that already exist (by title and project)."""
    existing_keys = {(t.title.lower().strip(), t.project) for t in existing_tasks}
    unique_tasks = []

    for task in new_tasks:
        key = (task.title.lower().strip(), task.project)
        if key not in existing_keys:
            unique_tasks.append(task)
            existing_keys.add(key)  # Prevent duplicates within new_tasks too

    return unique_tasks


def create_default_tasks_for_project(project_name: str, priority: str) -> list[Task]:
    """Create default explicit tasks for projects without detailed descriptions."""
    project_lower = project_name.lower()
    tasks = []

    # Common task patterns based on project type
    if "framework" in project_lower:
        tasks.extend(
            [
                "Define core concepts and principles for the framework",
                "Design architecture and component structure",
                "Implement core functionality and algorithms",
                "Create documentation and usage examples",
                "Test and validate framework components",
            ]
        )
    elif "mathematics" in project_lower or "math" in project_lower:
        tasks.extend(
            [
                "Define mathematical foundations and axioms",
                "Develop formal definitions and theorems",
                "Prove key mathematical properties",
                "Create examples and applications",
                "Document mathematical framework",
            ]
        )
    elif "physics" in project_lower or "resonance" in project_lower:
        tasks.extend(
            [
                "Define physical principles and equations",
                "Develop theoretical framework",
                "Create mathematical models",
                "Design experimental validation approach",
                "Document physics framework",
            ]
        )
    elif (
        "software" in project_lower
        or "platform" in project_lower
        or "mvp" in project_lower
    ):
        tasks.extend(
            [
                "Design system architecture and components",
                "Implement core features and functionality",
                "Create user interface and user experience",
                "Set up development environment and tooling",
                "Write tests and documentation",
                "Deploy and validate system",
            ]
        )
    elif "book" in project_lower or "writing" in project_lower:
        tasks.extend(
            [
                "Outline book structure and chapters",
                "Research and gather source materials",
                "Write first draft of content",
                "Review and revise content",
                "Format and prepare for publication",
            ]
        )
    elif "podcast" in project_lower:
        tasks.extend(
            [
                "Plan Season 1 episode topics and structure (10-12 episodes)",
                "Research and prepare content for pilot episode",
                "Record and edit pilot episode",
                "Create intro/outro branding and music",
                "Set up distribution channels (Spotify, Apple Podcasts, YouTube)",
                "Create show notes and transcripts",
            ]
        )
    elif "royal polyarchy" in project_lower or "cosmology" in project_lower:
        tasks.extend(
            [
                "Define worldbuilding concepts and rules",
                "Create character and entity definitions",
                "Develop narrative structure and arcs",
                "Design visual and symbolic elements",
                "Document worldbuilding framework",
            ]
        )
    else:
        # Generic tasks for any project
        tasks.extend(
            [
                "Define project scope, requirements, and success criteria",
                "Design core components, architecture, and structure",
                "Implement primary functionality and core features",
                "Test, validate, and verify implementation",
                "Create comprehensive documentation and deliverables",
            ]
        )

    # Create Task objects
    task_objects = []
    for i, task_text in enumerate(tasks):
        task = Task(
            id=0,
            title=task_text,
            project=project_name,
            status="TODO",
            priority=priority,
            due_date="",
            notes=f"Default task for project: {project_name}",
            owner="AIC",
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        task_objects.append(task)

    return task_objects


def main():
    """Main function to extract and create tasks."""
    conn = init_db()
    state = load_state(conn)

    print("Extracting tasks from project descriptions...\n")

    total_created = 0
    total_skipped = 0

    for project in state.projects:
        print(f"Processing: {project.name}")

        # Determine priority based on project priority
        task_priority = project.priority
        if project.priority == "CRITICAL":
            task_priority = "HIGH"

        # Create granular tasks from description
        new_tasks = []
        if project.description:
            new_tasks = create_granular_tasks(
                project.name, project.description, task_priority
            )

        # If no tasks extracted, create default tasks
        if not new_tasks:
            new_tasks = create_default_tasks_for_project(project.name, task_priority)
            print(f"  → Created {len(new_tasks)} default tasks (no Next Tasks found)")

        # Filter for uniqueness
        unique_tasks = ensure_unique_tasks(new_tasks, state.tasks)

        # Add to database
        for task in unique_tasks:
            task_id = db_insert_task(conn, task)
            task.id = task_id
            state.tasks.append(task)
            print(f"  ✓ Created: {task.title[:70]}")
            total_created += 1

        skipped = len(new_tasks) - len(unique_tasks)
        if skipped > 0:
            print(f"  ⊘ Skipped {skipped} duplicate task(s)")
            total_skipped += skipped

        print()

    conn.close()
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Created: {total_created} new tasks")
    print(f"  Skipped: {total_skipped} duplicate tasks")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
