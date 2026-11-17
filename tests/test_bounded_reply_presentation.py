import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/xarkon/pingtest"

class BoundedReplyPresentationTest(unittest.TestCase):
    def test_bounded_success_has_consistent_quality_color(self):
        source = (JAVA / "MainActivity.java").read_text(encoding="utf-8")
        self.assertIn("e.latencyMs==-2?QualityColors.GREEN", source)
        self.assertIn('setText("<1");setTextColor(QualityColors.GREEN)', source)
        self.assertIn('qualityState.setText(bounded?"ОТЛИЧНО"', source)
        self.assertIn("qualityState.setTextColor(bounded?QualityColors.GREEN", source)
        self.assertIn('timed?QualityColors.rtt(o.optDouble("avg")):QualityColors.GREEN', source)

    def test_graph_keeps_bounded_reply_out_of_loss_branch(self):
        source = (JAVA / "GraphView.java").read_text(encoding="utf-8")
        branch = source.split("if(v[i]==-2f){", 1)[1].split("if(v[i]<0){", 1)[0]
        self.assertIn("QualityColors.GREEN", branch)
        self.assertIn("continue;", branch)
        self.assertNotIn("QualityColors.RED", branch)

if __name__ == "__main__":
    unittest.main()
