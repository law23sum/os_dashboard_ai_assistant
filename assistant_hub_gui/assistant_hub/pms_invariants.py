"""Invariant checks for PMS canonical data + derived indices."""

from __future__ import annotations

from typing import Iterable, List, Mapping, Optional


def _field(item: object, key: str) -> Optional[object]:
    if isinstance(item, Mapping):
        return item.get(key)
    return getattr(item, key, None)


def validate_pms_invariants(
    epics: Iterable[object],
    tasks: Iterable[object],
    todos: Iterable[object],
    priority_tiers: Optional[Iterable[str]] = None,
) -> List[str]:
    """Validate canonical PMS invariants and return a list of errors."""

    errors: List[str] = []
    epic_ids = set()
    for epic in epics:
        epic_id = _field(epic, "epic_id")
        if epic_id is not None:
            epic_ids.add(str(epic_id))

    task_ids = {}
    for task in tasks:
        task_id = _field(task, "task_id")
        if task_id is None:
            continue
        task_id = str(task_id)
        task_ids[task_id] = task_ids.get(task_id, 0) + 1

        epic_id = _field(task, "epic_id")
        if epic_id and str(epic_id) not in epic_ids:
            errors.append(f"Task {task_id} references missing epic {epic_id}")

        if priority_tiers is not None:
            priority = _field(task, "priority")
            if priority and str(priority) not in priority_tiers:
                errors.append(f"Task {task_id} has unknown priority {priority}")

    for task_id, count in task_ids.items():
        if count > 1:
            errors.append(f"Task {task_id} appears more than once in canonical store")

    todo_positions_by_task: dict[str, List[int]] = {}
    for todo in todos:
        todo_id = _field(todo, "todo_id")
        task_id = _field(todo, "task_id")
        if task_id is None:
            continue
        task_id = str(task_id)
        if task_id not in task_ids:
            errors.append(f"Todo {todo_id} references missing task {task_id}")
            continue
        position = _field(todo, "position")
        if position is None:
            continue
        todo_positions_by_task.setdefault(task_id, []).append(int(position))

    for task_id, positions in todo_positions_by_task.items():
        if not positions:
            continue
        sorted_positions = sorted(positions)
        if len(sorted_positions) != len(set(sorted_positions)):
            errors.append(f"Todo ordering has duplicate positions for task {task_id}")
            continue
        expected = list(range(sorted_positions[0], sorted_positions[0] + len(sorted_positions)))
        if sorted_positions != expected:
            errors.append(f"Todo ordering is not contiguous for task {task_id}")

    return errors
