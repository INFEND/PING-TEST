"""Regression checks for defensive quality-color input handling."""
from pathlib import Path

SRC = Path("app/src/main/java/com/xarkon/pingtest/QualityColors.java").read_text(encoding="utf-8")


def test_invalid_probe_counts_are_unknown():
    assert "sent<=0||received<0||received>sent" in SRC
    assert "return UNKNOWN;" in SRC


def test_nan_blend_fraction_does_not_turn_into_black():
    assert "Float.isNaN(fraction)?0f" in SRC


def test_existing_quality_thresholds_unchanged():
    assert "map(ms,45,110,240)" in SRC
    assert "map(percent,0.1,4,18)" in SRC
    assert "map(ms,4,15,50)" in SRC
