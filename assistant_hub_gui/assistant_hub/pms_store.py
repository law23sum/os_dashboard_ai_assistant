"""Data access helpers for the Project Management System (PMS)."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from assistant_hub_gui.assistant_hub.config import get_attachment_path
from assistant_hub_gui.assistant_hub.db import db_record_project_event
from assistant_hub_gui.assistant_hub.pms_journal import generate_journal_blocks
from assistant_hub_gui.assistant_hub.pms_models import PMS_TASK_STATUSES


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _json_load(raw: Optional[str], default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def _json_loads(raw: Optional[str]) -> Any:
    return _json_load(raw, {})


def _json_dump(value: Any) -> Optional[str]:
    if value is None:
        return None
    return json.dumps(value)


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row) if row is not None else {}


def _require_row(row: Optional[sqlite3.Row], label: str, entity_id: str) -> sqlite3.Row:
    if row is None:
        raise ValueError(f"{label} not found: {entity_id}")
    return row


def _project_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["config"] = _json_load(data.pop("config_json", None), {})
    budget = _json_load(data.pop("budget_json", None), None)
    data["budget"] = budget
    data["scope"] = data.get("scope_id") or data.get("scope_type") or ""
    return data


def _epic_from_row(row: sqlite3.Row, rollup: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["rollup"] = rollup
    return data


def _todo_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = _row_to_dict(row)
    status = data.get("status") or "TODO"
    if status == "PENDING":
        status = "TODO"
    data["status"] = status
    return data




def _task_from_row(row: sqlite3.Row, todos: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["epic_id"] = data.get("epic_id") or None
    data["deliverable_spec"] = data.get("deliverable_spec") or ""
    data["acceptance_criteria"] = data.get("acceptance_criteria") or ""
    data["priority"] = data.get("priority") or "P1"
    data["category"] = data.get("category") or "General"
    data["task_type"] = data.get("task_type") or "General"
    data["status"] = data.get("status") or "TODO"
    data["enqueue_time"] = data.get("enqueue_time") or data.get("created_at") or _now()
    data["todos"] = todos or []
    return data


def _run_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["input_params"] = _json_load(data.get("input_params"), {})
    return data


def _artifact_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["size"] = data.get("size")
    return data


def _document_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = _row_to_dict(row)
    return data


def _document_revision_from_row(row: sqlite3.Row, content: Optional[str] = None) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["metadata"] = _json_load(data.get("metadata_json"), {})
    if content is not None:
        data["content"] = content
    return data


def _meeting_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["participants"] = _json_load(data.get("participants_json"), [])
    return data


def _journal_block_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = _row_to_dict(row)
    data["references"] = _json_load(data.get("references_json"), {})
    return data


def _speaker_mapping_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    return _row_to_dict(row)


def _load_speaker_mapping(conn: sqlite3.Connection, meeting_id: str) -> Tuple[Dict[str, str], bool]:
    rows = conn.execute(
        """
        SELECT speaker_label, participant_name, consented_by
        FROM pms_speaker_mappings
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    ).fetchall()
    mapping: Dict[str, str] = {}
    consent = False
    for row in rows:
        if row["speaker_label"] and row["participant_name"]:
            mapping[row["speaker_label"]] = row["participant_name"]
        if row["consented_by"]:
            consent = True
    return mapping, consent


DEFAULT_PROJECT_CONFIG: Dict[str, Any] = {
    "priority_tiers": ["P0", "P1", "P2", "P3"],
    "categories": ["General"],
    "types": ["General"],
}

TEMPLATE_PACK_CONFIGS: Dict[str, Dict[str, Any]] = {
    "dev": {
        "label": "Dev Pack",
        "description": "Engineering planning templates with CI/CD and release milestones.",
        "config": {
            "priority_tiers": ["P0", "P1", "P2", "P3"],
            "categories": ["Build", "Review", "Test", "Release"],
            "types": ["Feature", "Bugfix", "Chore", "Incident"],
        },
    },
    "research": {
        "label": "Research Pack",
        "description": "Experiment planning templates with hypothesis and validation steps.",
        "config": {
            "priority_tiers": ["P0", "P1", "P2", "P3"],
            "categories": ["Hypothesis", "Experiment", "Analysis", "Publication"],
            "types": ["Study", "Prototype", "Validation"],
        },
    },
    "writing": {
        "label": "Writer Pack",
        "description": "Editorial planning templates with drafts and reviews.",
        "config": {
            "priority_tiers": ["P0", "P1", "P2", "P3"],
            "categories": ["Draft", "Edit", "Review", "Publish"],
            "types": ["Chapter", "Outline", "Revision"],
        },
    },
    "finance": {
        "label": "Finance Pack",
        "description": "Cost tracking templates with budgets and approvals.",
        "config": {
            "priority_tiers": ["P0", "P1", "P2", "P3"],
            "categories": ["Ops", "Strategy", "Reporting", "Audit"],
            "types": ["Budget", "Forecast", "Reconciliation"],
        },
    },
    "cyber": {
        "label": "Cyber Pack",
        "description": "Security response templates with incident phases.",
        "config": {
            "priority_tiers": ["P0", "P1", "P2", "P3"],
            "categories": ["Detect", "Respond", "Recover", "Prevent"],
            "types": ["Alert", "Investigation", "Mitigation"],
        },
    },
}


def _merge_project_config(config: Optional[Dict[str, Any]], template_pack: Optional[str]) -> Dict[str, Any]:
    merged = dict(DEFAULT_PROJECT_CONFIG)
    if template_pack and template_pack in TEMPLATE_PACK_CONFIGS:
        merged.update(TEMPLATE_PACK_CONFIGS[template_pack]["config"])
        merged.setdefault("template_pack", template_pack)
    if config:
        merged.update(config)
    return merged


def list_template_packs() -> List[Dict[str, Any]]:
    return [
        {
            "id": pack_id,
            "label": payload["label"],
            "description": payload["description"],
            "config": payload["config"],
        }
        for pack_id, payload in TEMPLATE_PACK_CONFIGS.items()
    ]


def list_projects(
    conn: sqlite3.Connection,
    *,
    mode: Optional[str] = None,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None,
    include_samples: bool = False,
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM pms_projects"
    clauses = []
    params: List[Any] = []
    if mode:
        clauses.append("mode = ?")
        params.append(mode)
    if scope_type:
        clauses.append("scope_type = ?")
        params.append(scope_type)
    if scope_id:
        clauses.append("scope_id = ?")
        params.append(scope_id)
    if not include_samples:
        clauses.append("is_sample = 0")
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY datetime(updated_at) DESC"
    rows = conn.execute(query, params).fetchall()
    return [_project_from_row(row) for row in rows]


def create_project(
    conn: sqlite3.Connection,
    *,
    name: str,
    mode: str,
    scope_type: str,
    scope_id: str,
    status: str,
    config: Optional[Dict[str, Any]] = None,
    budget_amount: Optional[float] = None,
    budget_currency: Optional[str] = None,
    template_pack: Optional[str] = None,
    created_by: Optional[str] = None,
    is_sample: int = 0,
) -> Dict[str, Any]:
    existing = conn.execute(
        """
        SELECT * FROM pms_projects WHERE scope_type = ? AND scope_id = ? AND name = ?
        """,
        (scope_type, scope_id, name),
    ).fetchone()
    if existing:
        return _project_from_row(existing)

    project_id = uuid.uuid4().hex
    now = _now()
    if mode not in {"personal", "enterprise"}:
        mode = "personal"
    config_payload = _merge_project_config(config, template_pack)
    budget_payload = None
    if budget_amount is not None or budget_currency is not None:
        budget_payload = {"amount": budget_amount or 0.0, "currency": budget_currency or "USD"}

    conn.execute(
        """
        INSERT INTO pms_projects (
            project_id, name, mode, scope_type, scope_id, status,
            created_at, updated_at, config_json, budget_json, created_by, is_sample
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            name,
            mode,
            scope_type,
            scope_id,
            status,
            now,
            now,
            _json_dump(config_payload),
            _json_dump(budget_payload),
            created_by,
            int(is_sample),
        ),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.project.created",
        entity_type="project",
        entity_id=project_id,
        payload={"name": name, "mode": mode},
        user_id=created_by or "demo",
    )
    return get_project(conn, project_id)


def get_project(conn: sqlite3.Connection, project_id: str) -> Dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM pms_projects WHERE project_id = ?",
        (project_id,),
    ).fetchone()
    return _project_from_row(_require_row(row, "Project", project_id))


def update_project(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    patch: Dict[str, Any],
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not patch:
        return get_project(conn, project_id)
    now = _now()
    fields = []
    params: List[Any] = []
    current = get_project(conn, project_id)
    if "name" in patch:
        fields.append("name = ?")
        params.append(patch["name"])
    if "status" in patch:
        fields.append("status = ?")
        params.append(patch["status"])
    if "config" in patch:
        merged_config = {**(current.get("config") or {}), **(patch["config"] or {})}
        fields.append("config_json = ?")
        params.append(_json_dump(merged_config))
    if "budget" in patch:
        fields.append("budget_json = ?")
        params.append(_json_dump(patch["budget"]))
    if "budget_amount" in patch or "budget_currency" in patch:
        budget = current.get("budget") or {}
        if "budget_amount" in patch:
            budget["amount"] = patch["budget_amount"]
        if "budget_currency" in patch:
            budget["currency"] = patch["budget_currency"]
        fields.append("budget_json = ?")
        params.append(_json_dump(budget))
    fields.append("updated_at = ?")
    params.append(now)
    params.append(project_id)
    conn.execute(f"UPDATE pms_projects SET {', '.join(fields)} WHERE project_id = ?", params)
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.project.updated",
        entity_type="project",
        entity_id=project_id,
        payload=patch,
        user_id=user_id or "demo",
    )
    return get_project(conn, project_id)


def list_epics(conn: sqlite3.Connection, project_id: str) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM pms_epics
        WHERE project_id = ? AND is_archived = 0
        ORDER BY datetime(updated_at) DESC
        """,
        (project_id,),
    ).fetchall()

    rollups: Dict[str, Dict[str, Any]] = {}
    task_rows = conn.execute(
        """
        SELECT epic_id, status, COUNT(*) as count
        FROM pms_tasks
        WHERE project_id = ? AND is_archived = 0
        GROUP BY epic_id, status
        """,
        (project_id,),
    ).fetchall()
    for row in task_rows:
        epic_id = row["epic_id"] or ""
        rollup = rollups.setdefault(epic_id, {"total_tasks": 0, "done_tasks": 0})
        count = int(row["count"] or 0)
        rollup["total_tasks"] += count
        if row["status"] in {"DONE", "ARCHIVED"}:
            rollup["done_tasks"] += count
    for epic_id, rollup in rollups.items():
        total = rollup["total_tasks"]
        done = rollup["done_tasks"]
        rollup["completion_ratio"] = (done / total) if total else 0.0

    return [_epic_from_row(row, rollups.get(row["epic_id"])) for row in rows]


def create_epic(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    title: str,
    description: str,
    acceptance_criteria: str,
    status: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    epic_id = uuid.uuid4().hex
    now = _now()
    project = get_project(conn, project_id)
    conn.execute(
        """
        INSERT INTO pms_epics (
            epic_id, project_id, title, description, acceptance_criteria,
            status, created_at, updated_at, scope_type, scope_id, created_by, is_archived
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            epic_id,
            project_id,
            title,
            description,
            acceptance_criteria,
            status,
            now,
            now,
            project.get("scope_type"),
            project.get("scope_id"),
            user_id,
        ),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.epic.created",
        entity_type="epic",
        entity_id=epic_id,
        payload={"title": title},
        user_id=user_id or "demo",
    )
    row = conn.execute("SELECT * FROM pms_epics WHERE epic_id = ?", (epic_id,)).fetchone()
    return _epic_from_row(_require_row(row, "Epic", epic_id))


def get_epic(conn: sqlite3.Connection, epic_id: str) -> Dict[str, Any]:
    row = conn.execute("SELECT * FROM pms_epics WHERE epic_id = ?", (epic_id,)).fetchone()
    return _epic_from_row(_require_row(row, "Epic", epic_id))


def update_epic(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    epic_id: str,
    patch: Dict[str, Any],
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not patch:
        row = conn.execute("SELECT * FROM pms_epics WHERE epic_id = ?", (epic_id,)).fetchone()
        return _epic_from_row(_require_row(row, "Epic", epic_id))
    now = _now()
    fields = []
    params: List[Any] = []
    for key in ("title", "description", "acceptance_criteria", "status"):
        if key in patch:
            fields.append(f"{key} = ?")
            params.append(patch[key])
    fields.append("updated_at = ?")
    params.append(now)
    params.append(epic_id)
    conn.execute(f"UPDATE pms_epics SET {', '.join(fields)} WHERE epic_id = ?", params)
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.epic.updated",
        entity_type="epic",
        entity_id=epic_id,
        payload=patch,
        user_id=user_id or "demo",
    )
    row = conn.execute("SELECT * FROM pms_epics WHERE epic_id = ?", (epic_id,)).fetchone()
    return _epic_from_row(_require_row(row, "Epic", epic_id))


def archive_epic(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    epic_id: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    now = _now()
    conn.execute(
        "UPDATE pms_epics SET is_archived = 1, status = 'ARCHIVED', updated_at = ? WHERE epic_id = ?",
        (now, epic_id),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.epic.archived",
        entity_type="epic",
        entity_id=epic_id,
        payload={"status": "ARCHIVED"},
        user_id=user_id or "demo",
    )
    return get_epic(conn, epic_id)


def list_tasks(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    epic_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    task_type: Optional[str] = None,
    include_archived: bool = False,
) -> List[Dict[str, Any]]:
    clauses = ["project_id = ?"]
    params: List[Any] = [project_id]
    if epic_id:
        clauses.append("epic_id = ?")
        params.append(epic_id)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if priority:
        clauses.append("priority = ?")
        params.append(priority)
    if category:
        clauses.append("category = ?")
        params.append(category)
    if task_type:
        clauses.append("task_type = ?")
        params.append(task_type)
    if not include_archived:
        clauses.append("is_archived = 0")
    query = f"""
        SELECT * FROM pms_tasks
        WHERE {' AND '.join(clauses)}
        ORDER BY datetime(updated_at) DESC
    """
    rows = conn.execute(query, params).fetchall()
    results = []
    for row in rows:
        todos = list_todos(conn, row["task_id"])
        results.append(_task_from_row(row, todos))
    return results


# Compatibility helpers for router imports using pms_* naming.
def pms_get_project(
    conn: sqlite3.Connection,
    project_id: str,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if scope_type and scope_id:
        row = conn.execute(
            "SELECT * FROM pms_projects WHERE project_id = ? AND scope_type = ? AND scope_id = ?",
            (project_id, scope_type, scope_id),
        ).fetchone()
        return _project_from_row(row) if row else None
    try:
        return get_project(conn, project_id)
    except Exception:
        return None


def pms_list_tasks(conn: sqlite3.Connection, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
    return list_tasks(conn, *args, **kwargs)


def pms_get_task(conn: sqlite3.Connection, task_id: str) -> Optional[Dict[str, Any]]:
    try:
        return get_task(conn, task_id)
    except Exception:
        return None


def pms_update_task(conn: sqlite3.Connection, task_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT project_id FROM pms_tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not row:
        return None
    return update_task_metadata(conn, project_id=row["project_id"], task_id=task_id, patch=patch)


def pms_archive_task(conn: sqlite3.Connection, task_id: str) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT project_id FROM pms_tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not row:
        return None
    return archive_task(conn, project_id=row["project_id"], task_id=task_id)


def pms_list_todos(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    return list_todos(conn, task_id)


def pms_get_epic(conn: sqlite3.Connection, epic_id: str) -> Optional[Dict[str, Any]]:
    try:
        return get_epic(conn, epic_id)
    except Exception:
        return None


def pms_archive_epic(conn: sqlite3.Connection, epic_id: str) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT project_id FROM pms_epics WHERE epic_id = ?", (epic_id,)).fetchone()
    if not row:
        return None
    return archive_epic(conn, project_id=row["project_id"], epic_id=epic_id)


def pms_list_epics(conn: sqlite3.Connection, project_id: str) -> List[Dict[str, Any]]:
    return list_epics(conn, project_id)


def pms_get_meeting(conn: sqlite3.Connection, meeting_id: str) -> Optional[Dict[str, Any]]:
    try:
        return get_meeting(conn, meeting_id)
    except Exception:
        return None


def create_meeting(conn: sqlite3.Connection, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    return create_meeting_session(conn, *args, **kwargs)


def add_task(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    epic_id: Optional[str],
    title: str,
    deliverable_spec: str,
    acceptance_criteria: str,
    priority: str,
    category: str,
    task_type: str,
    status: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    task_id = uuid.uuid4().hex
    now = _now()
    project = get_project(conn, project_id)
    conn.execute(
        """
        INSERT INTO pms_tasks (
            task_id, project_id, epic_id, title, deliverable_spec, acceptance_criteria,
            priority, category, task_type, status, created_at, updated_at, enqueue_time,
            scope_type, scope_id, created_by, is_archived
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            task_id,
            project_id,
            epic_id,
            title,
            deliverable_spec,
            acceptance_criteria,
            priority,
            category,
            task_type,
            status,
            now,
            now,
            now,
            project.get("scope_type"),
            project.get("scope_id"),
            user_id,
        ),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.task.created",
        entity_type="task",
        entity_id=task_id,
        payload={"title": title},
        user_id=user_id or "demo",
    )
    return get_task(conn, task_id)


def get_task(conn: sqlite3.Connection, task_id: str) -> Dict[str, Any]:
    row = conn.execute("SELECT * FROM pms_tasks WHERE task_id = ?", (task_id,)).fetchone()
    row = _require_row(row, "Task", task_id)
    todos = list_todos(conn, task_id)
    return _task_from_row(row, todos)


def update_task_metadata(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    task_id: str,
    patch: Dict[str, Any],
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not patch:
        return get_task(conn, task_id)
    now = _now()
    current = get_task(conn, task_id)
    fields = []
    params: List[Any] = []
    priority = patch.get("priority", current.get("priority"))
    category = patch.get("category", current.get("category"))
    task_type = patch.get("task_type", current.get("task_type"))
    status = patch.get("status", current.get("status"))
    enqueue_time = patch.get("enqueue_time", current.get("enqueue_time"))

    if status not in PMS_TASK_STATUSES:
        status = current.get("status")

    if (
        priority != current.get("priority")
        or category != current.get("category")
        or task_type != current.get("task_type")
    ) and "enqueue_time" not in patch:
        enqueue_time = now

    updates = {
        "title": patch.get("title", current.get("title")),
        "deliverable_spec": patch.get("deliverable_spec", current.get("deliverable_spec")),
        "acceptance_criteria": patch.get("acceptance_criteria", current.get("acceptance_criteria")),
        "priority": priority,
        "category": category,
        "task_type": task_type,
        "status": status,
        "epic_id": patch.get("epic_id", current.get("epic_id")),
        "enqueue_time": enqueue_time,
    }
    for key, value in updates.items():
        if key in (
            "title",
            "deliverable_spec",
            "acceptance_criteria",
            "priority",
            "category",
            "task_type",
            "status",
            "epic_id",
            "enqueue_time",
        ):
            fields.append(f"{key} = ?")
            params.append(value)
    fields.append("updated_at = ?")
    params.append(now)
    params.append(task_id)
    conn.execute(f"UPDATE pms_tasks SET {', '.join(fields)} WHERE task_id = ?", params)
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.task.updated",
        entity_type="task",
        entity_id=task_id,
        payload={"before": current, "after": updates},
        user_id=user_id or "demo",
    )
    return get_task(conn, task_id)


def archive_task(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    task_id: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    now = _now()
    conn.execute(
        "UPDATE pms_tasks SET is_archived = 1, status = 'ARCHIVED', updated_at = ? WHERE task_id = ?",
        (now, task_id),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.task.archived",
        entity_type="task",
        entity_id=task_id,
        payload={"status": "ARCHIVED"},
        user_id=user_id or "demo",
    )
    return get_task(conn, task_id)


def list_todos(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM pms_todos
        WHERE task_id = ?
        ORDER BY position ASC
        """,
        (task_id,),
    ).fetchall()
    return [_todo_from_row(row) for row in rows]


def _next_todo_position(conn: sqlite3.Connection, task_id: str) -> int:
    row = conn.execute(
        "SELECT MAX(position) as max_pos FROM pms_todos WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    max_pos = row["max_pos"] if row else None
    return int(max_pos or 0) + 1


def add_todo(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    text: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    todo_id = uuid.uuid4().hex
    now = _now()
    position = _next_todo_position(conn, task_id)
    task_row = conn.execute(
        "SELECT project_id, scope_type, scope_id FROM pms_tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    task_row = _require_row(task_row, "Task", task_id)
    conn.execute(
        """
        INSERT INTO pms_todos (
            todo_id, task_id, text, status, position, created_at, updated_at,
            scope_type, scope_id, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            todo_id,
            task_id,
            text,
            "TODO",
            position,
            now,
            now,
            task_row["scope_type"],
            task_row["scope_id"],
            user_id,
        ),
    )
    row = conn.execute("SELECT * FROM pms_todos WHERE todo_id = ?", (todo_id,)).fetchone()
    db_record_project_event(
        conn,
        project_id=task_row["project_id"],
        event_type="pms.todo.created",
        entity_type="todo",
        entity_id=todo_id,
        payload={"text": text},
        user_id=user_id or "demo",
    )
    return _todo_from_row(_require_row(row, "Todo", todo_id))


def insert_todo(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    text: str,
    after_todo_id: Optional[str] = None,
    position: Optional[int] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    if after_todo_id:
        row = conn.execute(
            "SELECT position FROM pms_todos WHERE todo_id = ?",
            (after_todo_id,),
        ).fetchone()
        position = int(row["position"]) + 1 if row else _next_todo_position(conn, task_id)
    if position is None:
        position = _next_todo_position(conn, task_id)
    conn.execute(
        "UPDATE pms_todos SET position = position + 1 WHERE task_id = ? AND position >= ?",
        (task_id, position),
    )

    todo_id = uuid.uuid4().hex
    now = _now()
    task_row = conn.execute(
        "SELECT project_id, scope_type, scope_id FROM pms_tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    task_row = _require_row(task_row, "Task", task_id)
    conn.execute(
        """
        INSERT INTO pms_todos (
            todo_id, task_id, text, status, position, created_at, updated_at,
            scope_type, scope_id, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            todo_id,
            task_id,
            text,
            "TODO",
            position,
            now,
            now,
            task_row["scope_type"],
            task_row["scope_id"],
            user_id,
        ),
    )
    row = conn.execute("SELECT * FROM pms_todos WHERE todo_id = ?", (todo_id,)).fetchone()
    db_record_project_event(
        conn,
        project_id=task_row["project_id"],
        event_type="pms.todo.inserted",
        entity_type="todo",
        entity_id=todo_id,
        payload={"text": text},
        user_id=user_id or "demo",
    )
    return _todo_from_row(_require_row(row, "Todo", todo_id))


def reorder_todos(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    new_order: List[str],
    user_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    now = _now()
    existing = list_todos(conn, task_id)
    existing_ids = [todo["todo_id"] for todo in existing]
    ordered = [todo_id for todo_id in new_order if todo_id in existing_ids]
    ordered.extend([todo_id for todo_id in existing_ids if todo_id not in ordered])
    for index, todo_id in enumerate(ordered, start=1):
        conn.execute(
            "UPDATE pms_todos SET position = ?, updated_at = ? WHERE todo_id = ? AND task_id = ?",
            (index, now, todo_id, task_id),
        )
    task_row = conn.execute(
        "SELECT project_id FROM pms_tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    if task_row:
        db_record_project_event(
            conn,
            project_id=task_row["project_id"],
            event_type="pms.todo.reordered",
            entity_type="todo",
            entity_id=task_id,
            payload={"todo_ids": ordered},
            user_id=user_id or "demo",
        )
    return list_todos(conn, task_id)


def get_todo(conn: sqlite3.Connection, todo_id: str) -> Dict[str, Any]:
    row = conn.execute("SELECT * FROM pms_todos WHERE todo_id = ?", (todo_id,)).fetchone()
    return _todo_from_row(_require_row(row, "Todo", todo_id))


def complete_todo(
    conn: sqlite3.Connection,
    *,
    todo_id: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    now = _now()
    before = get_todo(conn, todo_id)
    conn.execute(
        "UPDATE pms_todos SET status = 'DONE', updated_at = ? WHERE todo_id = ?",
        (now, todo_id),
    )
    after = get_todo(conn, todo_id)
    task_row = conn.execute(
        "SELECT project_id FROM pms_tasks WHERE task_id = ?",
        (after["task_id"],),
    ).fetchone()
    if task_row:
        db_record_project_event(
            conn,
            project_id=task_row["project_id"],
            event_type="pms.todo.completed",
            entity_type="todo",
            entity_id=todo_id,
            payload={"before": before, "after": after},
            user_id=user_id or "demo",
        )
    return after


def start_run(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    epic_id: Optional[str],
    task_id: Optional[str],
    todo_id: Optional[str],
    input_params: Dict[str, Any],
    status: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    run_id = uuid.uuid4().hex
    now = _now()
    if status not in {"queued", "running", "succeeded", "failed", "needs_review"}:
        status = "queued"
    project = get_project(conn, project_id)
    conn.execute(
        """
        INSERT INTO pms_runs (
            run_id, project_id, epic_id, task_id, todo_id, input_params,
            status, started_at, ended_at, summary, created_by, scope_type, scope_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?)
        """,
        (
            run_id,
            project_id,
            epic_id,
            task_id,
            todo_id,
            _json_dump(input_params),
            status,
            now,
            user_id,
            project.get("scope_type"),
            project.get("scope_id"),
        ),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.run.started",
        entity_type="run",
        entity_id=run_id,
        payload={"status": status},
        user_id=user_id or "demo",
    )
    return get_run(conn, run_id)


def get_run(conn: sqlite3.Connection, run_id: str) -> Dict[str, Any]:
    row = conn.execute("SELECT * FROM pms_runs WHERE run_id = ?", (run_id,)).fetchone()
    return _run_from_row(_require_row(row, "Run", run_id))


def complete_run(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    project_id: str,
    status: str,
    summary: Optional[str],
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    now = _now()
    conn.execute(
        "UPDATE pms_runs SET status = ?, summary = ?, ended_at = ? WHERE run_id = ?",
        (status, summary, now, run_id),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.run.completed",
        entity_type="run",
        entity_id=run_id,
        payload={"status": status},
        user_id=user_id or "demo",
    )
    return get_run(conn, run_id)


def list_runs(
    conn: sqlite3.Connection,
    *,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    clauses = []
    params: List[Any] = []
    if project_id:
        clauses.append("project_id = ?")
        params.append(project_id)
    if task_id:
        clauses.append("task_id = ?")
        params.append(task_id)
    query = "SELECT * FROM pms_runs"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY datetime(started_at) DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    return [_run_from_row(row) for row in rows]


def attach_artifact(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    run_id: Optional[str],
    kind: str,
    content: Optional[bytes],
    filename: Optional[str] = None,
    display_name: Optional[str] = None,
    mime_type: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    artifact_id = uuid.uuid4().hex
    now = _now()
    project = get_project(conn, project_id)
    storage_path = None
    size = None
    sha256 = None

    if content is not None:
        name = filename or f"{artifact_id}.bin"
        storage_path = get_attachment_path("pms", "artifacts", project_id, run_id or "unlinked", name)
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)
        size = storage_path.stat().st_size
        sha256 = hashlib.sha256(content).hexdigest()

    conn.execute(
        """
        INSERT INTO pms_artifacts (
            artifact_id, project_id, run_id, kind, filename, display_name,
            mime_type, size, sha256, created_at, storage_path, scope_type, scope_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            artifact_id,
            project_id,
            run_id,
            kind,
            filename,
            display_name,
            mime_type,
            size,
            sha256,
            now,
            str(storage_path) if storage_path else None,
            project.get("scope_type"),
            project.get("scope_id"),
        ),
    )
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.artifact.attached",
        entity_type="artifact",
        entity_id=artifact_id,
        payload={"filename": filename, "kind": kind},
        user_id=user_id or "demo",
    )
    return get_artifact(conn, artifact_id)


def list_artifacts(
    conn: sqlite3.Connection,
    *,
    project_id: Optional[str] = None,
    run_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    clauses = []
    params: List[Any] = []
    if project_id:
        clauses.append("project_id = ?")
        params.append(project_id)
    if run_id:
        clauses.append("run_id = ?")
        params.append(run_id)
    if task_id:
        run_rows = conn.execute(
            "SELECT run_id FROM pms_runs WHERE task_id = ?",
            (task_id,),
        ).fetchall()
        run_ids = [row["run_id"] for row in run_rows]
        if run_ids:
            clauses.append(f"run_id IN ({', '.join('?' for _ in run_ids)})")
            params.extend(run_ids)
        else:
            return []
    query = "SELECT * FROM pms_artifacts"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY datetime(created_at) DESC"
    rows = conn.execute(query, params).fetchall()
    return [_artifact_from_row(row) for row in rows]


def get_artifact(conn: sqlite3.Connection, artifact_id: str) -> Dict[str, Any]:
    row = conn.execute("SELECT * FROM pms_artifacts WHERE artifact_id = ?", (artifact_id,)).fetchone()
    return _artifact_from_row(_require_row(row, "Artifact", artifact_id))


def create_document(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    title: str,
    kind: str,
    visibility: str,
    epic_id: Optional[str] = None,
    task_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    document_id = uuid.uuid4().hex
    now = _now()
    project = get_project(conn, project_id)
    conn.execute(
        """
        INSERT INTO pms_documents (
            document_id, project_id, epic_id, task_id, title, kind, visibility,
            created_at, updated_at, published_revision_hash, latest_revision_hash,
            scope_type, scope_id, created_by, is_archived
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, 0)
        """,
        (
            document_id,
            project_id,
            epic_id,
            task_id,
            title,
            kind,
            visibility,
            now,
            now,
            project.get("scope_type"),
            project.get("scope_id"),
            user_id,
        ),
    )
    doc = get_document(conn, document_id, view="latest")
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.document.created",
        entity_type="document",
        entity_id=document_id,
        payload={"title": title, "kind": kind},
        user_id=user_id or "demo",
    )
    return doc.get("document", doc)


def add_document_revision(
    conn: sqlite3.Connection,
    *,
    document_id: str,
    content: str,
    author: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    author = author or user_id
    doc_row = conn.execute(
        "SELECT latest_revision_hash, project_id FROM pms_documents WHERE document_id = ?",
        (document_id,),
    ).fetchone()
    parent_hash = doc_row["latest_revision_hash"] if doc_row else None
    revision_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    revision_id = uuid.uuid4().hex
    now = _now()

    conn.execute(
        """
        INSERT OR IGNORE INTO pms_document_blobs (blob_hash, content, size, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (revision_hash, content, len(content.encode("utf-8")), now),
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO pms_document_revisions (
            revision_id, document_id, revision_hash, parent_hash, author, created_at, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (revision_id, document_id, revision_hash, parent_hash, author, now, _json_dump(metadata or {})),
    )
    conn.execute(
        "UPDATE pms_documents SET latest_revision_hash = ?, updated_at = ? WHERE document_id = ?",
        (revision_hash, now, document_id),
    )
    if doc_row:
        db_record_project_event(
            conn,
            project_id=doc_row["project_id"],
            event_type="pms.document.revisioned",
            entity_type="document_revision",
            entity_id=revision_hash,
            payload={"document_id": document_id},
            user_id=author or "demo",
        )
    return {
        "revision_hash": revision_hash,
        "document_id": document_id,
        "project_id": doc_row["project_id"] if doc_row else None,
        "created_at": now,
        "metadata": metadata or {},
        "content": content,
    }


def publish_document_revision(
    conn: sqlite3.Connection,
    *,
    document_id: str,
    revision_hash: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    now = _now()
    conn.execute(
        """
        UPDATE pms_documents
        SET published_revision_hash = ?, updated_at = ?
        WHERE document_id = ?
        """,
        (revision_hash, now, document_id),
    )
    doc = get_document(conn, document_id, view="published")
    project_id = doc.get("document", {}).get("project_id")
    if project_id:
        db_record_project_event(
            conn,
            project_id=project_id,
            event_type="pms.document.published",
            entity_type="document",
            entity_id=document_id,
            payload={"revision_hash": revision_hash},
            user_id=user_id or "demo",
        )
    return doc.get("document", doc)


def get_document(conn: sqlite3.Connection, document_id: str, view: str) -> Dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM pms_documents WHERE document_id = ?",
        (document_id,),
    ).fetchone()
    row = _require_row(row, "Document", document_id)
    doc = _document_from_row(row)

    if view == "history":
        revisions = conn.execute(
            """
            SELECT * FROM pms_document_revisions
            WHERE document_id = ?
            ORDER BY datetime(created_at) DESC
            """,
            (document_id,),
        ).fetchall()
        return {"document": doc, "revisions": [_document_revision_from_row(r) for r in revisions]}

    revision_hash = doc.get("published_revision_hash") if view == "published" else doc.get("latest_revision_hash")
    content = None
    if revision_hash:
        blob = conn.execute(
            "SELECT content FROM pms_document_blobs WHERE blob_hash = ?",
            (revision_hash,),
        ).fetchone()
        content = blob["content"] if blob else None
    return {"document": doc, "revision_hash": revision_hash, "content": content}


def list_documents(
    conn: sqlite3.Connection,
    project_id: Optional[str] = None,
    kind: Optional[str] = None,
    published_only: bool = False,
) -> List[Dict[str, Any]]:
    clauses = ["is_archived = 0"]
    params: List[Any] = []
    if project_id:
        clauses.append("project_id = ?")
        params.append(project_id)
    if kind:
        clauses.append("kind = ?")
        params.append(kind)
    if published_only:
        clauses.append("published_revision_hash IS NOT NULL")
    query = f"""
        SELECT * FROM pms_documents
        WHERE {' AND '.join(clauses)}
        ORDER BY datetime(updated_at) DESC
    """
    rows = conn.execute(query, params).fetchall()
    return [_document_from_row(row) for row in rows]


def create_meeting_session(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    title: str,
    started_at: Optional[str] = None,
    ended_at: Optional[str] = None,
    participants: Optional[List[str]] = None,
    language: Optional[str] = None,
    epic_id: Optional[str] = None,
    task_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    meeting_id = uuid.uuid4().hex
    now = _now()
    project = get_project(conn, project_id)
    conn.execute(
        """
        INSERT INTO pms_meetings (
            meeting_id, project_id, epic_id, task_id, title, started_at, ended_at,
            participants_json, language, created_by, created_at, scope_type, scope_id,
            recording_status, transcript_status, journal_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            meeting_id,
            project_id,
            epic_id,
            task_id,
            title,
            started_at or now,
            ended_at,
            _json_dump(participants or []),
            language or "en",
            user_id,
            now,
            project.get("scope_type"),
            project.get("scope_id"),
            "none",
            "none",
            "none",
        ),
    )
    meeting = get_meeting(conn, meeting_id)
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.meeting.created",
        entity_type="meeting",
        entity_id=meeting_id,
        payload={"title": title},
        user_id=user_id or "demo",
    )
    return meeting


def list_meetings(conn: sqlite3.Connection, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    params: List[Any] = []
    query = """
        SELECT * FROM pms_meetings
    """
    if project_id:
        query += " WHERE project_id = ?"
        params.append(project_id)
    query += " ORDER BY datetime(created_at) DESC"
    rows = conn.execute(query, params).fetchall()
    results = []
    for row in rows:
        meeting = _meeting_from_row(row)
        mapping, consent = _load_speaker_mapping(conn, meeting["meeting_id"])
        meeting["speaker_mapping"] = mapping
        meeting["speaker_mapping_consent"] = consent
        results.append(meeting)
    return results


def get_meeting(conn: sqlite3.Connection, meeting_id: str) -> Dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM pms_meetings WHERE meeting_id = ?",
        (meeting_id,),
    ).fetchone()
    meeting = _meeting_from_row(_require_row(row, "Meeting", meeting_id))
    mapping, consent = _load_speaker_mapping(conn, meeting_id)
    meeting["speaker_mapping"] = mapping
    meeting["speaker_mapping_consent"] = consent
    return meeting


def attach_meeting_audio(
    conn: sqlite3.Connection,
    *,
    meeting_id: str,
    project_id: str,
    content: bytes,
    filename: str,
    mime_type: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    path = get_attachment_path("pms", "meeting_audio", project_id, f"{meeting_id}-{filename}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    sha256 = hashlib.sha256(content).hexdigest()
    size = path.stat().st_size
    now = _now()
    conn.execute(
        """
        UPDATE pms_meetings
        SET recording_status = ?, recording_path = ?, recording_mime_type = ?,
            recording_size = ?, recording_sha256 = ?
        WHERE meeting_id = ?
        """,
        ("stored", str(path), mime_type or "application/octet-stream", size, sha256, meeting_id),
    )
    meeting = get_meeting(conn, meeting_id)
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.meeting.audio_attached",
        entity_type="meeting",
        entity_id=meeting_id,
        payload={"filename": filename},
        user_id=user_id or "demo",
    )
    return meeting


def add_transcript_segments(
    conn: sqlite3.Connection,
    *,
    meeting_id: str,
    segments: List[Dict[str, Any]],
    user_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    now = _now()
    rows = []
    for index, segment in enumerate(segments, start=1):
        segment_id = uuid.uuid4().hex
        speaker_label = segment.get("speaker_label") or f"Speaker {index}"
        conn.execute(
            """
            INSERT INTO pms_transcript_segments (
                segment_id, meeting_id, ts_start, ts_end, speaker_label,
                text_original, text_translated, confidence, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                segment_id,
                meeting_id,
                segment.get("ts_start", 0),
                segment.get("ts_end", 0),
                speaker_label,
                segment.get("text_original") or "",
                segment.get("text_translated"),
                segment.get("confidence"),
                now,
            ),
        )
    conn.execute(
        "UPDATE pms_meetings SET transcript_status = ? WHERE meeting_id = ?",
        ("ready", meeting_id),
    )
    rows = conn.execute(
        "SELECT * FROM pms_transcript_segments WHERE meeting_id = ? ORDER BY ts_start ASC",
        (meeting_id,),
    ).fetchall()
    meeting = get_meeting(conn, meeting_id)
    db_record_project_event(
        conn,
        project_id=meeting.get("project_id"),
        event_type="pms.meeting.transcript_ingested",
        entity_type="meeting",
        entity_id=meeting_id,
        payload={"segments": len(segments)},
        user_id=user_id or "demo",
    )
    return [_row_to_dict(row) for row in rows]


def list_transcript_segments(conn: sqlite3.Connection, meeting_id: str) -> List[Dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM pms_transcript_segments WHERE meeting_id = ? ORDER BY ts_start ASC",
        (meeting_id,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def generate_meeting_journal(
    conn: sqlite3.Connection,
    *,
    meeting_id: str,
    user_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    transcript = list_transcript_segments(conn, meeting_id)
    blocks = generate_journal_blocks(transcript)
    now = _now()
    conn.execute("DELETE FROM pms_journal_blocks WHERE meeting_id = ?", (meeting_id,))
    for block in blocks:
        block_id = uuid.uuid4().hex
        conn.execute(
            """
            INSERT INTO pms_journal_blocks (
                block_id, meeting_id, ts_start, ts_end, section_type, speaker_label,
                content, references_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                block_id,
                meeting_id,
                block.get("ts_start", 0),
                block.get("ts_end", 0),
                block.get("section_type"),
                block.get("speaker_label"),
                block.get("content"),
                _json_dump(block.get("references") or {}),
                block.get("created_at") or now,
            ),
        )
    conn.execute(
        "UPDATE pms_meetings SET journal_status = ? WHERE meeting_id = ?",
        ("generated", meeting_id),
    )
    meeting = get_meeting(conn, meeting_id)
    db_record_project_event(
        conn,
        project_id=meeting.get("project_id"),
        event_type="pms.meeting.journal_generated",
        entity_type="meeting",
        entity_id=meeting_id,
        payload={"blocks": len(blocks)},
        user_id=user_id or "demo",
    )
    return list_journal_blocks(conn, meeting_id)


def list_journal_blocks(
    conn: sqlite3.Connection,
    meeting_id: str,
    section_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params: List[Any] = [meeting_id]
    query = "SELECT * FROM pms_journal_blocks WHERE meeting_id = ?"
    if section_type:
        query += " AND section_type = ?"
        params.append(section_type)
    query += " ORDER BY ts_start ASC"
    rows = conn.execute(query, params).fetchall()
    return [_journal_block_from_row(row) for row in rows]


def upsert_speaker_mapping(
    conn: sqlite3.Connection,
    *,
    meeting_id: str,
    speaker_label: str,
    display_name: str,
    consent: bool,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not consent:
        raise ValueError("Consent is required to map speakers")
    now = _now()
    existing = conn.execute(
        """
        SELECT mapping_id FROM pms_speaker_mappings
        WHERE meeting_id = ? AND speaker_label = ?
        """,
        (meeting_id, speaker_label),
    ).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE pms_speaker_mappings
            SET participant_name = ?, consented_by = ?, consented_at = ?, updated_at = ?
            WHERE meeting_id = ? AND speaker_label = ?
            """,
            (display_name, user_id, now, now, meeting_id, speaker_label),
        )
    else:
        mapping_id = uuid.uuid4().hex
        conn.execute(
            """
            INSERT INTO pms_speaker_mappings (
                mapping_id, meeting_id, speaker_label, participant_name,
                consented_by, consented_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (mapping_id, meeting_id, speaker_label, display_name, user_id, now, now),
        )
    row = conn.execute(
        "SELECT * FROM pms_speaker_mappings WHERE meeting_id = ? AND speaker_label = ?",
        (meeting_id, speaker_label),
    ).fetchone()
    mapping = _speaker_mapping_from_row(_require_row(row, "Speaker mapping", speaker_label))
    meeting = get_meeting(conn, meeting_id)
    db_record_project_event(
        conn,
        project_id=meeting.get("project_id"),
        event_type="pms.meeting.speaker_mapping",
        entity_type="meeting",
        entity_id=meeting_id,
        payload={"speaker_label": speaker_label, "display_name": display_name},
        user_id=user_id or "demo",
    )
    return mapping


def add_expense(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    epic_id: Optional[str],
    task_id: Optional[str],
    amount: float,
    currency: str,
    category: Optional[str],
    vendor: Optional[str],
    description: Optional[str],
    occurred_at: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    expense_id = uuid.uuid4().hex
    now = _now()
    project = get_project(conn, project_id)
    conn.execute(
        """
        INSERT INTO pms_expenses (
            expense_id, project_id, epic_id, task_id, amount, currency, category,
            vendor, description, occurred_at, created_at, updated_at, created_by,
            scope_type, scope_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            expense_id,
            project_id,
            epic_id,
            task_id,
            amount,
            currency,
            category,
            vendor,
            description,
            occurred_at,
            now,
            now,
            user_id,
            project.get("scope_type"),
            project.get("scope_id"),
        ),
    )
    row = conn.execute("SELECT * FROM pms_expenses WHERE expense_id = ?", (expense_id,)).fetchone()
    entry = _row_to_dict(_require_row(row, "Expense", expense_id))
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.expense.created",
        entity_type="expense",
        entity_id=expense_id,
        payload={"amount": amount, "currency": currency},
        user_id=user_id or "demo",
    )
    return entry


def list_expenses(conn: sqlite3.Connection, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    params: List[Any] = []
    query = "SELECT * FROM pms_expenses"
    if project_id:
        query += " WHERE project_id = ?"
        params.append(project_id)
    query += " ORDER BY datetime(occurred_at) DESC"
    rows = conn.execute(query, params).fetchall()
    return [_row_to_dict(row) for row in rows]


def add_time_entry(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    epic_id: Optional[str],
    task_id: Optional[str],
    actor_id: Optional[str],
    role: Optional[str],
    duration_minutes: int,
    hourly_rate: float,
    occurred_at: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    entry_id = uuid.uuid4().hex
    now = _now()
    project = get_project(conn, project_id)
    conn.execute(
        """
        INSERT INTO pms_time_entries (
            time_entry_id, project_id, epic_id, task_id, actor_id, role,
            duration_minutes, hourly_rate, occurred_at, created_at, updated_at,
            scope_type, scope_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry_id,
            project_id,
            epic_id,
            task_id,
            actor_id,
            role,
            duration_minutes,
            hourly_rate,
            occurred_at,
            now,
            now,
            project.get("scope_type"),
            project.get("scope_id"),
        ),
    )
    row = conn.execute("SELECT * FROM pms_time_entries WHERE time_entry_id = ?", (entry_id,)).fetchone()
    record = _row_to_dict(_require_row(row, "Time entry", entry_id))
    record["labor_cost"] = (duration_minutes / 60.0) * hourly_rate
    db_record_project_event(
        conn,
        project_id=project_id,
        event_type="pms.time_entry.created",
        entity_type="time_entry",
        entity_id=entry_id,
        payload={"duration_minutes": duration_minutes, "hourly_rate": hourly_rate},
        user_id=user_id or "demo",
    )
    return record


def list_time_entries(conn: sqlite3.Connection, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    params: List[Any] = []
    query = "SELECT * FROM pms_time_entries"
    if project_id:
        query += " WHERE project_id = ?"
        params.append(project_id)
    query += " ORDER BY datetime(occurred_at) DESC"
    rows = conn.execute(query, params).fetchall()
    results = []
    for row in rows:
        record = _row_to_dict(row)
        duration = record.get("duration_minutes") or 0
        rate = record.get("hourly_rate") or 0
        record["labor_cost"] = (duration / 60.0) * rate
        results.append(record)
    return results


def project_cost_rollup(
    conn: sqlite3.Connection,
    project_id: str,
    *,
    include_breakdown: bool = False,
) -> Dict[str, Any]:
    expenses = list_expenses(conn, project_id)
    time_entries = list_time_entries(conn, project_id)
    expense_total = sum(entry.get("amount", 0) or 0 for entry in expenses)
    labor_total = sum(entry.get("labor_cost", 0) or 0 for entry in time_entries)
    combined_total = expense_total + labor_total

    by_epic: Dict[str, float] = {}
    by_task: Dict[str, float] = {}
    if include_breakdown:
        for entry in expenses:
            epic = entry.get("epic_id")
            task = entry.get("task_id")
            by_epic[epic] = by_epic.get(epic, 0.0) + (entry.get("amount") or 0)
            by_task[task] = by_task.get(task, 0.0) + (entry.get("amount") or 0)
        for entry in time_entries:
            epic = entry.get("epic_id")
            task = entry.get("task_id")
            by_epic[epic] = by_epic.get(epic, 0.0) + (entry.get("labor_cost") or 0)
            by_task[task] = by_task.get(task, 0.0) + (entry.get("labor_cost") or 0)

    currency = None
    for entry in expenses:
        if entry.get("currency"):
            currency = entry.get("currency")
            break

    response = {
        "project_id": project_id,
        "expense_total": expense_total,
        "labor_total": labor_total,
        "combined_total": combined_total,
        "currency": currency or "USD",
    }
    if include_breakdown:
        response["by_epic"] = by_epic
        response["by_task"] = by_task
    return response


def search_pms(
    conn: sqlite3.Connection,
    *,
    scope_type: Optional[str],
    scope_id: Optional[str],
    query: str,
    include_samples: bool = False,
) -> List[Dict[str, Any]]:
    needle = f"%{query.lower()}%"
    results: List[Dict[str, Any]] = []
    project_scope_clause = ""
    project_scope_params: List[Any] = []
    sample_clause = "" if include_samples else " AND is_sample = 0"
    if scope_type and scope_id:
        project_scope_clause = " AND scope_type = ? AND scope_id = ?"
        project_scope_params.extend([scope_type, scope_id])

    scoped_projects = conn.execute(
        f"""
        SELECT project_id, name FROM pms_projects
        WHERE 1=1{project_scope_clause}{sample_clause}
        """,
        project_scope_params,
    ).fetchall()
    project_name_map = {row["project_id"]: row["name"] for row in scoped_projects}
    project_ids = list(project_name_map.keys())

    project_rows = conn.execute(
        f"""
        SELECT project_id, name FROM pms_projects
        WHERE LOWER(name) LIKE ?{project_scope_clause}{sample_clause}
        """,
        [needle, *project_scope_params],
    ).fetchall()
    for row in project_rows:
        results.append(
            {
                "kind": "project",
                "entity": "project",
                "title": row["name"],
                "project_id": row["project_id"],
                "project_name": row["name"],
                "entity_id": row["project_id"],
                "route": f"/pms/projects/{row['project_id']}",
            }
        )

    if scope_type and scope_id and not project_ids:
        return results

    scope_clause = ""
    scope_params: List[Any] = [needle]
    if project_ids:
        scope_clause = f" AND project_id IN ({', '.join('?' for _ in project_ids)})"
        scope_params.extend(project_ids)

    epic_rows = conn.execute(
        f"""
        SELECT epic_id, project_id, title FROM pms_epics
        WHERE LOWER(title) LIKE ?{scope_clause}
        """,
        scope_params,
    ).fetchall()
    for row in epic_rows:
        results.append(
            {
                "kind": "epic",
                "entity": "epic",
                "title": row["title"],
                "project_id": row["project_id"],
                "project_name": project_name_map.get(row["project_id"]),
                "entity_id": row["epic_id"],
                "route": f"/pms/projects/{row['project_id']}?tab=epics",
            }
        )

    task_rows = conn.execute(
        f"""
        SELECT task_id, project_id, title FROM pms_tasks
        WHERE LOWER(title) LIKE ?{scope_clause}
        """,
        scope_params,
    ).fetchall()
    for row in task_rows:
        results.append(
            {
                "kind": "task",
                "entity": "task",
                "title": row["title"],
                "project_id": row["project_id"],
                "project_name": project_name_map.get(row["project_id"]),
                "entity_id": row["task_id"],
                "route": f"/pms/projects/{row['project_id']}?tab=tasks&focus={row['task_id']}",
            }
        )

    doc_rows = conn.execute(
        f"""
        SELECT document_id, project_id, title FROM pms_documents
        WHERE LOWER(title) LIKE ?{scope_clause}
        """,
        scope_params,
    ).fetchall()
    for row in doc_rows:
        results.append(
            {
                "kind": "document",
                "entity": "document",
                "title": row["title"],
                "project_id": row["project_id"],
                "project_name": project_name_map.get(row["project_id"]),
                "entity_id": row["document_id"],
                "route": f"/pms/projects/{row['project_id']}?tab=documents",
            }
        )

    meeting_rows = conn.execute(
        f"""
        SELECT meeting_id, project_id, title FROM pms_meetings
        WHERE LOWER(title) LIKE ?{scope_clause}
        """,
        scope_params,
    ).fetchall()
    for row in meeting_rows:
        results.append(
            {
                "kind": "meeting",
                "entity": "meeting",
                "title": row["title"],
                "project_id": row["project_id"],
                "project_name": project_name_map.get(row["project_id"]),
                "entity_id": row["meeting_id"],
                "route": f"/pms/projects/{row['project_id']}?tab=journal",
            }
        )

    return results
