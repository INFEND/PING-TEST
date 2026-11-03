import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
VPN=(ROOT/"app/src/main/java/com/xarkon/pingtest/VpnGuard.java").read_text(encoding="utf-8")
MAIN=(ROOT/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
SERVICE=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class SplitTunnelPolicyTests(unittest.TestCase):
    def test_route_is_per_app_default_not_global_vpn_presence(self):
        self.assertIn("cm.getActiveNetwork()",VPN)
        self.assertIn("getNetworkCapabilities(network)",VPN)
        self.assertNotIn("getAllNetworks(",VPN)
    def test_direct_route_does_not_trigger_vpn_guard(self):
        self.assertIn("return route(context)==Route.VPN;",VPN)
        self.assertIn("return Route.DIRECT;",VPN)
    def test_unknown_not_labeled_as_vpn(self):
        self.assertIn("return Route.UNKNOWN;",VPN)
        self.assertIn("Не удалось определить маршрут сети",VPN)
    def test_app_and_service_agree_on_routing(self):
        self.assertIn("VpnGuard.statusText(this)",MAIN)
        self.assertIn("VpnGuard.Route selectedRoute=VpnGuard.route(this)",SERVICE)
        self.assertIn("currentRoute!=sessionRoute",SERVICE)
    def test_does_not_manipulate_global_vpn_or_sockets(self):
        self.assertNotIn("bindProcessToNetwork",VPN)
        self.assertNotIn("bindSocket(",VPN)

if __name__=="__main__":
    unittest.main()
