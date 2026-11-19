import pathlib
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text()

class SynchronousRouteTest(unittest.TestCase):
    def test_dns_baseline(self):
        self.assertLess(SOURCE.index("IcmpPath dnsPath=readIcmpPath"), SOURCE.index("activeNetwork.getAllByName(chosen)"))
        self.assertIn("!sameIcmpPath(dnsPath,publishPath)", SOURCE)
        self.assertIn("sessionPath=publishPath;", SOURCE)

    def test_commit_rechecks_path_before_counters(self):
        start = SOURCE.index("IcmpPath commitPath=readIcmpPath")
        end = SOURCE.index("live.done++;", start)
        block = SOURCE[start:end]
        self.assertIn("!sameIcmpPath(sessionPath,commitPath)", block)
        self.assertIn("commitPath==null", block)
        self.assertIn("if(!routeChangedAtCommit)", block)
        self.assertLess(block.index("readIcmpPath"), block.index("getActiveNetwork()"))

if __name__ == "__main__":
    unittest.main()
