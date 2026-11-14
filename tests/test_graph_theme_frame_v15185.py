from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphThemeFrameTests(unittest.TestCase):
    def test_theme_only_frame_preserves_animation(self):
        body = SOURCE.split("if(Arrays.equals(points,fresh)){", 1)[1].split("}", 1)[0]
        self.assertIn("accent=color;bg=background;", body)
        self.assertIn("invalidate();", body)
        self.assertIn("return;", body)
        for forbidden in ("progress=", "animator", "displayMax=", "previous="):
            self.assertNotIn(forbidden, body)
        self.assertLess(SOURCE.index("if(Arrays.equals(points,fresh)){"), SOURCE.index("previous=last;"))

if __name__ == "__main__":
    unittest.main()
