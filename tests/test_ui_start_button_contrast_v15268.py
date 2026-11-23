"""UI regression: idle start button must use accent-aware contrast color."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
UI = (ROOT / "app/src/main/java/com/xarkon/pingtest/Ui.java").read_text(encoding="utf-8")

def test_start_button_uses_dynamic_accent_contrast():
    assert "go.setTextColor(s.active?Ui.fg():Ui.onAccent(this));" in MAIN
    assert "go.setTextColor(s.active?Ui.fg():0xFF061216);" not in MAIN

def test_active_stop_button_keeps_theme_foreground():
    assert "go.setBackground(Ui.shape(s.active?Ui.surface2(this):AppPrefs.accent(this)" in MAIN
    assert "go.setTextColor(s.active?Ui.fg():Ui.onAccent(this));" in MAIN

def test_contrast_helper_chooses_light_or_dark_text():
    assert "public static int onAccent(Context c)" in UI
    assert ">.24?0xff071219:0xffffffff" in UI
