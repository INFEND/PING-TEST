"""Regression: vendor exit=1 must not invent a reply without a positive summary."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
SUMMARY = re.compile(r"(?m)^\s*1\s+packets? transmitted,\s*1\s+(?:packets? )?received\b", re.I)

class ContradictoryExitCode(unittest.TestCase):
    def test_guard_is_present(self):
        self.assertIn("receivedDespiteExitOne=exitCode==1", SOURCE)
        self.assertIn("&& !isNetworkFailure(output) && !isDnsFailure(output)", SOURCE)
        self.assertIn("?parseIcmpReply(output,probeAddress):null", SOURCE)

    def test_positive_summary_required(self):
        self.assertIsNotNone(SUMMARY.search("1 packets transmitted, 1 received, 0% packet loss"))
        for line in ("1 packets transmitted, 0 received", "0 packets transmitted, 1 received",
                     "2 packets transmitted, 1 received", "ping: invalid option"):
            self.assertIsNone(SUMMARY.search(line), line)

if __name__ == "__main__":
    unittest.main()
