from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class IdleMonitorTests(unittest.TestCase):
    def test_unchanged_idle_target_skips_rebuilding_views(self):
        body = SOURCE.split("private void refreshPing()", 1)[1].split("private String fmt", 1)[0]
        guard = "if(selectedHost.equals(idleMismatchHost)&&s.id==idleMismatchId&&s.version==idleMismatchVersion)return;"
        self.assertLess(body.index("VpnGuard.statusText(this)"), body.index(guard))
        self.assertLess(body.index(guard), body.index("recentEvents.removeAllViews()"))
        self.assertIn("idleMismatchHost=selectedHost;idleMismatchId=s.id;idleMismatchVersion=s.version;", body)
    def test_cache_invalidated_on_rebuild_and_matching_session(self):
        self.assertIn("renderedVersion=-1;idleMismatchHost=null;activeBefore=false;refreshPing();", SOURCE)
        self.assertIn("idleMismatchHost=null;\n        if(s.active!=activeBefore", SOURCE)

if __name__ == "__main__":
    unittest.main()
