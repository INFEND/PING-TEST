"""Regression guards for real sub-ms chart values versus bounded replies."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")


class GraphSubmillisecondTests(unittest.TestCase):
    def test_measured_sub_ms_uses_one_ms_axis(self):
        self.assertIn("if(highest<1f)return 1f;", SOURCE)
        self.assertIn("if(Float.isFinite(r)&&r>=0&&r>highest)highest=r;", SOURCE)
        self.assertIn("Math.round(tick*10f)/10f", SOURCE)

    def test_bounded_reply_is_not_numeric_or_loss(self):
        self.assertIn("if(v[i]==-2f)", SOURCE)
        self.assertIn("if(v[i]!=-1f)continue;", SOURCE)
        self.assertIn("v[latest]==-2f", SOURCE)
        self.assertRegex(SOURCE, r"if\(v\[i\]<0\)")


if __name__ == "__main__":
    unittest.main()
