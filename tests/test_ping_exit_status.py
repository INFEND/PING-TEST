"""Regression checks for ping exit-code classification (source-level guardrails)."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class PingExitStatusRegression(unittest.TestCase):
    def test_parse_reply_only_for_successful_exit(self):
        self.assertRegex(SOURCE, r"exitCode\s*==\s*0\s*\?\s*parseIcmpReply")

    def test_local_exit_failure_is_diagnostic(self):
        self.assertIn('else error="Локальная ошибка ping (код "+exitCode+")";', SOURCE)

    def test_local_error_is_excluded_from_packet_loss(self):
        self.assertIn('error.startsWith("Локальная ошибка ping")||', SOURCE)
        self.assertRegex(SOURCE, r"else if\(fatal\)\{live\.error=error;addProbeEvent")
        self.assertRegex(SOURCE, r"else\{live\.lost\+\+")

    def test_ping_exit_one_still_allows_timeout_loss(self):
        self.assertIn('else if(exitCode==1)error="Нет ответа";', SOURCE)
        self.assertNotIn('else error="Нет ответа";', SOURCE)

if __name__ == "__main__":
    unittest.main()
