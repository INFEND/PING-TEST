from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class HeaderStatusFocusRegression(unittest.TestCase):
    def test_status_is_readable_but_not_fake_button(self):
        header = SRC.split("private void header(){", 1)[1].split("private void refreshStatus()", 1)[0]
        self.assertRegex(header, r"status\.setClickable\(false\);\s*status\.setFocusable\(false\)")
        self.assertNotIn("status.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO)", header)
        self.assertIn('status=Ui.chip(this,"● ГОТОВ",false)', header)

    def test_existing_navigation_remains_accessible(self):
        nav = SRC.split("private void navigation(){", 1)[1].split("private TextView label(", 1)[0]
        self.assertIn("cell.setContentDescription(names[i])", nav)
        self.assertIn("cell.setOnClickListener", nav)

    def test_version_metadata(self):
        gradle = (ROOT / "app/build.gradle").read_text(encoding="utf-8")
        self.assertRegex(gradle, r"versionCode\s+(?:27[3-9]|2[8-9][0-9]|[3-9][0-9]{2,})")
        self.assertIn('"1.5.265": 273', (ROOT / "release_notes/versions.json").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
