"""Prevent default-network status from claiming per-packet ICMP routing."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
GUARD = (ROOT / "app/src/main/java/com/xarkon/pingtest/VpnGuard.java").read_text(encoding="utf-8")

class DefaultNetworkCopyTest(unittest.TestCase):
    def test_default_network_is_not_packet_route_proof(self):
        self.assertIn("Сеть приложения без VPN", SOURCE)
        self.assertIn("Сеть по умолчанию: без VPN", SOURCE)
        self.assertIn("Сеть по умолчанию: VPN", SOURCE)
        self.assertIn("Сеть приложения: ", SOURCE)
        self.assertNotIn("Прямой маршрут PING TEST", SOURCE)
        self.assertNotIn("Прямой маршрут (PING TEST вне VPN)", SOURCE)
        self.assertNotIn('addLog("Маршрут: "+route)', SOURCE)

    def test_unknown_state_stays_unknown(self):
        self.assertIn("Сеть по умолчанию не определена", SOURCE)
        self.assertIn('"Сеть приложения без VPN".equals(s.vpnInfo)?"Без VPN":"Сеть неизвестна";', SOURCE)
        self.assertIn("Сеть неизвестна", SOURCE)

    def test_uid_default_network_not_other_apps_vpn(self):
        self.assertIn("cm.getActiveNetwork()", GUARD)
        self.assertNotIn("getAllNetworks()", GUARD.split("public static Route route")[1])

if __name__ == "__main__":
    unittest.main()
