"""Regression: accept vendor ICMP sequence spacing without accepting wrong probes."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
SEQ = r"\bicmp_seq(?:[ \t]*=[ \t]*|[ \t]+)1(?![\w.,])"

class VendorSequenceSpacing(unittest.TestCase):
    def test_parser_uses_strict_sequence_one(self):
        self.assertIn(SEQ.replace("\\b", "\\\\b"), SOURCE)

    def test_vendor_spacing_and_wrong_sequences(self):
        pattern = re.compile(SEQ, re.I)
        for token in ("icmp_seq=1", "icmp_seq = 1", "icmp_seq= 1", "icmp_seq\t1", "ICMP_SEQ\t=\t1"):
            self.assertIsNotNone(pattern.search(token), token)
        for token in ("icmp_seq=2", "icmp_seq=10", "icmp_seq = 11", "icmp_seq==1", "icmp_seq=1abc", "icmp_seq1", "icmp_seq=1.5", "icmp_seq=1,5", "icmp_seq=1_5"):
            self.assertIsNone(pattern.search(token), token)

if __name__ == "__main__":
    unittest.main()
