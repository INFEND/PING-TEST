from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class ResultRouteIdentityTest(unittest.TestCase):
    def test_result_route_rechecks_network_before_classification(self):
        section = SOURCE.split("VpnGuard.Route resultRoute=VpnGuard.route(this);", 1)[1].split("boolean fatal=", 1)[0]
        self.assertIn("Network afterResultRoute=resultConnectivity==null?null:resultConnectivity.getActiveNetwork();", section)
        self.assertIn("if(!expectedNetwork.equals(afterResultRoute))", section)
        self.assertLess(section.index("if(stopping || capturedRun!=runId)return;"), section.index("if(!expectedNetwork.equals(afterResultRoute))"))
        self.assertIn("finishRun(capturedRun", section.split("if(!expectedNetwork.equals(afterResultRoute))", 1)[1].split("if(sessionRoute", 1)[0])

if __name__ == "__main__":
    unittest.main()
