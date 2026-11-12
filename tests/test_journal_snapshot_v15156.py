from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest"
SERVICE = (ROOT / "PingService.java").read_text(encoding="utf-8")
MAIN = (ROOT / "MainActivity.java").read_text(encoding="utf-8")
METHOD = SERVICE.split("public static Snapshot journalSnapshot(", 1)[1].split("private ScheduledExecutorService", 1)[0]

class JournalSnapshot(unittest.TestCase):
    def test_unchanged_tail_skips_allocation_under_lock(self):
        self.assertIn("synchronized(LOCK)", METHOD)
        self.assertLess(METHOD.index("if(live.id==sessionId)"), METHOD.index("return null"))
        self.assertLess(METHOD.index("tail==live.events.get(size-1)"), METHOD.index("new Snapshot()"))
        self.assertIn("size==0 && tail==null && emptyView", METHOD)

    def test_changed_session_copies_only_events(self):
        self.assertIn("s.id=live.id;", METHOD)
        self.assertIn("s.events.addAll(live.events);", METHOD)
        self.assertNotIn("live.copy()", METHOD)
        self.assertNotIn("s.chart.addAll", METHOD)
        self.assertNotIn("s.log.addAll", METHOD)

    def test_journal_uses_specialized_snapshot(self):
        method = MAIN.split("private void refreshJournal(){", 1)[1].split("// HISTORY", 1)[0]
        self.assertIn("PingService.journalSnapshot(journalSessionId,journalTail,journalRows.getChildCount()==0)", method)
        self.assertLess(method.index("if(snapshot==null)return;"), method.index("snapshot.events"))

if __name__ == "__main__":
    unittest.main()
