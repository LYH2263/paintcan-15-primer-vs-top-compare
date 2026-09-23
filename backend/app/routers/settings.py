from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.paint_service import PaintService
router = APIRouter()
class CoverageBody(BaseModel):
    coverage: float
@router.get("/settings")
def settings():
    with PaintService() as s: return s.settings()
# 只改面漆默认涂布率；已落库对照的钉选两侧升数不受影响。
@router.post("/settings/coverage")
def set_coverage(body: CoverageBody):
    try:
        with PaintService() as s: return s.update_coverage(body.coverage)
    except ValueError as e:
        raise HTTPException(400, str(e))
