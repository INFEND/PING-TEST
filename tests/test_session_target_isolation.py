import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SERVICE=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class TimerAndAddressIsolationTests(unittest.TestCase):
    def test_scheduler_captures_run_id(self):
        self.assertIn("c.scheduleAtFixedRate(()->tick(expectedRun)",SERVICE)
        self.assertNotIn("scheduleAtFixedRate(this::tick",SERVICE)
    def test_old_scheduler_cannot_tick_new_run(self):
        self.assertIn("private void tick(long scheduledRun)",SERVICE)
        self.assertIn("scheduledRun!=runId",SERVICE)
    def test_probe_captures_target_address(self):
        self.assertIn("probeAddress=live.ip",SERVICE)
        self.assertIn("probe(seq,capturedRun,probeAddress,probeBytes,probeTtl,probeTimeout)",SERVICE)
        self.assertIn("private void probe(int seq,long capturedRun,String probeAddress,int probeBytes,int probeTtl,int probeTimeout)",SERVICE)
    def test_command_and_reply_use_same_target(self):
        self.assertIn("Integer.toString(probeTtl),probeAddress}",SERVICE)
        self.assertIn("parseIcmpReply(output,probeAddress)",SERVICE)

if __name__=="__main__":
    unittest.main()
