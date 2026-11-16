from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/GraphView.java").read_text(encoding="utf-8")

class GraphMotionPreferenceTests(unittest.TestCase):
    def test_disabled_motion_settles_before_unchanged_frame_return(self):
        body = SOURCE.split("public void setData", 1)[1].split("if(sameSamples(points,values))", 1)[0]
        for expected in ('if(progress<1f&&!AppPrefs.bool(getContext(),"motion",true))', 'animator.cancel()', 'animator=null', 'progress=1f', 'displayMax=scaleTarget', 'invalidate()'):
            self.assertIn(expected, body)
        self.assertLess(body.index('animator.cancel()'), body.index('progress=1f'))

    def test_enabled_motion_keeps_existing_fast_path(self):
        body = SOURCE.split("if(sameSamples(points,values)){", 1)[1].split("}", 1)[0]
        self.assertIn("if(accent==color&&bg==background)return;", body)
        self.assertNotIn("animator.cancel()", body)

if __name__ == "__main__":
    unittest.main()
