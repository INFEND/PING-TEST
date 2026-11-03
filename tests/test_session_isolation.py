import pathlib
import unittest

SRC=(pathlib.Path(__file__).resolve().parents[1]/
     "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class SessionIsolationTests(unittest.TestCase):
    def test_late_dns_error_cannot_finish_new_session(self):
        self.assertIn("if(runId!=expectedRun || !live.active || stopping)return;",SRC)
        self.assertIn('finishRun(expectedRun,"Проверка недоступна:',SRC)
    def test_fatal_probe_uses_original_session(self):
        self.assertIn("finishRun(capturedRun,error)",SRC)
        self.assertNotIn("if(capturedRun==runId)finish(error)",SRC)
    def test_route_callback_uses_captured_session(self):
        self.assertIn("c.scheduleAtFixedRate(()->tick(expectedRun)",SRC)
        self.assertIn("finishRun(scheduledRun,",SRC)
    def test_guard_is_serialized_with_finish(self):
        self.assertIn("private synchronized void finishRun(long expectedRun,String reason)",SRC)
        self.assertIn("if(runId!=expectedRun || !live.active)return;",SRC)

if __name__=="__main__": unittest.main()
