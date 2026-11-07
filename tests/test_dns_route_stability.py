"""Prevent stale DNS answers from being used after a UID route change."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class DnsRouteStabilityTests(unittest.TestCase):
    def test_dns_uses_uid_active_network(self):
        self.assertIn("connectivity.getActiveNetwork()", SOURCE)
        self.assertIn("activeNetwork.getAllByName(chosen)", SOURCE)
        self.assertNotIn("InetAddress.getAllByName(chosen)", SOURCE)

    def test_route_change_invalidates_dns_result_before_ping(self):
        guard = "if(!activeNetwork.equals(connectivity.getActiveNetwork()))"
        self.assertIn(guard, SOURCE)
        self.assertIn('throw new UnknownHostException("Сеть приложения изменилась во время DNS");', SOURCE)
        self.assertLess(SOURCE.index(guard), SOURCE.index("final String resolvedAddress=preferV4(resolved).getHostAddress();"))

if __name__ == "__main__":
    unittest.main()
