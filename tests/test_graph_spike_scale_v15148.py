"""Regression: rising RTT axis must fit new samples from the first frame."""
from pathlib import Path
import unittest
SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")
class GraphSpikeScaleTests(unittest.TestCase):
    def test_upward_scale_applied_before_animation(self):
        start = SOURCE.index("if(required>displayMax){")
        end = SOURCE.index("points=fresh;", start)
        block = SOURCE[start:end]
        self.assertIn("displayMax=required;", block)
        self.assertIn("scaleStart=required;", block)
        self.assertLess(end, SOURCE.index("animator.start();", end))
    def test_downward_scale_keeps_hysteresis_and_animation(self):
        self.assertIn("required<displayMax*.70f?required:displayMax", SOURCE)
        self.assertIn("displayMax=scaleStart+(scaleTarget-scaleStart)*progress", SOURCE)
if __name__ == "__main__":
    unittest.main()
