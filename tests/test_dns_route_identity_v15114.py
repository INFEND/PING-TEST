import pathlib
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class DnsRouteIdentityRegression(unittest.TestCase):
    def test_network_identity_rechecked_after_route_lookup(self):
        start = SOURCE.index("VpnGuard.Route resolvedRoute=VpnGuard.route(this);")
        end = SOURCE.index("if(selectedRoute!=VpnGuard.Route.UNKNOWN", start)
        segment = SOURCE[start:end]
        self.assertIn("activeNetwork.equals(connectivity.getActiveNetwork())", segment)
        self.assertIn("throw new UnknownHostException", segment)

    def test_recheck_precedes_publication(self):
        check = SOURCE.index("Сеть приложения изменилась при проверке маршрута")
        publish = SOURCE.index("sessionNetwork=activeNetwork;", check)
        self.assertLess(check, publish)

if __name__ == "__main__":
    unittest.main()
