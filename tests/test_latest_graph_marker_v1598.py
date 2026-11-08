"""Only the actual latest sample may be highlighted after failures."""
from pathlib import Path
import unittest

GRAPH=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")
class LatestMarker(unittest.TestCase):
    def test_latest_only(self):
        block=GRAPH.split("// Highlight only the actual latest sample.",1)[1].split('p.setColor(0xff8b98a5)',1)[0]
        self.assertIn("int latest=v.length-1;",block)
        self.assertIn("if(v[latest]>=0||v[latest]==-2f)",block)
        self.assertIn("int i=latest;",block)
        self.assertNotIn("for(int i=v.length-1;i>=0;i--)",block)
        self.assertIn("if(v[i]==-2f)",block)
    def test_bounded_not_connected_to_exact(self):
        self.assertIn("if(v[i]==-2f)",GRAPH)
        self.assertIn("continue;",GRAPH.split("if(v[i]==-2f)",1)[1].split("if(v[i]<0)",1)[0])
        self.assertIn("if(i>0&&v[i-1]>=0)",GRAPH)
if __name__=="__main__":unittest.main()
