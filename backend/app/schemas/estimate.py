from pydantic import BaseModel, field_validator

class EstimateRequest(BaseModel):
    room_id: int
    coats: int | None = None
    coverage: float | None = None
    persist: bool = True

class CoatSide(BaseModel):
    """单侧（底漆或面漆）的涂布率与遍数。"""
    coverage: float
    coats: int

    @field_validator("coverage")
    @classmethod
    def _coverage_positive(cls, v):
        if v <= 0:
            raise ValueError("coverage must be positive")
        return float(v)

    @field_validator("coats", mode="before")
    @classmethod
    def _coats_positive_int(cls, v):
        # 遍数必须是真实正整数：拒绝 float、bool、字符串等
        if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
            raise ValueError("coats must be a positive integer")
        return v

class CompareRequest(BaseModel):
    room_id: int
    primer: CoatSide
    topcoat: CoatSide
    persist: bool = True

class SettingsUpdate(BaseModel):
    coverage: float | None = None
    @field_validator("coverage")
    @classmethod
    def _coverage_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("coverage must be positive")
        return v
