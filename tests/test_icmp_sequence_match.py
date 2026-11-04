import pathlib
import re
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class IcmpSequenceTest(unittest.TestCase):
    def test_single_probe_sequence_is_required(self):
        self.assertIn(r'\\bicmp_seq[= ]1\\b', SOURCE)
        self.assertNotIn(r'\\bicmp_seq[= ]\\d+\\b', SOURCE)

    def test_exact_sequence_boundary(self):
        pattern = re.compile(r'\\bicmp_seq[= ]1\\b')
        self.assertIsNotNone(pattern.search("icmp_seq=1 ttl=55 time=3.4"))
        self.assertIsNotNone(pattern.search("icmp_seq 1 ttl=55 time=3.4"))
        for line in ("icmp_seq=2 ttl=55 time=3.4", "icmp_seq=10 ttl=55 time=3.4", "icmp_seq=11 ttl=55 time=3.4"):
            self.assertIsNone(pattern.search(line))

if __name__ == "__main__":
    unittest.main()
