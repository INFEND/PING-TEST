"""Regression guard: do not mistake diagnostic output for an ICMP reply."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java")


class IcmpReplyValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.parser = cls.source.split("private static double[] parseIcmpReply(", 1)[1].split(
            "\n    private void probe(", 1)[0]

    def test_reply_requires_sequence_marker(self):
        # Toybox ping replies carry icmp_seq; a line containing only
        # 'bytes from <ip>' and 'time=' is not sufficient evidence.
        self.assertIn(r"icmp_seq(?:[ \t]*=[ \t]*|[ \t]+)1(?![\\w.,:/+\\-])", self.parser)
        self.assertIn("TIME.matcher(line)", self.parser)

    def test_reply_requires_selected_address(self):
        self.assertIn("Pattern.quote(expectedAddress)", self.parser)
        self.assertIn("Matcher lines=reply.matcher(output)", self.parser)

    def test_failed_process_cannot_report_success(self):
        self.assertIn("exitCode==0?parseIcmpReply(output,probeAddress):null",
                      self.source)

    def test_expected_toybox_reply_shape(self):
        # Independent fixture documents the intended acceptance boundary.
        pattern = re.compile(r"^\d+ bytes from 192\.0\.2\.7(?::|\s)(?=[^\r\n]*\bicmp_seq(?:[ \t]*=[ \t]*|[ \t]+)1(?![\w.,:/+\-]))[^\r\n]*$", re.I)
        self.assertIsNotNone(pattern.match("64 bytes from 192.0.2.7: icmp_seq=1 ttl=64 time=12.4 ms"))
        self.assertIsNone(pattern.match("64 bytes from 192.0.2.7: time=12.4 ms"))
        self.assertIsNone(pattern.match("64 bytes from 192.0.2.8: icmp_seq=1 ttl=64 time=12.4 ms"))
        self.assertIsNone(pattern.match("64 bytes from 192.0.2.7: icmp_seq=2 ttl=64 time=12.4 ms"))
        self.assertIsNone(pattern.match("64 bytes from 192.0.2.7: icmp_seq=1/2 ttl=64 time=12.4 ms"))


if __name__ == "__main__":
    unittest.main()
