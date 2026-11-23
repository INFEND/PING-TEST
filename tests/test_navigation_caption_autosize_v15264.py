from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class NavigationCaptionRegression(unittest.TestCase):
    def test_navigation_caption_fits_narrow_screens(self):
        navigation = SRC.split("private void navigation(){", 1)[1].split("private TextView label(", 1)[0]
        self.assertIn('String[] names={"Монитор","История","Настройки"}', navigation)
        self.assertRegex(navigation, r"label\.setSingleLine\(true\);\s*label\.setAutoSizeTextTypeUniformWithConfiguration\(9,11,1,android\.util\.TypedValue\.COMPLEX_UNIT_SP\)")
        self.assertIn("cell.setContentDescription(names[i])", navigation)
        self.assertIn("cell.setMinimumHeight(Ui.dp(51))", navigation)
        self.assertIn("cell.setOnClickListener", navigation)
    def test_version_metadata(self):
        gradle=(ROOT/"app/build.gradle").read_text(encoding="utf-8")
        self.assertRegex(gradle, r"versionCode\s+27[2-9]|versionCode\s+[3-9][0-9]{2,}")
        self.assertIn('"1.5.264": 272', (ROOT/"release_notes/versions.json").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
