from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
BODY = SOURCE.split("private final class ReplyMetric extends TextView", 1)[1].split("private final class Metric extends TextView", 1)[0]

class ReplyColorContinuity(unittest.TestCase):
    def test_same_destination_keeps_running_animation(self):
        guard = "if(animator!=null&&animator.isRunning()&&previousColor==finishColor)return;"
        self.assertLess(BODY.index('setText(nextOk+" / "+nextSent)'), BODY.index(guard))
        self.assertLess(BODY.index(guard), BODY.index("if(animator!=null)animator.cancel();", BODY.index(guard)))
    def test_no_animation_for_identical_color(self):
        self.assertLess(BODY.index("if(startColor==finishColor)return;"), BODY.index("ValueAnimator change="))
    def test_disabled_motion_cancels(self):
        self.assertIn("if(animator!=null)animator.cancel();\n                setTextColor(finishColor);return;", BODY)

if __name__ == "__main__":
    unittest.main()
