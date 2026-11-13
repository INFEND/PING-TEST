from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class DnsPublishRouteTest(unittest.TestCase):
    def test_revalidate_under_session_lock(self):
        section = SOURCE.split("// Publish the network atomically", 1)[1].split("sessionNetwork=activeNetwork;", 1)[0]
        self.assertIn("synchronized(LOCK)", section)
        self.assertIn("runId!=expectedRun", section)
        self.assertEqual(section.count("activeNetwork.equals(connectivity.getActiveNetwork())"), 2)
        self.assertIn("VpnGuard.Route publishRoute=VpnGuard.route(this);", section)
        self.assertIn("publishRoute!=effectiveRoute", section)
        self.assertLess(section.index("runId!=expectedRun"), section.index("VpnGuard.Route publishRoute"))

    def test_mismatch_aborts_before_publication(self):
        section = SOURCE.split("VpnGuard.Route publishRoute=VpnGuard.route(this);", 1)[1].split("sessionNetwork=activeNetwork;", 1)[0]
        self.assertIn("throw new UnknownHostException", section)
        self.assertIn("publishRoute!=effectiveRoute", section)

if __name__ == "__main__":
    unittest.main()
