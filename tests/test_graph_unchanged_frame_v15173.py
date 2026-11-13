from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphUnchangedFrameTests(unittest.TestCase):
    def test_unchanged_frame_returns_before_allocation(self):
        self.assertLess(SOURCE.index("if(accent==color&&bg==background&&sameSamples(points,values))return;"), SOURCE.index("float[] fresh=new float[values.size()]"))
    def test_comparison_checks_entire_window_and_float_bits(self):
        body = SOURCE.split("private static boolean sameSamples", 1)[1].split("@Override", 1)[0]
        self.assertIn("current.length!=incoming.size()", body)
        self.assertIn("for(float value:incoming)", body)
        self.assertIn("Float.floatToIntBits(current[i++])!=Float.floatToIntBits(value)", body)
        self.assertIn("return true;", body)

if __name__ == "__main__":
    unittest.main()
