"""Regressions for conservative ICMP loss classification."""
from pathlib import Path
import unittest
SOURCE=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
class IcmpLoss(unittest.TestCase):
    def test_exit_one_requires_confirmed_no_reply(self):
        self.assertIn('exitCode==1&&isConfirmedNoReply(output)',SOURCE)
        self.assertNotIn('else if(exitCode==1)error="Нет ответа"',SOURCE)
    def test_ambiguous_exit_is_fatal_not_packet_loss(self):
        self.assertIn('error="Неоднозначный результат ping (код 1)"',SOURCE)
        self.assertIn('error.startsWith("Неоднозначный результат ping")',SOURCE)
        self.assertIn('else if(fatal){live.error=error;addProbeEvent',SOURCE)
    def test_confirmed_loss_requires_explicit_evidence(self):
        code=SOURCE.split('private static boolean isConfirmedNoReply(',1)[1].split('private void probe(',1)[0]
        self.assertIn('zeroReceived.matcher(output).find()',code)
        self.assertIn('packets? transmitted',code)
        self.assertIn('received',code)
        self.assertNotIn('100% packet loss',code)
    def test_bounded_rtt_remains_success(self):
        self.assertIn('if(rtt>=0||rtt==-2)',SOURCE)
        self.assertIn('rtt==-2?-2f',SOURCE)
if __name__=="__main__": unittest.main()
