from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class TickUnknownRouteTest(unittest.TestCase):
    def test_known_route_must_remain_known_before_reserving_probe(self):
        tick = SOURCE.split("private void tick(", 1)[1].split("workers.execute", 1)[0]
        guard = "if(currentRoute!=sessionRoute)"
        self.assertIn(guard, tick)
        self.assertNotIn("currentRoute!=VpnGuard.Route.UNKNOWN&&", tick)
        self.assertLess(tick.index(guard), tick.index("seq=++live.planned"))
        self.assertIn("finishRun(scheduledRun", tick.split(guard, 1)[1].split("final int seq", 1)[0])

if __name__ == "__main__":
    unittest.main()
