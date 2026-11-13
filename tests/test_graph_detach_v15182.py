from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphDetachTests(unittest.TestCase):
    def test_detached_graph_does_not_start_animation(self):
        self.assertIn("boolean animate=isAttachedToWindow()&&AppPrefs.bool", SOURCE)

    def test_detach_cancels_animation_and_settles_frame(self):
        body = SOURCE.split("protected void onDetachedFromWindow()", 1)[1].split("/** Fixed autoscale", 1)[0]
        for expected in ("animator.cancel()", "animator=null", "progress=1f", "displayMax=scaleTarget", "super.onDetachedFromWindow()"):
            self.assertIn(expected, body)

if __name__ == "__main__":
    unittest.main()
