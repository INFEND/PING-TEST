"""Non-finite telemetry must not be rendered as RTT or a fabricated packet loss."""
from pathlib import Path
import unittest

GRAPH = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class InvalidGraphTelemetry(unittest.TestCase):
    def test_nan_and_infinity_are_skipped_before_loss_marker(self):
        render = GRAPH.split("private static void renderWithScale(", 1)[1]
        invalid = render.index("if(!Float.isFinite(v[i]))")
        bounded = render.index("if(v[i]==-2f)", invalid)
        loss = render.index("if(v[i]<0)", bounded)
        self.assertLess(invalid, bounded)
        self.assertLess(bounded, loss)
        self.assertIn("continue;", render[invalid:bounded])

    def test_nonfinite_previous_does_not_connect_line(self):
        self.assertIn("if(i>0&&Float.isFinite(v[i-1])&&v[i-1]>=0)", GRAPH)

    def test_nonfinite_latest_does_not_get_success_halo(self):
        self.assertIn("if(Float.isFinite(v[latest])&&(v[latest]>=0||v[latest]==-2f))", GRAPH)

    def test_animation_never_interpolates_nonfinite_rtt(self):
        self.assertIn("Float.isFinite(previous)&&previous>=0&&Float.isFinite(points[points.length-1])", GRAPH)

if __name__ == "__main__":
    unittest.main()
