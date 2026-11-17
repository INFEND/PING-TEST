from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class StartupGeneration(unittest.TestCase):
    def test_stale_child_is_destroyed_before_output_wait(self):
        probe = SOURCE.split("private void probe(", 1)[1]
        guard = probe.split("activePings.add(process);", 1)[1].split("final ByteArrayOutputStream", 1)[0]
        self.assertIn("synchronized(LOCK)", guard)
        self.assertIn("staleLaunch=routeGeneration!=sessionGeneration;", guard)
        stale = guard.split("if(staleLaunch){", 1)[1]
        self.assertLess(stale.index("process.destroyForcibly();"), stale.index("finishRun(capturedRun,"))
        self.assertIn("return;", stale)
        self.assertIn("finally{if(process!=null){activePings.remove(process);", probe)

if __name__ == "__main__":
    unittest.main()
