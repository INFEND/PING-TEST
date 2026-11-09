"""Regression: DNS publishes the route actually observed after resolution."""
from pathlib import Path
import unittest

SRC = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class DnsRouteMetadataTests(unittest.TestCase):
    def test_unknown_initial_route_can_be_upgraded_after_dns(self):
        self.assertIn("final VpnGuard.Route effectiveRoute=resolvedRoute==VpnGuard.Route.UNKNOWN", SRC)
        self.assertIn("?selectedRoute:resolvedRoute", SRC)
        self.assertIn("sessionRoute=effectiveRoute;", SRC)

    def test_published_route_and_vpn_info_use_same_classification(self):
        self.assertIn("live.route=effectiveRouteText;", SRC)
        self.assertIn("live.vpnInfo=effectiveRoute==VpnGuard.Route.VPN", SRC)
        self.assertIn('addLog("Сеть приложения: "+effectiveRouteText)', SRC)
        self.assertLess(SRC.index("sessionRoute=effectiveRoute;"), SRC.index("live.ip=resolvedAddress;"))

    def test_dns_still_rejects_known_route_handover(self):
        self.assertIn("selectedRoute!=VpnGuard.Route.UNKNOWN && resolvedRoute!=selectedRoute", SRC)

if __name__ == "__main__": unittest.main()
