from pathlib import Path
import unittest
s=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text()
class DnsRace(unittest.TestCase):
    def test_guard_before_network_publication(self):
        block=s.split("final String resolvedAddress=preferV4(resolved).getHostAddress();")[1].split("signalUpdate();")[0]
        self.assertLess(block.index("runId!=expectedRun"),block.index("sessionNetwork=activeNetwork;"))
    def test_scheduler_guard(self):
        block=s.split("signalUpdate();",2)[1]
        self.assertIn("c.scheduleAtFixedRate",s)
        self.assertIn("if(!live.active || runId!=expectedRun || stopping)return;",s)
    def test_uid_network(self):
        self.assertIn("activeNetwork.getAllByName(chosen)",s)
        self.assertNotIn("getAllNetworks()",s)
if __name__=="__main__": unittest.main()
