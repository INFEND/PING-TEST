"""A bounded <1 ms ICMP success must never be shown as a lost graph packet."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SERVICE=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
GRAPH=(ROOT/"app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class BoundedGraphOutcomeTests(unittest.TestCase):
    def test_success_marker_keeps_bound_without_fake_precision(self):
        self.assertIn("live.chart.add(rtt==-2?-2f:rtt<0?-1f:(float)rtt)",SERVICE)
        self.assertIn("if(rtt>=0||rtt==-2)",SERVICE)
        self.assertNotIn("live.chart.add(rtt<0?-1f:(float)rtt)",SERVICE)

    def test_bounded_reply_and_loss_markers_are_distinct(self):
        bounded=GRAPH.index("if(v[i]==-2f)")
        lost=GRAPH.index("if(v[i]<0)",bounded)
        self.assertLess(bounded,lost,"Bounded samples must be handled before generic negatives")
        bounded_block=GRAPH[bounded:lost]
        self.assertIn("QualityColors.GREEN",bounded_block)
        self.assertIn("Paint.Style.STROKE",bounded_block)
        self.assertNotIn("QualityColors.RED",bounded_block)
        self.assertIn("QualityColors.RED",GRAPH[lost:lost+260])

    def test_no_fabricated_line_between_bounded_and_exact(self):
        self.assertIn("if(i>0&&Float.isFinite(v[i-1])&&v[i-1]>=0)",GRAPH)
        self.assertIn("int latest=v.length-1;",GRAPH)
        self.assertIn("if(Float.isFinite(v[latest])&&(v[latest]>=0||v[latest]==-2f))",GRAPH)
        self.assertIn("int i=latest;",GRAPH)
        self.assertNotIn("for(int i=v.length-1;i>=0;i--)",GRAPH)
        self.assertNotIn("if(v[i]>=0||v[i]==-2f)",GRAPH)
        self.assertIn("if(v[i]==-2f)",GRAPH)

if __name__=="__main__":
    unittest.main()
