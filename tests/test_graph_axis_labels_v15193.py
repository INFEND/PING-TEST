from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphAxisLabelTests(unittest.TestCase):
    def test_axis_labels_avoid_per_frame_formatter(self):
        self.assertNotIn("String.format(", SOURCE)
        self.assertIn("Long.toString(Math.round((double)(max*(3-k)/3)))", SOURCE)

    def test_bounded_and_loss_markers_remain_distinct(self):
        self.assertLess(SOURCE.index("if(v[i]==-2f)"), SOURCE.index("if(v[i]<0)"))
        self.assertIn("if(v[i]!=-1f)continue;", SOURCE)

if __name__ == "__main__":
    unittest.main()
