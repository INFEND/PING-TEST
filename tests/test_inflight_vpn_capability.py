"""Guard against attributing ICMP results to a changed VPN route."""
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java"


class InFlightVpnRouteTests(unittest.TestCase):
    def test_recheck_after_native_ping_before_statistics(self):
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("Network resultNetwork=")
        end = source.index("synchronized(LOCK){", start)
        section = source[start:end]
        self.assertIn("expectedNetwork.equals(resultNetwork)", section)
        self.assertIn("VpnGuard.Route resultRoute=VpnGuard.route(this)", section)
        self.assertIn("resultRoute!=sessionRoute", section)
        self.assertIn("finishRun(capturedRun", section)
        self.assertLess(section.index("resultRoute!=sessionRoute"), section.index("// Local routing/permission/command failures"))


if __name__ == "__main__":
    unittest.main()
