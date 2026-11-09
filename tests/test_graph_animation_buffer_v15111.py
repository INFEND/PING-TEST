"""Regression: live RTT interpolation must not allocate a new sample array per frame."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphAnimationAllocationTests(unittest.TestCase):
    def test_interpolation_reuses_buffer(self):
        self.assertIn("private float[] animatedPoints=new float[0]", SOURCE)
        self.assertIn("if(animatedPoints.length!=fresh.length) animatedPoints=new float[fresh.length]", SOURCE)
        self.assertIn("System.arraycopy(points,0,animatedPoints,0,points.length)", SOURCE)
        self.assertIn("animated=animatedPoints", SOURCE)
        self.assertNotIn("Arrays.copyOf(points,points.length)", SOURCE)
    def test_real_samples_remain_unmodified(self):
        self.assertIn("animatedPoints[points.length-1]=previous+", SOURCE) if "animatedPoints[points.length-1]=previous+" in SOURCE else self.assertIn("animated[points.length-1]=previous+", SOURCE)
        self.assertIn("float[] animated=points", SOURCE)
    def test_bounded_reply_and_loss_markers_preserved(self):
        self.assertIn("if(v[i]==-2f)", SOURCE)
        self.assertIn("if(v[i]<0)", SOURCE)

if __name__=="__main__": unittest.main()
