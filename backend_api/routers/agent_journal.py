from fastapi import APIRouter

router = APIRouter()


@router.get("/agent-journal/status")
def agent_journal_status() -> dict:
    return {"status": "ok"}
