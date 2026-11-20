"""Regression guard for filter chip screen-reader labels."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = (ROOT / "app/src/main/java/com/xarkon/pingtest/Ui.java").read_text(encoding="utf-8")

class ChipAccessibilityTest(unittest.TestCase):
    def test_selected_chip_announces_selection(self):
        self.assertIn('t.setContentDescription(value+(selected?", выбран":""));', UI)
        self.assertIn("t.setSelected(selected)", UI)
        self.assertIn("t.setFocusable(true)", UI)

if __name__ == "__main__":
    unittest.main()
