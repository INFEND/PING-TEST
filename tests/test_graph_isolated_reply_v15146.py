"""Historical isolated measured replies remain visible between graph gaps."""
from pathlib import Path
import unittest

GRAPH = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class IsolatedGraphReply(unittest.TestCase):
    def test_isolated_reply_drawn_without_connecting_segment(self):
        self.assertIn("if(i<v.length-1&&!connectedBefore&&!connectedAfter)", GRAPH)
        self.assertIn("c.drawCircle(x,y,Math.max(1.5f,2.2f*density),p);", GRAPH)

    def test_neighbors_must_be_finite_measured_replies(self):
        self.assertIn("connectedBefore=i>0&&Float.isFinite(v[i-1])&&v[i-1]>=0", GRAPH)
        self.assertIn("connectedAfter=i+1<v.length&&Float.isFinite(v[i+1])&&v[i+1]>=0", GRAPH)

    def test_bounded_and_loss_markers_precede_measured_reply(self):
        self.assertLess(GRAPH.index("if(v[i]==-2f)"), GRAPH.index("boolean connectedBefore="))
        self.assertLess(GRAPH.index("if(v[i]<0)"), GRAPH.index("boolean connectedBefore="))

if __name__ == "__main__":
    unittest.main()
