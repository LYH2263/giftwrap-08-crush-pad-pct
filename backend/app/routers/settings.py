from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo

router = APIRouter()

class PadPctBody(BaseModel):
    pad_pct: float

@router.get("/settings")
def settings(): return settings_repo.get_all()

@router.put("/settings/pad_pct")
def update_pad_pct(body: PadPctBody):
    if body.pad_pct < 0:
        raise HTTPException(422, "pad_pct must be non-negative")
    try:
        settings_repo.set_pad_pct(body.pad_pct)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"pad_pct": settings_repo.get_pad_pct()}
