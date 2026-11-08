"""Do not count vendor timeout text as packet loss when zero packets were sent."""
from pathlib import Path
import re
import unittest

SRC=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
BODY=SRC.split("private static boolean isConfirmedNoReply(String output){",1)[1].split("\n    private void probe(",1)[0]

class ZeroTransmissionTimeoutRegression(unittest.TestCase):
    def test_zero_transmission_precedes_timeout(self):
        self.assertIn("zeroTransmitted.matcher(output).find()",BODY)
        self.assertLess(BODY.index("zeroTransmitted.matcher(output).find()"),BODY.index('text.contains("request timeout")'))
        self.assertIn("if(zeroTransmitted.matcher(output).find())return false;",BODY)
    def test_zero_transmission_pattern(self):
        p=re.compile(r"^\s*0\s+packets? transmitted\b",re.I|re.M)
        self.assertIsNotNone(p.search("Request timeout for icmp_seq 1\n0 packets transmitted, 0 received"))
        self.assertIsNone(p.search("Request timeout for icmp_seq 1\n1 packets transmitted, 0 received"))
        self.assertIsNone(p.search("10 packets transmitted, 0 received"))
    def test_existing_confirmed_loss_and_reply_policy_unchanged(self):
        self.assertIn("zeroReceived.matcher(output).find()",BODY)
        self.assertIn("exitCode==1&&isConfirmedNoReply(output)",SRC)
        self.assertIn("if(rtt>=0||rtt==-2)",SRC)

if __name__=="__main__":unittest.main()
