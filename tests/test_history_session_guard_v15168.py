from pathlib import Path
import unittest
SRC=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
class HistorySessionGuard(unittest.TestCase):
    def test_checkpoint_uses_original_run(self):
        self.assertIn("if(historyCheckpoint)persist(false,capturedRun);",SRC)
        self.assertIn("if(s.id==0 || s.id!=expectedRun)return;",SRC)
    def test_system_stop_only_updates_owned_active_session(self):
        body=SRC.split("public void onDestroy(){",1)[1].split("private void signalUpdate",1)[0]
        self.assertIn("if(live.active && live.id==runId)",body)
        self.assertIn("live.version++;interrupted=true;",body)
        self.assertIn("if(interrupted){signalUpdate();persist(true);}",body)
if __name__=="__main__": unittest.main()
