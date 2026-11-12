from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest"
SERVICE = (ROOT / "PingService.java").read_text(encoding="utf-8")
MAIN = (ROOT / "MainActivity.java").read_text(encoding="utf-8")

class MonitorIdleSnapshot(unittest.TestCase):
    def test_atomic_session_and_version_guard(self):
        body = SERVICE.split("monitorSnapshot(long sessionId,long version,String selectedHost){", 1)[1].split("/**", 1)[0]
        self.assertIn("synchronized(LOCK)", body)
        self.assertIn("live.id==sessionId && live.version==version", body)
        self.assertLess(body.index("return null"), body.index("return live.copy(false)"))

    def test_idle_target_change_is_not_suppressed(self):
        self.assertIn("(live.active || live.host.equals(selectedHost))", SERVICE)
        self.assertIn("!s.host.equals(selectedHost)", MAIN)
        self.assertIn("renderedVersion=-1;seenSession=-1;", MAIN)

    def test_recreated_view_forces_render(self):
        self.assertIn("renderedVersion=-1;activeBefore=false;refreshPing();", MAIN)
        self.assertIn("if(s==null)return;", MAIN)

if __name__ == "__main__":
    unittest.main()
