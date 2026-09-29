"""Wrap-paper math engine.

叠乘口径（固定、可测）：
    垫层在折边之后再抬升 —— PAD_ORDER = "fold_then_pad"
    paper_m2 = box_surface * overlap * (1 + pad_pct)

ribbon 永远只跟盒体基础三边 (L, W, H)，不吃 overlap 也不吃垫层。
"""

# 叠乘顺序标记：先折边（overlap）再垫层（pad_pct）。
# 引擎只承认这一种口径；落库时原样钉住，不随后续默认值变化而重算。
PAD_ORDER = "fold_then_pad"


def paper_area(
    length: float,
    width: float,
    height: float,
    overlap: float = 1.15,
    pad_enabled: bool = False,
    pad_pct: float | None = None,
) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")

    base = 2 * (L * W + L * H + W * H)          # 盒体展开表面积
    folded = base * float(overlap)              # 先折边

    enabled = bool(pad_enabled)
    pct = None if pad_pct is None else float(pad_pct)
    if enabled:
        if pct is None:
            pct = 0.0
        if pct < 0:
            # 垫层百分比为负不允许：调用方据此失败且不得落库。
            raise ValueError("pad_pct must be non-negative")
        need = folded * (1.0 + pct)             # 再垫层抬升
    else:
        need = folded                            # 关闭时与改造前完全一致

    return {
        "box_surface": round(base, 3),
        "overlap": float(overlap),
        "paper_m2": round(need, 3),
        "pad_enabled": enabled,
        "pad_pct": pct,
        "pad_order": PAD_ORDER,
    }


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric).

    只跟盒体基础三边，垫层与折边系数均不影响丝带。
    """
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
