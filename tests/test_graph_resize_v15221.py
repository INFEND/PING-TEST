from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphResizeTests(unittest.TestCase):
    def test_resize_disables_sample_interpolation_before_snapshot(self):
        self.assertIn("boolean historyResize=fresh.length<points.length||fresh.length>points.length+1;", SOURCE)
        self.assertIn("if(historyResize){last=-1;newSample=false;}", SOURCE)
        self.assertLess(SOURCE.index("if(historyResize)"), SOURCE.index("previous=last;"))
        self.assertLess(SOURCE.index("previous=last;"), SOURCE.index("points=fresh;"))

    def test_axis_animation_remains_independent(self):
        self.assertIn("&&(newSample||Math.abs(scaleTarget-scaleStart)>0.01f)", SOURCE)
        self.assertIn("progress<1f&&Float.isFinite(previous)&&previous>=0", SOURCE)

if __name__ == "__main__":
    unittest.main()
