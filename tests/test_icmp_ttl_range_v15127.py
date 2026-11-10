"""TTL is an 8-bit hop-limit field; malformed vendor output must not become a displayed TTL."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
TTL = re.compile(r'\bttl\s*(?:=\s*|\s+)([0-9]{1,3})(?![0-9\w.,])', re.I)

class TtlRangeTests(unittest.TestCase):
    def test_valid_values_and_vendor_spacing(self):
        for sample, expected in (("ttl=1", 1), ("TTL = 64", 64),
                                 ("ttl 255", 255), ("ttl\t=\t128", 128)):
            with self.subTest(sample=sample):
                m = TTL.search(sample)
                self.assertIsNotNone(m)
                self.assertEqual(int(m.group(1)), expected)

    def test_malformed_tokens_are_not_partial_matches(self):
        for sample in ("ttl=1234", "ttl=64.5", "ttl=64,5",
                       "ttl=64abc", "notttl=64", "ttl=abc"):
            with self.subTest(sample=sample):
                self.assertIsNone(TTL.search(sample))

    def test_out_of_range_values_are_ignored_by_java(self):
        self.assertIn("parsedTtl>=1&&parsedTtl<=255", SOURCE)
        for value in (0, 256, 999):
            with self.subTest(value=value):
                m = TTL.search("ttl=" + str(value))
                self.assertIsNotNone(m)
                self.assertFalse(1 <= int(m.group(1)) <= 255)

if __name__ == "__main__":
    unittest.main()
