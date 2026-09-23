from pydantic import BaseModel
class EstimateRequest(BaseModel):
    room_id: int
    coats: int | None = None
    coverage: float | None = None
    persist: bool = True

class CompareRequest(BaseModel):
    room_id: int
    # 底漆参数以请求体为准，不依赖 primer_coat 空桩模块。
    primer_coverage: float
    primer_coats: int
    # 面漆可缺省回落设置默认值，便于随后只改面漆默认涂布率。
    top_coverage: float | None = None
    top_coats: int | None = None
    persist: bool = True
