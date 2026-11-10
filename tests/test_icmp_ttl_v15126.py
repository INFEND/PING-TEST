"""Regression checks for Android ping TTL variants and strict field boundaries."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")


class TtlParserTests(unittest.TestCase):
    def test_vendor_whitespace_and_boundary(self):
        self.assertIn(r'\\bttl\\s*(?:=\\s*|\\s+)([0-9]{1,3})\\b', SOURCE)
        pattern = re.compile(r'\bttl\s*(?:=\s*|\s+)([0-9]{1,3})\b', re.I)
        for sample in ("ttl=64", "TTL = 64", "ttl 64", "ttl\t=\t64"):
            with self.subTest(sample=sample):
                self.assertEqual(pattern.search(sample).group(1), "64")
        for sample in ("notttl=64", "ttl=1234", "ttl=abc"):
            with self.subTest(sample=sample):
                self.assertIsNone(pattern.search(sample))


if __name__ == "__main__":
    unittest.main()
