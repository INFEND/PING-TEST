from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest"
SERVICE = (ROOT / "PingService.java").read_text(encoding="utf-8")
MAIN = (ROOT / "MainActivity.java").read_text(encoding="utf-8")

class MonitorSnapshot(unittest.TestCase):
    def test_monitor_uses_bounded_copy(self):
        self.assertIn("monitorSnapshot(){synchronized(LOCK){return live.copy(false);}}", SERVICE)
        self.assertIn("PingService.Snapshot s=PingService.monitorSnapshot();refreshStatus(s);", MAIN)

    def test_full_history_unchanged(self):
        self.assertIn("public Snapshot copy(){return copy(true);}", SERVICE)
        self.assertIn("if(full){s.log.addAll(log);s.events.addAll(events);}", SERVICE)

    def test_recent_probes_and_placeholder(self):
        self.assertIn("i>=0&&s.events.size()<4", SERVICE)
        self.assertIn("if(e.number>0)s.events.add(0,e);", SERVICE)
        self.assertIn("if(s.events.isEmpty()&&!events.isEmpty())s.events.add(events.get(events.size()-1));", SERVICE)

if __name__ == "__main__":
    unittest.main()
