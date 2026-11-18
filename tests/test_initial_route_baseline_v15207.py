from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class InitialRouteBaselineTest(unittest.TestCase):
    def test_seed_before_registration(self):
        block = SOURCE.split("private void startRouteMonitor()", 1)[1].split("private void stopRouteMonitor()", 1)[0]
        self.assertIn("Network initial=routeMonitor.getActiveNetwork();", block)
        self.assertIn("if(Objects.equals(initial,routeMonitor.getActiveNetwork()))", block)
        self.assertIn("if(caps!=null)observedRoute=VpnGuard.classify(caps);", block)
        self.assertLess(block.index("if(caps!=null)observedRoute=VpnGuard.classify(caps);"), block.index("registerDefaultNetworkCallback(callback)"))
        self.assertNotIn("getAllNetworks", block)

    def test_unknown_baseline_is_not_direct(self):
        block = SOURCE.split("private void startRouteMonitor()", 1)[1].split("private void stopRouteMonitor()", 1)[0]
        self.assertIn("observedRoute=null;", block)
        self.assertIn("catch(RuntimeException ignored)", block)

if __name__ == "__main__":
    unittest.main()
