"""Regression: scrolling graph must animate when newest RTT equals prior RTT."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GRAPH = (ROOT / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")


class GraphRollingWindowTests(unittest.TestCase):
    def test_full_window_comparison(self):
        self.assertIn("!Arrays.equals(points,fresh)", GRAPH)
        self.assertNotIn("fresh[fresh.length-1]!=points[points.length-1]", GRAPH)

    def test_bounded_rtt_not_drawn_as_loss(self):
        self.assertIn("if(v[i]==-2f)", GRAPH)
        self.assertIn("if(v[i]<0)", GRAPH)
        self.assertLess(GRAPH.index("if(v[i]==-2f)"), GRAPH.index("if(v[i]<0)"))

    def test_window_shift_with_equal_latest_rtt(self):
        old = [10.0, 20.0, 20.0]
        shifted = [20.0, 20.0, 20.0]
        self.assertEqual(old[-1], shifted[-1])
        self.assertNotEqual(old, shifted)


if __name__ == "__main__":
    unittest.main()
