"""UI regression: primary action remains legible with large fonts and narrow screens."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
GRADLE = (ROOT / "app/build.gradle").read_text(encoding="utf-8")

def test_primary_action_allows_two_lines():
    assert "go.setMaxLines(2);" in MAIN
    assert "go.setBreakStrategy(android.text.Layout.BREAK_STRATEGY_HIGH_QUALITY);" in MAIN

def test_primary_action_auto_sizes_for_narrow_layout():
    assert "go.setAutoSizeTextTypeUniformWithConfiguration(10,13,1,android.util.TypedValue.COMPLEX_UNIT_SP);" in MAIN

def test_existing_start_stop_actions_preserved():
    assert 'go.setText(s.active?"■  ОСТАНОВИТЬ":"НАЧАТЬ ПРОВЕРКУ  ›");' in MAIN
    assert "go.setOnClickListener(v->toggle());" in MAIN

def test_version_incremented():
    assert "versionCode 277" in GRADLE
    assert "versionName '1.5.269'" in GRADLE
