from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/history")
def history(limit: int = 50):
    with PaintService() as s: return {"items": s.history(limit)}
@router.get("/history/{rid}")
def history_detail(rid: int):
    with PaintService() as s:
        item = s.history_detail(rid)
        if not item: raise HTTPException(404)
        return item
