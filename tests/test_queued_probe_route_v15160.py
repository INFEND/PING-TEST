from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class QueuedProbeRouteTest(unittest.TestCase):
    def test_queued_probe_checks_session_before_launch(self):
        probe = SOURCE.split("private void probe(", 1)[1].split("new ProcessBuilder", 1)[0]
        self.assertGreaterEqual(probe.count("if(stopping || capturedRun!=runId)return;"), 2)
        self.assertIn("!launchExpected.equals(launchNetwork)", probe)
        self.assertIn("!launchExpected.equals(launchAfter)", probe)
        self.assertIn("launchRoute!=sessionRoute", probe)
        self.assertIn("finishRun(capturedRun", probe)
        self.assertIn("return;", probe.split("finishRun(capturedRun", 1)[1])

if __name__ == "__main__":
    unittest.main()
