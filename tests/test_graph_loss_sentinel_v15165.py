"""Only the explicit loss sentinel may draw a red cross."""
from pathlib import Path
import unittest

GRAPH = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphLossSentinel(unittest.TestCase):
    def test_unknown_negative_is_skipped_before_red_marker(self):
        block = GRAPH.split("if(v[i]<0){", 1)[1].split("float y=", 1)[0]
        self.assertLess(block.index("if(v[i]!=-1f)continue;"), block.index("p.setColor(QualityColors.RED)"))

    def test_bounded_reply_is_handled_before_negative_branch(self):
        self.assertLess(GRAPH.index("if(v[i]==-2f)"), GRAPH.index("if(v[i]<0)"))
        self.assertIn("QualityColors.GREEN", GRAPH.split("if(v[i]==-2f)", 1)[1].split("if(v[i]<0)", 1)[0])
