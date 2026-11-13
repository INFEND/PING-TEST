from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class RejectedProbeStopTest(unittest.TestCase):
    def test_rejected_probe_does_not_mutate_stopping_session(self):
        tick = SOURCE.split("private void tick(", 1)[1]
        rejected = tick.split("catch(RejectedExecutionException ex)", 1)[1]
        guard = "if(capturedRun!=runId || !live.active || stopping)return;"
        self.assertLess(rejected.index(guard), rejected.index("live.sent--;live.skipped++"))
