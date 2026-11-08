"""Contradictory vendor ICMP output must never fabricate packet loss."""
from pathlib import Path
import re
import unittest

SRC=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
BODY=SRC.split("private static boolean isConfirmedNoReply(String output){",1)[1].split("\n    private void probe(",1)[0]

class ContradictorySummaryRegression(unittest.TestCase):
    def test_received_summary_precedes_timeout(self):
        self.assertIn("positiveReceived.matcher(output).find()", BODY)
        self.assertLess(BODY.index("positiveReceived.matcher(output).find()"), BODY.index("zeroReceived.matcher(output).find()"))
    def test_received_summary_pattern(self):
        p=re.compile(r"^\s*[1-9]\d*\s+packets? transmitted,\s*[1-9]\d*\s+(?:packets? )?received\b", re.I|re.M)
        self.assertIsNotNone(p.search("Request timeout for icmp_seq 1\n1 packets transmitted, 1 received"))
        self.assertIsNone(p.search("1 packets transmitted, 0 received"))
        self.assertIsNone(p.search("0 packets transmitted, 1 received"))
    def test_existing_loss_guards(self):
        self.assertIn("zeroTransmitted.matcher(output).find()",BODY)
        self.assertIn("zeroReceived.matcher(output).find()",BODY)
        self.assertIn("exitCode==1&&isConfirmedNoReply(output)",SRC)

if __name__=="__main__": unittest.main()
