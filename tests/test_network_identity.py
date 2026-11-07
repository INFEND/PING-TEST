import pathlib
import unittest

SOURCE = pathlib.Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class NetworkIdentityRegression(unittest.TestCase):
    def test_session_captures_dns_network(self):
        self.assertIn("sessionNetwork=activeNetwork;", SOURCE)
        self.assertIn("activeNetwork.equals(connectivity.getActiveNetwork())", SOURCE)

    def test_tick_rejects_uid_network_change_even_without_vpn_change(self):
        self.assertIn("Network currentNetwork=cm==null?null:cm.getActiveNetwork();", SOURCE)
        self.assertIn("initialNetwork==null || !initialNetwork.equals(currentNetwork)", SOURCE)
        self.assertIn('finishRun(scheduledRun,"Сеть приложения изменилась.', SOURCE)

    def test_inflight_probe_discards_outcome_on_network_switch(self):
        self.assertIn("Network resultNetwork=resultConnectivity==null?null:resultConnectivity.getActiveNetwork();", SOURCE)
        self.assertIn("!expectedNetwork.equals(resultNetwork)", SOURCE)
        self.assertIn('finishRun(capturedRun,"Сеть приложения изменилась во время ICMP.', SOURCE)
        self.assertLess(SOURCE.index("!expectedNetwork.equals(resultNetwork)"), SOURCE.index("// Local routing/permission/command failures are not ICMP packet loss."))

if __name__ == "__main__":
    unittest.main()
