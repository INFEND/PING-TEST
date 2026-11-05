"""Regression checks: truncated native ping diagnostics must not become packet loss."""
import pathlib
import re
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class TruncatedPingOutputTests(unittest.TestCase):
    def test_capture_is_bounded_but_pipe_is_drained(self):
        self.assertIn("int remaining=8192-buffer.size()", SOURCE)
        self.assertIn("while((read=input.read(temp))!=-1)", SOURCE)

    def test_truncation_is_local_error_not_loss(self):
        self.assertRegex(SOURCE, r'if\(buffer\.size\(\)>=8192\)error="Вывод ping превышает 8 КиБ"')
        self.assertIn('error.startsWith("Вывод ping превышает 8 КиБ")', SOURCE)
        self.assertRegex(SOURCE, r'else if\(exitCode==1\)error="Нет ответа"')

if __name__ == "__main__":
    unittest.main()
