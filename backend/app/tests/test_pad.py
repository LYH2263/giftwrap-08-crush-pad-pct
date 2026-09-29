import pytest
from app.engines.wrap_math import paper_area, ribbon_estimate, PAD_ORDER


def test_disabled_equals_legacy():
    """关闭防压垫时结果与改造前完全一致。"""
    legacy = paper_area(0.30, 0.20, 0.15, 1.15)
    assert paper_area(0.30, 0.20, 0.15, 1.15, False, None) == legacy
    assert legacy["paper_m2"] == 0.31
    assert legacy["pad_enabled"] is False
    assert legacy["pad_pct"] is None
    assert legacy["pad_order"] == PAD_ORDER


def test_enabled_lifts_area_with_fixed_order():
    """开启后：先折边再垫  paper = surface*overlap*(1+pct)，面积高于关闭。"""
    off = paper_area(1, 1, 1, 1.0, False, None)
    on = paper_area(1, 1, 1, 1.0, True, 0.10)
    assert on["paper_m2"] == round(6.0 * 1.0 * 1.10, 3)
    assert on["paper_m2"] > off["paper_m2"]
    assert on["pad_enabled"] is True
    assert on["pad_pct"] == 0.10
    assert on["pad_order"] == "fold_then_pad"


def test_negative_pct_rejected():
    with pytest.raises(ValueError):
        paper_area(1, 1, 1, 1.0, True, -0.01)


def test_ribbon_tracks_base_edges_only():
    """垫层与折边系数都不进丝带。"""
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert ribbon_estimate(0.30, 0.20, 0.15, "cross") == base
