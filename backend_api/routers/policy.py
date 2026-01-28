from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def policy_status() -> dict:
    return {"status": "ok"}
