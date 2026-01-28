from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def exports_index() -> dict:
    return {"status": "ok", "exports": []}
