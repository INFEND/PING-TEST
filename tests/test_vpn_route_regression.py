"""Regression checks for UID-specific VPN routing (source-level guardrails)."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/VpnGuard.java").read_text(encoding="utf-8")

class VpnRouteRegression(unittest.TestCase):
    def test_uses_default_network_for_this_uid(self):
        self.assertRegex(SOURCE, r"\bcm\.getActiveNetwork\s*\(\s*\)")
        self.assertRegex(SOURCE, r"cm\.getNetworkCapabilities\s*\(\s*network\s*\)")
        self.assertNotIn("getAllNetworks(", SOURCE)

    def test_vpn_requires_active_network_vpn_transport(self):
        self.assertRegex(SOURCE, r"if\s*\(\s*caps\.hasTransport\(NetworkCapabilities\.TRANSPORT_VPN\)\s*\)\s*return Route\.VPN")
        self.assertIn("return route(context)==Route.VPN;", SOURCE)

    def test_excluded_uid_uses_direct_route(self):
        self.assertIn("NetworkCapabilities.NET_CAPABILITY_NOT_VPN", SOURCE)
        self.assertIn("NetworkCapabilities.TRANSPORT_WIFI", SOURCE)
        self.assertIn("NetworkCapabilities.TRANSPORT_CELLULAR", SOURCE)
        self.assertIn("return Route.DIRECT;", SOURCE)

    def test_unavailable_network_does_not_trigger_false_warning(self):
        self.assertRegex(SOURCE, r"if\s*\(network==null\)return Route\.UNKNOWN")
        self.assertRegex(SOURCE, r"if\s*\(caps==null\)return Route\.UNKNOWN")
        self.assertIn("catch(RuntimeException ignored)", SOURCE)
        self.assertIn('case DIRECT: return "● БЕЗ VPN";', SOURCE)
        self.assertIn('default: return "● МАРШРУТ НЕИЗВЕСТЕН";', SOURCE)

if __name__ == "__main__":
    unittest.main()
