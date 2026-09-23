from fastapi import APIRouter, HTTPException
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/history")
def history(limit: int = 50):
    with PaintService() as s: return {"items": s.history(limit)}
@router.get("/history/{run_id}")
def history_item(run_id: int):
    with PaintService() as s:
        item = s.history_item(run_id)
        if not item: raise HTTPException(404)
        return item
