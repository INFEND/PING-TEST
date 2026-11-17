from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class QueuedGeneration(unittest.TestCase):
    def test_generation_checked_before_native_ping(self):
        probe = SOURCE.split("private void probe(", 1)[1]
        guard = probe.split("new ProcessBuilder", 1)[0]
        self.assertIn("generationChanged=routeGeneration!=sessionGeneration;", guard)
        self.assertIn("if(generationChanged || launchExpected==null", guard)
        self.assertLess(guard.index("synchronized(LOCK)"), guard.index("generationChanged=routeGeneration"))
        self.assertIn("finishRun(capturedRun,", guard)

if __name__ == "__main__":
    unittest.main()
