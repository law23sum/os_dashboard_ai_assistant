from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def matlab_status() -> dict:
    return {"status": "ok"}
