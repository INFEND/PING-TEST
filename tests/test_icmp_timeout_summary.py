#!/usr/bin/env python3
"""Regression guard: a bare native ping timeout is not proof of ICMP loss."""
from pathlib import Path
import re

source = Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
start = source.index("private static boolean isConfirmedNoReply(")
end = source.index("\n    private void probe(", start)
method = source[start:end]

# The positive evidence must be the transmitted>0, received=0 summary.
assert "zeroReceived.matcher(output).find()" in method
assert "zeroTransmitted.matcher(output).find()" in method
assert "positiveReceived.matcher(output).find()" in method
assert not re.search(r'if\s*\(\s*text\.contains\("request timeout"\)', method), (
    "A timeout line alone must not count as packet loss"
)

cases = [
    ("Request timeout", False),
    ("Request timeout\n0 packets transmitted, 0 received", False),
    ("Request timeout\n1 packets transmitted, 1 received", False),
    ("Request timeout\n1 packets transmitted, 0 received", True),
    ("1 packets transmitted, 0 received", True),
]
summary = re.compile(r"(?m)^\s*[1-9]\d*\s+packets? transmitted,\s*0\s+(?:packets? )?received\b", re.I)
for output, expected in cases:
    actual = bool(summary.search(output))
    assert actual == expected, (output, actual, expected)
print("ICMP timeout summary regression checks: OK")
