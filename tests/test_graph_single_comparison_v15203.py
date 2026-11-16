from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphSingleComparisonTests(unittest.TestCase):
    def test_theme_and_unchanged_frames_do_not_allocate(self):
        body = SOURCE.split("public void setData", 1)[1].split("private static boolean sameSamples", 1)[0]
        self.assertEqual(body.count("sameSamples(points,values)"), 1)
        self.assertNotIn("Arrays.equals(", body)
        self.assertLess(body.index("return;"), body.index("float[] fresh="))
        self.assertIn("for(float value:values)fresh[index++]=value;", body)
        self.assertNotIn("values.get(", body)

if __name__ == "__main__":
    unittest.main()
