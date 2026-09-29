from pydantic import BaseModel

class EstimateRequest(BaseModel):
    box_id: int
    overlap: float | None = None
    wrap_style: str = "cross"
    save: bool = False
    note: str = ""
    # 防压垫：开关 + 加纸百分比。开启且未给 pad_pct 时取系统默认。
    pad_enabled: bool = False
    pad_pct: float | None = None
