from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphColorReuseTests(unittest.TestCase):
    def test_single_quality_lookup_per_measured_sample(self):
        self.assertEqual(SOURCE.count("QualityColors.rtt("), 1)
        self.assertIn("QualityColors.blend(previousColor,color,.5f)", SOURCE)
        self.assertIn("int col=previousColor;", SOURCE)

    def test_cached_color_only_used_for_adjacent_measurements(self):
        self.assertIn("if(i>0&&Float.isFinite(v[i-1])&&v[i-1]>=0)", SOURCE)
        self.assertLess(SOURCE.index("if(v[i]<0)"), SOURCE.index("previousColor=color;"))
        self.assertLess(SOURCE.index("if(!Float.isFinite(v[i]))"), SOURCE.index("previousColor=color;"))
        self.assertLess(SOURCE.index("if(v[i]==-2f)"), SOURCE.index("previousColor=color;"))

if __name__ == "__main__":
    unittest.main()
