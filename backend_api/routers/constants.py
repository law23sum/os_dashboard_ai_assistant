from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def constants_index() -> dict:
    return {"status": "ok", "constants": {}}
