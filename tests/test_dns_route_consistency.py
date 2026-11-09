"""Regression: reject DNS results after an in-place per-UID VPN route handover."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class DnsRouteConsistencyTests(unittest.TestCase):
    def test_dns_checks_network_identity_before_publishing(self):
        self.assertIn("activeNetwork.equals(connectivity.getActiveNetwork())", SOURCE)
    def test_dns_checks_capabilities_even_when_network_handle_is_unchanged(self):
        self.assertIn("VpnGuard.Route resolvedRoute=VpnGuard.route(this)", SOURCE)
        self.assertIn("selectedRoute!=VpnGuard.Route.UNKNOWN && resolvedRoute!=selectedRoute", SOURCE)
        self.assertLess(SOURCE.index("VpnGuard.Route resolvedRoute=VpnGuard.route(this)"),
                        SOURCE.index("final String resolvedAddress=preferV4(resolved).getHostAddress()"))
    def test_ping_results_still_validate_route_after_native_process(self):
        self.assertIn("VpnGuard.Route resultRoute=VpnGuard.route(this)", SOURCE)
        self.assertIn("resultRoute!=sessionRoute", SOURCE)

if __name__ == "__main__": unittest.main()
