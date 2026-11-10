import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class IcmpReplyLinePolicy(unittest.TestCase):
    def test_latency_and_ttl_from_same_reply(self):
        self.assertIn("Matcher time=TIME.matcher(line);",SOURCE)
        self.assertIn("Matcher ttl=TTL.matcher(line);",SOURCE)
        self.assertIn("parseIcmpReply(output,probeAddress)",SOURCE)
        self.assertNotIn("TIME.matcher(output)",SOURCE)
        self.assertNotIn("TTL.matcher(output)",SOURCE)
    def test_nonzero_exit_requires_confirmed_received_reply(self):
        self.assertIn("double[] parsed=(exitCode==0||receivedDespiteExitOne)",SOURCE)
        self.assertIn("boolean receivedDespiteExitOne=exitCode==1",SOURCE)
    def test_finite_nonnegative_latency(self):
        self.assertIn("Double.isFinite(latency)",SOURCE)
        self.assertIn("latency<0",SOURCE)

if __name__=="__main__": unittest.main()
