from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class RouteTransitionTest(unittest.TestCase):
    def test_all_probe_stages_reject_any_route_transition(self):
        for guard in ("if(currentRoute!=sessionRoute)", "(launchRoute!=sessionRoute)", "if(resultRoute!=sessionRoute)", "(commitRoute!=sessionRoute)"):
            with self.subTest(guard=guard):
                self.assertIn(guard, SOURCE)
        self.assertNotIn("sessionRoute!=VpnGuard.Route.UNKNOWN", SOURCE)

if __name__ == "__main__":
    unittest.main()
