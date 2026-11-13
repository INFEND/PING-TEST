from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class MetricColorAnimationTests(unittest.TestCase):
    def test_same_color_skips_animator_after_measured_text(self):
        body = SOURCE.split("private final class Metric extends TextView", 1)[1].split("private void checkClipboard", 1)[0]
        guard = "if(startColor==finishColor){setTextColor(finishColor);return;}"
        self.assertLess(body.index('shown=next;setText(fmt(next)', body.index("final int startColor")), body.index(guard))
        self.assertLess(body.index(guard), body.index("ValueAnimator a=ValueAnimator.ofFloat"))
    def test_changed_color_still_animates(self):
        body = SOURCE.split("private final class Metric extends TextView", 1)[1].split("private void checkClipboard", 1)[0]
        self.assertIn("if(motion!=null)motion.cancel()", body)
        self.assertIn("QualityColors.blend(startColor,finishColor", body)
        self.assertIn("a.start();", body)

if __name__ == "__main__":
    unittest.main()
