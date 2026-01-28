from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def knowledge_status() -> dict:
    return {"status": "ok"}
