from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.repositories import boxes, history, settings_repo

def run_estimate(
    box_id: int,
    overlap: float | None,
    wrap_style: str,
    save: bool,
    note: str,
    pad_enabled: bool = False,
    pad_pct: float | None = None,
):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")

    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()

    # 开启垫层且未显式给百分比时，用系统默认垫层百分比。
    enabled = bool(pad_enabled)
    pct = float(pad_pct) if pad_pct is not None else (settings_repo.get_pad_pct() if enabled else None)
    if enabled and pct is not None and pct < 0:
        # 百分比为负：直接失败，绝不落库。
        raise HTTPException(422, "pad_pct must be non-negative")

    try:
        calc = paper_area(box["length"], box["width"], box["height"], ov, enabled, pct)
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    # ribbon 只跟基础三边，与垫层/折边无关。
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)

    payload = {**calc, "ribbon": ribbon, "box_id": box_id}
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **calc, "ribbon": ribbon}
