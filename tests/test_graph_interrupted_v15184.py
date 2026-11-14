from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class InterruptedGraphTests(unittest.TestCase):
    def test_interruption_uses_visible_sample_before_cancel(self):
        self.assertIn("last=previous+(last-previous)*progress;", SOURCE)
        self.assertLess(SOURCE.index("previous=last;"), SOURCE.index("if(animator!=null)animator.cancel();"))

    def test_only_measured_finite_samples_interpolate(self):
        self.assertIn("if(progress<1f&&Float.isFinite(previous)&&previous>=0&&Float.isFinite(last)&&last>=0)", SOURCE)
        self.assertIn("Float.isFinite(points[points.length-1])&&points[points.length-1]>=0", SOURCE)

if __name__ == "__main__":
    unittest.main()
