"""Packet counts must be a single exact snapshot, not interpolated frames."""
from pathlib import Path
import unittest

class ReplyMetricAccuracy(unittest.TestCase):
    def test_exact_counts_before_color_animation(self):
        source = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
        metric = source.split("private final class ReplyMetric extends TextView", 1)[1].split("private final class Metric extends TextView", 1)[0]
        self.assertLess(metric.index('setText(nextOk+" / "+nextSent)'), metric.index('ValueAnimator change='))
        self.assertNotIn("Math.round", metric)
        self.assertNotIn("shownOk", metric)
        self.assertNotIn("setText(", metric.split("change.addUpdateListener", 1)[1])
        self.assertIn("QualityColors.blend(startColor,finishColor,progress)", metric)
        self.assertIn("if(animator!=null)animator.cancel()", metric)

if __name__ == "__main__":
    unittest.main()
