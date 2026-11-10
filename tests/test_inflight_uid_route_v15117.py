"""Regression guards for UID-network identity before committing ICMP results.

These checks prevent accidentally moving the network validation exclusively to
tick(): an in-flight native ping can finish after Android switches networks.
"""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")


class InflightUidRouteRegression(unittest.TestCase):
    def test_probe_rechecks_uid_network_after_native_ping(self):
        probe = SOURCE.split("private void probe(", 1)[1].split("private void ", 1)[0]
        native_done = probe.index("finally{if(process!=null)")
        uid_check = probe.index("resultConnectivity.getActiveNetwork()")
        lock = probe.index("synchronized(LOCK)", uid_check)
        self.assertLess(native_done, uid_check)
        self.assertLess(uid_check, lock)
        self.assertRegex(probe[uid_check:lock],
                         r"expectedNetwork\s*==\s*null\s*\|\|\s*!expectedNetwork\.equals\(resultNetwork\)")
        self.assertIn("finishRun(capturedRun", probe[uid_check:lock])
        self.assertIn("return;", probe[uid_check:lock])

    def test_route_classification_rechecked_before_stats(self):
        probe = SOURCE.split("private void probe(", 1)[1].split("private void ", 1)[0]
        uid_check = probe.index("resultConnectivity.getActiveNetwork()")
        route_check = probe.index("VpnGuard.route(this)", uid_check)
        stats_lock = probe.index("synchronized(LOCK)", route_check)
        self.assertLess(uid_check, route_check)
        self.assertLess(route_check, stats_lock)
        self.assertIn("resultRoute!=sessionRoute", probe[route_check:stats_lock])
        self.assertIn("finishRun(capturedRun", probe[route_check:stats_lock])

    def test_vpn_guard_uses_uid_default_not_all_networks(self):
        guard = (Path(__file__).resolve().parents[1] /
                 "app/src/main/java/com/xarkon/pingtest/VpnGuard.java").read_text(encoding="utf-8")
        self.assertIn("getActiveNetwork()", guard)
        self.assertNotIn("getAllNetworks()", guard)


if __name__ == "__main__":
    unittest.main()
