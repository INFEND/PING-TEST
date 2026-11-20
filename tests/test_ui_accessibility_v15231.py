"""UI-only regressions: accessible touch targets and Android motion preference."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = (ROOT / "app/src/main/java/com/xarkon/pingtest/Ui.java").read_text(encoding="utf-8")
SETTINGS = (ROOT / "app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java").read_text(encoding="utf-8")


class UiAccessibilityTests(unittest.TestCase):
    def test_compact_controls_remain_touch_accessible(self):
        self.assertGreaterEqual(UI.count("setMinimumHeight(dp(48))"), 2)
        self.assertIn("b.setFocusable(true)", UI)
        self.assertIn("t.setFocusable(true)", UI)
        self.assertIn("t.setSelected(selected)", UI)

    def test_press_animations_honor_android_reduced_motion(self):
        self.assertIn("ValueAnimator.areAnimatorsEnabled()", UI)
        self.assertIn('AppPrefs.bool(c,"motion",true)', UI)
        self.assertIn("v.animate().cancel();v.setScaleX(1f);v.setScaleY(1f);", UI)
        self.assertIn("MotionEvent.ACTION_CANCEL", UI)

    def test_settings_sections_keyboard_focus_and_state(self):
        self.assertIn("head.setClickable(true);head.setFocusable(true)", SETTINGS)
        self.assertIn("head.setSelected(opened[0])", SETTINGS)
        self.assertIn("head.setSelected(opening)", SETTINGS)
        self.assertIn("ValueAnimator.areAnimatorsEnabled()", SETTINGS)

    def test_theme_and_accent_tiles_expose_selection(self):
        self.assertGreaterEqual(SETTINGS.count("tile.setFocusable(true);tile.setSelected(selected)"), 2)
        self.assertIn('tile.setContentDescription("Тема: "+names[i]', SETTINGS)
        self.assertIn('tile.setContentDescription("Акцент: "+NAMES[n]', SETTINGS)


if __name__ == "__main__":
    unittest.main()
