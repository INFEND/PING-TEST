"""Regression guards for out-of-order history checkpoints."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/"app/src/main/java/com/xarkon/pingtest"
STORE=(JAVA/"HistoryStore.java").read_text()
SERVICE=(JAVA/"PingService.java").read_text()
class HistoryCheckpointOrder(unittest.TestCase):
    def test_guard_precedes_write(self):
        upsert=STORE.split("void upsert(",1)[1].split("static boolean isStaleCheckpoint",1)[0]
        self.assertLess(upsert.index("isStaleCheckpoint(previous,entry)"),upsert.index("updated.put(entry)"))
        self.assertIn('previous.optLong("id",-2)==id',upsert)
    def test_final_and_revision_guards(self):
        self.assertIn('previous.optBoolean("finished",false) && !incoming.optBoolean("finished",false)',STORE)
        self.assertIn('previous.optLong("revision",-1)>incoming.optLong("revision",-1)',STORE)
    def test_snapshot_revision_and_final_state(self):
        self.assertIn('j.put("revision",s.version)',SERVICE)
        self.assertIn('j.put("finished",finished || !s.active)',SERVICE)
if __name__=="__main__": unittest.main()
