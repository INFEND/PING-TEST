"""UI-only checks for edge-to-edge layout stability on Android 17/OriginOS."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest"
MAIN = (ROOT / "MainActivity.java").read_text(encoding="utf-8")
INSETS = (ROOT / "UiInsets.java").read_text(encoding="utf-8")

class UiSafeInsetsTests(unittest.TestCase):
    def test_fallback_applies_before_first_frame(self):
        self.assertIn("UiInsets.apply(this,root);", MAIN)
        self.assertLess(MAIN.index("UiInsets.apply(this,root);"), MAIN.index("setContentView(root);"))
        self.assertLess(INSETS.index("root.setPadding(baseLeft,baseTop+fallbackTop,baseRight,baseBottom);"),
                        INSETS.index("root.setOnApplyWindowInsetsListener("))

    def test_cutout_and_system_bars_cover_all_four_sides(self):
        self.assertIn("getInsetsIgnoringVisibility(bars)", INSETS)
        self.assertIn("WindowInsets.Type.displayCutout()", INSETS)
        for side in ("left", "top", "right", "bottom"):
            self.assertIn("safe." + side, INSETS)
            self.assertIn("cutout." + side, INSETS)

    def test_insets_are_not_added_repeatedly_on_tab_change(self):
        for side in ("baseLeft+left", "baseTop+top", "baseRight+right", "baseBottom+bottom"):
            self.assertIn(side, INSETS)
        self.assertIn("if(view.getPaddingLeft()!=l||view.getPaddingTop()!=t", INSETS)
        self.assertNotIn("root.setOnApplyWindowInsetsListener(", MAIN)

if __name__ == "__main__":
    unittest.main()
