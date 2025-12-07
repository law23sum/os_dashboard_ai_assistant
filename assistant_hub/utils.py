import os
from datetime import datetime
from typing import Optional
from .db import DATE_FORMAT, Task, AssistantState, Project, db_upsert_project
import sqlite3

def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except Exception:
        return None


def ensure_project_exists(conn: sqlite3.Connection, state: AssistantState, name: str) -> Project:
    proj = find_project(state, name)
    if proj is not None:
        return proj
    proj = Project(name=name, description="", status="active", priority="MEDIUM")
    state.projects.append(proj)
    db_upsert_project(conn, proj)
    return proj


def find_project(state: AssistantState, name: str) -> Optional[Project]:
    for p in state.projects:
        if p.name == name:
            return p
    return None
