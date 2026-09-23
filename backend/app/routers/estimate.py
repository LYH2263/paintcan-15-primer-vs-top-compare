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

@router.post("/estimate/compare")
def post_compare(body: CompareRequest):
    try:
        with PaintService() as s:
            r = s.compare(body.room_id, body.persist,
                          body.primer_coverage, body.primer_coats,
                          body.top_coverage, body.top_coats)
    except ValueError as e:
        # 非正/非正整数整单拒绝，服务层在校验通过前不落任何记录。
        raise HTTPException(400, str(e))
    if not r: raise HTTPException(404)
    return r
