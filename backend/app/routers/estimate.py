from fastapi import APIRouter, HTTPException
from app.schemas.estimate import CompareRequest, EstimateRequest
from app.services.paint_service import PaintService
router = APIRouter()
@router.post("/estimate")
def post_estimate(body: EstimateRequest):
    with PaintService() as s:
        r = s.estimate(body.room_id, body.persist, body.coats, body.coverage)
        if not r: raise HTTPException(404)
        return r
@router.post("/compare")
def post_compare(body: CompareRequest):
    with PaintService() as s:
        # 任一侧涂布率或遍数非法已在 schema 层整单拒绝，不会走到这里
        r = s.compare(body.room_id,
                      body.primer.model_dump(), body.topcoat.model_dump(),
                      body.persist)
        if not r: raise HTTPException(404)
        return r
