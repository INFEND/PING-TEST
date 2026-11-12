"""Regression checks for stable and honest live chart autoscaling."""
from pathlib import Path
import unittest
SOURCE=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")
class ChartScaleTests(unittest.TestCase):
    def test_axis_scale_does_not_oscillate_on_small_drops(self):
        self.assertIn("required<displayMax*.70f?required:displayMax",SOURCE)
        self.assertIn("required>displayMax?required",SOURCE)
    def test_scale_animated_with_frame_progress(self):
        self.assertIn("displayMax=scaleStart+(scaleTarget-scaleStart)*progress",SOURCE)
        self.assertIn("renderWithScale(canvas,getWidth(),getHeight(),animated,accent,bg,displayMax,paint,fillPath)",SOURCE)
        self.assertIn("displayMax=scaleTarget",SOURCE)
    def test_static_export_remains_deterministic(self):
        self.assertIn("renderWithScale(c,w,h,v,accent,background,axisMaximum(v))",SOURCE)
        self.assertIn("Float.isFinite(r)",SOURCE)
    def test_bounded_reply_marker_not_a_loss(self):
        self.assertIn("if(v[i]==-2f)",SOURCE)
        self.assertIn("if(v[i]<0)",SOURCE)
if __name__=="__main__": unittest.main()
