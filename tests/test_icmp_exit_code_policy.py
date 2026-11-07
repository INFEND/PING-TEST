"""ICMP exit code 1 is not sufficient proof of packet loss."""
import pathlib
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class ExitCodePolicy(unittest.TestCase):
    def test_exit_one_needs_explicit_no_reply_evidence(self):
        self.assertIn('exitCode==1&&isConfirmedNoReply(output)', SOURCE)
        self.assertNotIn('else if(exitCode==1)error="Нет ответа";', SOURCE)

    def test_ambiguous_exit_one_is_local_error_not_packet_loss(self):
        self.assertIn('error="Неоднозначный результат ping (код 1)"', SOURCE)
        self.assertIn('error.startsWith("Неоднозначный результат ping")', SOURCE)
        self.assertIn('else if(fatal){live.error=error;addProbeEvent', SOURCE)

    def test_other_codes_are_local_errors(self):
        self.assertIn('else error="Локальная ошибка ping (код "+exitCode+")";', SOURCE)
        self.assertIn('error.startsWith("Локальная ошибка ping")', SOURCE)

    def test_unparsed_success_is_not_packet_loss(self):
        self.assertIn('else if(exitCode==0)error="Ответ ping не распознан";', SOURCE)
        self.assertIn('error.startsWith("Ответ ping не распознан")', SOURCE)

if __name__ == "__main__":
    unittest.main()
