from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

import pytest

from assistant_hub_gui.assistant_hub import db as hub_db
from assistant_hub_gui.assistant_hub import pms_invariants, pms_scheduler, pms_store
from assistant_hub_gui.assistant_hub.db import db_list_project_events
from assistant_hub_gui.assistant_hub.pms_models import PMS_DEFAULT_PRIORITY_TIERS


@pytest.fixture()
def conn(tmp_path):
    db_path = tmp_path / "pms_test.db"
    connection = hub_db.init_db(db_path)
    try:
        yield connection
    finally:
        connection.close()


def _create_project(conn, name: str = "Test Project"):
    return pms_store.create_project(
        conn,
        name=name,
        mode="personal",
        scope_type="user",
        scope_id="user-1",
        status="active",
        created_by="user-1",
    )


def test_scheduler_determinism_and_tiebreak(conn):
    project = _create_project(conn)
    task_a = pms_store.add_task(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        title="Alpha task",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P0",
        category="Alpha",
        task_type="Build",
        status="TODO",
        user_id="user-1",
    )
    task_b = pms_store.add_task(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        title="Beta task",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P0",
        category="Beta",
        task_type="Build",
        status="TODO",
        user_id="user-1",
    )

    pms_store.update_task_metadata(
        conn,
        project_id=project["project_id"],
        task_id=task_a["task_id"],
        patch={"enqueue_time": "2023-01-01T00:00:00Z"},
    )
    pms_store.update_task_metadata(
        conn,
        project_id=project["project_id"],
        task_id=task_b["task_id"],
        patch={"enqueue_time": "2023-01-02T00:00:00Z"},
    )

    tasks = pms_store.list_tasks(conn, project_id=project["project_id"])
    tasks_by_id = {task["task_id"]: task for task in tasks}
    index = pms_scheduler.build_scheduler_index(project["project_id"], tasks_by_id, list(PMS_DEFAULT_PRIORITY_TIERS))
    assert pms_scheduler.select_next_task_id(index, tasks_by_id) == task_a["task_id"]

    # Tie-break on lane key when enqueue times match.
    pms_store.update_task_metadata(
        conn,
        project_id=project["project_id"],
        task_id=task_b["task_id"],
        patch={"enqueue_time": "2023-01-01T00:00:00Z"},
    )
    tasks = pms_store.list_tasks(conn, project_id=project["project_id"])
    tasks_by_id = {task["task_id"]: task for task in tasks}
    index = pms_scheduler.build_scheduler_index(project["project_id"], tasks_by_id, list(PMS_DEFAULT_PRIORITY_TIERS))
    lane_a = pms_scheduler.lane_key("Alpha", "Build")
    lane_b = pms_scheduler.lane_key("Beta", "Build")
    expected = task_a["task_id"] if lane_a < lane_b else task_b["task_id"]
    assert pms_scheduler.select_next_task_id(index, tasks_by_id) == expected


def test_scheduler_lane_fairness_peek(conn):
    project = _create_project(conn)
    task_a1 = pms_store.add_task(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        title="Alpha one",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P0",
        category="Alpha",
        task_type="Build",
        status="TODO",
        user_id="user-1",
    )
    task_a2 = pms_store.add_task(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        title="Alpha two",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P0",
        category="Alpha",
        task_type="Build",
        status="TODO",
        user_id="user-1",
    )
    task_b1 = pms_store.add_task(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        title="Beta one",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P0",
        category="Beta",
        task_type="Build",
        status="TODO",
        user_id="user-1",
    )
    pms_store.update_task_metadata(
        conn,
        project_id=project["project_id"],
        task_id=task_a1["task_id"],
        patch={"enqueue_time": "2023-01-01T00:00:00Z"},
    )
    pms_store.update_task_metadata(
        conn,
        project_id=project["project_id"],
        task_id=task_a2["task_id"],
        patch={"enqueue_time": "2023-01-03T00:00:00Z"},
    )
    pms_store.update_task_metadata(
        conn,
        project_id=project["project_id"],
        task_id=task_b1["task_id"],
        patch={"enqueue_time": "2023-01-02T00:00:00Z"},
    )
    tasks = pms_store.list_tasks(conn, project_id=project["project_id"])
    tasks_by_id = {task["task_id"]: task for task in tasks}
    index = pms_scheduler.build_scheduler_index(project["project_id"], tasks_by_id, list(PMS_DEFAULT_PRIORITY_TIERS))
    sequence = pms_scheduler.peek_next_task_ids(index, tasks_by_id, 2)
    assert sequence == [task_a1["task_id"], task_b1["task_id"]]


def test_todo_ordering_and_invariants(conn):
    project = _create_project(conn)
    epic = pms_store.create_epic(
        conn,
        project_id=project["project_id"],
        title="Epic",
        description="",
        acceptance_criteria="",
        status="active",
        user_id="user-1",
    )
    task = pms_store.add_task(
        conn,
        project_id=project["project_id"],
        epic_id=epic["epic_id"],
        title="Task",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P1",
        category="General",
        task_type="General",
        status="TODO",
        user_id="user-1",
    )
    todo_a = pms_store.add_todo(conn, task_id=task["task_id"], text="First", user_id="user-1")
    todo_b = pms_store.add_todo(conn, task_id=task["task_id"], text="Second", user_id="user-1")

    reordered = pms_store.reorder_todos(
        conn, task_id=task["task_id"], new_order=[todo_b["todo_id"], todo_a["todo_id"]], user_id="user-1"
    )
    assert [todo["todo_id"] for todo in reordered] == [todo_b["todo_id"], todo_a["todo_id"]]
    assert [todo["position"] for todo in reordered] == [1, 2]

    errors = pms_invariants.validate_pms_invariants(
        [epic],
        pms_store.list_tasks(conn, project_id=project["project_id"]),
        pms_store.list_todos(conn, task["task_id"]),
        PMS_DEFAULT_PRIORITY_TIERS,
    )
    assert errors == []


def test_persistence_roundtrip_keeps_scheduler(tmp_path):
    db_path = tmp_path / "pms_roundtrip.db"
    first = hub_db.init_db(db_path)
    project = _create_project(first)
    task = pms_store.add_task(
        first,
        project_id=project["project_id"],
        epic_id=None,
        title="Persisted",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P0",
        category="Core",
        task_type="Ops",
        status="TODO",
        user_id="user-1",
    )
    pms_store.update_task_metadata(
        first,
        project_id=project["project_id"],
        task_id=task["task_id"],
        patch={"enqueue_time": "2024-01-01T00:00:00Z"},
    )
    tasks = pms_store.list_tasks(first, project_id=project["project_id"])
    tasks_by_id = {t["task_id"]: t for t in tasks}
    index = pms_scheduler.build_scheduler_index(project["project_id"], tasks_by_id, list(PMS_DEFAULT_PRIORITY_TIERS))
    expected = pms_scheduler.select_next_task_id(index, tasks_by_id)
    first.close()

    second = hub_db.init_db(db_path)
    tasks = pms_store.list_tasks(second, project_id=project["project_id"])
    tasks_by_id = {t["task_id"]: t for t in tasks}
    index = pms_scheduler.build_scheduler_index(project["project_id"], tasks_by_id, list(PMS_DEFAULT_PRIORITY_TIERS))
    assert pms_scheduler.select_next_task_id(index, tasks_by_id) == expected
    second.close()


def test_document_revision_dedup_and_publish(conn):
    project = _create_project(conn)
    document = pms_store.create_document(
        conn,
        project_id=project["project_id"],
        title="Spec",
        kind="spec",
        visibility="private",
        user_id="user-1",
    )
    rev1 = pms_store.add_document_revision(
        conn, document_id=document["document_id"], content="hello world", user_id="user-1"
    )
    rev2 = pms_store.add_document_revision(
        conn, document_id=document["document_id"], content="hello world", user_id="user-1"
    )
    assert rev1["revision_hash"] == rev2["revision_hash"]

    history = pms_store.get_document(conn, document["document_id"], view="history")
    assert len(history.get("revisions", [])) == 1

    pms_store.publish_document_revision(
        conn, document_id=document["document_id"], revision_hash=rev1["revision_hash"], user_id="user-1"
    )
    published = pms_store.get_document(conn, document["document_id"], view="published")
    assert published.get("revision_hash") == rev1["revision_hash"]


def test_meeting_journal_generation(conn):
    project = _create_project(conn)
    meeting = pms_store.create_meeting_session(
        conn,
        project_id=project["project_id"],
        title="Weekly Sync",
        started_at=datetime.utcnow().isoformat() + "Z",
        participants=["Alex", "Jamie"],
        language="en",
        user_id="user-1",
    )
    pms_store.add_transcript_segments(
        conn,
        meeting_id=meeting["meeting_id"],
        segments=[
            {"ts_start": 0, "ts_end": 4, "text_original": "Next steps are to ship the draft."},
        ],
        user_id="user-1",
    )
    blocks = pms_store.generate_meeting_journal(conn, meeting_id=meeting["meeting_id"], user_id="user-1")
    assert any(block["section_type"] == "NextSteps" for block in blocks)


def test_speaker_mapping_consent(conn):
    project = _create_project(conn)
    meeting = pms_store.create_meeting_session(
        conn,
        project_id=project["project_id"],
        title="Consent Check",
        started_at=datetime.utcnow().isoformat() + "Z",
        participants=["Speaker 1"],
        language="en",
        user_id="user-1",
    )
    with pytest.raises(ValueError):
        pms_store.upsert_speaker_mapping(
            conn,
            meeting_id=meeting["meeting_id"],
            speaker_label="Speaker 1",
            display_name="Alex",
            consent=False,
            user_id="user-1",
        )
    mapping = pms_store.upsert_speaker_mapping(
        conn,
        meeting_id=meeting["meeting_id"],
        speaker_label="Speaker 1",
        display_name="Alex",
        consent=True,
        user_id="user-1",
    )
    assert mapping["speaker_label"] == "Speaker 1"
    refreshed = pms_store.get_meeting(conn, meeting["meeting_id"])
    assert refreshed["speaker_mapping"].get("Speaker 1") == "Alex"


def test_finance_rollup_and_audit(conn):
    project = _create_project(conn)
    pms_store.add_expense(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        task_id=None,
        amount=120.0,
        currency="USD",
        category="Ops",
        vendor="Vendor",
        description="Expense",
        occurred_at=pms_store._now(),
        user_id="user-1",
    )
    pms_store.add_time_entry(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        task_id=None,
        actor_id="user-1",
        role="Engineer",
        duration_minutes=120,
        hourly_rate=50.0,
        occurred_at=pms_store._now(),
        user_id="user-1",
    )
    rollup = pms_store.project_cost_rollup(conn, project["project_id"])
    assert rollup["expense_total"] == 120.0
    assert rollup["labor_total"] == 100.0

    events = db_list_project_events(conn, project_id=project["project_id"], limit=10)
    assert any(event["event_type"] == "pms.project.created" for event in events)


def test_run_artifact_storage(conn, tmp_path, monkeypatch):
    from assistant_hub_gui.assistant_hub import config as hub_config

    monkeypatch.setattr(hub_config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(hub_config, "ATTACHMENTS_DIR", tmp_path / "attachments")
    monkeypatch.setattr(hub_config, "INTEGRATIONS_DIR", tmp_path / "integrations")
    monkeypatch.setattr(hub_config, "FILE_CACHE_DIR", tmp_path / "file_cache")

    project = _create_project(conn)
    run = pms_store.start_run(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        task_id=None,
        todo_id=None,
        input_params={"mode": "test"},
        status="running",
        user_id="user-1",
    )
    content = b"artifact-data"
    artifact = pms_store.attach_artifact(
        conn,
        project_id=project["project_id"],
        run_id=run["run_id"],
        kind="file",
        content=content,
        filename="sample.txt",
        display_name="Sample",
        mime_type="text/plain",
        user_id="user-1",
    )
    stored = pms_store.get_artifact(conn, artifact["artifact_id"])
    assert stored["sha256"] == hashlib.sha256(content).hexdigest()
    assert stored["size"] == len(content)
    assert Path(stored["storage_path"]).exists()


def test_search_respects_scope(conn):
    project = _create_project(conn, name="Alpha Project")
    pms_store.add_task(
        conn,
        project_id=project["project_id"],
        epic_id=None,
        title="Find the scheduler",
        deliverable_spec="",
        acceptance_criteria="",
        priority="P1",
        category="General",
        task_type="General",
        status="TODO",
        user_id="user-1",
    )
    results = pms_store.search_pms(
        conn,
        scope_type="user",
        scope_id="user-1",
        query="scheduler",
        include_samples=False,
    )
    assert any(result.get("kind") == "task" for result in results)
