"""Live graph scratch objects must be reused without leaking paint state."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphScratchTests(unittest.TestCase):
    def test_live_draw_reuses_objects(self):
        self.assertIn("private final Path fillPath=new Path()", SOURCE)
        self.assertIn("displayMax,paint,fillPath)", SOURCE)
        body = SOURCE.split("protected void onDraw", 1)[1].split("public static void render", 1)[0]
        self.assertNotIn("new Paint", body)
        self.assertNotIn("new Path", body)

    def test_renderer_resets_reused_state(self):
        body = SOURCE.split("float scale,Paint p,Path area)", 1)[1]
        self.assertIn("p.reset();p.setAntiAlias(true)", body)
        self.assertIn("area.rewind()", body)
        self.assertNotIn("new Paint", body)
        self.assertNotIn("new Path", body)

    def test_export_uses_independent_scratch(self):
        self.assertIn("scale,new Paint(Paint.ANTI_ALIAS_FLAG),new Path()", SOURCE)

if __name__ == "__main__":
    unittest.main()
