"""Guard against claiming packet-level VPN route certainty from UID default network."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/VpnGuard.java").read_text(encoding="utf-8")

class VpnRouteCopyTest(unittest.TestCase):
    def test_uid_default_network_not_all_networks(self):
        self.assertIn("cm.getActiveNetwork()", SOURCE)
        self.assertIn("cm.getNetworkCapabilities(network)", SOURCE)
        self.assertNotIn("getAllNetworks(", SOURCE)

    def test_route_labels_are_indicators_not_packet_proof(self):
        self.assertIn('case VPN: return "● ЧЕРЕЗ VPN";', SOURCE)
        self.assertIn('case DIRECT: return "● БЕЗ VPN";', SOURCE)
        self.assertNotIn("реальный маршрут приложения", SOURCE)
        self.assertNotIn("VPN не используется", SOURCE)
        self.assertIn('default: return "● МАРШРУТ НЕИЗВЕСТЕН";', SOURCE)
        self.assertIn("return Route.UNKNOWN;", SOURCE)

if __name__ == "__main__":
    unittest.main()
