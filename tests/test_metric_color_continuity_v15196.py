from pathlib import Path
import unittest

BODY = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8").split("private final class Metric extends TextView", 1)[1]

class MetricColorContinuity(unittest.TestCase):
    def test_same_destination_keeps_animation(self):
        guard = "if(motion!=null&&motion.isRunning()&&quality(previous)==finishColor)return;"
        self.assertLess(BODY.index('shown=next;setText(fmt(next)+(percent?" %":""));', BODY.index("final int startColor")), BODY.index(guard))
        self.assertLess(BODY.index(guard), BODY.index("if(motion!=null)motion.cancel();", BODY.index(guard)))
    def test_special_values_cancel(self):
        self.assertIn("if(next==-2 && kind==0){if(motion!=null)motion.cancel();", BODY)
        self.assertIn("if(next<0||!Double.isFinite(next)){if(motion!=null)motion.cancel();", BODY)
    def test_disabled_motion_cancels(self):
        self.assertIn("if(motion!=null)motion.cancel();\n                shown=next;", BODY)

if __name__ == "__main__":
    unittest.main()
