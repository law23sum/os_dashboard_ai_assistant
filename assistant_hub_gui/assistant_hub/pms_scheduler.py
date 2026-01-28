"""Scheduler utilities for PMS tasks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Protocol, Tuple

from .pms_models import PMS_DEFAULT_PRIORITY_TIERS


@dataclass
class LaneQueue:
    lane_key: str
    task_ids: List[str]


@dataclass
class SchedulerTier:
    tier: str
    lanes: List[LaneQueue]


@dataclass
class SchedulerIndex:
    project_id: str
    tiers: List[SchedulerTier]


class SchedulerPolicy(Protocol):
    def select_lane(
        self, lanes: List[LaneQueue], tasks_by_id: Mapping[str, dict]
    ) -> Optional[LaneQueue]:
        ...


class OldestHeadPolicy:
    """Select the lane whose head task has the oldest enqueue time."""

    def select_lane(
        self, lanes: List[LaneQueue], tasks_by_id: Mapping[str, dict]
    ) -> Optional[LaneQueue]:
        best: Optional[Tuple[str, str, str, LaneQueue]] = None
        for lane in lanes:
            if not lane.task_ids:
                continue
            head_id = lane.task_ids[0]
            task = tasks_by_id.get(head_id)
            if not task:
                continue
            enqueue_time = task.get("enqueue_time") or task.get("created_at") or ""
            candidate = (enqueue_time, lane.lane_key, head_id, lane)
            if best is None or candidate < best:
                best = candidate
        return best[-1] if best else None


def lane_key(category: str, task_type: str) -> str:
    return f"{category}::{task_type}"


def _build_scheduler_index_internal(
    project_id: str,
    tasks_by_id: Mapping[str, dict],
    priority_tiers: List[str],
) -> SchedulerIndex:
    tier_map: Dict[str, Dict[str, List[str]]] = {tier: {} for tier in priority_tiers}
    extra_tiers: Dict[str, Dict[str, List[str]]] = {}

    for task_id, task in tasks_by_id.items():
        if task.get("project_id") != project_id:
            continue
        status = task.get("status")
        if status in {"DONE", "ARCHIVED"}:
            continue
        tier = task.get("priority") or priority_tiers[-1]
        lane = lane_key(task.get("category") or "General", task.get("task_type") or "General")
        target = tier_map if tier in tier_map else extra_tiers
        if tier not in target:
            target[tier] = {}
        target[tier].setdefault(lane, []).append(task_id)

    tiers_in_order = list(priority_tiers) + sorted(extra_tiers.keys())
    scheduler_tiers: List[SchedulerTier] = []

    for tier in tiers_in_order:
        lanes = []
        lane_map = tier_map.get(tier) or extra_tiers.get(tier) or {}
        for lane, task_ids in lane_map.items():
            task_ids.sort(
                key=lambda tid: (
                    tasks_by_id.get(tid, {}).get("enqueue_time")
                    or tasks_by_id.get(tid, {}).get("created_at")
                    or "",
                    tid,
                )
            )
            lanes.append(LaneQueue(lane_key=lane, task_ids=task_ids))
        lanes.sort(key=lambda lane: lane.lane_key)
        scheduler_tiers.append(SchedulerTier(tier=tier, lanes=lanes))

    return SchedulerIndex(project_id=project_id, tiers=scheduler_tiers)


def select_next_task_id(
    index: SchedulerIndex,
    tasks_by_id: Mapping[str, dict],
    policy: Optional[SchedulerPolicy] = None,
) -> Optional[str]:
    selector = policy or OldestHeadPolicy()
    for tier in index.tiers:
        lane = selector.select_lane(tier.lanes, tasks_by_id)
        if lane and lane.task_ids:
            return lane.task_ids[0]
    return None


def peek_next_task_ids(
    index: SchedulerIndex,
    tasks_by_id: Mapping[str, dict],
    count: int,
    policy: Optional[SchedulerPolicy] = None,
) -> List[str]:
    selector = policy or OldestHeadPolicy()
    results: List[str] = []
    tier_map = {
        tier.tier: [LaneQueue(lane_key=lane.lane_key, task_ids=list(lane.task_ids)) for lane in tier.lanes]
        for tier in index.tiers
    }

    for _ in range(count):
        chosen_lane: Optional[LaneQueue] = None
        for tier in index.tiers:
            lanes = tier_map.get(tier.tier, [])
            lane = selector.select_lane(lanes, tasks_by_id)
            if lane and lane.task_ids:
                chosen_lane = lane
                break
        if not chosen_lane:
            break
        results.append(chosen_lane.task_ids.pop(0))
    return results


def build_scheduler_index(
    project_id: str,
    tasks_by_id: Mapping[str, dict],
    priority_tiers: Optional[List[str]] = None,
) -> SchedulerIndex:
    """Build a scheduler index from a canonical tasks-by-id map."""
    tiers = list(priority_tiers or PMS_DEFAULT_PRIORITY_TIERS)
    return _build_scheduler_index_internal(project_id, tasks_by_id, tiers)


def build_scheduler_index_from_tasks(
    tasks: List[dict],
    priority_tiers: Optional[List[str]] = None,
    *,
    include_blocked: bool = False,
) -> SchedulerIndex:
    """Build a scheduler index from a list of task dicts."""
    filtered_tasks = [
        task for task in tasks if include_blocked or task.get("status") != "BLOCKED"
    ]
    if not filtered_tasks:
        return SchedulerIndex(project_id="", tiers=[])
    tasks_by_id = {
        task.get("task_id"): task for task in filtered_tasks if task.get("task_id")
    }
    project_id = filtered_tasks[0].get("project_id", "")
    return build_scheduler_index(project_id, tasks_by_id, priority_tiers)


def next_task(
    tasks: List[dict],
    priority_tiers: Optional[List[str]] = None,
    *,
    include_blocked: bool = False,
) -> Optional[dict]:
    """Return the next task based on priority tiers and enqueue time."""
    filtered_tasks = [
        task for task in tasks if include_blocked or task.get("status") != "BLOCKED"
    ]
    if not filtered_tasks:
        return None
    tasks_by_id = {
        task.get("task_id"): task for task in filtered_tasks if task.get("task_id")
    }
    index = build_scheduler_index(
        filtered_tasks[0].get("project_id", ""), tasks_by_id, priority_tiers
    )
    next_id = select_next_task_id(index, tasks_by_id)
    return tasks_by_id.get(next_id) if next_id else None


def peek_next_tasks(
    tasks: List[dict],
    count: int,
    priority_tiers: Optional[List[str]] = None,
    *,
    include_blocked: bool = False,
) -> List[dict]:
    """Return the next N tasks without mutating input."""
    filtered_tasks = [
        task for task in tasks if include_blocked or task.get("status") != "BLOCKED"
    ]
    if not filtered_tasks:
        return []
    tasks_by_id = {
        task.get("task_id"): task for task in filtered_tasks if task.get("task_id")
    }
    index = build_scheduler_index(
        filtered_tasks[0].get("project_id", ""), tasks_by_id, priority_tiers
    )
    ids = peek_next_task_ids(index, tasks_by_id, count)
    return [tasks_by_id[task_id] for task_id in ids if task_id in tasks_by_id]
