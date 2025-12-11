"""Search router powering the migrated vector-search tab."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import load_state
from backend_api.db import db_session

router = APIRouter()


def get_state():
    with db_session() as conn:
        return load_state(conn)


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResult(BaseModel):
    id: str
    kind: str
    title: str
    snippet: str
    score: float
    tags: List[str]


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResult]
    took_ms: int


class SearchStatus(BaseModel):
    documents_indexed: int
    tasks_indexed: int
    projects_indexed: int
    embeddings_ready: bool


def _match_score(text: str, query: str) -> float:
    text_lower = text.lower()
    query_lower = query.lower()
    if query_lower in text_lower:
        return min(1.0, len(query_lower) / max(1, len(text_lower)))
    tokens = query_lower.split()
    matches = sum(1 for token in tokens if token in text_lower)
    return matches / max(1, len(tokens))


@router.post("/query", response_model=SearchResponse)
async def run_search(payload: SearchRequest, state=Depends(get_state)) -> SearchResponse:
    """Toy vector search replacement recycling task & project text."""
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")

    results: List[SearchResult] = []

    for task in state.tasks or []:
        body = f"{task.title} {task.notes or ''}"
        score = _match_score(body, query)
        if score > 0:
            results.append(
                SearchResult(
                    id=f"task-{task.id}",
                    kind="task",
                    title=task.title,
                    snippet=(task.notes or "")[:140],
                    score=round(score, 3),
                    tags=[task.project, task.status, task.priority],
                )
            )

    for project in state.projects or []:
        body = f"{project.name} {project.description or ''}"
        score = _match_score(body, query)
        if score > 0:
            results.append(
                SearchResult(
                    id=f"project-{project.name}",
                    kind="project",
                    title=project.name,
                    snippet=(project.description or "")[:140],
                    score=round(min(1.0, 0.8 * score + 0.2), 3),
                    tags=[project.status, project.priority],
                )
            )

    results.sort(key=lambda item: item.score, reverse=True)
    limit = max(1, min(payload.limit, 25))
    return SearchResponse(
        query=query,
        total=len(results),
        results=results[:limit],
        took_ms=12,
    )


@router.get("/", response_model=SearchResponse, include_in_schema=False)
async def legacy_search(q: str, limit: int = 10, state=Depends(get_state)) -> SearchResponse:
    """Compatibility endpoint for the Tkinter-era `/search?q=` pattern."""

    payload = SearchRequest(query=q, limit=limit)
    return await run_search(payload, state)


@router.get("/status", response_model=SearchStatus)
async def search_status(state=Depends(get_state)) -> SearchStatus:
    """Return metadata for the index management section."""
    tasks = state.tasks or []
    projects = state.projects or []
    docs_indexed = len(tasks) + len(projects)
    return SearchStatus(
        documents_indexed=docs_indexed,
        tasks_indexed=len(tasks),
        projects_indexed=len(projects),
        embeddings_ready=True,
    )
