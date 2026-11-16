from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class DefaultNetworkGenerationTest(unittest.TestCase):
    def test_uid_callback_and_cleanup(self):
        self.assertIn("registerDefaultNetworkCallback(callback)", SOURCE)
        self.assertIn("unregisterNetworkCallback(callback)", SOURCE)
        self.assertIn("stopRouteMonitor();", SOURCE.split("public void onDestroy()", 1)[1])

    def test_duplicate_and_stale_events_do_not_increment(self):
        section = SOURCE.split("private void observeDefaultNetwork", 1)[1].split("private void startRouteMonitor", 1)[0]
        self.assertIn("if(lost && !Objects.equals(observedNetwork,network))return;", section)
        self.assertIn("if(!Objects.equals(observedNetwork,next))", section)
        self.assertIn("routeGeneration++;", section)

    def test_retired_callback_cannot_mutate_route(self):
        section = SOURCE.split("private void observeDefaultNetwork", 1)[1].split("private void startRouteMonitor", 1)[0]
        self.assertLess(section.index("if(source!=routeCallback)return;"), section.index("routeGeneration++;"))
        self.assertIn("observeDefaultNetwork(this,network,false)", SOURCE)
        self.assertIn("observeDefaultNetwork(this,network,true)", SOURCE)
        stop = SOURCE.split("private void stopRouteMonitor()", 1)[1].split("private volatile long runId", 1)[0]
        self.assertLess(stop.index("routeCallback=null;"), stop.index("unregisterNetworkCallback(callback)"))

    def test_dns_and_commit_reject_changed_generation(self):
        self.assertIn("dnsGeneration=routeGeneration;", SOURCE)
        self.assertLess(SOURCE.index("if(routeGeneration!=dnsGeneration)"), SOURCE.index("sessionNetwork=activeNetwork;"))
        self.assertIn("sessionGeneration=dnsGeneration;", SOURCE)
        section = SOURCE.split("routeChangedAtCommit=sessionNetwork", 1)[1]
        self.assertLess(section.index("routeGeneration!=sessionGeneration"), section.index("live.done++"))

if __name__ == "__main__":
    unittest.main()
