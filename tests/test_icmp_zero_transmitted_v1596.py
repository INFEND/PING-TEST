"""ICMP confirmed-loss regressions: zero-transmitted and local send failures."""
from pathlib import Path
import re
import unittest

SOURCE=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
METHOD=SOURCE.split("private static boolean isConfirmedNoReply(String output){",1)[1].split("\n    private void probe(",1)[0]

class ConfirmedLossRegression(unittest.TestCase):
    def test_requires_positive_transmitted_count(self):
        self.assertIn(r'[1-9]\\d*\\s+packets? transmitted',METHOD)
        self.assertNotIn(r'\\d+\\s+packets? transmitted',METHOD)
        pattern=re.compile(r'^\s*[1-9]\d*\s+packets? transmitted,\s*0\s+(?:packets? )?received\b',re.I|re.M)
        self.assertIsNone(pattern.search("0 packets transmitted, 0 received, 100% packet loss"))
        self.assertIsNotNone(pattern.search("1 packets transmitted, 0 received, 100% packet loss"))
        self.assertIsNotNone(pattern.search("2 packets transmitted, 0 packets received"))
    def test_local_send_failures_take_precedence(self):
        for token in ('isNetworkFailure(output)','isDnsFailure(output)','sendto:','sendmsg:','permission denied','operation not permitted'):
            self.assertIn(token,METHOD)
        self.assertLess(METHOD.index('isNetworkFailure(output)'),METHOD.index('zeroReceived.matcher(output).find()'))
        self.assertLess(METHOD.index('sendto:'),METHOD.index('zeroReceived.matcher(output).find()'))
    def test_bounded_reply_stays_success(self):
        self.assertIn('if(rtt>=0||rtt==-2)',SOURCE)
        self.assertIn('live.chart.add(rtt==-2?-2f:',SOURCE)

if __name__=="__main__":unittest.main()
