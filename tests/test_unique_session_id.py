import pathlib
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class UniqueSessionIdTests(unittest.TestCase):
    def test_new_run_id_exceeds_previous_even_with_same_millisecond(self):
        self.assertIn("live.id=Math.max(System.currentTimeMillis(),runId+1)", SOURCE)

    def test_old_session_callbacks_remain_guarded(self):
        self.assertIn("runId!=expectedRun", SOURCE)
        self.assertIn("runId!=capturedRun", SOURCE)

    def test_history_uses_unique_session_identifier(self):
        self.assertIn('j.put("id",s.id)', SOURCE)

if __name__ == "__main__":
    unittest.main()
