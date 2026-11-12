"""Regression: chart must not present stale successes as the newest response."""
from pathlib import Path
import unittest
SOURCE=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")
class LatestMarker(unittest.TestCase):
    def test_only_latest_success_is_emphasized(self):
        drawing=SOURCE.split("private static void renderWithScale(",1)[1]
        self.assertIn("int latest=v.length-1;",drawing)
        self.assertIn("if(Float.isFinite(v[latest])&&(v[latest]>=0||v[latest]==-2f))",drawing)
        self.assertNotIn("for(int i=v.length-1;i>=0;i--)if(v[i]>=0||v[i]==-2f)",drawing)
    def test_bounded_rtt_is_not_loss(self):
        self.assertIn("if(v[i]==-2f)",SOURCE)
        self.assertIn("QualityColors.GREEN",SOURCE)
        self.assertIn("if(v[i]<0)",SOURCE)
    def test_non_latest_samples_are_still_drawn(self):
        self.assertIn("for(int i=0;i<v.length;i++)",SOURCE)
if __name__=="__main__": unittest.main()
